import cv2
import time
import string
import numpy as np
import pandas as pd
import shutil
from pyzbar import pyzbar
from pathlib import Path
from datetime import date


# Add location of images folder here
IMAGES_FOLDER = ''


def get_date():
    """Returns properly formatted date string for image folder name"""
    today = date.today()
    return today.strftime('%Y-%m-%d')


def get_month():
    today = date.today()
    return today.strftime('%Y-%m')


class Ledger:
    """Keeps track of letter order for filename and returns propoerly formmatted filename"""
    @staticmethod
    def number_to_letter():
        """Returns a dict of all letters and their numerical order"""
        letters = string.ascii_lowercase
        number_translator = dict(zip([ord(letter) % 32 for letter in letters], letters))
        return number_translator

    def __init__(self):
        self.ledger = {}
        self.translator = self.number_to_letter()

    def __add_cat_number(self, cat_number):
        if cat_number in self.ledger:
            self.ledger[cat_number] += 1
        else:
            self.ledger[cat_number] = 1

    def __return_letter(self, cat_number):
        self.__add_cat_number(cat_number)
        frequency = self.ledger[cat_number]
        return self.translator[frequency]

    def return_filename(self, cat_number, taxon):
        letter = self.__return_letter(cat_number)
        cat_num = format_cat_number(cat_number)
        file_name = f'LACMIP_{cat_num}_{taxon}_{letter}.jpg' if taxon else f'LACMIP_{cat_num}_{letter}.jpg'
        return file_name



class FilePaths:
    """Class to contain all file paths"""
    def __init__(self, fp=None):
        # Get the parent directory of the script where images are, if no filepath is provided
        self.images = Path(fp) if fp else Path.cwd().parent
        self.records = self.images.joinpath('PhotosRecord.csv')
        self.parent = self.images.joinpath(get_date())
        self.successes_parent = self.images.joinpath('successes')
        self.failures_parent = self.images.joinpath('failures')
        self.unnamed_parent = self.images.joinpath('original-photos')
        self.successes = self.successes_parent.joinpath(f'{get_month()}_successes')
        self.failures = self.failures_parent.joinpath(f'{get_month()}_failures')
        self.unnamed = self.unnamed_parent.joinpath(f'{get_date()}_originals')
        # Make success/failure directories if they don't already exist
        self.unnamed_parent.mkdir(parents=True, exist_ok=True)
        self.successes_parent.mkdir(parents=True, exist_ok=True)
        self.failures_parent.mkdir(parents=True, exist_ok=True)
        self.unnamed.mkdir(parents=True, exist_ok=True)
        self.successes.mkdir(parents=True, exist_ok=True)
        self.failures.mkdir(parents=True, exist_ok=True)

    def save_to_records(self, record_dict):
        # If no photos were processed, do not write to the csv file
        if record_dict["TOTAL"] == 0:
            return
        record_df = pd.DataFrame(record_dict, index=[0])
        if self.records.exists():
            records_df = pd.read_csv(str(self.records))
            records_df = records_df.append(record_df, ignore_index=True)
        else:
            records_df = record_df
        records_df.to_csv(str(self.records), index=False)


class Taxonomy:
    fields = ['catalogNumber', 'scientificName']

    def __init__(self):
        self.df = pd.read_csv('taxonomy.csv', usecols=self.fields)

    def return_taxon(self, cat_num):
        row = self.df.loc[self.df.catalogNumber == cat_num]
        if not row.empty:
            scientific_name = row['scientificName'].values[0]
            taxon = scientific_name if scientific_name else None
        else:
            taxon = None
        return taxon


def format_cat_number(number):
    return number.replace('.', '-')


class Image:
    """Reads in an image and provides processing with cv2"""
    def __init__(self, fp):
        self.image = cv2.imread(str(fp), 0)
        self.original_image = cv2.imread(str(fp), 0)

    def sharpen(self, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
        """Return a sharpened version of the image, using an unsharp mask."""
        blurred = cv2.GaussianBlur(self.image, kernel_size, sigma)
        sharpened = float(amount + 1) * self.image - float(amount) * blurred
        sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
        sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
        sharpened = sharpened.round().astype(np.uint8)
        if threshold > 0:
            low_contrast_mask = np.absolute(self.image - blurred) < threshold
            np.copyto(sharpened, self.image, where=low_contrast_mask)
        self.image = sharpened

    def apply_brightness_contrast(self, brightness=0, contrast=0):
        """Return an image with increased/decreased brightness and/or contrast"""
        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                highlight = 255
            else:
                shadow = 0
                highlight = 255 + brightness
            alpha_b = (highlight - shadow) / 255
            gamma_b = shadow

            buf = cv2.addWeighted(self.image, alpha_b, self.image, 0, gamma_b)
        else:
            buf = self.image.copy()

        if contrast != 0:
            f = 131 * (contrast + 127) / (127 * (131 - contrast))
            alpha_c = f
            gamma_c = 127 * (1 - f)

            buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

        self.image = buf

    def binarize(self):
        ret, self.image = cv2.threshold(self.image, 127, 255, cv2.THRESH_BINARY)

    def read_barcode(self):
        self.binarize()
        self.sharpen(amount=2)
        barcodes = pyzbar.decode(self.image)
        return barcodes



def main(dir=None):
    """Iterate over directory and detect all barcodes in .jpg images and print the barcode data"""
    ledger = Ledger()
    paths = FilePaths(fp=dir)
    taxonomy = Taxonomy()
    start = time.time()
    taxonomy_df = pd.read_csv('taxonomy.csv')
    stats = {'SUCCESSES': 0, 'FAILURES': 0, 'TOTAL': 0, 'DATE': get_date()}
    for fp in paths.images.iterdir():
        if fp.suffix in ['.jpg', '.jpeg', '.JPG', '.jpeg']:
            image = Image(fp)
            barcodes = image.read_barcode()
            if barcodes:
                barcode_values = [b.data.decode('utf-8') for b in barcodes]
                if 'LABELS' in barcode_values:
                    barcode_values.remove('LABELS')
                    taxon = None
                    barcode_value = f'{barcode_values[0]}_labels'
                else:
                    taxon = taxonomy.return_taxon(f'LACMIP {barcode_values[0]}')
                    barcode_value = barcode_values[0]
                print(f'{fp.stem}: {barcode_value}')
                cat_num = format_cat_number(barcode_value)
                stats['SUCCESSES'] += 1
                stats["TOTAL"] += 1
                file_name = ledger.return_filename(cat_num, taxon)
                #file_name = f'LACMIP_{cat_num}_{taxon}_{letter}.jpg' if taxon else f'LACMIP_{cat_num}_{letter}.jpg'
                save_path = paths.successes.joinpath(file_name)
                cv2.imwrite(str(save_path), image.original_image)
            else:
                print(f'{fp.stem}: Null')
                stats['FAILURES'] += 1
                stats["TOTAL"] += 1
                failure_date = get_date()
                save_path = paths.failures.joinpath(f'{fp.stem}_{failure_date}_FAILURE.jpg')
                cv2.imwrite(str(save_path), image.original_image)
            # Move original photo original_images folder
            shutil.move(str(fp), str(paths.unnamed))
    print(f'{stats["SUCCESSES"]} successes \n{stats["FAILURES"]} failures.\
    \nThis function took {round(time.time()-start)} seconds')
    paths.save_to_records(stats)


main(dir=IMAGES_FOLDER)