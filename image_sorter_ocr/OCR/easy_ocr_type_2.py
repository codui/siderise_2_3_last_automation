import json
import locale
import re
import shutil
import sys
from pathlib import Path

import cv2
import easyocr
import numpy as np

# Set UTF-8 encoding for file operations
if sys.platform.startswith("win"):
    # For Windows, ensure proper encoding
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Set locale for proper character handling
try:
    locale.setlocale(locale.LC_ALL, "")
except locale.Error:
    pass


def log_func(log_str):
    with open("log.txt", "a+", encoding="utf-8") as log_file:
        log_file.write(log_str)


def extract_text_from_image(image_path):
    # Convert Path to string with proper encoding
    image_path_str = str(image_path)

    # For OpenCV on Windows with Cyrillic characters, use np.fromfile
    if sys.platform.startswith("win") and any(
        ord(char) > 127 for char in image_path_str
    ):
        try:
            # Read image using numpy for better Unicode support
            img_array = np.fromfile(image_path_str, dtype=np.uint8)
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        except Exception as e:
            print(f"Error reading image with numpy method: {e}")
            image = cv2.imread(image_path_str)
    else:
        image = cv2.imread(image_path_str)

    if image is None:
        print(f"Error: Could not read image {image_path}")
        log_func(f"Error: Could not read image {image_path}\n")
        return None

    height, width = image.shape[:2]

    if width > height:
        roi_width = int(width * 0.4)
        roi_height = int(height * 0.4)
        roi = image[roi_height : int(height * 0.7), 0:roi_width]
    else:
        roi_width = int(width * 0.5)
        roi_height = int(height * 0.4)
        roi = image[roi_height : int(height * 0.8), 0:roi_width]

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    lower_orange = np.array([20, 120, 120])
    upper_orange = np.array([25, 255, 255])

    orange_mask = cv2.inRange(hsv, lower_orange, upper_orange)
    text_mask = cv2.bitwise_not(orange_mask)
    kernel = np.ones((4, 4), np.uint8)
    text_mask = cv2.morphologyEx(text_mask, cv2.MORPH_OPEN, kernel)
    text_mask = cv2.morphologyEx(text_mask, cv2.MORPH_CLOSE, kernel)

    text_mask_inv = cv2.bitwise_not(text_mask)

    # Create an OCR reader object
    reader = easyocr.Reader(["en"])

    # Read text from an image
    result = reader.readtext(text_mask_inv)

    # Print the extracted text
    text = ""
    for detection in result:
        text += detection[1].strip()

    log_func(text)
    return text


def process_images_in_folder(folder_path):
    folder_path = Path(folder_path)
    image_extensions = (".jpg", ".jpeg", ".png", ".bmp")

    # Get all files and filter by extension, handling encoding properly
    try:
        image_files = [
            f
            for f in folder_path.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ]
    except OSError as e:
        print(f"Error accessing folder: {e}")
        log_func(f"Error accessing folder: {e}\n")
        return {}

    results = {}
    for image_file in image_files:
        try:
            log_func(f"\nProcessing {image_file.name}...\n")
            log_func(f"image name: {image_file.name}\n")

            text = extract_text_from_image(image_file)
            if text:
                # Use the actual filename as key, preserving Cyrillic characters
                results[image_file.name] = text
                log_func(f"Extracted text: {text}\n")
            else:
                log_func(f"No text extracted from {image_file.name}\n")
        except Exception as e:
            print(f"Error processing {image_file.name}: {e}")
            log_func(f"Error processing {image_file.name}: {e}\n")
            continue

    return results


