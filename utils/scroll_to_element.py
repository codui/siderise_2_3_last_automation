from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from auth.decorators import check_session


@check_session
def scroll_up_to_element(
    driver: WebDriver, element: WebElement
) -> tuple[WebDriver, WebElement]:
    """Scroll the page up to the "element" element so that it is in the viewport.
    This is necessary so that Selenium can interact with the element.

    Args:
        driver (WebDriver)
        element (WebElement): The element to which you need to scroll the page.

    Returns:
        tuple(drive, webelement)
    """
    actions = ActionChains(driver)
    actions.scroll_to_element(element).perform()
    actions.scroll_by_amount(0, -300).perform()
    return (driver, element)


@check_session
def scroll_down_to_element(
    driver: WebDriver, element: WebElement
) -> tuple[WebDriver, WebElement]:
    """Scroll down the page to the element "element" so that it is in the viewing area.
        This is necessary so that Selenium can interact with the element.

    Args:
        driver (WebDriver)
        element (WebElement): The element to which you need to scroll the page.

    Returns:
        tuple(drive, webelement)
    """
    actions = ActionChains(driver)
    actions.scroll_to_element(element).perform()
    actions.scroll_by_amount(0, 300).perform()
    return (driver, element)
