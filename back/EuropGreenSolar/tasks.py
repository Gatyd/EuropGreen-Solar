"""
Tâche Celery pour l'envoi d'emails en arrière-plan.

Cette tâche permet de déléguer l'envoi d'emails à Celery pour ne pas bloquer
les requêtes HTTP et améliorer les performances.
"""

from celery import shared_task
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union
from EuropGreenSolar.email_utils import send_mail as sync_send_mail


@shared_task(
    name='EuropGreenSolar.tasks.send_email_async',
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 1 minute entre les tentatives
)
def send_email_async(
    self,
    template: str,
    context: Optional[Dict[str, Any]],
    subject: str,
    to: Union[str, List[str]],
    from_email: Optional[str] = None,
    text_template: Optional[str] = None,
    timeout: int = 30,
    attachments: Optional[List[Union[str, Tuple[str, bytes, str]]]] = None,
    save_to_log: bool = True,
) -> Tuple[bool, str]:
    """
    Tâche Celery pour envoyer un email en arrière-plan.
    
    Paramètres identiques à send_mail() de email_utils.
    Retente automatiquement en cas d'échec (max 3 fois).
    """
    try:
        print("Envoi en arrière plan...")
        success, message = sync_send_mail(
            template=template,
            context=context,
            subject=subject,
            to=to,
            from_email=from_email,
            text_template=text_template,
            timeout=timeout,
            attachments=attachments,
            save_to_log=save_to_log,
            async_send=False,  # Important: envoi synchrone dans la tâche Celery !
        )
        
        if not success:
            # Si l'envoi a échoué, on retente
            raise Exception(f"Échec de l'envoi d'email: {message}")
        
        return success, message
    
    except Exception as exc:
        # Retenter l'envoi en cas d'erreur
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        else:
            # Après 3 tentatives, on abandonne et on log l'erreur
            error_msg = f"Échec définitif après {self.max_retries} tentatives: {exc}"
            print(f"[Celery Email] {error_msg}")
            return False, error_msg
