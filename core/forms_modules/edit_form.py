import logging
import shutil
import time
from pathlib import Path
from pprint import pprint

from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

# Used for setting wait times
from selenium.webdriver.support.ui import WebDriverWait

from auth.decorators import check_session
from core.forms import add_photo_to_side_rise_point_2_3, insert_data_into_field
from utils.database import add_photos_to_data_base
from utils.helpers import collect_photos_from_photo_dir
from utils.scroll_to_element import scroll_down_to_element


@check_session
def edit_form(
    driver: WebDriver,
    base_dir: Path,
    dict_plots_with_new_photos: dict[str, list[Path]],
    block_level_plot: str,
    add_photo_or_not: str,
) -> WebDriver:
    r"""
    The function fills in the form fields related to the sections - "Additional Fields",
    SECTION 2 - SIDE-RISE IREBREAK - item 2.1.
    And also adds a photo to item 2.3 if it has less than 30 photos.
    After filling in the form with data - clicks on the "Update" button to save the changes.

    Args:
        driver (WebDriver)
        base_dir (Path): Path to the folder where folders with apartment location names are stored.
            Folders with the apartment location name may contain photos related to point 2.3
            of the Side-Rise inspection for this apartment.
            The apartment location name consists of the block, floor, and apartment number.
            For example:
                Path(r"D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise")
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
        block_level_plot (str): The apartment code adopted in this project.
            The code consists of three parts - Block, Level, Plot.
                Block - one letter from this letters (A,B,C,D,E,F,G)
                Level - big letter "L" plus one number from this numbers (1,2,3,4,5,6,7,8)
                Plot - word "Plot" plus one number from this numbers (1, ... 456)
            For example:
                "A_L1_Plot_1"
        add_photo_or_not (str): Label to determine whether adding photos to the inspection will work or not.
            If it contains the text "." - means adding photos.
            If it contains the text - "Not add photo" - means not adding photos.

    Returns:
        WebDriver
    """
    final_dir_name_with_photos_uploaded_on_asite: Path = Path(r"2.3\photos_on_asite")
    wait: WebDriverWait = WebDriverWait(driver, 5)
    # Get a button to switch to the inspection form editing mode
    btn_edit_form_xpath: str = '//*[@id="edit-ori-btn"]/i'
    btn_edit_form: WebElement = WebDriverWait(driver, 100).until(
        EC.element_to_be_clickable((By.XPATH, btn_edit_form_xpath))
    )
    # Click on the button to switch to the inspection form editing mode
    btn_edit_form.click()
    # Подождать пока страница для редактирования отобразится
    wait: WebDriverWait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "html")))
    # Get a list of elements - fields for text input
    fields_xpath: str = (
        '//*[@id="custFormTD"]/div//div[@class="obr-section"]/div[contains(@ng-switch-when, "textbox")]//input'
    )
    fields: list[WebElement] = wait.until(
        EC.visibility_of_all_elements_located((By.XPATH, fields_xpath))
    )

    # ! Fill in the input field contractors_q_a_form_ref_numb
    # Contractor’s Quality Assurance form reference number
    contractors_q_a_form_ref_numb: WebElement = fields[0]
    # If the field is empty, then insert data into it
    if len(contractors_q_a_form_ref_numb.get_attribute("value")) <= 2:
        insert_data_into_field(contractors_q_a_form_ref_numb, "BMS01.G01")

    # ! Fill in the input field contractors_q_a_form_name_title
    # Contractor’s Quality Assurance form name/title
    contractors_q_a_form_name_title: WebElement = fields[1]
    # If the field is empty, then insert data into it
    if len(contractors_q_a_form_name_title.get_attribute("value")) <= 2:
        insert_data_into_field(contractors_q_a_form_name_title, "Quality policy")

    # ! Fill in the contract_cert input field
    # Contractor’s certification body
    contract_cert: WebElement = fields[2]
    # If the field is empty, then insert data into it
    if len(contract_cert.get_attribute("value")) <= 2:
        insert_data_into_field(contract_cert, "IFC Certificate number: IFCC 3054")

    # ! Fill in the input field area_of_inspection
    # Area of inspection (please note the gridlines or structural elements to locate this area and floor/level)
    area_of_inspection: WebElement = fields[3]
    # If the field is empty, then insert data into it
    if len(area_of_inspection.get_attribute("value")) <= 2:
        location_site_area_xpath: str = (
            '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/div[1]/div[3]/input'
        )
        # Get the element containing the text - the name of the inspection
        location_site_area_input: WebElement = driver.find_element(
            By.XPATH, location_site_area_xpath
        )
        # Remove the "disabled" attribute from the "input" element so that text can be copied from it
        driver.execute_script(
            "arguments[0].removeAttribute('disabled')", location_site_area_input
        )
        # Get the text of the inspection name
        location_site_area_raw_text: str = location_site_area_input.get_attribute(
            "value"
        )
        # Format the resulting text
        location_site_area_text: str = " ".join(location_site_area_raw_text.split(">"))
        # Insert the resulting text into the "area_of_inspection" element
        insert_data_into_field(area_of_inspection, location_site_area_text)

    # ! Fill in the input field confirm_that_materials_stored_correctly
    # Please confirm that the materials have been stored and protected in accordance
    # with manufacturer’s instructions and the Contractor’s Quality Management System:
    сonfirm_that_materials_stored_correctly: WebElement = fields[-1]
    # If the field is empty, then insert data into it
    if len(сonfirm_that_materials_stored_correctly.get_attribute("value")) <= 2:
        # Scroll to the element "confirm_that_materials_stored_correctly"
        scroll_down_to_element(driver, сonfirm_that_materials_stored_correctly)
        # Insert data into the field "confirm_that_materials_stored_correctly"
        insert_data_into_field(сonfirm_that_materials_stored_correctly, "Yes")

    # ! Check if input field exists check_comment_field
    # 2.1 Confirm that a copy of the contractor’s Project Quality Plan
    check_comment_field_xpath: str = (
        '//*[@id="custFormTD"]//div[contains(@class, "comment-section")]'
    )
    check_comment_field: WebElement = driver.find_elements(
        By.XPATH, check_comment_field_xpath
    )
    # logging.info(f"{len(check_comment_field)=}")
    # Work if there is no comment field
    if len(check_comment_field) == 0:
        # Найти кнопку создания комментария
        btn_create_comment_xpath: str = (
            '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[2]/div/div[8]/div/div[1]/div[2]/div[1]/div[2]/button'
        )
        btn_create_comment: WebElement = wait.until(
            EC.element_to_be_clickable((By.XPATH, btn_create_comment_xpath))
        )
        # Scroll to the button "btn_create_comment"
        actions = ActionChains(driver)
        actions.scroll_to_element(btn_create_comment).perform()
        actions.scroll_by_amount(0, 200).perform()
        # Click on the button "btn_create_comment"
        btn_create_comment.click()
        # Get the comment field
        field_to_insert_comment_xpath: str = '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[2]/div/div[8]/div/div[2]//div[contains(@class, "comment-section")]/div[2]/textarea'
        field_to_insert_comment: WebElement = driver.find_element(
            By.XPATH, field_to_insert_comment_xpath
        )
        # Paste data into the comment field
        insert_data_into_field(
            field_to_insert_comment,
            "ITP and PQP uploaded on Asite\n"
            "H8499-LEM-SW-ZZ-QA-CT-19715 PQP\n"
            "H8499-LEM-SW-ZZ-QA-CO-LM123 ITP\n",
        )

    # ! Send photos from PC to field 2.3:
    # Confirm that all firebreaks installed are located in accordance with the approved project fire strategy drawings,
    # details, specifications and that only Barratt approved materials have been used.
    # Please attach various photos proving compliance.
    # ! Work if in the Side-Rise location in point 2.3 on asite there are less than 30 photos
    if add_photo_or_not != "Not add photo":
        driver, new_photos_on_asite = add_photo_to_side_rise_point_2_3(
            driver, dict_plots_with_new_photos, block_level_plot
        )
        logging.info("\n new_photos_on_asite:")
        pprint(new_photos_on_asite)

        for new_photo in new_photos_on_asite:
            dest: Path = (
                base_dir
                / block_level_plot
                / final_dir_name_with_photos_uploaded_on_asite
                / new_photo.name
            )
            # Move photos sent to Side-Rise inspection of block_level_plot location in point 2.3
            # from new_photos_send_to_asite folder on PC to photos_on_asite folder on PC
            shutil.move(str(new_photo), str(dest))
            logging.info(f"Move {str(new_photo)} to {str(dest)}")

        photos_on_asite_path: Path = (
            base_dir / block_level_plot / Path(r"2.3\photos_on_asite")
        )
        logging.info(f"{photos_on_asite_path=}")

        photos_on_asite_list: list[Path] = collect_photos_from_photo_dir(
            photos_on_asite_path
        )
        logging.info(f"{photos_on_asite_list=}")

        # Add to the database photos sent to Side-Rise inspection in item 2.3 on asite
        add_photos_to_data_base(
            block_level_plot,
            str(final_dir_name_with_photos_uploaded_on_asite),
            photos_on_asite_list,
        )
    # Get the "Update" button and click on it
    btn_update_xpath: str = '//*[@id="btnSaveForm"]'
    btn_update: WebElement = wait.until(EC.element_to_be_clickable((By.XPATH, btn_update_xpath)))
    btn_update.click()
    # Pause for form saving to work
    time.sleep(1)
    # Wait for the information on the page to be saved after editing is completed
    WebDriverWait(driver, 60).until(
        EC.text_to_be_present_in_element_attribute(
            (By.XPATH, '//div[contains(@class, "form-container")]'), "class", "loaded"
        )
    )
    return driver
