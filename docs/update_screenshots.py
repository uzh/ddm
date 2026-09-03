import os
import time
from pathlib import Path

from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

BASE_URL = "http://127.0.0.1:8000/"
PROJECT_ID = "F1svPg1v"
PROJECT_SLUG = "your-individual-url"
FILE_UPLOADER_ID = 27

# Resolve resource paths relative to this file so the script works regardless of
# the current working directory it is started from.
DOCS_DIR = Path(__file__).resolve().parent
DEMO_ZIP_PATH = DOCS_DIR / "takeout-demo.zip"

# Browser window width; matches the viewport the committed screenshots use. The
# height is grown per screenshot so elements taller than the viewport are still
# captured in full (see screenshot_element).
WINDOW_WIDTH = 1680


def initialize_driver():
    firefox_options = Options()
    firefox_options.set_preference("intl.accept_languages", "en,en-US")  # Force English UI.
    firefox_options.set_preference("general.useragent.locale", "en-US")
    if os.environ.get("DDM_HEADLESS"):
        firefox_options.add_argument("--headless")

    driver = webdriver.Firefox(options=firefox_options)
    driver.set_window_size(WINDOW_WIDTH, 2160)
    return driver

def login_to_ddm(driver, url):
    driver.get(url)

    username_field = driver.find_element(By.ID, "id_username")
    username_field.send_keys("admin")

    password_field = driver.find_element(By.ID, "id_password")
    password_field.send_keys("password")

    login_button = driver.find_element(By.ID, "login-btn")
    login_button.click()

def hide_debug_toolbar(driver):
    """Remove the Django Debug Toolbar so it does not overlay the screenshots.

    The test project enables ``debug_toolbar`` whenever ``DEBUG`` is on; its
    fixed-position panel would otherwise cover the right-hand side of every
    captured element. Recent versions render the toolbar inside a shadow root
    attached to ``#djDebugRoot``, so removing that host element is enough.
    """
    driver.execute_script(
        "document.querySelectorAll("
        "'#djDebugRoot, #djDebug, #djDebugToolbar, #djDebugToolbarHandle'"
        ").forEach(function (el) { el.remove(); });"
        "try { localStorage.setItem('djdt.show', 'false'); } catch (e) {}"
    )


def screenshot_element(driver, element, path):
    """Capture a full element, even when it is taller than the viewport.

    geckodriver clips element screenshots of tall elements that contain
    sticky/fixed-positioned descendants (the questionnaire's sticky question
    headers, for example). Growing the window so the element fits entirely
    avoids the clipping.
    """
    hide_debug_toolbar(driver)
    needed_height = driver.execute_script(
        "const el = arguments[0];"
        "const rect = el.getBoundingClientRect();"
        "return Math.ceil(Math.max("
        "  document.body.scrollHeight,"
        "  document.documentElement.scrollHeight,"
        "  rect.height + rect.top + window.scrollY"
        "));",
        element,
    )
    driver.set_window_size(WINDOW_WIDTH, max(1000, int(needed_height) + 250))
    time.sleep(0.5)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.3)
    hide_debug_toolbar(driver)
    element.screenshot(path)


def js_click(driver, element):
    """Click an element via JavaScript.

    The consent toggle and some buttons are visually replaced by custom-styled
    elements that intercept native pointer events, which makes Selenium's
    ``element.click()`` raise ``ElementClickInterceptedException``. Dispatching
    the click through the DOM sidesteps that.
    """
    driver.execute_script("arguments[0].click();", element)


