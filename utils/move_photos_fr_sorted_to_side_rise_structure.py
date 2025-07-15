import logging
import shutil
from pathlib import Path
from pprint import pprint

from core.forms import get_list_photos_from_download_dir_os
from utils.helpers import collect_photos_from_photo_dir, find_plot_dirs

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


def move_photos_sorted_to_side_rise_structure(base_dir: Path, target_path: Path):
    r""" The function moves photos in which the text has been successfully recognized
    to the folder corresponding to the recognized text.
    The folders to which the photos are moved are located in the folder structure by apartments.
    Namely, in the folder:
    D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise
    Moved photos from the "base_dir" folder are deleted.

    Args:
        base_dir (Path): Path to the "sorted" folder in which folders of the A_L1_Plot_1 type with recognized
            photos are located. These folders of the A_L1_Plot_1 type must be moved to the target_path folder.
            That is, in folders of the following type:
            "D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\A_L1_Plot_1\2.3\new_photos_send_to_asite"
            For example:
                Path(r"D:\WORK\Horand_LTD\TASKS_DOING_NOW\side_rise_download_photo_to_asite_point_2_3_refactor_ready\image_sorter_ocr\sorted")

        target_path (Path): Folder where you need to move folders of the type A_L1_Plot_1 with recognized photos.
            For example:
                Path(r"D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise")
    """
    # list_plot_dir:
    # [WindowsPath('D:/WORK/Horand_LTD/TASKS_DOING_NOW/side_rise_download_photo_to_asite_point_2_3_refactor_ready/image_sorter_ocr/sorted/B_L1_Plot_100'),
    # WindowsPath('D:/WORK/Horand_LTD/TASKS_DOING_NOW/side_rise_download_photo_to_asite_point_2_3_refactor_ready/image_sorter_ocr/sorted/B_L1_Plot_104'),
    list_plot_dir: list[Path] = find_plot_dirs(base_dir)
    # print("list_plot_dir: ")
    # pprint(list_plot_dir)

    # plot_dir:
    # WindowsPath('D:/WORK/Horand_LTD/TASKS_DOING_NOW/side_rise_download_photo_to_asite_point_2_3_refactor_ready/image_sorter_ocr/sorted/B_L1_Plot_100')
    for plot_dir in list_plot_dir:
        # [WindowsPath('D:/WORK/Horand_LTD/TASKS_DOING_NOW/side_rise_download_photo_to_asite_point_2_3_refactor_ready/image_sorter_ocr/sorted/B_L1_Plot_100/DFKV5430.JPG')]
        photos: list[Path] = collect_photos_from_photo_dir(plot_dir)
        logging.info(f"{photos=}")
        logging.info(f"{plot_dir=}")

        for photo in photos:
            dest = target_path / plot_dir.name / Path(r"2.3\new_photos_send_to_asite") / photo.name
            logging.info(f"{dest=}")
            # Move photo "photo":
            # WindowsPath('D:/WORK/Horand_LTD/TASKS_DOING_NOW/side_rise_download_photo_to_asite_point_2_3_refactor_ready/image_sorter_ocr/sorted/B_L1_Plot_100/DFKV5430.JPG')
            # on the path "dest":
            # WindowsPath("D:\WORK\Horand_LTD\TASK TO DO\Locations with data for inspections\SideRise\B_L1_Plot_100\2.3\new_photos_send_to_asite")
            shutil.move(str(photo), str(dest))
            logging.info(f"\nMove {str(photo)} \nto {str(dest)}")
        plot_dir.rmdir()
        # break
