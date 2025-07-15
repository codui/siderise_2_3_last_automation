# OCR Module


This module contains OCR solution for images with this type of stamp 

![](docs/type_2.jpg)

## Running easy_ocr_type_2.py

First you need to install python3 and requirements from requirements.txt
```
pip install -r requirements.txt
```

For better performance it is recommended to run gpu accelerated(CUDA) version of pytorch 
if available (see https://pytorch.org/get-started/locally/)

Next, put the images you need to sort into 'pics' folder(create if necessary)
after that run easy_ocr_type_2.py

As a result the script will:
 - create sort_results folder with images sorted into folders according to recognised text 
   * images with unrecognised text and images that didn't pass validation will be placed into 'unsorted' folder
 - create log.txt with detailed information about the script execution
 - create image_info.json with information about every picture (name, recognised text) and it's path after sorting
 - create cache.json with recognition results (just in case of script erroring after recognition) 
