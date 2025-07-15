import logging

# import shutil
import time
from pathlib import Path
from pprint import pprint

# from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

# Used for setting wait times
from selenium.webdriver.support.ui import WebDriverWait

from auth.decorators import check_session
from core.forms import (
    download_photos_from_asite_block_level_plot_2_3_to_os,
    get_list_photos_from_download_dir_os,
    move_duplicate_photos_from_new_photos_send_to_asite_to_photos_to_delete,
    move_photos_from_download_dir_to_photos_on_asite,
    move_photos_from_new_photos_to_photos_not_on_asite,
)
from core.forms_modules.edit_form import edit_form
from utils.database import add_photos_to_data_base
from utils.scroll_to_element import scroll_down_to_element


@check_session
def processs_form_qc4j_side_rise_rain_screen_firebreak(
    driver: WebDriver,
    base_dir: Path,
    download_dir: Path,
    dict_plots_with_new_photos: dict[str, list[Path]],
    block_level_plot: str,
) -> WebDriver:
    r""" The function checks whether the inspection form is available for editing.
    If it is, it processes it.
    If the form is not available and has been transferred to other specialists for review,
    then it closes the page with the form and returns to the main table of the site.
    If the inspection form is available for editing, then it checks whether the form fields need to be filled in.
    If necessary, it starts editing the inspection form.

    Args:
        base_dir (Path): Path to the folder where folders with apartment location names are stored.
            Folders with the apartment location name may contain photos related to point 2.3
            of the Side-Rise inspection for this apartment.
            The apartment location name consists of the block, floor, and apartment number.
            For example:
                Path(r"D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise")

        download_dir (Path): Directory for loading photos into Side-Rise inspection of block_level_plot location
            from point 2.3.
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

        block_level_plot (str): The apartment code adopted in this project.
            The code consists of three parts - Block, Level, Plot.
                Block - one letter from this letters (A,B,C,D,E,F,G)
                Level - big letter "L" plus one number from this numbers (1,2,3,4,5,6,7,8)
                Plot - word "Plot" plus one number from this numbers (1, ... 456)
            For example:
                "A_L1_Plot_1"
    }

    Returns:
        WebDriver

    Just in case:
        project_title_xpath = //*[@id="form-holder"]//*[@id="header-section"]/div[1]/h3
        is_not_editable_inspection_xpath = //*[@id="form-holder"]//div[contains(@class, "dropdown dist-users ng-scope")]
        xpath_elements = //*[@id="form-holder"] //*[@id="formWrapper"]//div[contains(@ng-switch-when, "textbox")]
    """
    wait: WebDriverWait = WebDriverWait(driver, 30)
    # Element from which to obtain the required form elements of fields for processing
    main_element_xpath: str = '//*[@id="form-holder"]'
    main_element: WebElement = wait.until(
        EC.visibility_of_element_located((By.XPATH, main_element_xpath))
    )
    logging.info(f"{main_element=}")
    # Get the title of the inspection form header
    project_title_xpath: str = '//*[@id="header-section"]/div[1]/h3'
    project_title: WebElement = wait.until(
        EC.visibility_of_element_located((By.XPATH, project_title_xpath))
    )
    project_title_text = project_title.text.lower()
    logging.info(f"{project_title_text=}")
    # Check if the page is editable
    try:
        is_not_editable_inspection_xpath: str = (
            '//*[contains(@class, "dropdown") and contains(@class, "dist-users") and contains(@class, "ng-star-inserted")]'
        )
        is_not_editable_inspection: WebElement = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located(
                (By.XPATH, is_not_editable_inspection_xpath)
            )
        )
        time.sleep(1)
        # If the page is not editable, then close it and return to the main page
        logging.info(f"Cтраница не редактируемая {bool(is_not_editable_inspection)=}")
        main_tab = driver.window_handles[0]
        driver.close()
        # Go to the main page (change context for Selenium)
        driver.switch_to.window(main_tab)
        return driver
    except Exception:
        # If the is_not_editable_inspection_xpath element is not on the page, then the inspection is editable
        is_not_editable_inspection = False
        logging.info(f"{is_not_editable_inspection=}")
    # Check that the Side-Rise inspection form is open
    if "qc4j side-rise rain-screen firebreak" in project_title_text:
        fields_xpath: str = (
            '//*[@id="formWrapper"]//div[contains(@ng-switch-when, "textbox")]'
        )
        # Get a list of form field elements to process
        fields: list[WebElement] = main_element.find_elements(By.XPATH, fields_xpath)
        # Contractor’s Quality Assurance form reference number
        form_number: str = fields[0].text
        # Contractor’s Quality Assurance form name/title
        form_name_title: str = fields[1].text
        # Contractor’s certification body
        contract_cert: str = fields[2].text
        # Area of inspection (please note the gridlines or structural elements to locate this area and floor/level)
        area_of_inspect: str = fields[3].text
        # Please confirm that the materials have been stored and protected in accordance with manufacturer’s
        # instructions and the Contractor’s Quality Management System:
        сonfirm_that_materials_stored_correctly: str = fields[4].text

        try:
            # time.sleep(1)
            # driver.implicitly_wait(1)
            # 2.1 Confirm that a copy of the contractor’s Project Quality Plan
            # Search for the comments field in paragraph 2.1
            comment_xpath: str = '//div[contains(@class, "comment-section")]'
            comments: WebElement | str = main_element.find_element(By.XPATH, comment_xpath).text
            logging.info(f"{comments=}")
        except Exception:
            comments = ""
            logging.info(
                f"There is no comments: {comments=}. Error in search comments field."
            )

        # Scroll to point 2.3
        wait: WebDriverWait = WebDriverWait(driver, 3)
        photos_on_asite_container_xpath: str = (
            '//div[.//div[normalize-space(text()) = "2.3"]]/following-sibling::div[not(@class)]'
        )
        photos_on_asite_container: WebElement = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, photos_on_asite_container_xpath)
            )
        )
        # Scroll to the element with photos "photos_on_asite_container"
        scroll_down_to_element(driver, photos_on_asite_container)
        time.sleep(1)  # ! if effor change value to 2 seconds

        # Label indicating whether to add photos to the site or not
        add_photo_or_not: str = "Not add photo"
        # ! Work if there are photos in point 2.3
        try:
            photos_on_asite_xpath: str = (
                '//div[.//div[normalize-space(text()) = "2.3"]]/following-sibling::div[not(@class)]//a'
            )
            # Find out the number of photos on asite in point 2.3
            photos_on_asite_elements: list[WebElement] = wait.until(
                EC.visibility_of_all_elements_located((By.XPATH, photos_on_asite_xpath))
            )
            logging.info(f"{len(photos_on_asite_elements)=}")

            # ! Work if there are less than 30 photographs in the inspection.
            # Prepare to upload new photos in step 2.3
            if len(photos_on_asite_elements) < 30:
                add_photo_or_not = "."
                logging.info(f"{add_photo_or_not=}")
                # Download Side-Rise inspection photos for location block_level_plot from section 2.3
                driver = download_photos_from_asite_block_level_plot_2_3_to_os(
                    driver, photos_on_asite_elements
                )
                # List of photos downloaded from Side-Rise inspection for location block_level_plot item 2.3,
                # which are currently in the PC download folder
                photos_from_download_dir: list[Path] = (
                    get_list_photos_from_download_dir_os(download_dir)
                )
                # logging.info("photos_from_download_dir")
                # pprint(photos_from_download_dir)

                # List of new photos to upload to the inspection form
                new_photos: list[Path] = dict_plots_with_new_photos[block_level_plot]
                logging.info("new_photos")
                pprint(new_photos)
                # Move the list of photos downloaded from Side-Rise to the block_level_plot location of point 2.3
                # (these photos are currently located in the download folder
                # C:\Users\Human\Downloads\download_from_asite)
                # to the block_level_plot + 2.3\photos_on_asite folder
                # (for example:
                # D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\A_L1_Plot_6\2.3\photos_on_asite).
                photos_on_asite: list[Path] = (
                    move_photos_from_download_dir_to_photos_on_asite(
                        base_dir,
                        block_level_plot,
                        photos_from_download_dir,
                    )
                )
                logging.info("photos_on_asite")
                pprint(photos_on_asite)
                # ! - - - - - - - - - - - - -
                # From the new photos in the new_photos folder, move the photos duplicated in the photos_on_asite folder to the photos_to_delete folder.
                new_photos_without_duplicates: list[Path] = (
                    move_duplicate_photos_from_new_photos_send_to_asite_to_photos_to_delete(
                        new_photos,
                        photos_on_asite,
                    )
                )
                # Update the list of new photos in the dictionary for a specific block_level_plot after removing duplicate photos
                dict_plots_with_new_photos[block_level_plot] = (
                    new_photos_without_duplicates
                )
            # ! Work if there are more than or equal to 30 photos in the inspection.
            elif len(photos_on_asite_elements) >= 30:
                add_photo_or_not = "Not add photo"
                # Move photos from the new_photos_without_duplicates list to the folder:
                # D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\<block_level_plot>\
                # \2.3\photos_not_on_asite_because_in_2_3_already_30_photos
                move_photos_from_new_photos_to_photos_not_on_asite(
                    base_dir, dict_plots_with_new_photos, block_level_plot
                )
                # Download Side-Rise inspection photos for location block_level_plot from point 2.3 to PC
                driver = download_photos_from_asite_block_level_plot_2_3_to_os(
                    driver, photos_on_asite_elements
                )
                # List of photos downloaded from Side-Rise by location block_level_plot point 2.3,
                # which are currently in the PC download folder
                photos_from_download_dir = get_list_photos_from_download_dir_os(
                    download_dir
                )
                # logging.info("photos_from_download_dir")
                # pprint(photos_from_download_dir)

                # Move the list of photos downloaded from Side-Rise to the block_level_plot location of point 2.3
                # (these photos are currently located in the download folder
                # C:\Users\Human\Downloads\download_from_asite)
                # to the block_level_plot + 2.3\photos_on_asite folder
                # (for example:
                # D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\A_L1_Plot_6\2.3\photos_on_asite).
                photos_on_asite = move_photos_from_download_dir_to_photos_on_asite(
                    base_dir,
                    block_level_plot,
                    photos_from_download_dir,
                )
                logging.info("photos_on_asite")
                pprint(photos_on_asite)
                # Add to the Database photos that were not entered by the script,
                # but were already and are now on asite
                add_photos_to_data_base(
                    block_level_plot,
                    str(Path(r"2.3\photos_on_asite")),
                    photos_on_asite,
                )
        # ! Work if there are no photos in point 2.3
        except Exception:
            # Label for the inspection editing mechanism to work
            add_photo_or_not = "."
            logging.info(f"{add_photo_or_not=}")
            logging.info("В пункте 2.3 фотографий нет.")
        # Check input fields for missing text and
        # galleries for the ability to upload photos
        elements_to_check_for_edit = (
            form_number,
            form_name_title,
            contract_cert,
            area_of_inspect,
            сonfirm_that_materials_stored_correctly,
            add_photo_or_not,
            comments,
        )
        # If at least one field is not filled in, but contains only a period and possibly a space
        # then the inspection form needs to be edited
        is_edit = any(len(element) <= 2 for element in elements_to_check_for_edit)
        if is_edit:
            # EDIT INSPECTION FORM (fill in missing information)
            driver = edit_form(
                driver,
                base_dir,
                dict_plots_with_new_photos,
                block_level_plot,
                add_photo_or_not,
            )
        # Switch to main page
        main_tab = driver.window_handles[0]
        driver.close()
        driver.switch_to.window(main_tab)
    return driver