def output_path(extracted_text, name_dir_with_script):

    if len(extracted_text) < 4:
        return "unsorted"

    pattern = r"^((?:BLOCK)?)([A-G])((?:L|LV|LEV|LVL))((?:1[0-4]|[1-9]|I|L))((?:PLOT|PLT|PL|PT|P)?)(\d{1,3})([A-Za-z]+)?(\d{1,4})?"
    match = re.match(pattern, extracted_text)
    if not match:
        pattern = r"^((?:BLOCK)?)([A-G])((?:L|LV|LEV|LVL))((?:1[0-4]|[1-9]))([A-Za-z]+)(\d{1,4})((?:PLOT|PLT|PL|PT|P))(\d{1,3})"
        match = re.match(pattern, extracted_text)
        if not match:
            pattern = r"^((?:BLOCK)?)([A-G])((?:L|LV|LEV|LVL))((?:1[0-4]|[1-9]))((?:PLOT|PLT|PL|PT|P))([A-Za-z]+)(\d{1,4})"
            match = re.match(pattern, extracted_text)
            if not match:
                log_func("Recognized text doesn`t match any format \n")
                return "unsorted"
            else:
                window = match.group(6)
                window = window.replace("O", "0")
                log_func("window(gr6) = " + window + "\n")
                window_number = match.group(7)
                log_func("window_number(gr7) = " + window_number + "\n")
                with open(
                    "window_mapping.json", "r", encoding="utf-8"
                ) as window_mapping_file:
                    window_mapping = json.load(window_mapping_file)
                if window + window_number not in window_mapping.keys():
                    log_func(f"Window {window+window_number} not found" + "\n")
                    return "unsorted"
                else:
                    return window_mapping[window + window_number]
        else:
            block = match.group(2)
            log_func("block(gr1) = " + block + "\n")
            level = match.group(3)
            log_func("level(gr2) = " + level + "\n")
            level_num = match.group(4)
            if level_num == "I" or level_num == "L":
                level_num = "1"
            log_func("level_num(gr3) = " + level_num + "\n")
            window = match.group(5)
            window = window.replace("O", "0")
            log_func("window(gr4) = " + window + "\n")
            window_number = match.group(6)
            log_func("window_number(gr5) = " + window_number + "\n")
            plot = match.group(7)
            log_func("plot(gr6) = " + plot + "\n")
            plot_number = match.group(8)
            log_func("plot_number(gr7) = " + plot_number + "\n")
    else:
        block = match.group(2)
        log_func("block(gr1) = " + block + "\n")
        level = match.group(3)
        log_func("level(gr2) = " + level + "\n")
        level_num = match.group(4)
        if level_num == "I" or level_num == "L":
            level_num = "1"
        log_func("level_num(gr3) = " + level_num + "\n")
        plot = match.group(5)
        log_func("plot(gr4) = " + plot + "\n")
        plot_number = match.group(6)
        log_func("plot_number(gr5) = " + plot_number + "\n")
        window = match.group(7)
        if window:
            window = window.replace("O", "0")
            log_func("window(gr6) = " + window + "\n")
            window_number = match.group(8)
            log_func("window_number(gr7) = " + window_number + "\n")

    with open(f"{name_dir_with_script}\\plot_mapping.json", "r", encoding="utf-8") as plot_mapping_file:
        plot_mapping = json.load(plot_mapping_file)
    with open(f"{name_dir_with_script}\\window_mapping.json", "r", encoding="utf-8") as window_mapping_file:
        window_mapping = json.load(window_mapping_file)

    print(block + "_L" + level_num + "_Plot_" + plot_number)
    log_func(block + "_L" + level_num + "_Plot_" + plot_number + "\n")
    try:
        # Check if this plot exists in this block and level
        if (
            block not in plot_mapping.keys()
            or level_num not in plot_mapping[block]
            or plot_number not in plot_mapping[block][level_num]
        ):
            log_func(
                f"Plot {plot_number} not found on level {level_num} of block {block}"
                + "\n"
            )
            if window + window_number not in window_mapping.keys():
                log_func(f"Window {window+window_number} not found" + "\n")
                return "unsorted"
            else:
                log_func(
                    "Moved to folder " + window_mapping[window + window_number] + "\n"
                )
                return window_mapping[window + window_number]

    except Exception as e:
        log_func("An error occurred during validation" + repr(e) + "\n")
        return "unsorted"

    log_func(
        "Moved to folder " + block + "_L" + level_num + "_Plot_" + plot_number + "\n"
    )
    return block + "_L" + level_num + "_Plot_" + plot_number


def main():
    """
    Скрипт распознает все изображения (формата ".jpg", ".jpeg", ".png", ".bmp") из папки "pics".

    Если удалось распознать текст из фотографии и этот текст соответствует шаблону,
    то в папке sorted создается папка называющяяся распознанным текстом.
        Наприммер так "sorted/B_L1_Plot_100/"

    Если не удалось распознать текст из фотографии или распознанный текст не возможно соотнести с шаблоном,
    то в папке sorted создается папка "unsorted" куда переносится эта фотография.
        Например, "sorted/unsorted/Marius_175.jpg"
    """
    name_dir_with_script = Path("image_sorter_ocr")
    pictures_folder = Path.cwd() / name_dir_with_script / "pics"
    print(f"{pictures_folder=}")

    if not pictures_folder.exists():
        print("Error: Pictures folder not found!")
        log_func("Error: Pictures folder not found!" + "\n")
        return

    results = process_images_in_folder(pictures_folder)
    with open(f"{name_dir_with_script}\\cache.json", "w", encoding="utf-8") as json_cache_file:
        json.dump(results, json_cache_file, ensure_ascii=False, indent=2)
    # with open('cache.json','r', encoding='utf-8') as json_cache_file:
    #     results = json.load(json_cache_file)

    log_func(str(results) + "\n")
    json_info = {}
    paths = set()
    for image_name, text in results.items():
        text = text.upper()
        cleaned_text = re.sub(r"[^a-zA-Z0-9]+", "", text)
        log_func("image name: " + image_name + "\n")
        log_func("Extracted text:" + text + "\n")
        log_func("Cleaned text:" + cleaned_text + "\n")

        if cleaned_text not in json_info.keys():
            json_info[cleaned_text] = {
                cleaned_text: {
                    "Image": image_name,
                    "Extracted text": cleaned_text,
                }
            }
        else:
            json_info[cleaned_text][cleaned_text] = {
                "Image": image_name,
                "Extracted text": cleaned_text,
            }

        im_path = pictures_folder / image_name
        dest_path = Path.cwd() / name_dir_with_script / "sorted" / output_path(cleaned_text, name_dir_with_script)
        paths.add(str(dest_path.resolve()))
        dest_path.mkdir(parents=True, exist_ok=True)
        try:
            # Handle file moving with proper encoding support
            if sys.platform.startswith("win") and (
                any(ord(char) > 127 for char in image_name)
                or any(ord(char) > 127 for char in str(dest_path))
            ):
                # For Windows with Unicode filenames, use shutil.move directly
                shutil.move(str(im_path), str(dest_path / image_name))
            else:
                shutil.move(str(im_path), str(dest_path), copy_function=shutil.copy2)
        except Exception as e:
            print(f"Error moving file {image_name}: {e}")
            log_func(f"Error moving file {image_name}: {e}\n")
            pass
        json_info[cleaned_text][cleaned_text]["Path"] = str(
            Path.cwd().resolve() / cleaned_text[:4]
        )

    json_info["Abs paths"] = list(paths)
    with open(f"{name_dir_with_script}\\image_info_2.json", "w", encoding="utf-8") as json_info_file:
        json.dump(json_info, json_info_file, ensure_ascii=False, indent=2)

    log_func("\nProcessing complete! Results saved to extracted_text.txt")


if __name__ == "__main__":
    main()