def set_combined_consent(driver, enabled):
    """Open the file uploader edit page and set the combined consent toggle."""
    url = f"projects/{PROJECT_ID}/data-donation/file-uploader/{FILE_UPLOADER_ID}/edit/"
    driver.get(BASE_URL + url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[id="id_combined_consent"]'))
    )
    consent_toggle = driver.find_element(By.CSS_SELECTOR, 'input[id="id_combined_consent"]')
    time.sleep(1)

    driver.execute_script("arguments[0].scrollIntoView({ block: 'center' });", consent_toggle)
    time.sleep(1)

    # The visible toggle is a styled element that intercepts pointer events, so
    # the checkbox itself has to be toggled through the DOM.
    if consent_toggle.is_selected() != enabled:
        js_click(driver, consent_toggle)

    # "Display name" is a required field on this form. If the demo uploader has
    # none set, the save would be rejected (silently, client-side), so fill it
    # with the uploader's internal name.
    display_name = driver.find_element(By.CSS_SELECTOR, 'input[id="id_display_name"]')
    if not display_name.get_attribute("value"):
        name_value = driver.find_element(By.CSS_SELECTOR, 'input[id="id_name"]').get_attribute("value")
        display_name.send_keys(name_value or "Uploader")

    # The submit button sits outside <form id="base-form"> (linked via its
    # ``form`` attribute); a synthetic click on such a button does not submit
    # the form, so a real click is required here.
    save_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"][value="Update Uploader"]')
    driver.execute_script("arguments[0].scrollIntoView({ block: 'center' });", save_button)
    time.sleep(1)
    save_button.click()

    # Wait for the form submission to complete and the page to reload before
    # the caller navigates on (otherwise the participant frontend may still be
    # served the previous configuration).
    WebDriverWait(driver, 15).until(EC.staleness_of(save_button))
    time.sleep(2)


def prepare_project(driver):
    set_combined_consent(driver, enabled=False)

def add_margins_to_sc(sc_path):
    # Load screenshot.
    img = Image.open(sc_path)
    width, height = img.size

    # Add margins on top and bottom.
    margin_top = 10
    margin_bottom = 20
    new_height = height + margin_top + margin_bottom
    new_img = Image.new("RGB", (width, new_height), color="white")
    new_img.paste(img, (0, margin_top))

    # Replace the original screenshot.
    new_img.save(sc_path)

# CSS class the Uploader frontend puts on each rendered question body, mapped to
# the slug used in the screenshot file name (questionnaire_<slug>.png).
QUESTION_TYPE_SLUGS = {
    "ddm-question--single-choice": "singlechoice",
    "ddm-question--multi-choice": "multichoice",
    "ddm-question--matrix": "matrix",
    "ddm-question--semantic-diff": "semanticdifferential",
    "ddm-question--transition": "textblock",
    "ddm-question--open": "open",
}


def pass_briefing(driver):
    """Accept the briefing consent if the participation flow redirected to it.

    Visiting the data donation / questionnaire page directly bounces the
    participant back to the briefing page until they have consented.
    """
    if "briefing" not in driver.current_url:
        return
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "consent_yes")))
    js_click(driver, driver.find_element(By.ID, "consent_yes"))
    js_click(driver, driver.find_element(By.CLASS_NAME, "flow-btn"))
    WebDriverWait(driver, 15).until_not(EC.url_contains("briefing"))
    time.sleep(1)


def uploader_click_next(driver):
    """Click the Uploader's primary 'next' control.

    The redesigned Uploader is a wizard (Instructions -> Upload -> Review). The
    step navigation lives in a button with class ``ddm-primary-button-base`` and
    a right chevron; on the instructions step that button sits inside
    ``.instruction-nav-next`` instead.
    """
    clicked = driver.execute_script(
        "const visible = (el) => el && el.offsetParent !== null && !el.disabled;"
        "const buttons = Array.prototype.slice"
        "  .call(document.querySelectorAll('button.ddm-primary-button-base'))"
        "  .filter(b => visible(b) && b.querySelector('i.bi-chevron-right'));"
        "const target = buttons.find(b => !b.closest('.instruction-nav-next'))"
        "  || buttons[0];"
        "if (!target) { return false; }"
        "target.scrollIntoView({ block: 'center' });"
        "target.click();"
        "return true;"
    )
    if not clicked:
        raise RuntimeError("Could not find the Uploader 'next' button.")
    time.sleep(1.5)


def advance_to_upload_step(driver):
    """Move the Uploader from the instructions step to the file upload step.

    The instructions step can span several pages: each one has a secondary
    "next page" button, and only the last page shows the primary button that
    jumps to the upload step.
    """
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".uploader-container"))
    )
    for _ in range(15):
        drop_zones = driver.find_elements(By.CSS_SELECTOR, ".ddm-file-drop")
        if drop_zones and drop_zones[0].is_displayed():
            return
        instruction_buttons = [
            b for b in driver.find_elements(By.CSS_SELECTOR, ".instruction-nav-next button")
            if b.is_displayed() and b.is_enabled()
        ]
        if instruction_buttons:
            button = instruction_buttons[-1]
            driver.execute_script("arguments[0].scrollIntoView({ block: 'center' });", button)
            js_click(driver, button)
            time.sleep(1)
        else:
            uploader_click_next(driver)
    raise RuntimeError("Could not reach the Uploader upload step.")


