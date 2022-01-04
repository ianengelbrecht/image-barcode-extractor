# LACMIP Type Specimen Barcode Reader
Reads barcodes from images, originally designed for the LACMIP IMLS 2019 grant project.

Documentation for how this script was used can be found in the [here in the LACMIP EMu Handbook](https://lacmip.github.io/emu/documentation/imaging/).

## Requirements

- Python 3.6 + 
- macOS
- Connection to the LACMIP Imaging folder via the macOS Google Drive client
- This app downloaded

This script relies upon Python 3.6+. You can find the latest version of Python for your system on the [official Python.org downloads page](https://www.python.org/downloads/). 

## Installation

1. Download the code from this repository 
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

However, this script was designed to run on a periodic basis. On macOS this can be accomplished with Cron. 

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
LACMIP_10093-21_Tessarolax grahami_a.jpg
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

The `taxonomy.csv`  is used by the python script to retireve the taxonomic data from the barcode/LACMIP catalog number. This csv is generated from EMu with the "IP Basic Taxonomy Output for Imaging" report. 

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
          |-- LACMIP_10093-21_Tessarolax grahami_a.jpg
          |-- LACMIP_10093-21_Tessarolax grahami_b.jpg
          |-- LACMIP_10093-21_labels_a.jpg
 			|-- 2022-02_successes
          |-- LACMIP_11951-2_Tessarolax incrustata_a.jpg'
          |-- LACMIP_11951-2_labels_a.jpg
```

  

