from pdfrw import PdfReader, PdfWriter, PdfDict, PdfName, PdfObject
from io import BytesIO

def extract_pdf_fields(pdf_path):
    """
    Récupère tous les champs d'un PDF (AcroForms)
    et retourne un dict avec le nom du champ et sa valeur.
    """
    pdf = PdfReader(pdf_path)
    fields = {}

    for page in pdf.pages:
        annotations = page.Annots
        if annotations:
            for annotation in annotations:
                if annotation.T:
                    key = annotation.T[1:-1]  # retire les parenthèses
                    value = annotation.V[1:-1] if annotation.V else ""
                    fields[key] = value
    return fields

def fill_pdf(input_pdf_path, output_pdf_path, data: dict):
    """
    Remplit un PDF avec les données fournies dans un dict {pdf_field: value}
    """
    pdf = PdfReader(input_pdf_path)

    def _is_button(annot):
        try:
            ft = getattr(annot, 'FT', None) or getattr(getattr(annot, 'Parent', None), 'FT', None)
            return ft == PdfName('Btn')
        except Exception:
            return False

    def _coerce_bool(val):
        if isinstance(val, (int, float)):
            return bool(val)
        s = str(val).strip().lower()
        return s in {"1", "true", "yes", "on", "oui", "vrai"}

    def _get_on_state(annot):
        try:
            ap = getattr(annot, 'AP', None)
            n = getattr(ap, 'N', None) if ap else None
            if isinstance(n, dict) and n:
                for k in n.keys():
                    # k is a PdfName like /Yes, /On, /1, etc.
                    name = str(k)[1:] if str(k).startswith('/') else str(k)
                    if name and name.lower() != 'off':
                        return name
        except Exception:
            pass
        return 'Yes'

    for page in pdf.pages:
        annotations = page.Annots
        if annotations:
            for annotation in annotations:
                if annotation.T:
                    key = annotation.T[1:-1]  # retirer parenthèses
                    if key in data:
                        value = data[key]
                        if _is_button(annotation):
                            on_name = _get_on_state(annotation)
                            checked = _coerce_bool(value)
                            if checked:
                                annotation.V = PdfName(on_name)
                                annotation.update(PdfDict(AS=PdfName(on_name)))
                            else:
                                annotation.V = PdfName('Off')
                                annotation.update(PdfDict(AS=PdfName('Off')))
                        else:
                            # Champ texte
                            annotation.V = "" if value is None else str(value)
                            # forcer le rerendu de l'apparence texte
                            annotation.AP = None
    # Demander aux lecteurs de régénérer les apparences des champs
    try:
        if pdf.Root and getattr(pdf.Root, 'AcroForm', None):
            pdf.Root.AcroForm.update(PdfDict(NeedAppearances=PdfObject('true')))
    except Exception:
        pass

    PdfWriter().write(output_pdf_path, pdf)


def fill_pdf_bytes(input_pdf_path: str, data: dict) -> bytes:
    """
    Remplit un PDF et retourne les octets du PDF généré en mémoire (sans écrire sur disque).
    """
    pdf = PdfReader(input_pdf_path)

    def _is_button(annot):
        try:
            ft = getattr(annot, 'FT', None) or getattr(getattr(annot, 'Parent', None), 'FT', None)
            return ft == PdfName('Btn')
        except Exception:
            return False

    def _coerce_bool(val):
        if isinstance(val, (int, float)):
            return bool(val)
        s = str(val).strip().lower()
        return s in {"1", "true", "yes", "on", "oui", "vrai"}

    def _get_on_state(annot):
        try:
            ap = getattr(annot, 'AP', None)
            n = getattr(ap, 'N', None) if ap else None
            if isinstance(n, dict) and n:
                for k in n.keys():
                    name = str(k)[1:] if str(k).startswith('/') else str(k)
                    if name and name.lower() != 'off':
                        return name
        except Exception:
            pass
        return 'Yes'

    for page in pdf.pages:
        annotations = page.Annots
        if annotations:
            for annotation in annotations:
                if annotation.T:
                    key = annotation.T[1:-1]
                    if key in data:
                        value = data[key]
                        if _is_button(annotation):
                            on_name = _get_on_state(annotation)
                            checked = _coerce_bool(value)
                            if checked:
                                annotation.V = PdfName(on_name)
                                annotation.update(PdfDict(AS=PdfName(on_name)))
                            else:
                                annotation.V = PdfName('Off')
                                annotation.update(PdfDict(AS=PdfName('Off')))
                        else:
                            annotation.V = "" if value is None else str(value)
                            annotation.AP = None
    # Demander aux lecteurs de régénérer les apparences des champs
    try:
        if pdf.Root and getattr(pdf.Root, 'AcroForm', None):
            pdf.Root.AcroForm.update(PdfDict(NeedAppearances=PdfObject('true')))
    except Exception:
        pass

    buf = BytesIO()
    PdfWriter().write(buf, pdf)
    return buf.getvalue()