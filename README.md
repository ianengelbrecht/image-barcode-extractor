# LACMIP Image Barcode Reader
Reads and renames image files containing barcoded LACMIP specimen labels.

Documentation for how this script was used can be found in the [here in the LACMIP EMu Handbook](https://lacmip.github.io/emu/documentation/imaging/).

## Requirements

- Python 3.6 + 
- macOS
- Connection to the LACMIP Imaging folder via the macOS Google Drive client
- This app downloaded

This script relies upon Python 3.6+. You can find the latest version of Python for your system on the [official Python.org downloads page](https://www.python.org/downloads/). 

## Installation

1. Download the code from this repository (or clone using git)
2. Open Terminal
3. Ensure that python 3.6 or greater is installed by running `python --version` or `python3 --version` (depending on how your PATH variable is set)
4. `cd` into the folder where you installed the code
5. Run `pip install -r requirements.txt` — this will install all of the dependencies for the python script
6. Copy the full file path of where the images are stored
7. Open the `imls_barcode_reader.py` file in a text editor and pate the full file path copied in the previous step between the `''` on line 13. 

At this point, the script can be run manually by issuing the following command in Terminal:

```
python imls_barcode_reader.py
```

However, this script was designed to run on a periodic basis. On macOS this can be accomplished with Cron, use [this guide on how to schedule python scripts with cron](https://towardsdatascience.com/how-to-schedule-python-scripts-with-cron-the-only-guide-youll-ever-need-deea2df63b4e).

1. Cron uses a specific syntax to schedule scripts. For example, to run a script every Friday at 3:00PM, the following would be used:

   ```
   0 3 * * FRI
   ```

   To create your own cron schedule expression, use [crontab.guru](https://crontab.guru/).

2. Open Terminal

3. Run `which python3` and copy the file path — this is the absolute file path of where your Python executable is saved

4. In a text editor, enter the following, all on the same line

   ```
   <cronScheduleExpression> cd <scriptFolderPath> && <pythonFilePath> <scriptFilePath>
   ```

   - **cronScheduleExpression** : this is the cron schedule expression created in step 1
   - **scriptFolderPath** : the file path of the folder that contains the imls_barcode_reader.py file
   - **pythonFilePath** : the file path from step 3 (the output of `which python3`)
   - **scriptFilePath** : the file path of the ims_barcode_reader.py file

   An example of a cron schedule is below:

   ```
   * * * * * cd /Users/dmarkbreiter/Code/image_barcode_reader && /Users/dmarkbreiter/Code/image_barcode_reader/venv/bin/python3 /Users/dmarkbreiter/Code/image_barcode_reader/imls_barcode_reader.py
   ```

5. Enter `crontab -e` into Terminal

6. Press `I` to enter INSERT mode

7. Enter the line of code from step 4

8. Press `ESC` to exit INSERT mode

9. Enter `wq` to save and exit

10. Open "System Preferences"

11. Navigate to Security & Privacy > Privacy > Full Disk Access

12. Click on the lock in the lower left corner to make changes

13. Open Finder and press Go > Go to Folder and enter `/usr/sbin`

14. Drag the `cron` folder into the list of folders listed in Full Disk Access

15. Click on the lock again to save changes

This will schedule the Python script to run and allows for Cron to make changes to your Google Drive folder. To see if the script was successfully run, open Terminal and enter `mail`. 

A list of numbered items should appear (each corresponding to a time the script was run). Enter the number of a message into Terminal and you can read the output of the script. 

### Scheduling the script

Scheduling a python script on macOS can be accomplished used Cron, using the following the steps.

## Filename pattern

### Successes

The default filename pattern for photos with readable barcodes are as follows: 

```
LACMIP_<catNumber>_<taxon>_<letter>.jpg
```

- `<catNumber>` refers the LACMIP catalogue number and lot number
- `<taxon>` : The taxon of a specimen is pulled from the taxonomy.csv and is space delimited — photos with a "labels" barcode will have the word "labels" instead of a taxon
- `<letter>` : The letter at the end is added to photos of a series with the same barcode

And example of a file name is as follows:

```
LACMIP_10093-21_Tessarolax_grahami_a.jpg
```

The file name pattern is controlled by the Ledger objects `return_filename`method. 

### Failures

For images where the script could not read a barcode, the filename pattern is as follows:

```
<originalFileName>_<YYYY_MM_DD>_FAILURE
```

- `<originalFileName>` : Refers to the original file name 
- `YYYY_MM_DD` : The current date, formmated by the `get_date()` function
- `FAILURE`: a string

## taxonomy.csv

The file `Imaging-FileName-Taxonomy.csv` (saved to _LACMIP Imaging > Imaging Templates_) is used by the python script to retireve the taxonomic data from the barcode/LACMIP catalog number. This file was generated by running the "IP Basic Taxonomy Output for Imaging" on all records in EMu's Catalogue module. **Do not move or rename this file; however, it should be periodically refreshed by re-running the report and overwriting the older CSV file in _Imaging Templates_.**

The script requires the following fields (in any order) in the taxonomy.csv: 

- `catalogNumber` : The LACMIP catalog number in the following format `LACMIP CAT_NUM.LOT_NUM`
- `scientificName` : The taxonomic name (preferably Genus/species), space delimited

An example of a properly formatted taxonomy.csv:

| catalogNumber   | scientificName |
| --------------- | -------------- |
| LACMIP 2533.232 | Bibio aerosus  |
| LACMIP 2533.1   | Elvina antiqua |
| LACMIP 2533.2   | Daphnia        |

Any extra fields will be ignored by the script (such as irn).

## File structure

The output of the script will be the following file structure:

```
images
  |-- PhotosRecord.csv
  |-- failures
      |-- 2022-01_failures
          |-- Img6604_2022_01_03_FAILURE.jpg
      |-- 2022-02_failures
          |-- Img6605_2022_02_01_FAILURE.jpg
  |-- successes
      |-- 2022-01_successes
          |-- LACMIP_10093-21_Tessarolax_grahami_a.jpg
          |-- LACMIP_10093-21_Tessarolax_grahami_b.jpg
          |-- LACMIP_10093-21_labels_a.jpg
      |-- 2022-02_successes
          |-- LACMIP_11951-2_Tessarolax_incrustata_a.jpg'
          |-- LACMIP_11951-2_labels_a.jpg
```

  

