import asyncio
from typing import Optional

from django.conf import settings
from django.http import HttpRequest

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
    "destination_primary_residence": "C2ZF1_principale",
    "destination_secondary_residence": "C2ZF2_secondaire",

    "protection_monument_abords": "X1A_ABF",
    "protection_site_classe_or_instance": "X1C_classe",
    "protection_site_patrimonial": "X2H_historique",

    "engagement_city": "E1L_lieu",
    "engagement_date": "E1D_date",
    # Signature -> nom du signataire
    "signer_name": "E1S_signature",
}



async def _render_cerfa16702_pdf_playwright_async(form_id: str, request: Optional[HttpRequest] = None) -> bytes:
    """Render the CERFA 16702 as PDF via the front print page."""
    from playwright.async_api import async_playwright

    base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000').rstrip('/')
    url = f"{base_url}/print/installation-form/{form_id}/cerfa16702"

    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])  # type: ignore
        context = await browser.new_context()
        try:
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle")
            pdf_bytes = await page.pdf(
                format="A4",
                print_background=True,
                display_header_footer=True,
                margin={"top": "12mm", "right": "10mm", "bottom": "16mm", "left": "10mm"},
                header_template='<div style="font-size:8px; color:#999; width:100%; padding:4px 10px;"></div>',
                footer_template='''
                    <div style="font-size:10px; color:#666; width:100%; padding:6px 10px; text-align:center;">
                        Page <span class="pageNumber"></span> / <span class="totalPages"></span>
                    </div>
                ''',
            )
            return pdf_bytes
        finally:
            try:
                await context.close()
            except Exception:
                pass
            try:
                await browser.close()
            except Exception:
                pass


def render_cerfa16702_pdf(form_id: str, request: Optional[HttpRequest] = None) -> Optional[bytes]:
    """Sync wrapper to render the CERFA 16702 PDF for the given form id."""
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            new_loop = asyncio.new_event_loop()
            try:
                return new_loop.run_until_complete(_render_cerfa16702_pdf_playwright_async(form_id, request))
            finally:
                new_loop.close()
        else:
            return asyncio.run(_render_cerfa16702_pdf_playwright_async(form_id, request))
    except Exception:
        return None