def advance_to_review_step(driver):
    """Move the Uploader from the upload step to the review-and-consent step."""
    for _ in range(10):
        consent_labels = [
            el for el in driver.find_elements(By.CSS_SELECTOR, "label[for^='donate-agree-']")
            if el.is_displayed()
        ]
        if consent_labels:
            return
        uploader_click_next(driver)
    raise RuntimeError("Could not reach the Uploader review step.")


def access_donation_stage(driver):
    """Prepare the data donation page for the initial (instructions step) screenshot."""
    pass_briefing(driver)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".uploader-container"))
    )
    time.sleep(1)


def upload_file(driver):
    """Walk the Uploader through instructions -> upload -> review with the demo file."""
    pass_briefing(driver)
    advance_to_upload_step(driver)

    file_input = driver.find_element(By.CSS_SELECTOR, "input[class='d-none'][type='file']")
    file_input.send_keys(str(DEMO_ZIP_PATH))

    # Wait until the frontend has finished extracting the uploaded file.
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".ddm-file-drop .bi-check-circle"))
    )
    time.sleep(1)

    advance_to_review_step(driver)
    time.sleep(1)

def enable_all_in_one_consent(driver):
    set_combined_consent(driver, enabled=True)

    url = f"studies/{PROJECT_SLUG}/data-donation/"
    driver.get(BASE_URL + url)

    upload_file(driver)

def agree_to_donate(driver, element=None):
    url = f"studies/{PROJECT_SLUG}/data-donation/"
    driver.get(BASE_URL + url)
    upload_file(driver)  # Leaves the Uploader on the review-and-consent step.

    # Consent to every blueprint (or the single combined-consent question).
    for label in driver.find_elements(By.CSS_SELECTOR, "label[for^='donate-agree-']"):
        if label.is_displayed():
            driver.execute_script("arguments[0].scrollIntoView({ block: 'center' });", label)
            js_click(driver, label)
            time.sleep(0.3)
    time.sleep(1)

    # Advancing past the last step submits the donation and redirects onwards.
    uploader_click_next(driver)
    WebDriverWait(driver, 20).until(EC.url_contains("questionnaire"))
    time.sleep(5)
    return element

def create_question_screenshots(driver, element):
    hide_debug_toolbar(driver)
    captured = set()
    for _ in range(20):
        for container in driver.find_elements(By.CSS_SELECTOR, ".question-app-container"):
            if not container.is_displayed():
                continue
            bodies = container.find_elements(By.CSS_SELECTOR, ".ddm-question")
            if not bodies:
                continue
            classes = (bodies[0].get_attribute("class") or "").split()
            slug = next((QUESTION_TYPE_SLUGS[c] for c in classes if c in QUESTION_TYPE_SLUGS), None)
            if slug is None or slug in captured:
                continue
            driver.execute_script("arguments[0].scrollIntoView({ block: 'center' });", container)
            time.sleep(0.5)
            target = container.find_element(By.CSS_SELECTOR, ".question-container")
            target.screenshot(get_output_dir("researchers") + f"questionnaire_{slug}.png")
            captured.add(slug)

        if len(captured) >= len(QUESTION_TYPE_SLUGS):
            break

        # Advance to the next questionnaire page. A page with unanswered
        # soft-required questions only advances on the second click (the first
        # click just reveals the hint), so try twice before giving up.
        advanced = False
        for _ in range(2):
            buttons = [
                b for b in driver.find_elements(By.CSS_SELECTOR, "#next-page-btn, .flow-btn")
                if b.is_displayed() and b.is_enabled()
            ]
            if not buttons:
                break
            js_click(driver, buttons[0])
            time.sleep(2)
            if _page_changed(driver, captured):
                advanced = True
                break
        if not advanced:
            break

    # Return to the first page so questionnaire_page.png shows the questionnaire
    # start rather than wherever the paging above stopped.
    driver.execute_script(
        "try { localStorage.removeItem('questionnaire-current-page'); } catch (e) {}"
    )
    driver.get(BASE_URL + f"studies/{PROJECT_SLUG}/questionnaire/")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".question-app-container"))
    )
    time.sleep(1)
    return driver.find_element(By.ID, "ddm-participation-main")


