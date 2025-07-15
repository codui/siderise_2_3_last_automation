import logging
import time
from pathlib import Path

# Importing Selenium WebDriver to interact with the browser
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

# Used for setting wait times
from selenium.webdriver.support.ui import WebDriverWait

from auth.decorators import check_session
from core.forms import fill_created_form
from core.forms_modules.processs_form_qc4j_side_rise_rain_screen_firebreak import (
    processs_form_qc4j_side_rise_rain_screen_firebreak,
)
from utils.helpers import (
    edit_or_create_inspection,
    get_location_title,
    set_color_to_element,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


@check_session
def click_btn_more(driver: WebDriver) -> WebDriver:
    """Click on the "more" button in the header of the first page of the asite.
        https://adoddleak.asite.com/adoddle/home?action_id=1

    Args:
        driver (WebDriver)

    Returns:
        WebDriver
    """
    # Get the button btn_more
    btn_more_xpath: str = '//*[@id="header_moreNav"]'
    wait: WebDriverWait = WebDriverWait(driver, 20)
    btn_more: WebElement = wait.until(
        EC.visibility_of_element_located((By.XPATH, btn_more_xpath))
    )
    # Click on the btn_more button
    btn_more.click()
    return driver


@check_session
def click_btn_quality(driver: WebDriver) -> WebDriver:
    """Click on the "Quality" button in the drop-down menu of the header on the first page of the asite.
        https://adoddleak.asite.com/adoddle/home?action_id=1

    Args:
        driver (WebDriver)

    Returns:
        WebDriver
    """
    # Get the button btn_quality
    btn_quality_xpath: str = '//*[@id="navquality"]'
    wait: WebDriverWait = WebDriverWait(driver, 5)
    btn_quality: WebElement = wait.until(
        EC.visibility_of_element_located((By.XPATH, btn_quality_xpath))
    )
    # Click on the btn_quality button
    btn_quality.click()
    return driver


@check_session
def click_new_malden_quality_plan(driver: WebDriver) -> WebDriver:
    """Click on the "New Malden Quality Plan" label in the main table on the second page of the asite
        https://adoddleak.asite.com/adoddle/quality?action_id=1

    Args:
        driver (WebDriver)

    Returns:
        WebDriver
    """
    # Get the label new_malden
    new_malden_xpath: str = (
        '//*[@id="qualities-list"]/div/div/adoddle-table-listing/div/div[2]/div[2]/div/ul[1]/li[2]/a'
    )
    wait: WebDriverWait = WebDriverWait(driver, 5)
    new_malden: WebElement = wait.until(
        EC.visibility_of_element_located((By.XPATH, new_malden_xpath))
    )
    # Click on the new_malden label
    new_malden.click()
    return driver


@check_session
def click_arrow_to_open_block(driver: WebDriver, number_line: int) -> WebDriver:
    """The function clicks on the arrow in the "Block N" cells on the next page of the asite.
    Where N is the block (house) letter from the list of letters A, B, C, D, E, F, G.
    As a result, a drop-down list with the floors of the house opens.
    https://adoddleak.asite.com/adoddle/quality?action_id=1

    Args:
        driver (WebDriver)
        number_line (int): Row number in the site table.

    Returns:
        WebDriver
    """
    # Get the button arrow_open_block
    wait: WebDriverWait = WebDriverWait(driver, 10)
    arrow_open_block_xpath: str = (
        f'//*[@id="table_body_header_scroller"]/div/div[{number_line}]/div/i'
    )
    # Wait until the arrow_open_block button becomes clickable
    arrow_open_block = wait.until(
        EC.element_to_be_clickable((By.XPATH, arrow_open_block_xpath))
    )
    # Click on the arrow_open_block button
    arrow_open_block.click()
    # Wait until the chevron-up class appears in the element.
    # This means that the list of elements has opened and you can continue working without time.sleep()
    wait.until(
        EC.text_to_be_present_in_element_attribute(
            (By.XPATH, arrow_open_block_xpath), "class", "chevron-up"
        )
    )

    return driver


@check_session
def click_arrow_to_open_level(driver: WebDriver, number_line: int) -> WebDriver:
    """The function clicks on the arrow in the "Level N" cells, where N is the floor number.
    Clicking this will open a drop-down list with apartment numbers.
    https://adoddleak.asite.com/adoddle/quality?action_id=1

    Args:
        driver (WebDriver)
        number_line (int): Row number in the site table.

    Returns:
        WebDriver
    """
    try:
        wait: WebDriverWait = WebDriverWait(driver, 5)
        arrow_open_level_xpath: str = (
            f'//*[@id="table_body_header_scroller"]/div/div[{number_line}]/div/i'
        )
        # Wait until the arrow_open_level button becomes clickable
        arrow_open_level: WebElement = wait.until(
            EC.element_to_be_clickable((By.XPATH, arrow_open_level_xpath))
        )
        # Click on the arrow_open_level button
        arrow_open_level.click()
        # Wait until the chevron-up class appears in the element.
        # This means that the list of elements has opened and you can continue working without time.sleep()
        wait.until(
            EC.text_to_be_present_in_element_attribute(
                (By.XPATH, arrow_open_level_xpath), "class", "chevron-up"
            )
        )
    except Exception:
        return driver
    return driver


@check_session
def click_card_in_progress(driver: WebDriver, element: WebElement) -> WebDriver:
    """The function clicks on the "element",
    which opens a new tab with an inspection form for the current apartment.
    (element by XPATH of the following type //*[@id="table_body_content_scroller"]/div/div[6]/div/div[33])

    Args:
        driver (WebDriver)
        element (WebElement): Element that contains the button for opening the current apartment inspection
            in a new tab. This element contains the button and the inspection status "In Progress" are indicated.

    Returns:
        WebDriver
    """
    # Get from the element a button that opens the inspection form of the current apartment in a new tab
    element.find_element(By.XPATH, '//span[contains(@class, "ng-star-inserted")]')
    # Hide the support window if it exists
    try:
        support_window = driver.find_element(By.CLASS_NAME, "intercom-lightweight-app")
        driver.execute_script("arguments[0].style.display = 'none';", support_window)
    except Exception:
        pass
    # If the support window is not found, continue working
    try:
        # Click on element and open the inspection form for the current apartment in a new tab
        element.click()
    except ElementClickInterceptedException as err:
        logging.info(f"Work ElementClickInterceptedException {err}")
        # Use JavaScript to click on an element if the element is covered
        driver.execute_script("arguments[0].click();", element)
    return driver


@check_session
def click_select_form_action(
    driver: WebDriver, btn_select_form_action: WebElement
) -> WebDriver:
    """Click on the image to create a new form.
    The click will cause a pop-up window of options to appear called "Select Form Action".

    Args:
        driver (WebDriver)
        btn_select_form_action (_type_): An image button that calls the "Select Form Action" options popup.
            The button is obtained via an XPATH path similar to this:
            //*[@id="table_body_content_scroller"]/div/div[37]/div/div[33]/div/img

    Returns:
        WebDriver
    """
    try:
        # Click to bring up the "Select Form Action" options popup
        btn_select_form_action.click()
    except ElementClickInterceptedException:
        logging.info("Work click_select_form_action ElementClickInterceptedException")
        # Use JavaScript to click on an element if the element is covered
        driver.execute_script("arguments[0].click();", btn_select_form_action)
    return driver


@check_session
def click_btn_create_form(driver: WebDriver) -> WebDriver:
    """The function waits for the pop-up window of options named "Select Form Action" to appear.
    From it it receives a button named "Create Form" and clicks on it.
    As a result, a new inspection is created for the current apartment, which opens instead of the current tab.

    Args:
        driver (WebDriver)

    Returns:
        WebDriver
    """
    # Get the element with label "Select Form Action"
    wait: WebDriverWait = WebDriverWait(driver, 10)
    select_form_action: str = '//*[@id="subscriptionPlanId-2"]/ngb-modal-window'
    # Wait until the "Select Form Action" modal window appears with two buttons to select an action
    wait.until(
        EC.text_to_be_present_in_element_attribute(
            (By.XPATH, select_form_action), "class", "form-modal"
        )
    )
    # Get button btn_create_form with label "Create Form"
    btn_create_form_xpath: str = (
        '//*[@id="subscriptionPlanId-2"]/ngb-modal-window/div/div/div[2]/div[1]/img'
    )
    btn_create_form: WebElement = wait.until(
        EC.visibility_of_element_located((By.XPATH, btn_create_form_xpath))
    )
    # Click on the btn_create_form button
    btn_create_form.click()
    return driver


@check_session
def switch_to_new_tab(driver: WebDriver) -> WebDriver:
    """The function gets access to a new browser tab with an inspection of the current apartment.
    Then switches the Seleinum context to this new tab and waits for the main html element to load.

    Args:
        driver (WebDriver)

    Returns:
        WebDriver
    """
    # Access a new browser tab with an inspection of the current apartment
    new_tab = driver.window_handles[1]
    # Switch Selenium context to this new tab
    driver.switch_to.window(new_tab)
    # TODO - Rework the waiting logic
    # Wait for the main html element of the page to load
    WebDriverWait(driver, 60).until(
        EC.visibility_of_all_elements_located((By.TAG_NAME, "html"))
    )
    return driver


@check_session
def scroll_to_location_title(driver: WebDriver, number_line: int) -> WebDriver:
    """Performs a scroll to the element of the "Activities / Locations" column by the received number_line.
    This is necessary so that the element is in the visible part of the browser window
    and Selenium can interact with it.
    The element of the "Activities / Locations" column can contain the text either "Block" or "Level" or "Plot".
        Also colors the active element light green.
    This is only necessary for visual control of what is happening or to demonstrate the work.

    Args:
        driver (WebDriver)
        number_line (int): The row number of the "Activities / Locations" column of the table "New Malden Quality Plan"
            listing all inspections.

    Returns:
        WebDriver:
    """
    wait: WebDriverWait = WebDriverWait(driver, 10)
    # Get the cell of the "Activities / Locations" column
    location_cell_xpath: str = (
        f'//*[@id="table_body_header_scroller"]/div/div[{number_line}]'
    )
    location_cell: WebElement = wait.until(
        EC.visibility_of_element_located((By.XPATH, location_cell_xpath))
    )
    # Get the location_title element so that it can be highlighted in light green
    location_title: WebElement = location_cell.find_element(
        By.CLASS_NAME, "location-title"
    )
    # Scroll to the desired element with Javascript, if suddenly scrolling with Python stops working
    # driver.execute_script("arguments[0].scrollIntoView(true);", btn_open_new_tab)

    # Scroll to desired element with Python
    ActionChains(driver).scroll_to_element(location_title).perform()
    # Color the location_title element light green
    driver = set_color_to_element(driver, location_title, "#7ff6bf")
    return driver


@check_session
def moving_through_quality_checklist(
    driver: WebDriver,
    base_dir: Path,
    download_dir: Path,
    dict_plots_with_new_photos: dict[str, list[Path]],
    number_line: int = 2,
    letter_block_to_start: str | bool = False,
    number_level_to_start: str | bool = False,
    number_plot_to_start: str | bool = False,
) -> WebDriver:
    r"""
    The function moves from top to bottom along the rows of the "Activities / Locations" column of the
    "New Malden Quality Plan" table which is located in the "Quality" section of the asite website.
    The movement occurs from the 2nd to the last row of the table.
    https://adoddleak.asite.com/adoddle/quality?action_id=1

    As you move, the main logic of the script is executed, described in the comments of the code of this function.

    Args:
        driver (WebDriver)
        number_line (int): The row number of the "Activities / Locations" column of the table "New Malden Quality Plan"
            listing all inspections.
        base_dir: (Path) Path to the folder where folders with apartment location names are stored.
            Folders with the apartment location name may contain photos related to point 2.3
            of the Side-Rise inspection for this apartment.
            The apartment location name consists of the block, floor, and apartment number.
            For example:
                Path(r"D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise")
        download_dir (Path): Folder for uploading photos from point 2.3 of the current location
            block_level_plot of the Side-Rise inspection
            For example:
                Path(r"C:\Users\Human\Downloads\download_from_asite")
        dict_plots_with_new_photos (dict[str, list[Path]]): A dictionary in which keys are strings taken
            from the names of folders designating an apartment in the apartment structure (inspection locations).
            The values ​​are lists with absolute paths to photographs,
            which are located in folders designating apartments.
            For example:
                dict_with_new_photos = {
                    'A_L1_Plot_2': [
                            WindowsPath('D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\A_L1_Plot_2\2.3\new_photos_send_to_asite\plot 02 block A lev 1 WA0118.jpg')
                        ],
                    'A_L1_Plot_4': [
                            WindowsPath('D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\A_L1_Plot_4\2.3\new_photos_send_to_asite\WhatsAppImage 2025-04-29 at 16.00.05_71d3d084.jpg')
                        ],
                    ...,
                    'G_L8_Plot_456': [
                            WindowsPath('D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\G_L8_Plot_456\2.3\new_photos_send_to_asite')
                        ]
                }
        number_line (int): The row number of the "Activities / Locations" column of the table "New Malden Quality Plan"
            listing all inspections. By default is 2.
        letter_block_to_start (str | bool): The letter of the name of the block from which
            the script will start working. By default is False.
        number_level_to_start (str | bool): The floor number from which the script will start working.
            By default is False.
        number_plot_to_start (str | bool): Номер квартиры с которой скрипт начнет работу. By default is False.

    Variables:
        block_level_plot (str): The apartment code adopted in this project.
            The code consists of three parts - Block, Level, Plot.
                Block - one letter from this letters (A,B,C,D,E,F,G)
                Level - big letter "L" plus one number from this numbers (1,2,3,4,5,6,7,8)
                Plot - word "Plot" plus one number from this numbers (1, ... 456)
            For example:
                "A_L1_Plot_1"

    Returns:
        WebDriver
    """
    stopword: bool = True
    block_letter: str = ""
    level_number: int | None = None
    plot_number: int | None = None

    while stopword:
        # Get the text content of the current cell of the "Activities / Locations" column
        # (Block or Level or Plot) of the "New Malden Quality Plan" table.
        driver, location_title = get_location_title(driver, number_line)
        # Performs a scroll to the element of the "Activities / Locations" column by the received number_line
        driver = scroll_to_location_title(driver, number_line)

        if type(location_title) is str:
            location_title = location_title.lower()
            logging.info(f"\n{location_title=}, {number_line=}")

            # ! PROCESS SECTION Block
            if "block" in location_title:
                # Block name letter from "location_title"
                block_letter = str(location_title.split()[-1]).upper()
                # Works if "letter_block_to_start" is False.
                # That is, if "letter_block_to_start" was never set by the user at the beginning of the script
                # or when "letter_block_to_start" was set by the user,
                # but became False after passing the specified "letter_block_to_start".
                if not letter_block_to_start:
                    # Click on the arrow in the cell with the text “Block” in the “Actions/Locations” column
                    driver = click_arrow_to_open_block(driver, number_line)
                # Works if the user specified letter_block_to_start from which the script will start working.
                elif location_title == f"block {letter_block_to_start}":
                    letter_block_to_start = False
                    # Click on the arrow in the cell with the text “Block” in the “Actions/Locations” column
                    # if location_title equal text from "block {letter_block_to_start}"
                    driver = click_arrow_to_open_block(driver, number_line)

            # ! PROCESS SECTION Level
            elif "level" in location_title:
                # Floor number from cell "location_title"
                level_number = int(location_title.split()[-1])
                # *  - - - - - - -
                # # The script skips all floors after the 5th
                # if int(location_title[-2:]) > 5:
                #     number_line += 1
                #     continue
                # * - - - - - - -

                # Works if the variable "number_level_to_start" is False.
                # That is, if "number_level_to_start"
                # was either never set by the user at the beginning of the script
                # or when "number_level_to_start" was set by the user,
                # but became False after passing the specified "number_level_to_start".
                if not number_level_to_start:
                    driver = click_arrow_to_open_level(driver, number_line)
                # Works if the user specified "number_level_to_start" from which the script will start working.
                elif location_title == f"level {number_level_to_start}":
                    number_level_to_start = False
                    # Click on the arrow in the cell with the text “Level” in the “Actions/Locations” column
                    # if location_title equal text from "level {number_level_to_start}"
                    driver = click_arrow_to_open_level(driver, number_line)

            # ! PROCESS SECTION Plot
            elif "plot" in location_title:
                # Apartment number from "location_title"
                plot_number = int(location_title.split()[-1])
                # A_L1_Plot_1
                block_level_plot: str = (
                    f"{block_letter}_L{level_number}_Plot_{plot_number}"
                )
                logging.info(f"\n {plot_number=}")
                logging.info(f"{block_level_plot=}")
                logging.info(f"{block_level_plot in dict_plots_with_new_photos=}")

                # If location "block_level_plot" is in dictionary with new photos "dict_plots_with_new_photos"
                if block_level_plot in dict_plots_with_new_photos:
                    if (
                        not number_plot_to_start
                        or location_title == f"plot {number_plot_to_start}"
                    ):
                        # ! WORK HERE
                        # ! WORK HERE
                        number_plot_to_start = False
                        logging.info(f"in elif plot {block_level_plot=}")
                        # Determine what needs to be done: edit the inspection or create a new one
                        driver, element, edit_or_create = edit_or_create_inspection(
                            driver, number_line
                        )
                        # Scroll to element "element" horizontally
                        actions = ActionChains(driver)
                        actions.scroll_to_element(element).perform()
                        time.sleep(1)
                        # Perform another horizontal scroll so that the element is closer to the center of the page
                        driver.execute_script(
                            """
                            const element = arguments[0];
                            const rect = element.getBoundingClientRect();
                            const absoluteElementLeft = rect.left + window.
                            pageXOffset;
                            const middle = absoluteElementLeft - (window.innerWidth / 2) + (rect.width / 2);
                            window.scrollTo({ left: middle, behavior: 'smooth' });
                        """,
                            element,
                        )
                        # time.sleep(1)
                        if edit_or_create is not None:
                            # Work if variable "edit_or_create" contains word "edit"
                            if edit_or_create == "edit":
                                # Click on "element" (inspection progress element with text "In Progress")
                                driver = click_card_in_progress(driver, element)
                                # If a new (second) tab is opened
                                if len(driver.window_handles) > 1:
                                    # Switch to a new tab with inspection by current apartment
                                    driver = switch_to_new_tab(driver)
                                    # Process the open tab with the inspection form of the current apartment
                                    driver = processs_form_qc4j_side_rise_rain_screen_firebreak(
                                        driver,
                                        base_dir,
                                        download_dir,
                                        dict_plots_with_new_photos,
                                        block_level_plot,
                                    )
                            # Work if the variable "edit_or_create" contains the word "create"
                            elif edit_or_create == "create":
                                # Click on the form creation icon to open the "Select Form Action" options window
                                driver = click_select_form_action(driver, element)
                                # Click on the "Create Form" button to create a new inspection form
                                # for the current apartment
                                driver = click_btn_create_form(driver)
                                # Fill the created empty form with data (images, documents, data from files)
                                driver = fill_created_form(
                                    driver,
                                    dict_plots_with_new_photos,
                                    block_level_plot,
                                    base_dir,
                                )
                                time.sleep(2)
        # Go to the next line below in the "New Malden Quality Plan" table
        number_line += 1
    return driver
