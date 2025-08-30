import base64
from typing import Optional, Tuple
from django.core.files.base import ContentFile
from django.http import HttpRequest


def get_client_ip(request: HttpRequest) -> Optional[str]:
    """Récupère l'adresse IP du client à partir des en-têtes de la requête."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # X-Forwarded-For peut contenir une liste d'IPs
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def decode_data_url_image(data_url: Optional[str]) -> Tuple[Optional[ContentFile], Optional[str]]:
    """Décoder une data URL d'image en (ContentFile, ext) ou (None, None) si invalide."""
    if not data_url or not data_url.startswith('data:image/'):
        return None, None

    try:
        header, data = data_url.split(',', 1)
        ext = header.split(';')[0].split('/')[1]
        if ext == 'jpeg':
            ext = 'jpg'

        image_data = base64.b64decode(data)
        return ContentFile(image_data), ext
    except Exception:
        return None, None
