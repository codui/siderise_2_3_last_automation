import logging
import shutil
import time
import datetime
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
from utils.database import add_photos_to_data_base
from utils.helpers import (
    collect_photos_from_photo_dir,
    fill_photo_contractors_competency,
    get_hash_photo_by_dhash,
    get_location_site_area,
)
from utils.scroll_to_element import scroll_down_to_element

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


def insert_data_into_field(field: WebElement, data: str) -> None:
    """Insert data into a web element field.

    Args:
        field (WebElement): A web element of type input or something similar,
            into whose field the data should be passed.
        data (str): The data to be passed into the field
    """
    logging.info(f"insert data {data=} into_field {field=}")
    # Clear the input field and pass data to it
    field.clear()
    field.send_keys(data)


def get_now_date_plus_six_month() -> tuple[str, str]:
    """ The function returns a tuple that consists of the current date of the month
    and the name of the month that will be in 6 months.

    Returns:
        tuple[str, str]:
            For example:
                ("15", "December")
    """
    now: datetime.datetime = datetime.datetime.now()
    # Current date of the month
    current_date: str = str(int(now.strftime("%d")))
    current_month_numb: int = int(now.strftime("%m"))
    # Name of the month that will be in 6 months
    current_month_number_plus_six: int = (
        (current_month_numb + 6)
        if (current_month_numb + 6) <= 12
        else (current_month_numb + 6) % 12
    )
    current_year_numb: int = now.year
    current_month_name_plus_six: str = datetime.date(current_year_numb, current_month_number_plus_six, 1).strftime("%B")
    return (current_date, current_month_name_plus_six)


@check_session
def set_date_to_created_inspection(driver: WebDriver) -> WebDriver:
    """Set the date in the calendar of the created inspection.

    Args:
        driver (WebDriver):

    Returns:
        driver (WebDriver):
    """
    wait = WebDriverWait(driver, 10)
    # Get the calendar element and click on it to expand it
    calendar_xpath = '//*[@id="custFormTD"]//div[2]/datepicker/label/input[1]'
    calendar = wait.until(EC.visibility_of_element_located((By.XPATH, calendar_xpath)))
    actions = ActionChains(driver)
    actions.scroll_to_element(calendar).perform()
    actions.scroll_by_amount(0, 200).perform()
    calendar.click()

    # Current date and name of the month that will be in 6 months
    current_date, current_month_name_plus_six = get_now_date_plus_six_month()

    month_select_xpath: str = (
        f'(//span[@class="ng-binding" and contains(normalize-space(.), "{current_month_name_plus_six}") and i[contains (@class, "datepicker-calendar")]])[2]'
    )
    # # ! If there ERROR in month_select_xpath than use this selector
    # month_select_xpath: str = (
    #     f'(//span[@class="ng-binding" and contains(normalize-space(.), "{current_month_name_plus_six}") and i[contains (@class, "datepicker-calendar")]])'
    # )
    month_select = wait.until(
        EC.element_to_be_clickable((By.XPATH, month_select_xpath))
    )
    month_select.click()

    month_xpath = f'(//div[contains(@class, "datepicker-calendar-header months")]//a[@title="Select month" and contains(normalize-space(.), "{current_month_name_plus_six}")])[2]'
    month = wait.until(EC.element_to_be_clickable((By.XPATH, month_xpath)))
    month.click()

    date_xpath: str = f'(//div[contains(@class, "datepicker-calendar-body")])[2]//a[contains(text(), "{current_date}")]'
    date = wait.until(EC.element_to_be_clickable((By.XPATH, date_xpath)))
    date.click()
    return driver