def _page_changed(driver, captured):
    """True if a question type not yet captured is now visible."""
    for container in driver.find_elements(By.CSS_SELECTOR, ".question-app-container"):
        if not container.is_displayed():
            continue
        bodies = container.find_elements(By.CSS_SELECTOR, ".ddm-question")
        if not bodies:
            continue
        classes = (bodies[0].get_attribute("class") or "").split()
        slug = next((QUESTION_TYPE_SLUGS[c] for c in classes if c in QUESTION_TYPE_SLUGS), None)
        if slug and slug not in captured:
            return True
    return False


def access_debriefing(driver):
    for i in range(20):
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "flow-btn")))
        next_button = driver.find_element(By.CLASS_NAME, "flow-btn")
        driver.execute_script("arguments[0].scrollIntoView({ block: 'center' });", next_button)
        time.sleep(1)
        js_click(driver, next_button)
        time.sleep(1)
        if "debriefing" in driver.current_url:
            break

def scroll_to_bottom(driver, element=None):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    return element

def load_element_list():
    elements_to_capture = [
        {
            "module": "researchers",
            "sc_name": "project_list.png",
            "url": "projects/",
            "element_id": "ddm-main",
            "function_pre": None,
            "function_post": None,
        },
        {
            "module": "researchers",
            "sc_name": "project_create.png",
            "url": "projects/create/",
            "element_id": "ddm-main",
            "function_pre": None,
            "function_post": scroll_to_bottom,
        },
        {
            "module": "researchers",
            "sc_name": "project_hub.png",
            "url": f"projects/{PROJECT_ID}/",
            "element_id": "ddm-main",
            "function_pre": None,
            "function_post": scroll_to_bottom,
        },
        {
            "module": "researchers",
            "sc_name": "project_settings_pub_info.png",
            "url": f"projects/{PROJECT_ID}/edit/public-information",
            "element_id": "ddm-main",
            "function_pre": None,
            "function_post": scroll_to_bottom,
        },
        {
            "module": "researchers",
            "sc_name": "project_settings_url_param.png",
            "url": f"projects/{PROJECT_ID}/edit/url-parameter",
            "element_id": "ddm-main",
            "function_pre": None,
            "function_post": None,
        },
        {
            "module": "researchers",
            "sc_name": "project_settings_redirect.png",
            "url": f"projects/{PROJECT_ID}/edit/redirect",
            "element_id": "ddm-main",
            "function_pre": None,
            "function_post": None,
        },
        {
            "module": "researchers",
            "sc_name": "project_settings_branding.png",
            "url": f"projects/{PROJECT_ID}/edit/branding",
            "element_id": "ddm-main",
            "function_pre": None,
            "function_post": None,
        },
        {
            "module": "researchers",
            "sc_name": "project_configuration_section.png",
            "url": f"projects/{PROJECT_ID}/",
            "element_id": "project-configuration",
            "function_pre": None,
            "function_post": None,
        },
        {
            "module": "researchers",
            "sc_name": "datadonation_admin_page.png",
            "url": f"projects/{PROJECT_ID}/data-donation",
            "element_id": "ddm-main",
            "function_pre": None,
            "function_post": scroll_to_bottom,
        },
        # Screenshot Briefing Page
        {
            "module": "researchers",
            "sc_name": "briefing_page.png",
            "url": f"studies/{PROJECT_SLUG}/briefing/",
            "element_id": "ddm-participation-main",
            "function_pre": None,
            "function_post": None,
        },
        # Screenshot Data Donation Page. Must be executed after briefing page screenshots.
        {
            "module": "researchers",
            "sc_name": "datadonation_page.png",
            "url": f"studies/{PROJECT_SLUG}/data-donation/",
            "element_id": "ddm-participation-main",
            "function_pre": access_donation_stage,
            "function_post": None,
        },
        {
            "module": "researchers",
            "sc_name": "datadonation_after_upload_page.png",
            "url": f"studies/{PROJECT_SLUG}/data-donation/",
            "element_id": "ddm-participation-main",
            "function_pre": upload_file,
            "function_post": None,
        },
        {
            "module": "researchers",
            "sc_name": "datadonation_after_upload_page_allinone.png",
            "url": f"studies/{PROJECT_SLUG}/data-donation/",
            "element_id": "ddm-participation-main",
            "function_pre": enable_all_in_one_consent,
            "function_post": None,
        },
        # Screenshot Questionnaire. Must be executed after data donation screenshots.
        {
            "module": "researchers",
            "sc_name": "questionnaire_page.png",
            "url": f"studies/{PROJECT_SLUG}/questionnaire/",
            "element_id": "ddm-participation-main",
            "function_pre": agree_to_donate,
            "function_post": create_question_screenshots,
        },
        # Screenshot Debriefing Page. Must be executed after questionnaire screenshots.
        {
            "module": "researchers",
            "sc_name": "debriefing_page.png",
            "url": f"studies/{PROJECT_SLUG}/questionnaire/",
            "element_id": "ddm-participation-main",
            "function_pre": access_debriefing,
            "function_post": None,
        },
        {
            "module": "researchers",
            "sc_name": "data_center.png",
            "url": f"projects/{PROJECT_ID}/",
            "element_id": "data-center",
            "function_pre": None,
            "function_post": None,
        },
        {
            "module": "researchers",
            "sc_name": "data_download_section.png",
            "url": f"projects/{PROJECT_ID}/",
            "element_id": "data-center",
            "function_pre": None,
            "function_post": None,
        },
        {
            "module": "researchers",
            "sc_name": "project_log_section.png",
            "url": f"projects/{PROJECT_ID}/",
            "element_id": "project-logs",
            "function_pre": None,
            "function_post": None,
        },
        {
            "module": "researchers",
            "sc_name": "danger_zone.png",
            "url": f"projects/{PROJECT_ID}/",
            "element_id": "danger-zone",
            "function_pre": None,
            "function_post": None,
        },
    ]
    return elements_to_capture

