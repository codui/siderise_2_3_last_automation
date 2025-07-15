# Importing Selenium WebDriver to interact with the browser
import hashlib
import logging
import shutil
import time
from pathlib import Path

import imagehash
from PIL import Image
from PIL.Image import Image as PILImage

# from pprint import pprint
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

# Used for setting wait times
from selenium.webdriver.support.ui import WebDriverWait

from auth.decorators import check_session
from utils.scroll_to_element import scroll_down_to_element, scroll_up_to_element

# from pprint import pprint


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


@check_session
def set_color_to_element(
    driver: WebDriver, element: WebElement, color: str = "#5cc695"
) -> WebDriver:
    """Highlights the received element with color for 1 second.
    To control the script operation and for demonstration.

    Args:
        driver (WebDriver):
        element (WebElement): A web element that needs to be highlighted in color.
        color (str, optional): Color in html recording standard. Defaults to "#5cc695".

    Returns:
        WebDriver
    """
    original_style = element.get_attribute("style")
    # Highlight the active element "element"
    driver.execute_script(
        "arguments[0].setAttribute('style', arguments[1]);",
        element,
        f"background: {color}",
    )
    time.sleep(1)
    # Restore the original style to the element "element"
    driver.execute_script(
        "arguments[0].setAttribute('style', arguments[1]);", element, original_style
    )
    return driver


def get_letter_block_to_start() -> str:
    """Asks the user for the letter of the block from which the script will start working.

    Returns:
        (str): Returns the block letter from which the script will start working.
    """
    letter_validity: bool = False
    block_letters: str = "ABCDEFG"
    while letter_validity is False:
        letter_block_to_start: str = input(
            "Enter the letter of the block name you want to start automation from.\n"
            "Press one letter from the letters A, B, C, D, E, F, G on your keyboard in lowercase or uppercase.\n"
            "If you want the program to start from the first block, just press the 'Enter' key.\n"
            "Please make your choice, enter the letter of the block name or press 'Enter': "
        )
        if len(letter_block_to_start) > 0:
            logging.info(f"\nYou enter letter_block_to_start: {letter_block_to_start}")
        # If user entered one letter from ABCDEFG stop loop
        if (
            len(letter_block_to_start) == 1
            and letter_block_to_start.upper() in block_letters
        ):
            letter_validity = True
            logging.info(
                f"The program will start working from the block with the letter {letter_block_to_start}"
            )
        # If the user has not entered anything, but simply pressed "Enter", then stop the loop,
        # so that the script starts working from the first row of the table. That is, from the very top of the table.
        elif len(letter_block_to_start) == 0:
            letter_validity = True
            logging.info("The program will work from the beginning of the list.")
    return letter_block_to_start.lower()


def get_number_level_to_start() -> str:
    """The function receives the level number from which to start working.
    Formats number_level_to_start - adds 0 to the variable value,
    if number_level_to_start consists of one digit.
    Returns digits of the form "01" as a string.

    Returns:
        (str): Returns digits of the form "01"
    """
    get_number_level: bool = False
    while get_number_level is False:
        number_level_to_start: str = input(
            "\nEnter the number of the 'level' from which you want to start automation.\n"
            "Press one number on the keyboard.\n\n"
            "If you want the program to process everything from the very beginning, \n"
            "then you don't need to enter anything, just press the 'Enter' key.\n\n"
            "Please enter the level number: "
        )
        if 1 <= len(number_level_to_start) <= 2 and number_level_to_start != "0":
            get_number_level = True
            logging.info(f"\nYou enter number_level_to_start: {number_level_to_start}")
            logging.info(
                f"The program will start working from the level with the number {number_level_to_start}"
            )
        elif len(number_level_to_start) == 0:
            get_number_level = True
            logging.info("The program will work from the beginning of the list.")
        else:
            logging.info(
                f"\nThe number that you enter {number_level_to_start} is not correct.\n"
            )
    return (
        "0" + number_level_to_start
        if len(number_level_to_start) == 1
        else number_level_to_start
    )


