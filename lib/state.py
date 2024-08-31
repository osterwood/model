
## Upstream emission factors by region

# Delivered Natural Gas
# units: g CO2/MJ 
NATURAL_GAS_UPSTREAM = {
    'Southeast': 12.9,
    'Southwest': 11.2,
    'Midwest': 12.2,
    'Northeast': 8.1,
    'Rocky Mountain': 11.3,
    'Pacific': 13,
}

# Heating Oil
# units: kg CO2e/gallon 
HEATING_OIL_UPSTREAM = {
    'East Coast': 3.05,
    'Midwest': 3.67,
    'Gulf Coast': 3.47,
    'Rocky Mountain': 3.17,
    'West Coast': 4.15
}

## Heat Content (HHV) 

# units: mmBtu / gallon
HEATING_OIL_HHV = 0.138

# 1 MJ is this many mmBtu
NATURAL_GAS_HHV = 0.00094738


NAMES = dict(
    AL = 'Alabama',
    AK = 'Alaska',
    AZ = 'Arizona',
    AR = 'Arkansas',
    CA = 'California',
    CO = 'Colorado',
    CT = 'Connecticut',
    DE = 'Deleware',
    DC = 'District of Columbia',
    FL = 'Florida',
    GA = 'Georgia',
    HI = 'Hawaii',
    ID = 'Idaho',
    IL = 'Illinois',
    IN = 'Indiana',
    IA = 'Iowa',
    KS = 'Kansas',
    KY = 'Kentucky',
    LA = 'Louisiana',
    ME = 'Maine',
    MD = 'Maryland',
    MA = 'Massachusetts',
    MI = 'Michigan',
    MN = 'Minnesota',
    MS = 'Mississippi',
    MO = 'Missouri',
    MT = 'Montana',
    NE = 'Nebraska',
    NV = 'Nevada',
    NH = 'New Hampshire',
    NJ = 'New Jersey',
    NM = 'New Mexico',
    NY = 'New York',
    NC = 'North Carolina',
    ND = 'North Dakota',
    OH = 'Ohio',
    OK = 'Oklahoma',
    OR = 'Oregon',
    PA = 'Pennsylvania',
    RI = 'Rhode Island',
    SC = 'South Carolina',
    SD = 'South Dakota',
    TN = 'Tennessee',
    TX = 'Texas',
    UT = 'Utah',
    VT = 'Vermont',
    VA = 'Virginia',
    WA = 'Washington',
    WV = 'West Virginia',
    WI = 'Wisconsin',
    WY = 'Wyoming'
)

GAS_REGION = dict(
    AL = 'Southeast',
    AK = 'Noncontinguous',
    AZ = 'Southwest',
    AR = 'Southeast',
    CA = 'Pacific',
    CO = 'Rocky Mountain',
    CT = 'Northeast',
    DE = 'Southeast',
    DC = 'Southeast',
    FL = 'Southeast',
    GA = 'Southeast',
    HI = 'Noncontinguous',
    ID = 'Rocky Mountain',
    IL = 'Midwest',
    IN = 'Midwest',
    IA = 'Midwest',
    KS = 'Midwest',
    KY = 'Southeast',
    LA = 'Southeast',
    ME = 'Northeast',
    MD = 'Southeast',
    MA = 'Northeast',
    MI = 'Midwest',
    MN = 'Midwest',
    MS = 'Southeast',
    MO = 'Midwest',
    MT = 'Rocky Mountain',
    NE = 'Midwest',
    NV = 'Rocky Mountain',
    NH = 'Northeast',
    NJ = 'Northeast',
    NM = 'Southwest',
    NY = 'Northeast',
    NC = 'Southeast',
    ND = 'Midwest',
    OH = 'Midwest',
    OK = 'Southwest',
    OR = 'Pacific',
    PA = 'Northeast',
    RI = 'Northeast',
    SC = 'Southeast',
    SD = 'Midwest',
    TN = 'Southeast',
    TX = 'Southeast',
    UT = 'Rocky Mountain',
    VT = 'Northeast',
    VA = 'Southeast',
    WA = 'Pacific',
    WV = 'Southeast',
    WI = 'Midwest',
    WY = 'Rocky Mountain'
)

OIL_REGION = dict(
    AL = 'Gulf Coast',
    AK = 'West Coast',
    AZ = 'West Coast',
    AR = 'Gulf Coast',
    CA = 'West Coast',
    CO = 'Rocky Mountain',
    CT = 'East Coast',
    DE = 'East Coast',
    DC = 'East Coast',
    FL = 'East Coast',
    GA = 'East Coast',
    HI = 'West Coast',
    ID = 'Rocky Mountain',
    IL = 'Midwest',
    IN = 'Midwest',
    IA = 'Midwest',
    KS = 'Midwest',
    KY = 'Midwest',
    LA = 'Gulf Coast',
    ME = 'East Coast',
    MD = 'East Coast',
    MA = 'East Coast',
    MI = 'Midwest',
    MN = 'Midwest',
    MS = 'Gulf Coast',
    MO = 'Midwest',
    MT = 'Rocky Mountain',
    NE = 'Midwest',
    NV = 'West Coast',
    NH = 'East Coast',
    NJ = 'East Coast',
    NM = 'Gulf Coast',
    NY = 'East Coast',
    NC = 'East Coast',
    ND = 'Midwest',
    OH = 'Midwest',
    OK = 'Midwest',
    OR = 'West Coast',
    PA = 'East Coast',
    RI = 'East Coast',
    SC = 'East Coast',
    SD = 'Midwest',
    TN = 'Midwest',
    TX = 'Gulf Coast',
    UT = 'Rocky Mountain',
    VT = 'East Coast',
    VA = 'East Coast',
    WA = 'West Coast',
    WV = 'East Coast',
    WI = 'Midwest',
    WY = 'Rocky Mountain'
)

class State:

    def __init__(self, abbreviation):
        self.abbr = abbreviation

        self.name = NAMES[self.abbr]
        self.gas_region = GAS_REGION[self.abbr]
        self.oil_region = OIL_REGION[self.abbr]

    def summary(self):
        return [self.abbr, self.name, self.gas_region, self.oil_region]

    ## returns kg CO2e/mmBtu
    def upstream_factor(self, source):
        if source.startswith('Fuel oil'):
            return HEATING_OIL_UPSTREAM[self.oil_region] / HEATING_OIL_HHV

        if source.startswith('Natural gas'):
            return NATURAL_GAS_UPSTREAM[self.gas_region] / 1000.0 / NATURAL_GAS_HHV

        print("ERROR : Upsream for source {} is unknown for state {}".format(source, self.abbr))
