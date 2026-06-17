from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.iimjobs.com/login")

    print("Log in manually in the browser window, then come back here and press Enter...")
    input()

    context.storage_state(path="auth.json")
    print("Saved session to auth.json")

    browser.close()