def get_number_plot_to_start() -> str:
    """The function gets the plot number to start with.
    Formats number_plot_to_start - adds 0 to the variable value,
    if number_plot_to_start consists of one digit.

    Returns:
        (str): Returns the data type string in the form of numbers "01", "09", "10", etc.
    """
    get_number_level = False
    while get_number_level is False:
        number_plot_to_start = input(
            "\nEnter the number of the 'plot' from which you want to start automation.\n"
            "Press one number on the keyboard.\n\n"
            "If you want the program to process everything from the very beginning, \n"
            "then you don't need to enter anything, just press the 'Enter' key.\n\n"
            "Please enter the plot number: "
        )
        if 1 <= len(number_plot_to_start) <= 3 and number_plot_to_start != "0":
            get_number_level = True
            logging.info(f"\nYou enter number_plot_to_start: {number_plot_to_start}")
            logging.info(
                f"The program will start working from the plot with the number {number_plot_to_start}"
            )
        elif len(number_plot_to_start) == 0:
            get_number_level = True
            logging.info("The program will work from the beginning of the list.")
        else:
            logging.info(
                f"\nThe number that you enter {number_plot_to_start} is not correct.\n"
            )
    return (
        "0" + number_plot_to_start
        if len(number_plot_to_start) == 1
        else number_plot_to_start
    )


@check_session
def get_location_title(
    driver: WebDriver, number_line: int
) -> tuple[WebDriver, str | None]:
    """
    The function gets the apartment number text from the title attribute of the current cell
    in the "Actions/Locations" column of the "New Malden Quality Plan" table.

    Args:
        driver (WebDriver)
        number_line (int): The row number of the "Activities / Locations" column of the table "New Malden Quality Plan"
            listing all inspections.

    Returns:
        (driver, location_title) tuple[WebDriver, str | None]:
            For example:
                (WebDriver, "Plot 03")
    """
    wait: WebDriverWait = WebDriverWait(driver, 100)
    # f'//*[@id="table_body_header_scroller"]/div/div[{number_line}]'
    location_cell_xpath: str = (
        f'//*[@id="table_body_header_scroller"]/div/div[{number_line}]//div[contains(@class, "location-title")]'
    )
    location_cell: WebElement = wait.until(
        EC.visibility_of_element_located((By.XPATH, location_cell_xpath))
    )
    location_title: str | None = location_cell.get_attribute("title")
    return (driver, location_title)


def get_location_site_area(driver: WebDriver) -> tuple[WebDriver, str]:
    """In the editing mode of the apartment inspection form, from the form field "Location / Site / Area"
    receives the location of the apartment in the form of the text "Block A Level 01 Plot 07".
    To further insert this text into the "Area of ​​inspection" field.

    Args:
        driver (WebDriver)

    Returns:
        (driver, location_site_area_text) tuple[WebDriver, str]: Location of the apartment type
            "Block A Level 01 Plot 07".
            For example:
                (WebDriver, "Block A Level 01 Plot 07")
    """
    location_site_area_xpath: str = (
        '//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/div[1]/div[3]/input'
    )
    location_site_area_input: WebElement = driver.find_element(
        By.XPATH, location_site_area_xpath
    )
    driver.execute_script(
        "arguments[0].removeAttribute('disabled')", location_site_area_input
    )
    location_site_area_raw_text: str | None = location_site_area_input.get_attribute(
        "value"
    )
    location_site_area_text: str = " ".join(location_site_area_raw_text.split(">"))
    return (driver, location_site_area_text)


def find_plot_dirs(base_dir: Path) -> list[Path]:
    r"""Returns a list of directories in "base_dir" of the form "A_L1_Plot_1" that may contain images.

    Args:
        base_dir (Path): Path to the root folder with folders of the form "A_L1_Plot_1".
            For example:
                WindowsPath("D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise")

    Returns:
        list[Path]: List of folders of type A_L<number>_Plot_<number>.
    """
    return [
        obj for obj in base_dir.iterdir() if obj.is_dir() and "plot" in obj.name.lower()
    ]


