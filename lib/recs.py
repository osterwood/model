import pandas as pd
import csv
from pprint import pprint

def parse_codebook_row(row):
    # print(row)

    data = dict(
        variable=row[0],
        type=row[1],
        desc=row[2],
        section=row[4]
    )

    if data['type'] == 'Char':
        data['codes'] = row[3].split('\n')

    elif data['type'] == 'Num':
        chunks = row[3].strip().split('\n')

        if row[0] == 'ELOTHER' or row[0] == 'USEEL':
            data['codes'] = dict([(1, 'Yes'), (0, 'No')])

        elif row[0] == 'ZTYPEHUQ':
            data['codes'] = dict([(1, 'Imputed'), (0, 'Not imputed')])            

        elif len(chunks) == 1:
            if chunks[0].index('-') > 0:
                if row[0].startswith('NWEIGHT'):
                    data['codes'] = list(map(float, chunks[0].split('-')))
                else:
                    data['codes'] = list(map(int, chunks[0].split('-')))
            else:
                print('WARN: single row, but not a range')
        else:
            codes = {}
            for code in chunks:
                code = code.split(' ')
                codes[code[0]] = ' '.join(code[1:])
            data['codes'] = codes

    else:
        pass

    if data['variable'] == 'FUELHEAT':
        pprint(data)

    return data

class RECS:

    def __init__(self, file):
        self.file = file
        self.df = pd.read_csv(file)
        self.codebook = []

        with open(file.replace('.csv','_codebook.csv')) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for idx,row in enumerate(reader):
                ## Skip header rows
                if idx < 2:
                    continue

                self.codebook.append(parse_codebook_row(row))

    def fuel_heat(self):
        pass

if __name__ == '__main__':
    import os, inspect
    
    lib_folder = os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0], '..', 'lib')
    file = '{}/../data/recs2020_public_v6.csv'.format(lib_folder)

    recs = RECS(file)
