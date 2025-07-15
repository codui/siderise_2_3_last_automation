# Importing Selenium WebDriver to interact with the browser
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from pprint import pprint

from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import image_sorter_ocr.OCR.easy_ocr_type_2 as easy_ocr
from auth.web_driver import perform_authorization
from core.navigation import (
    click_btn_more,
    click_btn_quality,
    click_new_malden_quality_plan,
    moving_through_quality_checklist,
)
from utils.database import (
    create_database_if_not_exist,
    create_index_for_column_data_base,
)
from utils.helpers import (
    create_dict_plots_with_new_photos,
    get_letter_block_to_start,
    get_number_level_to_start,
    get_number_plot_to_start,
    move_duplicate_photos_to_dir_double,
    transfer_files_received_from_whatsapp,
)
from utils.move_photos_fr_sorted_to_side_rise_structure import (
    move_photos_sorted_to_side_rise_structure,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


def main() -> None:
    """
    base_dir: (Path) Path to the folder where folders with apartment location names are stored.
            Folders with the apartment location name may contain photos related to point 2.3
            of the Side-Rise inspection for this apartment.
            The apartment location name consists of the block, floor, and apartment number.
            For example:
                Path(r"D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise")
    """
    # Get login and password for autorization
    load_dotenv()
    site_login = os.getenv("SITE_LOGIN")
    site_password = os.getenv("SITE_PASSWORD")

    base_dir: Path = Path(
        r"D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise"
    )
    # base_dir_sorted: Path = Path(
    #     r"D:\WORK\Horand_LTD\TASKS_DOING_NOW\side_rise_download_photo_to_asite_point_2_3_refactor_ready\image_sorter_ocr\sorted"
    # )
    base_dir_sorted: Path = Path.cwd() / Path("image_sorter_ocr/sorted")
    # Запустить как отдельный процесс файл synchronizer.py для получения фото с WhatsApp в папку chats
    sync_proc = subprocess.Popen(
        [sys.executable, "synchronize/synchronizer.py"],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    try:
        while True:
            # # Запустить файл synchronizer.py для получения фото с WhatsApp в папку chats
            # subprocess.run([sys.executable, "synchronize/synchronizer.py"])

            transfer_files_received_from_whatsapp(Path(r"chats\Python dev chat"))

            # Запустить сортировку
            easy_ocr.main()

            # Переместить фотографии из папки base_dir_sorted в base_dir
            move_photos_sorted_to_side_rise_structure(base_dir_sorted, base_dir)

            name_database: str = "side_rise_database.db"
            name_table: str = "photos"

            # Folder for uploading photos from point 2.3 of the current location block_level_plot
            # of the Side-Rise inspection
            download_dir: Path = Path(r"C:\Users\Human\Downloads\download_from_asite")
            # Get letter block where script start working
            letter_block_to_start: str = get_letter_block_to_start()
            # Get number lever where script start working
            number_level_to_start: str = get_number_level_to_start()
            # Get number plot where script start working
            number_plot_to_start: str = get_number_plot_to_start()

            # ! WORK HERE
            # logging.info("Please wait before work function move_duplicate_photos_to_dir_double...")
            dir_with_new_photo: Path = Path(r"2.3\new_photos_send_to_asite")
            # # ! UNCOMMENT THIS BEFORE RUN SCRIPT
            # move_duplicate_photos_to_dir_double(base_dir, dir_with_new_photo)
            # logging.info("Function move_duplicate_photos_to_dir_double end work.")

            """
            dict_with_new_photos = {
                "A_L1_Plot_2": [
                    "D:\\WORK\\Horand_LTD\\TASK TO DO\\Locations with data for "
                    "inspections\\SideRise\\A_L1_Plot_2\\2.3\\new_photos_send_to_asite\\plot "
                    "02 block A lev 1 WA0118.jpg"
                ],
                "A_L1_Plot_4": [
                    "D:\\WORK\\Horand_LTD\\TASK TO DO\\Locations with data for "
                    "inspections\\SideRise\\A_L1_Plot_4\\2.3\\new_photos_send_to_asite\\WhatsApp "
                    "Image 2025-04-29 at 16.00.05_71d3d084.jpg"
                ],
            }
            """
            dict_plots_with_new_photos: dict[str, list[Path]] = (
                create_dict_plots_with_new_photos(base_dir, dir_with_new_photo)
            )
            pprint(dict_plots_with_new_photos)

            # Autorization
            driver_authorized = perform_authorization(site_login, site_password)

            # Close modal window in the start page
            try:
                btn_modal_xpath: str = (
                    '//div[contains(@class, "modal-scrollable")]//*[@id="myModal-annoucement"]/div[1]/button'
                )
                btn_modal = WebDriverWait(driver_authorized, 5).until(
                    EC.visibility_of_element_located((By.XPATH, btn_modal_xpath))
                )
                btn_modal.click()
            except Exception:
                logging.info("There is no modal window.")

            time.sleep(1)

            # Создать базу данных
            create_database_if_not_exist(
                name_database,
                name_table,
                subfolder="subfolder_with_photo",
            )

            # Создать индекс столбца базы данных
            create_index_for_column_data_base(
                name_database,
                name_table,
                name_column="filename",
            )

            driver_first_page = click_btn_more(driver_authorized)
            time.sleep(0.5)

            driver_quality_page = click_btn_quality(driver_first_page)

            driver = click_new_malden_quality_plan(driver_quality_page)

            driver = moving_through_quality_checklist(
                driver,
                base_dir,
                download_dir,
                dict_plots_with_new_photos,
                letter_block_to_start=letter_block_to_start,
                number_level_to_start=number_level_to_start,
                number_plot_to_start=number_plot_to_start,
            )
            driver.quit()
    finally:
        sync_proc.terminate()


if __name__ == "__main__":
    # ! Testing
    # ! Start run script to upload photo from inspection B_L2_Plot_105
    main()