def create_sub_dir(base_dir: Path, sub_dir: Path) -> None:
    r"""In each folder of the type
    D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\A_L10_Plot_82
    creates a folder "2.3", and in the folder "2.3" creates a folder "new_photos_send_to_asite"

    As a result, we get the following folder structure:
    D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\A_L10_Plot_82\2.3
    D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\A_L10_Plot_82\2.3\new_photos_send_to_asite

    Args:
        base_dir (Path): Path to the folder with the apartment name
            For example:
                WindowsPath('D:/WORK/Horand_LTD/TASK TO DO/Locations with data for inspections/SideRise/A_L10_Plot_82'
        sub_dir (Path): Subfolder to be created
    """
    target_dir_path: Path = base_dir / sub_dir
    # If the target_dir_path folder does not exist, create it
    if not target_dir_path.exists():
        target_dir_path.mkdir()


def create_sub_dir_in_dir(base_dir, sub_dir) -> None:
    r"""Creates in each folder of the type:
    D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\A_L1_Plot_2\2.3

    folder:
    D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\A_L1_Plot_2\2.3\photos_on_asite

    Args:
        base_dir (Path): Path to folder with folders by apartment names.
            For example:
                D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise
    """
    # list_plot_dir = [
    #   WindowsPath('D:/WORK/Horand_LTD/TASK TO DO/Locations with data for inspections/SideRise/A_L10_Plot_82'),
    #   WindowsPath('D:/WORK/Horand_LTD/TASK TO DO/Locations with data for inspections/SideRise/G_L8_Plot_456')
    # ]
    list_plot_dir: list[Path] = find_plot_dirs(base_dir)

    for plot_dir in list_plot_dir:
        # WindowsPath('D:/WORK/Horand_LTD/TASK TO DO/Locations with data for inspections/SideRise/A_L10_Plot_82/2.3')
        create_sub_dir(plot_dir, sub_dir)


def get_hash_photo_by_dhash(photo_path: Path) -> imagehash.ImageHash:
    """The function receives the hash of the photo file and returns it.

    Args:
        photo_path(Path): Absolute path to the photo.

    Returns:
        hash_photo(imagehash.ImageHash): Photo hash.
    """
    # Create a PILImage object of the photo
    photo: PILImage = Image.open(str(photo_path))
    # Get hash for photo
    hash_photo: imagehash.ImageHash = imagehash.dhash(photo)
    return hash_photo


def get_hash_photo_by_pixel_plus_file_size(
    photo_path: Path,
    algo="sha256",
    resize_to: None | tuple[int, int] = None,
    mode="RGB",
) -> str:
    """Calculates a hash from the pixels of a photo.
    During the calculation, the photo is resized to the value specified in the resize_to argument.
    Returns the photo hash as a string.

    Args:
        photo_path (Path): Absolute path to the photo file.

        algo (str, optional): The algorithm used to calculate the hash.
            Defaults to "sha256".

        resize_to (tuple[int, int], optional): The size to which the image will be converted
        before calculating the hash.
            Defaults to (2016, 2016).

        mode (str, optional): The mode in which the interaction with the photo will occur.
            Defaults to "RGB".

    Returns:
        str: Returns the image hash
        For example:
            '4ef74692c099ff52838a320d7d6ec5e044daf329c0802e5991c207df9a2559ad'
    """
    # logging.info(f"{photo_path=}")
    # Open photo
    image: PILImage = Image.open(photo_path).convert(mode)
    # Change size of image to fixed size
    if resize_to:
        image = image.resize(resize_to)
    # Get pixel byte data
    pixel_bytes: bytes = image.tobytes()
    # Calculate the hash
    hash_func = getattr(hashlib, algo)()
    # hash_func=<sha256 _hashlib.HASH object @ 0x0000021D447EF030>, type(hash_func)=<class '_hashlib.HASH'>
    hash_func.update(pixel_bytes)
    return hash_func.hexdigest()  # + str(len(pixel_bytes))


