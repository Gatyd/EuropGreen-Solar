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


def _serialize_context(context: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Sérialise le contexte pour qu'il soit JSON serializable (pour Celery).
    Convertit les objets Django en dictionnaires simples.
    """
    if not context:
        return context
    
    import json
    from django.db import models
    from django.core.serializers.json import DjangoJSONEncoder
    
    def serialize_value(value):
        """Sérialise une valeur récursivement."""
        # None, bool, int, float, str : déjà sérialisables
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        
        # Listes et tuples
        if isinstance(value, (list, tuple)):
            return [serialize_value(item) for item in value]
        
        # Dictionnaires
        if isinstance(value, dict):
            return {k: serialize_value(v) for k, v in value.items()}
        
        # Modèles Django : extraire les champs principaux
        if isinstance(value, models.Model):
            # Construire un dict avec les champs du modèle
            serialized = {
                '__model__': f"{value._meta.app_label}.{value._meta.model_name}",
                '__pk__': value.pk,
            }
            
            # Ajouter les champs simples (non-relations)
            for field in value._meta.fields:
                field_name = field.name
                try:
                    field_value = getattr(value, field_name)
                    
                    # Ignorer les fichiers/images (non JSON serializable)
                    if isinstance(field, (models.FileField, models.ImageField)):
                        if field_value:
                            serialized[field_name] = str(field_value)
                        else:
                            serialized[field_name] = None
                    # Relations (ForeignKey, etc.) : stocker l'ID
                    elif isinstance(field, models.ForeignKey):
                        if field_value:
                            serialized[field_name] = {
                                'id': field_value.pk,
                                '__str__': str(field_value)
                            }
                        else:
                            serialized[field_name] = None
                    else:
                        # Autres champs : sérialiser directement
                        serialized[field_name] = serialize_value(field_value)
                                
                except Exception:
                    # En cas d'erreur, ignorer le champ
                    pass
            
            return serialized
        
        # Autres objets : convertir en string
        try:
            # Tenter de sérialiser avec DjangoJSONEncoder
            json.dumps(value, cls=DjangoJSONEncoder)
            return value
        except (TypeError, ValueError):
            # Fallback : convertir en string
            return str(value)
    
    return {k: serialize_value(v) for k, v in context.items()}


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
    save_to_log: bool = True,
    async_send: bool = True,
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
    - attachments: optionnel, liste de pièces jointes (chemins ou tuples).
    - save_to_log: si True (défaut), enregistre l'email dans EmailLog après envoi réussi.
                   Passer False pour les emails contenant des données sensibles.
    - async_send: si True (défaut), envoie l'email en arrière-plan via Celery.
                  Si False, envoie synchrone immédiat (bloque la requête).

    Retourne: (success: bool, message: str)
    
    Note: Si async_send=True, retourne (True, "Email mis en file d'attente") immédiatement
          sans attendre l'envoi réel. L'email sera envoyé par un worker Celery.
    """
    # Si envoi asynchrone demandé, déléguer à Celery
    if async_send:
        try:
            print(f"[EMAIL] Tentative d'envoi asynchrone vers {to}")
            # Import ici pour éviter les dépendances circulaires
            from EuropGreenSolar.tasks import send_email_async
            
            # Normaliser les destinataires en liste pour sérialisation JSON
            to_list = _normalize_recipients(to)
            
            # Sérialiser le contexte pour qu'il soit JSON serializable
            serializable_context = _serialize_context(context)
            print(f"[EMAIL] Contexte sérialisé, envoi à Celery...")
            
            # Convertir les attachments en format sérialisable si nécessaire
            serializable_attachments = None
            if attachments:
                serializable_attachments = []
                for att in attachments:
                    if isinstance(att, str):
                        # Chemin de fichier - garder tel quel
                        serializable_attachments.append(att)
                    else:
                        # Tuple (filename, bytes, mimetype) - garder tel quel
                        serializable_attachments.append(att)
            
            # Envoyer la tâche à Celery
            result = send_email_async.delay(
                template=template,
                context=serializable_context,
                subject=subject,
                to=to_list,
                from_email=from_email,
                text_template=text_template,
                timeout=timeout,
                attachments=serializable_attachments,
                save_to_log=save_to_log,
            )
            print(f"[EMAIL] Tâche Celery créée avec ID: {result.id}")
            
            return True, "Email mis en file d'attente pour envoi asynchrone"
        
        except Exception as e:
            # Si Celery n'est pas disponible, fallback sur envoi synchrone
            print(f"Celery non disponible, envoi synchrone: {e}")
            # Continue avec l'envoi synchrone ci-dessous
    
    # Envoi synchrone (si async_send=False ou si Celery a échoué)
    to_list = _normalize_recipients(to)

    # Enrichir le contexte avec des valeurs par défaut utiles
    ctx: Dict[str, Any] = dict(context or {})
    ctx.setdefault('frontend_url', getattr(settings, 'FRONTEND_URL', ''))
    ctx.setdefault('site_url', getattr(settings, 'SITE_URL', ''))

    # Rendu des templates
    html_message = render_to_string(template, ctx)
    if text_template:
        plain_message = render_to_string(text_template, ctx)
    else:
        plain_message = strip_tags(html_message)

    # Variables pour tracking
    send_method = None
    success = False
    message = ""
    final_from_email = None
    attachments_info_for_log = []

    # Préparer les infos sur les pièces jointes pour le log
    if attachments and save_to_log:
        for att in attachments:
            if isinstance(att, str):
                fname = att.split('/')[-1] or att.split('\\')[-1]
                attachments_info_for_log.append({
                    'filename': fname,
                    'mimetype': 'application/octet-stream'
                })
            else:
                try:
                    fname, _, mtype = att
                    attachments_info_for_log.append({
                        'filename': fname,
                        'mimetype': mtype
                    })
                except Exception:
                    pass

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
                send_method = 'mailgun'
                success = True
                message = "Email envoyé via Mailgun"
                final_from_email = mg_from
                # Pas de return ici, on continue pour enregistrer le log
            else:
                # Log simple et fallback
                print(f"Mailgun a renvoyé une erreur: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Erreur lors de l'envoi via Mailgun: {e}")

    # 2) Fallback SMTP (Django) - seulement si Mailgun n'a pas réussi
    if not success:
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
                send_method = 'smtp'
                success = True
                message = "Email envoyé via SMTP"
                final_from_email = django_from
            else:
                success = False
                message = "Aucun email n'a été envoyé via SMTP"
        except Exception as e:
            success = False
            message = f"Erreur SMTP: {e}"
    
    # 3) Enregistrement dans EmailLog si l'envoi a réussi et save_to_log est True
    if success and save_to_log:
        try:
            from admin_platform.models import EmailLog
            
            EmailLog.objects.create(
                recipients=to_list,
                subject=subject,
                html_content=html_message,
                plain_content=plain_message,
                from_email=final_from_email or from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', ''),
                template_used=template,
                send_method=send_method,
                attachments_info=attachments_info_for_log if attachments_info_for_log else None,
            )
        except Exception as e:
            # En cas d'erreur lors de l'enregistrement, on continue quand même
            # car l'email a été envoyé avec succès
            print(f"Erreur lors de l'enregistrement du log d'email: {e}")
    
    return success, message