@check_session
def get_field_to_insert_comment(driver: WebDriver) -> tuple[WebDriver, WebElement]:
    """
    Get a field to insert a comment in item 2.1 of the Side-Rise inspection.

    Args:
        driver (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Find the create comment button
    btn_create_comment_xpath: str = (
        '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[2]/div/div[8]/div/div[1]/div[2]/div[1]/div[2]/button'
    )
    btn_create_comment: WebElement = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, btn_create_comment_xpath))
    )
    # Scroll to the button so that it is visible and click on it
    actions = ActionChains(driver)
    actions.scroll_to_element(btn_create_comment).perform()
    actions.scroll_by_amount(0, 200).perform()
    btn_create_comment.click()
    # Select the comment field after it appears on the page
    field_to_insert_comment_xpath: str = (
        '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[2]/div/div[8]/div/div[2]//div[contains(@class, "comment-section")]/div[2]/textarea'
    )
    field_to_insert_comment: WebElement = driver.find_element(
        By.XPATH, field_to_insert_comment_xpath
    )
    return (driver, field_to_insert_comment)


def wait_for_upload_photo(
    driver: WebDriver, check_upload_xpath: str, photo: Path
) -> tuple[WebDriver, Path]:
    """The function waits for one photo to be uploaded to the site for Side-Rise inspection.

    Args:
        driver (WebDriver):
        check_upload_xpath (str): XPATH of the photo loading indicator element
            For example:
                "//img[contains(@ng-if, "file.isUploading")]"

        photo (Path):
            For example:
                WindowsPath('D:/WORK/Horand_LTD/TASK TO DO/Locations with data for inspections/SideRise/A_L1_Plot_4/2.3/new_photos_send_to_asite/WhatsApp Image 2025-04-29 at 16.00.05_71d3d084.jpg')

    Returns:
        (driver, photo) tuple[WebDriver, Path]
    """
    check_upload: WebElement = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.XPATH, check_upload_xpath))
    )
    while check_upload:
        time.sleep(0.5)
        # Check if there is a loading indicator element, which means that the photo is still loading
        try:
            check_upload = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, check_upload_xpath))
            )
        # If you couldn't get the loading indicator element, it means it's already gone,
        # which means the photo has already loaded and you need to break the cycle
        except Exception:
            logging.info(f"Photo {photo} is upload.")
            break
    return (driver, photo)


def add_photo_to_side_rise_point_2_3(
    driver: WebDriver,
    dict_plots_with_new_photos: dict[str, list[Path]],
    block_level_plot: str,
) -> tuple[WebDriver, list[Path]]:
    r"""
    Adds a photo from a folder of the type:
    D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\A_L1_Plot_1\2.3\new_photos_send_to_asite
    on asite in the appropriate (for example A_L1_Plot_1) Side-Rise inspection in item 2.3

    Args:
        driver (WebDriver):

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

        block_level_plot (str): The apartment code adopted in this project. The code consists of three parts.
            The first part corresponds to the name of the block (house).
            This is one large letter from the following list of letters - A, B, C, D, E, F, G.

            The second part is responsible for the floor of the apartment. This is one large letter L (from Level)
            and a number (depending on the floor on which the apartment is located, it can be from 1 to 8).

            The third part is responsible for the apartment number and
            consists of the word Plot and the number of the apartment.
            For example:
                "A_L1_Plot_2"

    Returns:
        (driver, new_photos_on_asite) tuple[WebDriver, list[Path]]

    """
    wait: WebDriverWait = WebDriverWait(driver, 10)
    # List of photos to send to asite Side-Rise in item 2.3
    # new_photos:
    # [WindowsPath('D:/WORK/Horand_LTD/TASK TO DO/Locations with data for inspections/SideRise/A_L1_Plot_4/2.3/new_photos_send_to_asite/WhatsApp Image 2025-04-29 at 16.00.05_71d3d084.jpg')]
    new_photos: list[Path] = dict_plots_with_new_photos[block_level_plot]
    logging.info(f"photos in add_photo_to_side_rise_point_2_3: {new_photos}")

    try:
        # ! Get the add_new_attachment element if there are photos in item 2.3
        add_new_attachment_xpath: str = (
            "//div[contains(text(), '2.3')]/ancestor::div[contains(@class, 'activity-row')]//div[contains(@class, 'add-new-item') and contains(., 'Add New Attachment')]//span"
        )
        # Get add_new_attachment button
        add_new_attachment: WebElement = wait.until(
            EC.presence_of_element_located((By.XPATH, add_new_attachment_xpath))
        )
        logging.info(f"{add_new_attachment=}")
        scroll_down_to_element(driver, add_new_attachment)
        # Click on the add_new_attachment button to display the button for sending images
        add_new_attachment.click()

        # Get button to send images
        btn_input_xpath: str = (
            '//div[.//div[normalize-space(text()) = "2.3"]]/following-sibling::div[not(@class)]//child::div[2]/child::div[2]/child::div[2]/child::div[3]//input'
        )
        btn_input: WebElement = driver.find_element(By.XPATH, btn_input_xpath)
        # logging.info(f"btn_input is {btn_input=}")
        time.sleep(1)

        # check_upload_xpath: str = '//img[contains(@ng-if, "file.isUploading")]'
        # new_photos_on_asite: list = []

        # for new_photo in new_photos:
        #     # Отправить фото
        #     btn_input.send_keys(str(new_photo))
        #     # Проскролить к элементу
        #     actions = ActionChains(driver)
        #     actions.scroll_to_element(add_new_attachment).perform()
        #     # Подождать пока фото загрузится
        #     driver, new_photo_on_asite = wait_for_upload_photo(
        #         driver, check_upload_xpath, new_photo
        #     )
        #     new_photos_on_asite.append(new_photo_on_asite)
    except Exception:
        # ! Get the add_new_attachment element if there are no photos in 2.3
        paperclip_xpath: str = (
            "//div[contains(text(), '2.3')]/ancestor::div[contains(@class, 'activity-row')]//i[contains(@class, 'fa-paperclip')]"
        )
        # Get the button with the paperclip icon and click on it
        paperclip: WebElement = wait.until(
            EC.presence_of_element_located((By.XPATH, paperclip_xpath))
        )
        # Scroll to paperclip element
        scroll_down_to_element(driver, paperclip)
        paperclip.click()
        time.sleep(1)

        add_new_attachment_xpath = "//div[contains(text(), '2.3')]/ancestor::div[contains(@class, 'activity-row')]//div[contains(@class, 'add-new-item') and contains(., 'Add New Attachment')]//span"
        # Get add_new_attachment button
        add_new_attachment = wait.until(
            EC.presence_of_element_located((By.XPATH, add_new_attachment_xpath))
        )

        # Get button to send images
        btn_input_xpath = '//div[.//div[normalize-space(text()) = "2.3"]]//input[contains(@id, "imgupload_multi_AttachedDocs")]'
        btn_input = driver.find_element(By.XPATH, btn_input_xpath)
        logging.info(f"btn_input is {btn_input=}")
        time.sleep(1)

        # for new_photo in new_photos:
        #     # Отправить фото
        #     btn_input.send_keys(str(new_photo))
        #     # Проскролить к элементу
        #     actions = ActionChains(driver)
        #     actions.scroll_to_element(add_new_attachment).perform()
        #     # Подождать пока фото загрузится
        #     driver, new_photo_on_asite = wait_for_upload_photo(
        #         driver, check_upload_xpath, new_photo
        #     )
        #     new_photos_on_asite.append(new_photo_on_asite)

    check_upload_xpath: str = '//img[contains(@ng-if, "file.isUploading")]'
    new_photos_on_asite: list = []

    for new_photo in new_photos:
        # Send photo
        btn_input.send_keys(str(new_photo))
        # Scroll to the add_new_attachment element
        actions = ActionChains(driver)
        actions.scroll_to_element(add_new_attachment).perform()
        # Wait for the photo to load
        driver, new_photo_on_asite = wait_for_upload_photo(
            driver, check_upload_xpath, new_photo
        )
        new_photos_on_asite.append(new_photo_on_asite)
    return (driver, new_photos_on_asite)


@check_session
def download_photos_from_asite_block_level_plot_2_3_to_os(
    driver: WebDriver, photos_on_asite_elements: list[WebElement]
) -> WebDriver:
    """Download photos from Side-Rise inspection of specific location block_level_plot from point 2.3

    Args:
        driver (WebDriver)

        photos_on_asite (list[WebElement]): List of photos that are already on asite in point 2.3

    Returns:
        driver (WebDriver)
    """
    for photo_element in photos_on_asite_elements:
        # logging.info(f"{dir(photo_element)=}")
        # Scroll to the photo_element element (to the inspection photo in point 2.3)
        driver.execute_script("arguments[0].scrollIntoView(true);", photo_element)
        # Get the height of a photo element on a website
        height = photo_element.rect.get("height", 0)
        # Scroll to the top of the photo_element
        driver.execute_script(f"window.scrollBy(0, {height - 150});")
        time.sleep(1)
        # Click on photo_element
        photo_element.click()
        time.sleep(1)
    return driver


def get_list_photos_from_download_dir_os(
    download_dir: Path = Path(r"C:\Users\Human\Downloads\download_from_asite"),
    extensions: tuple[str, ...] = (".jpg", ".jpeg"),
) -> list[Path]:
    r"""Get a list of photos downloaded from Side-Rise inspection of location block_level_plot point 2.3,
    in order to then move these photos to folders of the following type:
    D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\G_L8_Plot_456\2.3\photos_on_asite

    The downloaded photos are located in the operating system at download_dir.
    "C:\Users\Human\Downloads\download_from_asite

    If download_dir does not exist or is not an absolute path, an error is raised.

    Args:
        download_dir (Path): The folder where the photos downloaded from the block_level_plot location are located.
            Defaults to r"C:\Users\Human\Downloads\download_from_asite".

        extensions tuple[str, ...]: A tuple of file extensions to select.
            Defaults (".jpg", ".jpeg")
    """
    if download_dir.exists() and download_dir.is_absolute():
        return [
            obj
            for obj in download_dir.glob("*")
            if obj.is_file() and obj.suffix.lower() in extensions
        ]
    message_error: str = (
        f"Error in function get_list_photos_from_download_dir_os.\n"
        f"Directory {dir} is not exists or path {dir} is not absolute."
    )
    raise Exception(message_error)


def move_photos_from_download_dir_to_photos_on_asite(
    base_dir: Path,
    block_level_plot: str,
    photos_from_download_dir: list[Path],
    dir_name: Path = Path(r"2.3/photos_on_asite"),
) -> list[Path]:
    r"""Transfer the list of photos downloaded from Side-Rise inspection by location block_level_plot of point 2.3,
    (which at the moment of the function execution are in the operating system download folder at the address
    C:\Users\Human\Downloads\download_from_asite)

    to the folder block_level_plot\2.3\photos_on_asite of the operating system.
    For example, to the folder:
    D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\A_L1_Plot_6\2.3\photos_on_asite

    Args:
        base_dir: (Path) Path to the folder where folders with apartment location names are stored.
            Folders with the apartment location name may contain photos related to point 2.3
            of the Side-Rise inspection for this apartment.
            The apartment location name consists of the block, floor, and apartment number.
            For example:
                Path(r"D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise")

        block_level_plot (str): The apartment code adopted in this project. The code consists of three parts.
            The first part corresponds to the name of the block (house).
            This is one large letter from the following list of letters - A, B, C, D, E, F, G.

            The second part is responsible for the floor of the apartment. This is one large letter L (from Level)
            and a number (depending on the floor on which the apartment is located, it can be from 1 to 8).

            The third part is responsible for the apartment number and
            consists of the word Plot and the number of the apartment.
            For example:
                "A_L1_Plot_2"

        photos_from_download_dir (list[Path]): List of photos downloaded from Side-Rise inspection
            by location block_level_plot point 2.3, which are currently in the operating system boot folder.
            For example:
                [
                    WindowsPath('C:/Users/Human/Downloads/download_from_asite/APIM8352.JPG'),
                    WindowsPath('C:/Users/Human/Downloads/download_from_asite/IMG-20250204-WA0036.jpg')
            ]

        dir_name (Path): Relative path to the folder for photos that are already on asite.
            Defaults Path(r"2.3/photos_on_asite")
    """
    # target_dir=WindowsPath('D:/WORK/Horand_LTD/TASK TO DO/Locations with data for inspections/SideRise/A_L1_Plot_6/2.3/photos_on_asite')
    target_dir: Path = base_dir / block_level_plot / dir_name
    logging.info(f"{target_dir=}")

    for photo in photos_from_download_dir:
        dest = target_dir / photo.name
        shutil.move(str(photo), str(dest))

    return list(target_dir.iterdir())


def move_duplicate_photos_from_new_photos_send_to_asite_to_photos_to_delete(
    new_photos: list[Path],
    photos_on_asite: list[Path],
) -> list[Path]:
    r""" Compare the hash of each photo from the new_photos photo list
    with the hash of each photo from the photos_on_asite photo list.
    Photos from the new_photos list whose hash matches the hash of photos from photos_on_asite -
    move to the folder C:\Users\Human\Downloads\photos_to_delete.

    Args:
        new_photos (list[Path]): List of new photos to send to inspections on asite.
            For example:
                [WindowsPath('D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\A_L1_Plot_1\2.3\new_photos_send_to_asite')]

        photos_on_asite (list[Path]): List of photos that are already in inspections on asite.
            For example:
                [WindowsPath('D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\A_L1_Plot_6\2.3\photos_on_asite')]
    """
    # Temporary folder where you need to move duplicate photos from the new_photos folder
    photos_to_delete_dir: Path = Path(r"C:\Users\Human\Downloads\photos_to_delete")

    # List of photo hashes from the new_photos list
    new_photos_hash: list = [
        get_hash_photo_by_dhash(new_photo) for new_photo in new_photos
    ]
    # List of photo hashes from photos_on_asite list
    photos_on_asite_hash: list = [
        get_hash_photo_by_dhash(photo_on_asite) for photo_on_asite in photos_on_asite
    ]
    # logging.info(f"{new_photos=}")
    # logging.info(f"{photos_on_asite=}")

    # logging.info(f"{new_photos_hash=}")
    # logging.info(f"{photos_on_asite_hash=}")

    # List of photos to move to the folder photos_to_delete_dir
    new_photos_to_delete: list[Path] = []

    for photo, hash in zip(new_photos, new_photos_hash):
        for photo_on_asite_hash in photos_on_asite_hash:
            # Compare Hamming distance
            distance = hash - photo_on_asite_hash
            # Consider images to be the same if distance <= 5
            if distance <= 5:
                logging.info(f"{distance=}")
                logging.info(f"{photo=}")
                new_photos_to_delete.append(photo)

    while len(new_photos_to_delete) > 0:
        # D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\A_L1_Plot_6\2.3\new_photos_send_to_asite\viewThumb (1).jpg
        new_photo_to_delete: Path = new_photos_to_delete[0]
        # photos_to_delete_dir = Path(r"C:\Users\Human\Downloads\photos_to_delete")
        dest: Path = photos_to_delete_dir / new_photo_to_delete.name
        logging.info(f"Move {str(new_photo_to_delete)} to {str(dest)}")
        # Move a photo from the new_photos folder, for example
        # D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\A_L1_Plot_6\2.3\new_photos_send_to_asite\viewThumb (1).jpg
        # to folder C:\Users\Human\Downloads\photos_to_delete\viewThumb (1).jpg
        shutil.move(str(new_photo_to_delete), str(dest))
        new_photos_to_delete.remove(new_photo_to_delete)
        new_photos.remove(new_photo_to_delete)

    logging.info("\n new_photos after delete")
    pprint(new_photos)

    logging.info("\n new_photos_to_delete after delete")
    pprint(new_photos_to_delete)
    return new_photos


def move_photos_from_new_photos_to_photos_not_on_asite(
    base_dir: Path,
    dict_plots_with_new_photos: dict[str, list[Path]],
    block_level_plot: str,
) -> None:
    """ Переместить фотографии из папок "new_photos_send_to_asite"
    в папки "photos_not_on_asite_because_in_2_3_already_30_photos".

    Args:
        base_dir (Path): Base directory with plots.
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
    """
    # Relative path to the folders to which you want to move photos
    photos_not_on_asite: Path = Path(
        r"2.3\photos_not_on_asite_because_in_2_3_already_30_photos"
    )
    # Photos that were not sent to the inspection because there are already 30 or more photos in the inspection.
    # Therefore, they need to be moved to the folder photos_not_on_asite_because_in_2_3_already_30_photos.
    new_photos_send_to_asite: list[Path] = dict_plots_with_new_photos[block_level_plot]
    for new_photo in new_photos_send_to_asite:
        dest: Path = base_dir / block_level_plot / photos_not_on_asite / new_photo.name
        # Move photos from new_photos_send_to_asite
        # to photos_not_on_asite_because_in_2_3_already_30_photos
        shutil.move(str(new_photo), str(dest))
        logging.info(f"Move {str(new_photo)} to {str(dest)}")


@check_session
def fill_created_form(
    driver: WebDriver,
    dict_plots_with_new_photos: dict[str, list[Path]],
    block_level_plot: str,
    base_dir: Path,
) -> WebDriver:
    """ Fills in the required fields of the newly created Side-Rise Inspection form with the appropriate data.

    Args:
        driver (WebDriver)
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
        base_dir (Path): Base directory with plots.
            Path(r"D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise")

    Returns:
        WebDriver
    """
    dir_with_photos_uploaded_on_asite: Path = Path(r"2.3\photos_on_asite")
    wait: WebDriverWait = WebDriverWait(driver, 10)
    # Wait for the page to load
    iframe_with_form: WebElement = wait.until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='createFormIframe']"))
    )
    # Switch to another iframe
    driver.switch_to.frame(iframe_with_form)
    # Dictionary with XPATH paths to web elements
    xpaths: dict[str, str] = {
        "ref_numb": '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[1]/div/div/div[1]/div/div[2]/div/div/div/input',
        "form_name_title": '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[1]/div/div/div[2]/div/div[2]/div/div/div/input',
        "contract_cert": '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[1]/div/div/div[3]/div/div[2]/div/div/div/input',
        "area_of_inspection": '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[1]/div/div/div[4]/div/div[2]/div/div/div/input',
        "confirm_materials_stored_with_instructions": '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[1]/div/div/div[6]/div/div[2]/div/div/div/input',
    }
    # ! Fill in the input field contractors_q_a_form_ref_numb_xpath
    # Contractor’s Quality Assurance form reference number
    contractors_q_a_form_ref_numb: WebElement = wait.until(
        EC.visibility_of_element_located((By.XPATH, xpaths["ref_numb"]))
    )
    insert_data_into_field(contractors_q_a_form_ref_numb, "BMS01.G01")
    # ! Fill in the input field contractors_q_a_form_name_title
    # Contractor’s Quality Assurance form name/title
    contractors_q_a_form_name_title: WebElement = wait.until(
        EC.visibility_of_element_located((By.XPATH, xpaths["form_name_title"]))
    )
    insert_data_into_field(contractors_q_a_form_name_title, "Quality policy")
    # ! Fill in the contract_cert input field
    # Contractor’s certification body
    contract_cert: WebElement = wait.until(
        EC.visibility_of_element_located((By.XPATH, xpaths["contract_cert"]))
    )
    insert_data_into_field(contract_cert, "IFC Certificate number: IFCC 3054")
    # ! Fill in the input field area_of_inspection
    # Area of inspection (please note the gridlines or structural elements to locate this area and floor/level)
    area_of_inspection: WebElement = driver.find_element(By.XPATH, xpaths["area_of_inspection"])
    driver, location_site_area_text = get_location_site_area(driver)
    insert_data_into_field(area_of_inspection, location_site_area_text)
    # ! Fill in the input field confirm_materials_stored_with_instructions
    # Please confirm that the materials have been stored and protected in accordance with
    # manufacturer’s instructions and the Contractor’s Quality Management System
    confirm_materials_stored_with_instructions: WebElement = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, xpaths["confirm_materials_stored_with_instructions"])
        )
    )
    insert_data_into_field(confirm_materials_stored_with_instructions, "Yes")
    # ! Upload all photos in the Add photo of Contractor’s competency/CSCS card field
    driver: WebDriver = fill_photo_contractors_competency(driver)
    # ! Fill in the input field field_to_insert_comment
    # Confirm that a copy of the contractor’s Project Quality Plan
    driver, field_to_insert_comment = get_field_to_insert_comment(driver)
    insert_data_into_field(
        field_to_insert_comment,
        "ITP and PQP uploaded on Asite\n"
        "H8499-LEM-SW-ZZ-QA-CT-19715 PQP\n"
        "H8499-LEM-SW-ZZ-QA-CO-LM123 ITP\n",
    )

    # List of new photos
    new_photos: list[Path] = dict_plots_with_new_photos[block_level_plot]
    logging.info("new_photos")
    pprint(new_photos)
    # new_photos_on_asite: list[Path]]
    driver, new_photos_on_asite = add_photo_to_side_rise_point_2_3(
        driver, dict_plots_with_new_photos, block_level_plot
    )
    logging.info("\n new_photos_on_asite:")
    pprint(new_photos_on_asite)

    for new_photo in new_photos_on_asite:
        dest: Path = (
            base_dir
            / block_level_plot
            / dir_with_photos_uploaded_on_asite
            / new_photo.name
        )
        # Move photos sent to Side-Rise inspection to block_level_plot location in step 2.3
        # from new_photos_send_to_asite folder to photos_on_asite folder
        shutil.move(str(new_photo), str(dest))
        logging.info(f"Move {str(new_photo)} to {str(dest)}")

    photos_on_asite_path: Path = (
        base_dir / block_level_plot / Path(r"2.3\photos_on_asite")
    )
    logging.info(f"{photos_on_asite_path=}")

    photos_on_asite: list[Path] = collect_photos_from_photo_dir(photos_on_asite_path)
    logging.info(f"{photos_on_asite=}")

    # Add photos sent to asite to the database
    add_photos_to_data_base(
        block_level_plot,
        str(dir_with_photos_uploaded_on_asite),
        photos_on_asite,
    )

    # ! Set the date in the calendar - the current date and the month that will be in half a year
    driver = set_date_to_created_inspection(driver)
    # Get the "Update" button and click on it
    btn_update_xpath: str = '//*[@id="btnSaveForm"]'
    btn_update: WebElement = wait.until(EC.element_to_be_clickable((By.XPATH, btn_update_xpath)))
    btn_update.click()
    time.sleep(3)
    # # Switch to default iframe
    driver.switch_to.default_content()
    time.sleep(2)
    return driver
