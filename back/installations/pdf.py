import asyncio
from typing import Optional

from django.conf import settings
from django.http import HttpRequest


async def _render_technical_visit_pdf_playwright_async(form_id: str, request: Optional[HttpRequest] = None) -> bytes:
    """Render the Technical Visit report as PDF via the front print page."""
    from playwright.async_api import async_playwright

    base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000').rstrip('/')
    url = f"{base_url}/print/installation-forms/{form_id}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])  # type: ignore
        context = await browser.new_context()
        try:
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle")
            pdf_bytes = await page.pdf(
                format="A4",
                print_background=True,
                # margin={"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"},
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
