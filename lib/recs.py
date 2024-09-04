import csv
import sys
from pprint import pprint

import tabulate
from pypika import Query, Table, Field

import sqlite3

import state

HEADER = []
CODEBOOK = dict()
DECODES = dict()

class Sample:

    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        return self.data[key]

    def readable(self, key):
        value = self.data[key]

        if key in DECODES.keys():
            return DECODES[key][value]

        return value

    def __repr__(self):
        return self.data.__repr__()

    def to_array(self, cols):
        return [self.data[col] for col in cols]

    @classmethod
    def parse(cls, row):
        data = dict()

        for idx,value in enumerate(row):
            col = HEADER[idx]

            if col in CODEBOOK.keys():
                
                if 'outtype' in CODEBOOK[col].keys():
                    outtype = CODEBOOK[col]['outtype']

                    if outtype == 'float':
                        value = float(value)
                    elif outtype == 'int':
                        value = int(value)

                    # maps can also have string keys, so we check for 'num' type
                    elif outtype == 'map' and CODEBOOK[col]['intype'] == 'num':
                        # Sometimes a map will not have an entry, in that case
                        # set the value to -2, which commonly means 'Not applicable'
                        if value == '':
                            value = -2
                        else:
                            value = int(value)

                if col == 'DIVISION':
                    value = value.replace(' ', '_')

                data[col] = value

        return cls(data)

SKIP_ROWS = [
    'state_name',
    'ELXBTU',
]

for num in range(1,61):
    SKIP_ROWS.append("NWEIGHT{}".format(num))

def parse_codebook_row(row):

    if row[0] in SKIP_ROWS:
        return None

    if row[4].startswith('ELECTRONICS'):
        return None

    if row[2].startswith('Imputation'):
        return None

    data = dict(
        variable=row[0],
        intype=row[1].lower(),
        desc=row[2],
        section=row[4]
    )

    if data['intype'] == 'char':
        if row[0] == 'UATYP10':
            data['codes'] = dict([('C', 'Urban cluster'), ('R', 'Rural area'), ('U', 'Urban area')])
            data['outtype'] = 'map'
        else:
            data['codes'] = row[3].split('\n')

    elif data['intype'] == 'num':
        data['outtype'] = 'map'
        chunks = row[3].strip().split('\n')

        # These entries in the codebook are incomplete
        if row[0] == 'ELOTHER' or row[0] == 'USEEL':
            data['codes'] = dict([(1, 'Yes'), (0, 'No')])

        elif row[0] == 'ZTYPEHUQ':
            data['codes'] = dict([(1, 'Imputed'), (0, 'Not imputed')])            

        elif row[0] == 'EVCHRGHOME':
            data['codes'] = dict([(1, 'Yes'), (0, 'No'), (-2, 'Not applicable')])

        elif row[0] in ['FOXBTU', 'NGXBTU', 'LPXBTU']:
            data['codes'] = [50, 150]
            data['outtype'] = 'float'

        elif row[0] == 'EQUIPM':
            data['codes'] = dict([
                (3, 'Central furnace'),
                (2, 'Steam or water radiators'),
                (4, 'Central heat pump'),
                (13, 'Ductless heat pump'),
                (5, 'Built-in electric heater'),
                (7, 'Built-in gas or oil heater '),
                (8, 'Wood or pellet stove'),
                (10, 'Portable electric heaters'),
                (99, 'Other'),
                (-2, 'None')
            ])

        elif row[0] == 'FUELHEAT':
            data['codes'] = dict([
                (5,'Electricity'),
                (1, 'Natural Gas'),
                (2, 'Propane'),
                (3, 'Fuel oil'),
                (7, 'Wood or pellets'),
                (99, 'Other'),
                (-2, 'None')
            ])

        elif len(chunks) == 1:
            if '-' in chunks[0]:
                # Can't naively split the range by '-' as the first number might be negative.
                # So, we look for the last dash and extract the first and second number from that
                split_point = chunks[0].rindex("-")
                nums = [chunks[0][0:split_point].strip(), chunks[0][split_point+1:].strip()]
                
                if '.' in chunks[0]:
                    data['codes'] = list(map(float, nums))
                    data['outtype'] = 'float'
                else:
                    data['codes'] = list(map(int, nums))
                    data['outtype'] = 'int'
            else:
                print("WARN: {} is single row, but not a range".format(data['variable']))
        else:
            codes = {}
            for code in chunks:
                code = code.split(' ')
                codes[int(code[0])] = ' '.join(code[1:])
            data['codes'] = codes

        if data['variable'].startswith('BTU'):
            data['outtype'] = 'float'

        if data['variable'].startswith('TOTAL') and data['section'] == 'End-use Model':
            data['outtype'] = 'float'            

    else:
        pass

    return data

