import playwright
from playwright.sync_api import sync_playwright

def main():
    jd = getIIMJobsJD("https://iimjobs.com/j/amadeus-labs-director-delivery-management-18-20-yrs-1702636?ref=recom_apply")
    print(jd)

def getIIMJobsJD(link) ->str:
    jd = ''
    if len(link) > 0:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)  # headless=False to *see* the browser
                context = browser.new_context(storage_state="auth.json")
                page = context.new_page()
                page.goto(link)
                page.wait_for_load_state("domcontentloaded")
                if isAlreadyApplied(page):
                    jd = 'APPLIED'
                else:
                    jd = extractJD(page)
                browser.close()
            except playwright.sync_api.TimeoutError as e:
                jd = "ERROR_TIMEOUT"
    else:
        jd = "NO_LINK"
    return jd


def isAlreadyApplied(page):
    try:
        content = page.locator('.MuiBox-root.mui-style-mtktrd').inner_text(timeout=5000)
    except playwright.sync_api.TimeoutError:
        try:
            content = page.locator('.MuiBox-root.mui-style-bjgt5f').inner_text(timeout=5000)
        except playwright.sync_api.TimeoutError:
            content = 'APPLIED_STATUS_NOT_SCRAPABLE'
            return False

    if content == None:
        return False
    elif content.lower().find("applied") != -1:
        return True
    else:
        return False

def extractJD(page):
    try:
        jd = page.locator('.MuiBox-root.mui-style-12ypbxt').inner_text(timeout=5000)
    except playwright.sync_api.TimeoutError:
        try:
            jd = page.locator('.MuiBox-root.mui-style-669c1p').inner_text(timeout=5000)
        except playwright.sync_api.TimeoutError:
            jd = "NOT_SCRAPABLE"
    return jd

if __name__ == "__main__":
    main()