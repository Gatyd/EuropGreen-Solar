"""
Utilitaires d'envoi d'emails pour le projet.

La fonction `send_mail` rend un template HTML, génère un fallback texte,
essaie l'envoi via Mailgun en premier puis bascule sur SMTP (Django) en cas d'échec.

Signature flexible pour couvrir la majorité des besoins courants.
"""

from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import requests
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives


def _normalize_recipients(to: Union[str, Iterable[str]]) -> List[str]:
    if isinstance(to, str):
        return [to]
    return list(to)


def _build_from_display(for_mailgun: bool, from_email: Optional[str]) -> str:
    """
    Construit l'adresse d'expéditeur affichée, ex: "Europ'Green Solar <noreply@domaine>".
    Si `from_email` est fourni et contient déjà un display-name, on le renvoie tel quel.
    """
    if from_email:
        # Si déjà au format "Nom <email@domaine>", on laisse tel quel
        if "<" in from_email and ">" in from_email:
            return from_email
        display = getattr(settings, 'DEFAULT_FROM_DISPLAY', "Europ'Green Solar")
        return f"{display} <{from_email}>"

    display = getattr(settings, 'DEFAULT_FROM_DISPLAY', "Europ'Green Solar")
    if for_mailgun:
        domain = getattr(settings, 'MAILGUN_DOMAIN', None)
        address = f"noreply@{domain}" if domain else getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
    else:
        address = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
    return f"{display} <{address}>"


def send_mail(
    template: str,
    context: Optional[Dict[str, Any]],
    subject: str,
    to: Union[str, Iterable[str]],
    *,
    from_email: Optional[str] = None,
    text_template: Optional[str] = None,
    timeout: int = 30,
    attachments: Optional[Iterable[Union[str, Tuple[str, bytes, str]]]] = None,
) -> Tuple[bool, str]:
    """
    Envoie un email en tentant d'abord Mailgun puis SMTP en fallback.

    Paramètres:
    - template: chemin du template HTML à rendre (ex: 'emails/welcome_user.html').
    - context: dictionnaire de contexte pour le rendu du template.
    - subject: sujet de l'email.
    - to: destinataire ou liste de destinataires.
    - from_email: optionnel, expéditeur (peut être au format "Nom <email>").
    - text_template: optionnel, template texte; sinon dérivé du HTML via strip_tags.
    - timeout: délai (s) pour les appels réseau (Mailgun).

    Retourne: (success: bool, message: str)
    """
    to_list = _normalize_recipients(to)

    # Enrichir le contexte avec des valeurs par défaut utiles
    ctx: Dict[str, Any] = dict(context or {})
    ctx.setdefault('frontend_url', getattr(settings, 'FRONTEND_URL', ''))

    # Rendu des templates
    html_message = render_to_string(template, ctx)
    if text_template:
        plain_message = render_to_string(text_template, ctx)
    else:
        plain_message = strip_tags(html_message)

    # 1) Tentative via Mailgun
    mailgun_configured = (
        hasattr(settings, 'MAILGUN_API_KEY') and
        hasattr(settings, 'MAILGUN_DOMAIN') and
        bool(getattr(settings, 'MAILGUN_API_KEY')) and
        bool(getattr(settings, 'MAILGUN_DOMAIN'))
    )

    if mailgun_configured:
        try:
            mg_domain = settings.MAILGUN_DOMAIN
            mg_api_key = settings.MAILGUN_API_KEY
            mg_from = _build_from_display(True, from_email)

            files = None
            # Support des pièces jointes
            # - Si str: chemin de fichier à ouvrir en binaire.
            # - Si tuple: (filename, content_bytes, mimetype)
            if attachments:
                files = []
                for att in attachments:
                    if isinstance(att, str):
                        try:
                            f = open(att, 'rb')
                            files.append(("attachment", (att.split('/')[-1] or att.split('\\')[-1], f, 'application/octet-stream')))
                        except Exception as e:
                            print(f"Impossible d'ouvrir la pièce jointe {att}: {e}")
                    else:
                        try:
                            fname, content, mtype = att
                            files.append(("attachment", (fname, content, mtype)))
                        except Exception as e:
                            print(f"Pièce jointe invalide (tuple attendu): {e}")

            response = requests.post(
                f"https://api.mailgun.net/v3/{mg_domain}/messages",
                auth=("api", mg_api_key),
                data={
                    "from": mg_from,
                    "to": ", ".join(to_list),
                    "subject": subject,
                    "text": plain_message,
                    "html": html_message,
                },
                files=files,
                timeout=timeout,
            )

            if response.status_code in (200, 202):
                return True, "Email envoyé via Mailgun"
            else:
                # Log simple et fallback
                print(f"Mailgun a renvoyé une erreur: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Erreur lors de l'envoi via Mailgun: {e}")

    # 2) Fallback SMTP (Django)
    try:
        django_from = _build_from_display(False, from_email)
        # Préparer les attachements sous forme de tuples (name, content_bytes, mimetype)
        django_attachments = []
        if attachments:
            for att in attachments:
                if isinstance(att, str):
                    try:
                        with open(att, 'rb') as f:
                            content = f.read()
                        fname = att.split('/')[-1] or att.split('\\')[-1]
                        django_attachments.append((fname, content, 'application/pdf'))
                    except Exception as e:
                        print(f"Impossible d'attacher le fichier {att}: {e}")
                else:
                    try:
                        fname, content, mtype = att
                        django_attachments.append((fname, content, mtype))
                    except Exception as e:
                        print(f"Pièce jointe invalide (tuple attendu): {e}")

        # Construire un message multi-part avec HTML et pièces jointes
        msg = EmailMultiAlternatives(subject=subject, body=plain_message, from_email=django_from, to=to_list)
        msg.attach_alternative(html_message, "text/html")
        for fname, content, mtype in django_attachments:
            msg.attach(fname, content, mtype)
        sent_count = msg.send(fail_silently=False)
        if sent_count > 0:
            return True, "Email envoyé via SMTP"
        return False, "Aucun email n'a été envoyé via SMTP"
    except Exception as e:
        return False, f"Erreur SMTP: {e}"
