from django.db import migrations
from django.core.files.base import ContentFile
import os


DPC_KEYS = [f"dpc{i}" for i in range(1, 9)] + ["dpc11"]


def forwards(apps, schema_editor):
    Cerfa16702 = apps.get_model("administrative", "Cerfa16702")
    Cerfa16702Attachment = apps.get_model("administrative", "Cerfa16702Attachment")

    for cerfa in Cerfa16702.objects.all():
        for key in DPC_KEYS:
            file_field = getattr(cerfa, key, None)
            if not file_field:
                continue
            try:
                if not getattr(file_field, 'name', None):
                    continue
                # Ne pas dupliquer si déjà une attachment ordering=1
                if Cerfa16702Attachment.objects.filter(cerfa_id=cerfa.id, dpc_key=key, ordering=1).exists():
                    continue
                # Lire le contenu pour le recopier dans le nouveau répertoire upload_to
                try:
                    file_field.open('rb')
                except Exception:
                    pass
                data = file_field.read()
                if not data:
                    continue
                base_name = os.path.basename(file_field.name)
                new_attachment = Cerfa16702Attachment(
                    cerfa_id=cerfa.id,
                    dpc_key=key,
                    ordering=1,
                )
                # Sauvegarde: déclenche upload_to du modèle Attachment
                new_attachment.file.save(base_name, ContentFile(data), save=True)
            except Exception:
                # migration best-effort: on ignore les erreurs individuelles
                continue


def backwards(apps, schema_editor):
    """Reverse: si les anciens champs sont vides, on remet le premier attachment ordering=1 dedans.
    Best-effort uniquement, on ne supprime pas les attachments.
    """
    Cerfa16702 = apps.get_model("administrative", "Cerfa16702")
    Cerfa16702Attachment = apps.get_model("administrative", "Cerfa16702Attachment")

    for cerfa in Cerfa16702.objects.all():
        for key in DPC_KEYS:
            try:
                file_field = getattr(cerfa, key, None)
                if file_field and getattr(file_field, 'name', None):
                    continue  # déjà présent
                att = (
                    Cerfa16702Attachment.objects
                    .filter(cerfa_id=cerfa.id, dpc_key=key, ordering=1)
                    .order_by('created_at')
                    .first()
                )
                if not att:
                    continue
                # Copier le contenu inversement dans l'ancien champ
                try:
                    att.file.open('rb')
                except Exception:
                    pass
                data = att.file.read()
                if not data:
                    continue
                base_name = os.path.basename(att.file.name)
                # Affecter directement (réutilise upload_to du champ legacy)
                getattr(cerfa, key).save(base_name, ContentFile(data), save=True)
            except Exception:
                continue


class Migration(migrations.Migration):
    dependencies = [
        ("administrative", "0010_cerfa16702attachment"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
