import asyncio
from typing import Optional, Dict, Any, List

from django.conf import settings
from django.http import HttpRequest
import os, io, base64, mimetypes

try:
    from pdfrw import PdfReader, PdfWriter, PageMerge
except Exception:
    PdfReader = None  # type: ignore
    PdfWriter = None  # type: ignore
    PageMerge = None  # type: ignore

from administrative.consuel_views import _draw_overlay, _filter_items_for_page
from administrative.serializers import EnedisMandatePreviewSerializer
from installations.models import Form


async def _render_technical_visit_pdf_playwright_async(form_id: str, request: Optional[HttpRequest] = None) -> bytes:
    """Render the Technical Visit report as PDF via the front print page."""
    from playwright.async_api import async_playwright

    base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000').rstrip('/')
    url = f"{base_url}/print/installation-form/{form_id}/technical-visit"

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
                # margin={"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"},
                # header_template='<div style="font-size:8px; color:#999; width:100%; padding:4px 10px;"></div>',
                footer_template='''
                    <div style="font-size:11px; color:#666; width:100%; padding:6px 10px; text-align:center;">
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


def render_technical_visit_pdf(form_id: str, request: Optional[HttpRequest] = None) -> Optional[bytes]:
    """Sync wrapper to render the Technical Visit report PDF for the given form id."""
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            new_loop = asyncio.new_event_loop()
            try:
                return new_loop.run_until_complete(_render_technical_visit_pdf_playwright_async(form_id, request))
            finally:
                new_loop.close()
        else:
            return asyncio.run(_render_technical_visit_pdf_playwright_async(form_id, request))
    except Exception:
        return None


async def _render_representation_mandate_pdf_playwright_async(form_id: str, request: Optional[HttpRequest] = None) -> bytes:
    """Render the Representation Mandate PDF via the front print page."""
    from playwright.async_api import async_playwright

    base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000').rstrip('/')
    url = f"{base_url}/print/installation-form/{form_id}/representation-mandate"

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


def render_representation_mandate_pdf(form_id: str, request: Optional[HttpRequest] = None) -> Optional[bytes]:
    """Sync wrapper to render the Representation Mandate PDF for the given form id."""
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            new_loop = asyncio.new_event_loop()
            try:
                return new_loop.run_until_complete(_render_representation_mandate_pdf_playwright_async(form_id, request))
            finally:
                new_loop.close()
        else:
            return asyncio.run(_render_representation_mandate_pdf_playwright_async(form_id, request))
    except Exception:
        return None


def render_enedis_mandate_pdf(form_id: str, request: Optional[HttpRequest] = None) -> Optional[bytes]:
    """Génère le PDF Mandat ENEDIS via overlay pdfrw en se basant sur les données persistées."""
    try:
        if PdfReader is None or PdfWriter is None or PageMerge is None:
            return None

        # Charger la fiche et le mandat associé
        f = Form.objects.select_related('enedis_mandate', 'enedis_mandate__client_signature', 'enedis_mandate__installer_signature').get(pk=form_id)
        em = getattr(f, 'enedis_mandate', None)
        if not em:
            return None

        # Construire le payload pour le serializer preview
        payload: Dict[str, Any] = {}
        field_list = [
            # Client
            'client_type', 'client_civility', 'client_name', 'client_address',
            'client_company_name', 'client_company_siret', 'client_company_represented_by_name', 'client_company_represented_by_role',
            # Entreprise mandataire
            'contractor_type', 'contractor_civility', 'contractor_name', 'contractor_address',
            'contractor_company_name', 'contractor_company_siret', 'contractor_company_represented_by_name', 'contractor_company_represented_by_role',
            # Mandat
            'mandate_type', 'authorize_signature', 'authorize_payment', 'authorize_l342', 'authorize_network_access',
            # Localisation et nature de raccordement
            'geographic_area', 'connection_nature',
            # Signatures (lieux)
            'client_location', 'installer_location',
        ]
        for fld in field_list:
            payload[fld] = getattr(em, fld, None)

        # Signatures -> convertir en data URLs pour le serializer
        def _file_to_data_url(dj_file) -> str | None:
            try:
                if not dj_file:
                    return None
                fobj = dj_file
                try:
                    fobj.open('rb')
                except Exception:
                    pass
                data = fobj.read()
                if not data:
                    return None
                ctype, _ = mimetypes.guess_type(getattr(fobj, 'name', '') or '')
                if not ctype:
                    ctype = 'image/png'
                b64 = base64.b64encode(data).decode('ascii')
                return f"data:{ctype};base64,{b64}"
            except Exception:
                return None

        cs = getattr(em, 'client_signature', None)
        if cs and getattr(cs, 'signature_image', None):
            du = _file_to_data_url(cs.signature_image)
            if du:
                payload['client_signature_data_url'] = du
                payload['client_signature_signer_name'] = getattr(cs, 'signer_name', '')
                try:
                    if getattr(cs, 'signed_at', None):
                        payload['client_signature_date'] = cs.signed_at.strftime('%d/%m/%Y')
                except Exception:
                    pass
        isg = getattr(em, 'installer_signature', None)
        if isg and getattr(isg, 'signature_image', None):
            du2 = _file_to_data_url(isg.signature_image)
            if du2:
                payload['installer_signature_data_url'] = du2
                payload['installer_signature_signer_name'] = getattr(isg, 'signer_name', '')
                try:
                    if getattr(isg, 'signed_at', None):
                        payload['installer_signature_date'] = isg.signed_at.strftime('%d/%m/%Y')
                except Exception:
                    pass

        # Valider et construire les items
        ser = EnedisMandatePreviewSerializer(data=payload)
        ser.is_valid(raise_exception=True)
        items = ser.get_items()
        y_offset_mm = ser.validated_data.get('y_offset_mm', 8.0)

        # Charger template et fusionner
        input_pdf = os.path.join(settings.BASE_DIR, 'static', 'pdf', 'Enedis-FOR-RAC_02E.pdf')
        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        for i, pg in enumerate(reader.pages, 1):
            try:
                m = pg.MediaBox
                width = float(m[2]) - float(m[0])
                height = float(m[3]) - float(m[1])
            except Exception:
                from reportlab.lib.pagesizes import letter as _letter
                width, height = _letter
            page_items = _filter_items_for_page(items, i, height)
            if not page_items:
                writer.addpage(pg)
                continue
            overlay_buf = _draw_overlay(width, height, page_items, y_offset_mm)
            try:
                ov_reader = PdfReader(overlay_buf)
                ov_pages = getattr(ov_reader, 'pages', []) or []
                if len(ov_pages) == 0:
                    writer.addpage(pg)
                    continue
                PageMerge(pg).add(ov_pages[0]).render()
                writer.addpage(pg)
            except Exception:
                writer.addpage(pg)

        out_buf = io.BytesIO()
        writer.write(out_buf)
        out_buf.seek(0)
        return out_buf.getvalue()
    except Exception:
        return None
    

async def _render_installation_completed_pdf_playwright_async(form_id: str, request: Optional[HttpRequest] = None) -> bytes:
    """Render the Installation Completed report as PDF via the front print page."""
    from playwright.async_api import async_playwright

    base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000').rstrip('/')
    url = f"{base_url}/print/installation-form/{form_id}/installation-completed"


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
                footer_template='''
                    <div style="font-size:11px; color:#666; width:100%; padding:6px 10px; text-align:center;">
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


def render_installation_completed_pdf(form_id: str, request: Optional[HttpRequest] = None) -> Optional[bytes]:
    """Sync wrapper to render the Installation Completed report PDF for the given form id."""
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            new_loop = asyncio.new_event_loop()
            try:
                return new_loop.run_until_complete(_render_installation_completed_pdf_playwright_async(form_id, request))
            finally:
                new_loop.close()
        else:
            return asyncio.run(_render_installation_completed_pdf_playwright_async(form_id, request))
    except Exception:
        return None