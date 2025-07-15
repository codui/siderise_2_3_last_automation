import logging
from functools import wraps
import os
from termcolor import colored
from dotenv import load_dotenv
from auth.web_driver import perform_authorization
from selenium.webdriver.chrome.webdriver import WebDriver


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


def check_session(func):
    """
    DECORATOR for check status session.
    """

    @wraps(func)
    def wrapper(driver: WebDriver, *args, **kwargs):
        """
        Checks if the client is authorized. If not, re-authorizes.

        Returns:
            webdriver.Chrome - current copy of the driver (restarted if necessary).
        """
        load_dotenv()
        # login = "andrii.khoroshchak@leemarley.com"
        # password = "1992d1992D!"
        login = os.getenv("SITE_LOGIN")
        password = os.getenv("SITE_PASSWORD")
        print(os)
        try:
            # if "login" in driver.current_url or driver.title == "Unauthorised":
            if driver.title == "Unauthorised":
                logging.info(
                    colored("Session is invalid. Re-authorization...", "red")
                )
                driver.quit()  # Close the old driver
                driver = perform_authorization(login, password)
            # else:
            #     logging.info(colored("Сессия активна.", "green"))
        except Exception as err:
            logging.info(colored(f"Error checking session: {err}", "red"))
            # Exit the old driver where the crash occurred
            driver.quit()
            # Log in to the site again
            driver = perform_authorization(login, password)
        return func(driver, *args, **kwargs)

    return wrapper
