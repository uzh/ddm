import time

from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

BASE_URL = "http://127.0.0.1:8000/"
PROJECT_ID = "F1svPg1v"
PROJECT_SLUG = "your-individual-url"
FILE_UPLOADER_ID = 27


def initialize_driver():
    firefox_options = Options()
    firefox_options.set_preference("intl.accept_languages", "en,en-US")  # Example: German
    firefox_options.set_preference("general.useragent.locale", "en-US")  # Set UI locale too

    driver = webdriver.Firefox(options=firefox_options)
    driver.set_window_size(3840, 2160)
    return driver

def login_to_ddm(driver, url):
    driver.get(url)

    username_field = driver.find_element(By.ID, "id_username")
    username_field.send_keys("admin")

    password_field = driver.find_element(By.ID, "id_password")
    password_field.send_keys("password")

    login_button = driver.find_element(By.ID, "login-btn")
    login_button.click()

def prepare_project(driver):
    url = f"projects/{PROJECT_ID}/data-donation/file-uploader/{FILE_UPLOADER_ID}/edit/"
    driver.get(BASE_URL + url)

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[id="id_combined_consent"]')))
    consent_toggle = driver.find_element(By.CSS_SELECTOR, 'input[id="id_combined_consent"]')
    driver.maximize_window()
    time.sleep(1)

    driver.execute_script("arguments[0].scrollIntoView(true);", consent_toggle)
    time.sleep(1)
    driver.execute_script("window.scrollBy(0, 100);")
    time.sleep(1)

    if consent_toggle.is_selected():
        consent_toggle.click()

    save_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"][value="Update Uploader"]')
    time.sleep(1)
    save_button.click()

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

def access_donation_stage(driver):
    consent_button = driver.find_element(By.ID, "consent_yes")
    time.sleep(1)
    driver.execute_script("window.scrollBy(0, 300);")
    time.sleep(1)
    consent_button.click()

    next_button = driver.find_element(By.CLASS_NAME, "flow-btn")
    next_button.click()

def upload_file(driver):
    file_path = r"C:\Users\nipfif\PyCharmProjects\DDM\docs\takeout-demo.zip"
    file_input = driver.find_element(By.CSS_SELECTOR, "input[class='d-none'][type='file']")
    file_input.send_keys(file_path)

    # Wait until file has been processed
    WebDriverWait(driver, 10)

def enable_all_in_one_consent(driver):
    url = f"projects/{PROJECT_ID}/data-donation/file-uploader/{FILE_UPLOADER_ID}/edit/"
    driver.get(BASE_URL + url)

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[id="id_combined_consent"]')))
    consent_toggle = driver.find_element(By.CSS_SELECTOR, 'input[id="id_combined_consent"]')
    driver.maximize_window()
    time.sleep(1)

    if not consent_toggle.is_selected():
        consent_toggle.click()

    save_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"][value="Update Uploader"]')
    time.sleep(1)
    driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
    time.sleep(1)
    driver.execute_script("window.scrollBy(0, 300);")
    time.sleep(1)
    save_button.click()

    url = f"studies/{PROJECT_SLUG}/data-donation/"
    driver.get(BASE_URL + url)

    upload_file(driver)

def agree_to_donate(driver, element=None):
    url = f"studies/{PROJECT_SLUG}/data-donation/"
    driver.get(BASE_URL + url)
    upload_file(driver)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'label[for="donate-agree-null"]')))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

    # Get the checkbox itself
    checkbox = driver.find_element(By.ID, "donate-agree-null")
    checkbox_label = driver.find_element(By.CSS_SELECTOR, 'label[for="donate-agree-null"]')

    # Ensure the checkbox is visible
    if not checkbox.is_selected():
        actions = ActionChains(driver)
        actions.move_to_element(checkbox_label).perform()
        time.sleep(0.5)
        checkbox_label.click()

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "flow-btn")))
    next_button = driver.find_element(By.CLASS_NAME, "flow-btn")
    driver.maximize_window()
    driver.execute_script("arguments[0].scrollIntoView({ block: 'center' });", next_button)
    time.sleep(1)
    next_button.click()
    time.sleep(10)
    return element

def create_question_screenshots(driver, element):
    question_types = [
        "singlechoice",
        "multichoice",
        "matrix",
        "semanticdifferential",
        "textblock",
        "open"
    ]
    question_containers = driver.find_elements(By.CLASS_NAME, "question-container")
    for idx, container in enumerate(question_containers, start=1):
        driver.execute_script("arguments[0].scrollIntoView({ block: 'center' });", container)
        sc_path = docs_module_paths["researchers"] + f"questionnaire_{question_types[idx-1]}.png"
        container.screenshot(sc_path)
    return element

def access_debriefing(driver):
    for i in range(20):
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "flow-btn")))
        next_button = driver.find_element(By.CLASS_NAME, "flow-btn")
        driver.maximize_window()
        driver.execute_script("arguments[0].scrollIntoView({ block: 'center' });", next_button)
        time.sleep(1)
        next_button.click()
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

        sc_path = docs_module_paths[entry["module"]] + entry["sc_name"]
        element.screenshot(sc_path)
        add_margins_to_sc(sc_path)

    driver.quit()

docs_module_paths = {
    "ROOT": "docs/modules/ROOT/images/",
    "administrators": "docs/modules/administrators/images/",
    "developers": "docs/modules/developers/images/",
    "researchers": "modules/researchers/images/",
}

if __name__ == "__main__":
    """ 
    Run this script to re-generate screenshots used in the documentation.
    
    Please note that you must start the local development server for this script
    to be able to run (i.e., ddm/test_project/> python manage.py runserver).
    
    Also note that:
     a. the screenshots will be taken for a project that already exists 
     in the development database. You have to refer to this project and its components 
     by adjusting the variables defined at the beginning of this document.
     
     b. there needs to be a file called 'takeout-demo.zip' in the docs folder 
     that contains a valid data donation for demonstration purposes.
    """
    main()