def main():
    driver = initialize_driver()
    login_to_ddm(driver, BASE_URL)
    elements_to_capture = load_element_list()
    prepare_project(driver)
    for entry in elements_to_capture:
        driver.set_window_size(WINDOW_WIDTH, 2160)
        entry_url = BASE_URL + entry["url"]
        driver.get(entry_url)

        if entry["function_pre"]:
            fun = entry["function_pre"]
            fun(driver)
            time.sleep(2)

        element = driver.find_element(By.ID, entry["element_id"])

        if entry["function_post"]:
            fun = entry["function_post"]
            element = fun(driver, element)
            time.sleep(2)

        sc_path = get_output_dir(entry["module"]) + entry["sc_name"]
        screenshot_element(driver, element, sc_path)
        add_margins_to_sc(sc_path)

    driver.quit()

docs_module_paths = {
    "ROOT": str(DOCS_DIR / "modules/ROOT/images") + "/",
    "administrators": str(DOCS_DIR / "modules/administrators/images") + "/",
    "developers": str(DOCS_DIR / "modules/developers/images") + "/",
    "researchers": str(DOCS_DIR / "modules/researchers/images") + "/",
}


def get_output_dir(module):
    """Return the directory screenshots for ``module`` are written to.

    Set the ``DDM_SCREENSHOT_DIR`` environment variable to redirect all output
    to a scratch directory (useful for testing without overwriting the
    screenshots committed to the repository).
    """
    override = os.environ.get("DDM_SCREENSHOT_DIR")
    if override:
        return override.rstrip("/") + "/"
    return docs_module_paths[module]

if __name__ == "__main__":
    """
    Run this script to re-generate screenshots used in the documentation.

    Prerequisites:
     a. Start the local development server first
        (i.e., ddm/test_project/> python manage.py runserver). The script can be
        run from any working directory; all paths are resolved relative to this
        file.

     b. The screenshots are taken for a project that already exists in the
        development database. Point the script at that project and its
        components via the variables defined at the top of this file
        (BASE_URL, PROJECT_ID, PROJECT_SLUG, FILE_UPLOADER_ID).

     c. A file called 'takeout-demo.zip' must sit next to this script (in the
        docs folder) containing a valid data donation for demonstration
        purposes.

    Optional environment variables:
     - DDM_HEADLESS=1        run Firefox headless.
     - DDM_SCREENSHOT_DIR    write all screenshots to this directory instead of
                             docs/modules/<module>/images/ (useful for testing
                             without overwriting the committed screenshots).
    """
    main()
