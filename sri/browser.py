from playwright.sync_api import sync_playwright
from config.settings import DEFAULT_TIMEOUT, HEADLESS, NAVIGATION_TIMEOUT


def create_browser():
    """Devuelve recursos Playwright; el llamador los cierra en finally."""
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=HEADLESS)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()
    page.set_default_timeout(DEFAULT_TIMEOUT)
    page.set_default_navigation_timeout(NAVIGATION_TIMEOUT)
    return playwright, browser, context, page
