import cv2
import time
import string
import numpy as np
import pandas as pd
import shutil
from pyzbar import pyzbar
from pathlib import Path
from datetime import date


def get_date():
    """Returns properly formatted date string for image folder name"""
    today = date.today()
    return today.strftime('%Y-%m-%d')

class Ledger:
    @staticmethod
    def number_to_letter():
        letters = string.ascii_lowercase # Returns a string of all letters (lowercase to uppercase)
        # Creates a dictionary of letters and their numerical order as values by zipping together the string of
        # letters and a list of their numerical order. The list comprehension gets a list of order by taking the
        # modulus of ascii_letter order (ord() function).
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

    def return_letter(self, cat_number):
        self.__add_cat_number(cat_number)
        frequency = self.ledger[cat_number]
        return self.translator[frequency]


class FilePaths:
    def __init__(self, fp=None):
        self.images = Path(fp) if fp else Path.cwd().parent # get the parent directory of the script where images are
        self.records = self.images.joinpath('PhotosRecord.csv')
        self.parent = self.images.joinpath(get_date())
        self.successes_parent = self.images.joinpath('successes')
        self.failures_parent = self.images.joinpath('failures')
        self.unnamed_parent = self.images.joinpath('original-photos')
        self.successes = self.successes_parent.joinpath(f'{get_date()}_successes')
        self.failures = self.failures_parent.joinpath(f'{get_date()}_failures')
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
    fields = ['catalogNumber', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'specificEpithet', 'taxonRank']

    def __init__(self):
        self.df = pd.read_csv('taxonomy.csv', usecols=self.fields)

    def return_taxon(self, cat_num):
        row = self.df.loc[self.df.catalogNumber == cat_num]
        if not row.empty:
            kingdom = row['kingdom'].values[0]
            taxon_rank = row['taxonRank'].values[0]
            taxon_rank = taxon_rank.replace('Sub', '')
            if taxon_rank == 'Species':
                genus = row['genus'].values[0]
                species = row['specificEpithet'].values[0]
                taxon = f'{genus}_{species}'
            elif taxon_rank == 'Kingdom' and kingdom == 'Unknown':
                taxon = None
            else:
                taxon = row[taxon_rank.lower()].values[0]
        else:
            taxon = None
        return taxon


def format_cat_number(number):
    return number.replace('.', '-')


def sharp_mask(image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
    """Return a sharpened version of the image, using an unsharp mask."""
    blurred = cv2.GaussianBlur(image, kernel_size, sigma)
    sharpened = float(amount + 1) * image - float(amount) * blurred
    sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
    sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
    sharpened = sharpened.round().astype(np.uint8)
    if threshold > 0:
        low_contrast_mask = np.absolute(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)
    return sharpened


def apply_brightness_contrast(input_img, brightness=0, contrast=0):
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

        buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
    else:
        buf = input_img.copy()

    if contrast != 0:
        f = 131 * (contrast + 127) / (127 * (131 - contrast))
        alpha_c = f
        gamma_c = 127 * (1 - f)

        buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

    return buf


def print_barcode(dir=None):
    """Iterate over directory and detect all barcodes in .jpg images and print the barcode data"""
    ledger = Ledger()
    paths = FilePaths(fp=dir)
    taxonomy = Taxonomy()
    start = time.time()
    taxonomy_df = pd.read_csv('taxonomy.csv', usecols=['catalogNumber',
                                                       'kingdom',
                                                       'phylum',
                                                       'class',
                                                       'order',
                                                       'family',
                                                       'genus',
                                                       'specificEpithet',
                                                       'taxonRank'])
    stats = {'SUCCESSES': 0, 'FAILURES': 0, 'TOTAL': 0, 'DATE': get_date()}
    for fp in paths.images.iterdir():
        if fp.suffix in ['.jpg', '.jpeg', '.JPG', '.jpeg']:
            # Use opencv to read in image
            image = cv2.imread(str(fp),0)  # The '0' parameter reads image in greyscale
            original_image = cv2.imread(str(fp))
            ret, image = cv2.threshold(image,127,255,cv2.THRESH_BINARY)
            image = sharp_mask(image, amount=2)
            '''
            #image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE) # Rotate image
            image = unsharp_mask(image)


            image = apply_brightness_contrast(image, brightness=0, contrast=50)
            #blur = cv2.GaussianBlur(image, (5, 5), 0)

            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            se = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 8))
            bg = cv2.morphologyEx(image, cv2.MORPH_DILATE, se)
            out_gray = cv2.divide(image, bg, scale=255)
            #image = cv2.threshold(out_gray, 0, 255, cv2.THRESH_OTSU)[1]
            '''

            # Finds all barcodes in image
            barcodes = pyzbar.decode(image)

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
                letter = ledger.return_letter(barcode_value)
                cat_num = format_cat_number(barcode_value)
                stats['SUCCESSES'] += 1
                stats["TOTAL"] += 1
                file_name = f'LACMIP_{cat_num}_{taxon}_{letter}.jpg' if taxon else f'LACMIP_{cat_num}_{letter}.jpg'
                save_path = paths.successes.joinpath(file_name)
                cv2.imwrite(str(save_path), image)
            else:
                print(f'{fp.stem}: Null')
                stats['FAILURES'] += 1
                stats["TOTAL"] += 1
                failure_date = get_date()
                save_path = paths.failures.joinpath(f'{fp.stem}_{failure_date}_LACMIP_loc-lot_a.jpg')
                cv2.imwrite(str(save_path), original_image)
            shutil.move(str(fp), str(paths.unnamed))
    print(f'{stats["SUCCESSES"]} successes \n{stats["FAILURES"]} failures.\
    \nThis function took {round(time.time()-start)} seconds')
    paths.save_to_records(stats)



print_barcode(
    dir=r'/Volumes/GoogleDrive/Shared drives/LACMIP Imaging/IMLS Type Specimens/2021-08-26 IMLS Barcode test for Daniel'
)