class RECS:

    def __init__(self, file=None):
        self.file = file
        
        if file is None:
            codebook_file = "data/recs2020_public_v6_codebook.csv"
            self.con = sqlite3.connect("recs.db")
        else:
            codebook_file = file.replace('_sample','').replace('.csv','_codebook.csv')

        with open(codebook_file) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for idx,row in enumerate(reader):
                ## Skip header rows
                if idx < 2:
                    continue

                data = parse_codebook_row(row)

                if data is not None:

                    if 'codes' in data.keys() and data['codes'].__class__ == dict:
                        DECODES[data['variable']] = data['codes']

                    CODEBOOK[data['variable']] = data

        print("RECS Codebook loaded")

    def select(self, columns, where):    
        cur = self.con.cursor()

        query = "SELECT {} FROM entries WHERE {}".format(",".join(columns), where)        
        cur.execute(query)

        return [Sample(dict(zip(columns,entry))) for entry in cur.fetchall()]

    def sample(self, save='csv'):

        output_columns = CODEBOOK.keys()
        output = []
        
        if save == 'csv':
            output.append(output_columns)

        with open(self.file) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for idx,row in enumerate(reader):

                if idx == 0:
                    for col in row:
                        HEADER.append(col)
                    print("{} of {} columns of RECS data will be loaded".format(len(CODEBOOK.keys()), len(HEADER)))

                else:
                    sample = Sample.parse(row)
                    output.append(sample.to_array(output_columns))
             
        if save == 'csv':       
            with open(self.file.replace(".csv", "_sample.csv"), 'w', newline='') as handle:
                csv_writer = csv.writer(handle, delimiter=',')
                for row in output:
                    csv_writer.writerow(row)
            handle.close()

        if save == 'sqlite':
            cur = self.con.cursor()
            cur.execute("DROP TABLE IF EXISTS entries")
            cur.execute("CREATE TABLE entries({})".format(",".join(output_columns)))

            for row in output:
                string = str(row).replace('[','').replace(']','')
                cur.execute("INSERT INTO entries VALUES ({})".format(string))

            self.con.commit()
            self.con.close()


    def print_codebook(self):
        for key in CODEBOOK.keys():
            print(CODEBOOK[key])

    def run_state_agg(self, column):
        states = sorted(state.NAMES.keys())

        variable = CODEBOOK[column]
        codes = {v: k for k, v in variable['codes'].items()}

        columns = list(variable['codes'].values())
        statedata = dict()

        for statekey in states:
    
            agg = dict()
            cols = [column, 'NWEIGHT', 'TYPEHUQ']
            entries = self.select(columns=cols, where="state_postal == '{}'".format(statekey))

            for entry in entries:
                # Skip over apartments in buildings with 2 or more units
                if entry['TYPEHUQ'] > 3:
                    continue

                value = entry[column]

                if value not in agg:
                    agg[value] = dict(count=0, weight=0)

                agg[value]['count'] += 1
                agg[value]['weight'] += entry['NWEIGHT']

            statedata[statekey] = dict()

            counts = sum([x['count'] for x in agg.values()])
            weigths = sum([x['weight'] for x in agg.values()])

            for key in columns:
                percent = 0.0

                if codes[key] in agg.keys():
                    weight = agg[int(codes[key])]['weight']
                    percent = round(float(weight) / weigths * 100.0,2)

                statedata[statekey][key] = percent

        return columns, statedata
           
    def print_table(self, name, columns, statedata):     

        header = ['State'] + columns
        rows = []

        for state in sorted(statedata.keys()):
            data = statedata[state]
            row = [state]
            
            for col in columns:
                row.append(data[col])

            rows.append(row)

        print()
        print("=== {} ===".format(name))
        print(tabulate.tabulate(rows, header))
        print()

        with open("{}.csv".format(name), 'w') as csvfile:
            file = csv.writer(csvfile)
            file.writerow(header)
            for row in rows:
                file.writerow(row)

    def fuel_heat(self):
        columns, data = self.run_state_agg('FUELHEAT')
        self.print_table('FUELHEAT', columns, data)
        
    def equipt_heat(self):
        columns, data = self.run_state_agg('EQUIPM')
        self.print_table('EQUIPM', columns, data)



if __name__ == '__main__':
    import os, inspect
    
    lib_folder = os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0], '..', 'lib')

    # file = '{}/../data/recs2020_public_v6.csv'.format(lib_folder)
    # recs = RECS(file)
    # recs.sample(save='sqlite')

    # file = '{}/../data/recs2020_public_v6_sample.csv'.format(lib_folder)
    recs = RECS()
    recs.equipt_heat()
    recs.fuel_heat()
