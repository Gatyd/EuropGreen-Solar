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

# Mapping ORM -> PDF (comme on avait défini)
CERFA_FIELD_MAPPING = {
    "last_name": "D1N_nom",
    "first_name": "D1P_prenom",
    "birth_date": "D1A_naissance",
    "birth_place": "D1C_commune",
    "birth_department": "D1D_dept",
    "birth_country": "D1E_pays",

    "company_denomination": "D2D_denomination",
    "company_reason": "D2R_raison",
    "company_siret": "D2S_siret",
    "company_type": "D2J_type",

    "address_number": "D3N_numero",
    "address_street": "D3V_voie",
    "address_lieu_dit": "D3W_lieudit",
    "address_locality": "D3L_localite",
    "address_postal_code": "D3C_code",
    "address_bp": "D3B_boite",
    "address_cedex": "D3X_cedex",
    "phone": "D3T_telephone",
    "phone_country_code": "D3K_indicatif",

    "email": "D5GE1_email",
    "email_consent": "D5A_acceptation",

    "land_number": "T2Q_numero",
    "land_street": "T2V_voie",
    "land_lieu_dit": "T2W_lieudit",
    "land_locality": "T2L_localite",
    "land_postal_code": "T2C_code",
    "cadastral_prefix": "T2F_prefixe",
    "cadastral_section": "T2S_section",
    "cadastral_number": "T2N_numero",
    "cadastral_surface_m2": "T2T_superficie",
    "cadastral_prefix_p2": "T2FP2_prefixe",
    "cadastral_section_p2": "T2SP2_section",
    "cadastral_number_p2": "T2NP2_numero",
    "cadastral_surface_m2_p2": "T2TP2_superficie",
    "cadastral_prefix_p3": "T2FP3_prefixe",
    "cadastral_section_p3": "T2SP3_section",
    "cadastral_number_p3": "T2NP3_numero",
    "cadastral_surface_m2_p3": "T2TP3_superficie",

    "project_new_construction": "C2ZA1_nouvelle",
    "project_existing_works": "C2ZB1_existante",
    "project_description": "C2ZD1_description",
    "electrical_power_text": "C2ZE1_puissance",
    "peak_power_text": "C2ZP1_crete",
    "energy_destination": "C2ZR1_destination",
    "agrivoltaic_project": "C2ZI1_agrivoltaique",

    "protection_monument_abords": "X1A_ABF",
    "protection_site_classe_or_instance": "X1C_classe",
    "protection_site_patrimonial": "X2H_historique",

    "engagement_city": "E1L_lieu",
    "engagement_date": "E1D_date",
    # Signature -> nom du signataire
    "signer_name": "E1S_signature",
}


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