def collect_photos_from_photo_dir(
    photo_dir: Path,
    extensions: tuple[str, ...] = (".jpg", ".jpeg"),
) -> list[Path]:
    """
    Searches for files with the specified extensions in the "photo_dir" directory.
    Returns a list path of photo files in the "photo_dir" directory.

    Args:
        photo_dir (Path): Absolute path to the image directory.
            For example:
                WindowsPath('D:/WORK/Horand_LTD/TASK TO DO/Locations with data for inspections/SideRise/A_L1_Plot_2/2.3')

        extensions (tuple[str, ...]): Valid file extensions.

    Returns:
        list[Path]: List of image files.
            For example:
                [
                    WindowsPath('D:/WORK/Horand_LTD/TASK TO DO/Locations with data for inspections/SideRise/A_L1_Plot_4/2.3/WhatsApp Image 2025-04-29 at 16.00.05_7054b046.jpg'),
                    WindowsPath('D:/WORK/Horand_LTD/TASK TO DO/Locations with data for inspections/SideRise/A_L1_Plot_4/2.3/WhatsApp Image 2025-04-29 at 16.00.05_71d3d084.jpg')
                ]
    """
    # logging.info(f"collect_photos_from_photo_dir {photo_dir=}")
    return [
        obj
        for obj in photo_dir.glob("*")
        if obj.is_file() and obj.suffix.lower() in extensions
    ]


def transfer_files_received_from_whatsapp(
    rel_path_to_photo_from_whatsapp: Path,
) -> None:
    r"""Move files from folder
    D:/WORK/Horand_LTD/TASKS_DOING_NOW/side_rise_download_photo_to_asite_point_2_3_refactor_ready/chats/Python dev chat/

    to folder
    D:\WORK\Horand_LTD\TASKS_DOING_NOW\side_rise_download_photo_to_asite_point_2_3_refactor_ready\image_sorter_ocr\pics

    Args:
        path_to_photo_from_whatsapp (Path): Relative path to folder with photo from WhatsApp.
            For example:
                Path(r"chats\Python dev chat")
    """
    # Project root folder
    current_dir: Path = Path.cwd()
    # abs_path_to_photo_from_whatsapp:
    # WindowsPath('D:/WORK/Horand_LTD/TASKS_DOING_NOW/side_rise_download_photo_to_asite_point_2_3_refactor_ready/chats/Python dev chat')
    abs_path_to_photo_from_whatsapp: Path = (
        current_dir / rel_path_to_photo_from_whatsapp
    )
    photos: list[Path] = collect_photos_from_photo_dir(abs_path_to_photo_from_whatsapp)

    for photo in photos:
        dest: Path = current_dir / Path("image_sorter_ocr/pics") / photo.name
        logging.info(f"{dest=}")
        # Move photo "photo":
        # WindowsPath('D:/WORK/Horand_LTD/TASKS_DOING_NOW/side_rise_download_photo_to_asite_point_2_3_refactor_ready/chats/Python dev chat/Marius_175.jpg')
        # on the path "dest":
        # WindowsPath("D:\WORK\Horand_LTD\TASKS_DOING_NOW\side_rise_download_photo_to_asite_point_2_3_refactor_ready\image_sorter_ocr\pics")
        shutil.move(str(photo), str(dest))
        logging.info(f"\nMove {str(photo)} \nto {str(dest)}")


