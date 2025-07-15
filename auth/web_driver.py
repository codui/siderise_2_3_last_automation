import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Service class introduced in Selenium 4 for managing driver installation, opening, and closing
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# Used for setting wait times
# Used for setting wait times
from selenium.webdriver.support.ui import WebDriverWait

# ChromeDriverManager is used to install the driver without manually downloading the binary file
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


def initialize_web_driver(site: str) -> WebDriver:
    """
    Initializes the Selenium WebDriver for Chrome and opens the target website.

    Args:
        site (str): The name of the site to be opened.
            For example:
                "https://system.asite.com/login"

    Returns:
        webdriver.Chrome: An instance of the Chrome WebDriver.
    """
    # Absolute path to the folder in which to save files downloaded
    # from the asite site of the Side-Rise inspection, paragraph 2.3
    download_dir: str = r"C:\Users\Human\Downloads\download_from_asite"

    options = Options()
    # Disable pop-up notifications
    prefs = {
        "profile.default_content_setting_values.notifications": 2,  # turn off notifications
        "download.default_directory": download_dir,  # specify default download folder
        "download.prompt_for_download": False,  # do not ask for confirmation to download
        "directory_upgrade": True,  # allow directory change
        "safebrowsing.enabled": True,  # disable chrome blocking
    }
    options.add_experimental_option("prefs", prefs)
    # Installing the ChromeDriverManager driver
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(site)
    # driver.set_window_size(1920, 1080)

    # Expand window to full screen
    driver.maximize_window()
    # Explicit wait for element with tag-name "html"
    wait = WebDriverWait(driver, 10)
    wait.until(EC.visibility_of_element_located((By.TAG_NAME, "html")))
    return driver


def perform_authorization(login: str, password: str) -> WebDriver:
    """Performs authorization on the site "https://system.asite.com/login"

    Args:
        login (str): Login for authorization on site
        password (str): Password for authorization on site

    Returns:
        driver (WebDriver)
    """
    driver = initialize_web_driver("https://system.asite.com/login")
    # driver.fullscreen_window()  # ! Не раскрывает окно для людей, но для Selenium это работает
    # Раскрываем браузер на весь экран монитора
    # driver.set_window_size(1920, 1080)
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)
    # If there is an iframe then need to switch to it
    iframe = wait.until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="iFrameAsite"]'))
    )
    # Switch to iframe
    driver.switch_to.frame(iframe)
    # logging.info(f"Found iframe: {len(iframes)}")
    btn_login_xpath: str = '//*[@id="_58_login"]'
    btn_password_xpath: str = '//*[@id="_58_password"]'
    btn_submit_xpath: str = '//*[@id="login-cloud"]'
    # btn_login_el = driver.find_element(By.XPATH, btn_login_xpath)
    # btn_login_el.send_keys(login)
    input_login_el = wait.until(
        EC.visibility_of_element_located((By.XPATH, btn_login_xpath))
    )
    input_password_el = wait.until(
        EC.visibility_of_element_located((By.XPATH, btn_password_xpath))
    )
    btn_submit_el = wait.until(
        EC.visibility_of_element_located((By.XPATH, btn_submit_xpath))
    )
    input_login_el.send_keys(login)
    input_password_el.send_keys(password)
    btn_submit_el.click()
    # Switch driver focus back to main page (outside all iframes)
    driver.switch_to.default_content()
    # btn_login_el.clear()
    return driver
