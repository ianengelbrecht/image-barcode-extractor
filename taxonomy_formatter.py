import pandas as pd

fields = ['catalogNumber', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'specificEpithet', 'taxonRank']
taxonomy_df = pd.read_csv('taxonomy.csv', usecols=fields)

nums = taxonomy_df["catalogNumber"].to_list()

for num in nums:
    row =  taxonomy_df.loc[taxonomy_df.catalogNumber == num]
    kingdom = row['kingdom'].values[0]
    taxonRank = row['taxonRank'].values[0]
    if taxonRank == 'Species':
        genus = row['genus'].values[0]
        species = row['species'].values[0]
        taxon = f'{genus}_{species}'
    elif taxonRank == 'Kingdom' and kingdom == 'Unknown':
        taxon = None
    else:
        taxon = row[taxonRank.lower()].values[0]

class Taxonomy:
    fields = ['catalogNumber', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'specificEpithet', 'taxonRank']

    def __init__(self):
        self.df = pd.read_csv('taxonomy.csv', fields)

    def return_taxon(self, cat_num):
        row = self.df.loc[self.df.catalogNumber == cat_num]
        kingdom = row['kingdom'].values[0]
        taxonRank = row['taxonRank'].values[0]
        if taxonRank == 'Species':
            genus = row['genus'].values[0]
            species = row['species'].values[0]
            taxon = f'{genus}_{species}'
        elif taxonRank == 'Kingdom' and kingdom == 'Unknown':
            taxon = None
        else:
            taxon = row[taxonRank.lower()].values[0]
        return taxon