def move_duplicate_photos_to_dir_double(
    base_dir: Path, dir_with_new_photo: Path
) -> None:
    r"""Moves duplicate photos from a folder:
    D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\A_L1_Plot_1\2.3\new_photos_send_to_asite

    to folder:
    D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\A_L1_Plot_1\2.3\duplicated_photos

    Args:
        base_dir (Path): Path to folder with folders by apartment names.
            For example:
                D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise

        dir_with_new_photo (Path): Relative path to folder with new photo.
            WindowsPath("2.3\new_photos_send_to_asite")
    """
    list_plot_dir: list[Path] = find_plot_dirs(base_dir)
    # plot_dir:
    # WindowsPath('D:/WORK/Horand_LTD/TASK TO DO/Locations with data for inspections/SideRise/A_L10_Plot_82')
    for plot_dir in list_plot_dir:
        # dir_with_new_photos:
        # WindowsPath('D:/WORK/Horand_LTD/TASK TO DO/Locations with data for inspections/SideRise/A_L10_Plot_82/2.3/new_photos_send_to_asite')
        dir_with_new_photos = plot_dir / dir_with_new_photo
        # photos = [
        # 'D:/WORK/Horand_LTD/TASK TO DO/Locations with data for inspections/SideRise/A_L3_Plot_26/2.3/new_photos_send_to_asite/JIEN0141.JPG',
        # 'D:/WORK/Horand_LTD/TASK TO DO/Locations with data for inspections/SideRise/A_L3_Plot_26/2.3/new_photos_send_to_asite/RIAQ5261.JPG',
        # ]
        photos: list[Path] = collect_photos_from_photo_dir(dir_with_new_photos)
        # logging.info(f"\n{photos=}\n")

        # Если в папке нет фотографий - то пропустить эту итерацию
        if not photos:
            continue

        # hash_photos_path_in_dir_new_photos = [
        # '43c00c24612081bdb2cc5e69b4eb8d00b538f52a5697aae52dc4b4bef4ae1e45552589',
        # 'f27e62efc73c3017eb778864b80b719f71cf02f283080dd2bdbd32a7eb536da4633129',
        # ]
        hash_photos_path_in_dir_new_photos: list[tuple[str, str]] = [
            (get_hash_photo_by_pixel_plus_file_size(photo), str(photo))
            for photo in photos
        ]
        # logging.info("hash_photos_path_in_dir_new_photos: \n")
        # logging.info(hash_photos_path_in_dir_new_photos, end="\n")

        # Get the list of files
        hash_photos_in_dir_new_photos: list[str] = [
            tuple_photo_hash_path[0]
            for tuple_photo_hash_path in hash_photos_path_in_dir_new_photos
        ]

        for tuple_photo_hash_path in hash_photos_path_in_dir_new_photos:
            hash_photo: str = tuple_photo_hash_path[0]
            path_photo: Path = Path(tuple_photo_hash_path[1])
            # logging.info(f"In plot {plot_dir=}: \n{hash_photo}, {path_photo}")
            # logging.info(f"{hash_photos_in_dir_new_photos=}\n")

            # Check for duplicate photos in the new_photos_send_to_asite folder
            possible_photo_duplication: int = hash_photos_in_dir_new_photos.count(
                hash_photo
            )
            # Work if there are identical photos
            if possible_photo_duplication > 1:
                # logging.info(
                #     f"{possible_photo_duplication=} hash: {hash_photo} of photo: {path_photo} in {plot_dir}\n"
                # )
                # Create folder
                # D:/WORK/Horand_LTD/TASK TO DO/Locations with data for inspections/SideRise/A_L10_Plot_82/2.3/duplicated_photos
                create_sub_dir(plot_dir, Path(r"2.3\duplicated_photos"))
                # Remove duplicate photo hash from "hash_photos_in_dir_new_photos"
                hash_photos_in_dir_new_photos.remove(hash_photo)
                # Path where to move identical photos
                dest: Path = plot_dir / Path(r"2.3\duplicated_photos") / path_photo.name
                # logging.info(f"{dest=}")
                # Move photo path_photo to path dest
                shutil.move(str(path_photo), str(dest))
        # logging.info("\n\n")


def create_dict_plots_with_new_photos(
    base_dir: Path, dir_with_new_photo: Path
) -> dict[str, list[Path]]:
    r"""Создает словарь с новыми фотографиями, которые нужно загрузть на asite Side-Rise
    инспекции квартир в пункт 2.3

    Args:
        base_dir (Path): Path to folder with folders by apartment names.
            D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise

        dir_with_new_photo (Path): Relative path to base folder with folder by apartment names with photos.
            WindowsPath("2.3\new_photos_send_to_asite")

    Returns:
        dict_with_new_photos (dict[str, list[Path]):
            For example:
            dict_with_new_photos = {
            'A_L1_Plot_2': ['D:\\WORK\\Horand_LTD\\TASK TO DO\\Locations with data for '
                    'inspections\\SideRise\\A_L1_Plot_2\\2.3\\new_photos_send_to_asite\\plot '
                    '02 block A lev 1 WA0118.jpg'],
            'A_L1_Plot_4': ['D:\\WORK\\Horand_LTD\\TASK TO DO\\Locations with data for '
                            'inspections\\SideRise\\A_L1_Plot_4\\2.3\\new_photos_send_to_asite\\WhatsApp '
                            'Image 2025-04-29 at 16.00.05_71d3d084.jpg'],
            'A_L1_Plot_6': ['D:\\WORK\\Horand_LTD\\TASK TO DO\\Locations with data for '
                            'inspections\\SideRise\\A_L1_Plot_6\\2.3\\new_photos_send_to_asite\\viewThumb '
                            '(1).jpg',
                            'D:\\WORK\\Horand_LTD\\TASK TO DO\\Locations with data for '
                            'inspections\\SideRise\\A_L1_Plot_6\\2.3\\new_photos_send_to_asite\\viewThumb '
                            '(2).jpg',
                            ..., ],
                        ..: [...],
            }
    """
    dict_with_new_photos: dict[str, list[Path]] = {}
    logging.info(f"{base_dir=}")
    list_plot_dir: list[Path] = find_plot_dirs(base_dir)
    # plot_dir:
    # WindowsPath('D:/WORK/Horand_LTD/TASK TO DO/Locations with data for inspections/SideRise/A_L10_Plot_82')
    for plot_dir in list_plot_dir:
        # logging.info(f"{plot_dir=}")
        # dir_with_new_photos:
        # WindowsPath('D:/WORK/Horand_LTD/TASK TO DO/Locations with data for inspections/SideRise/A_L10_Plot_82/2.3/new_photos_send_to_asite')
        dir_with_new_photos = plot_dir / dir_with_new_photo
        # logging.info(f"{dir_with_new_photos=}\n")
        # photos = [
        # 'D:/WORK/Horand_LTD/TASK TO DO/Locations with data for inspections/SideRise/A_L3_Plot_26/2.3/new_photos_send_to_asite/JIEN0141.JPG',
        # 'D:/WORK/Horand_LTD/TASK TO DO/Locations with data for inspections/SideRise/A_L3_Plot_26/2.3/new_photos_send_to_asite/RIAQ5261.JPG',
        # ]
        photos: list[Path] = collect_photos_from_photo_dir(dir_with_new_photos)
        # If there are photos in the folder, then add them to the dictionary "dict_with_new_photos"
        if len(photos) > 0:
            dict_with_new_photos[str(plot_dir.name)] = photos
            # logging.info(f"{photos=}\n\n")
    return dict_with_new_photos


def edit_or_create_inspection(
    driver: WebDriver, number_line: int
) -> tuple[WebDriver, WebElement, str | None]:
    """The function determines whether to edit or create an inspection.

    Returns:
        tuple[WebDriver, WebElement, str | None]: Returns a tuple of the driver, the web element, and
            the string "edit" or "create" or the value None.

    Just in case:
        Old path to column with data
        element_xpath = (
            f'//*[@id="table_body_content_scroller"]/div/div[{number_line}]/div/div[36]'
        )
        '//*[@id="table_body_content_scroller"]/div/div[5]/div/div[36]'
    """
    column_number_side_rise: int = 33
    wait: WebDriverWait = WebDriverWait(driver, 1)
    # New path to column with data
    element_xpath: str = (
        f'//*[@id="table_body_content_scroller"]/div/div[{number_line}]/div/div[{column_number_side_rise}]'
    )
    element: WebElement = wait.until(
        EC.visibility_of_element_located((By.XPATH, element_xpath))
    )
    btn_select_form_action_xpath: str = (
        f'//*[@id="table_body_content_scroller"]/div/div[{number_line}]/div/div[{column_number_side_rise}]/div/img'
    )
    try:
        btn_select_form_action: WebElement | None = wait.until(
            EC.visibility_of_element_located((By.XPATH, btn_select_form_action_xpath))
        )
    except Exception:
        btn_select_form_action = None
        logging.info(
            f"In edit_or_create_inspection element {btn_select_form_action_xpath} not exists. \n"
        )
    # If the element contains the text "in progress" then return the text "edit"
    if element.text and element.text.lower() == "in progress":
        return (driver, element, "edit")
    # If the element contains the inscription "completed" then skip this inspection
    elif element.text and element.text.lower() == "completed":
        logging.info(f"{element.text.lower()=} in edit_or_create_inspection.")
        return (driver, element, None)
    # If the element contains an image of the form creation btn_select_form_action then return the text "create"
    elif btn_select_form_action is not None:
        logging.info(f"{btn_select_form_action=}")
        return (driver, btn_select_form_action, "create")
    raise Exception("Error in edit_or_create_inspection")


def get_photo_contractors_competency(
    folder_with_data_folders_for_form: str = "inspections",
) -> tuple[str, ...]:
    r"""Функция относительно исполняемого python файла возвращает котреж изображений из папки
    D:\WORK\Horand_LTD\TASKS_DOING_NOW\side_rise_rain_screen_firebreak_modify\inspections\00\Add Photo Of Contractors comp
    для загрузки фотографий в поле формы 'Add photo of Contractor’s competency/CSCS card'.

    Returns:
        tuple[str, ...]
    """
    # D:\WORK\Horand_LTD\TASK READY\side_rise_rain_screen_firebreak_modify\inspections
    folder_with_inspections: Path = Path.cwd() / folder_with_data_folders_for_form
    # Проходим по списку папок в папке
    # '\D:\WORK\Horand_LTD\TASKS_DOING_NOW\side_rise_rain_screen_firebreak_modify\inspections'
    for folder in folder_with_inspections.iterdir():
        # Если полный путь у папки заканчивается на 00
        if str(folder).endswith("00"):
            for folder_or_file in folder.iterdir():
                # 'D:/WORK/Horand_LTD/TASKS_DOING_NOW/side_rise_rain_screen_firebreak_modify/inspections/00/Add Photo Of Contractors comp'
                if folder_or_file.is_dir():
                    # Получить последнюю папку в системном пути
                    # folder_with_images_contractors = 'add photo of contractors comp'
                    folder_with_images_contractors: str = folder_or_file.parts[
                        -1
                    ].lower()
                    if str(folder_with_images_contractors).startswith(
                        "add photo of contractors"
                    ):
                        tuple_images_contractors: tuple[str, ...] = tuple(
                            str(img) for img in folder_or_file.iterdir()
                        )
                break
    return tuple_images_contractors


@check_session
def fill_photo_contractors_competency(driver: WebDriver) -> WebDriver:
    """ The function works in the inspection creation mode.
    Adds photos to the "Add photo of Contractor’s competency/CSCS card" field.

    Args:
        driver (WebDriver)

    Returns:
        WebDriver
    """
    wait: WebDriverWait = WebDriverWait(driver, 10)
    # Image tuple for the "Add photo of Contractor’s competency/CSCS card" field
    photo_contractors_competency: tuple[str, ...] = get_photo_contractors_competency()
    # Counter to move through the buttons. Should increase by one for each new button
    n_select_file: int = 1
    n_add_new_attach: int = 2
    last_photo: str = photo_contractors_competency[-1]

    for img in photo_contractors_competency:
        # Add photo of Contractor’s competency/CSCS card
        # Button for selecting a photo of the contractor
        click_to_select_file_xpath: str = f'//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[1]/div/div/div[5]/div/div[2]/div/div[{n_select_file}]/div[2]/inlineattachment/div/label'
        click_to_select_file: WebElement = wait.until(
            EC.visibility_of_element_located((By.XPATH, click_to_select_file_xpath))
        )
        if n_select_file == 1:
            # Scroll up to the "click_to_select_file" button element
            driver, click_to_select_file = scroll_up_to_element(
                driver, click_to_select_file
            )
        time.sleep(2)
        # Element for sending photos to the form
        input_xpath: str = f"{click_to_select_file_xpath}/following-sibling::input"
        input_element: WebElement = driver.find_element(By.XPATH, input_xpath)
        # Open contractor photo selection window
        # click_to_select_file.click()

        # Send contractor photo
        input_element.send_keys(img)
        time.sleep(1)
        # "Add New Attachment" button
        btn_add_new_attachment_xpath: str = f'//*[@id="custFormTD"]/div[2]/div/section[2]/div[1]/section[1]/div/div/div[5]/div/div[2]/div/div[{n_add_new_attach}]/div'
        btn_add_new_attachment: WebElement = wait.until(
            EC.visibility_of_element_located((By.XPATH, btn_add_new_attachment_xpath))
        )
        # Scroll down to the "btn_add_new_attachment" button
        driver, btn_add_new_attachment = scroll_down_to_element(
            driver, btn_add_new_attachment
        )
        time.sleep(1)
        # Work if not the last photo of the contractor in the folder
        if img != last_photo:
            # Click on "btn_add_new_attachment" to make a new button for selecting a photo appear
            btn_add_new_attachment.click()
            time.sleep(1)
            # Increase button counters
            n_select_file += 1
            n_add_new_attach += 1
    return driver
