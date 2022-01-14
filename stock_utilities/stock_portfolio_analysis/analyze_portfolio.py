import csv
import json
import pprint
from typing import Dict, Any

exported_holdings_filepath = 'static/holdings.csv'
holdings_analysis_filepath = 'static/output/holdings_analysis.csv'
sectors_analysis_filepath = 'static/output/sectors_analysis.csv'

class Constants(object):
    UNKNOWN = 'UNKNOWN'
    FMCG = 'FMCG'
    IT = 'IT'
    INTERNET = 'INTERNET'
    BANKS = 'BANKS'
    NBFC = 'NBFC'
    INSURANCE = 'INSURANCE'
    AMC_AND_RT = 'AMC_AND_RT'
    FMEG = 'FMEG'
    RETAIL = 'RETAIL'
    FASHION_AND_LIFESTYLE = 'FASHION_AND_LIFESTYLE'
    CONSTRUCTION = 'CONSTRUCTION'
    PAINTS = 'PAINTS'
    CHEMICAL = 'CHEMICAL'
    AGRO_CHEMICAL = 'AGRO_CHEMICAL'
    OIL_AND_GAS = 'OIL_AND_GAS'
    PHARMA = 'PHARMA'
    AUTO_AND_EV = 'AUTO_AND_EV'

class Sector(object):
    def __init__(self, key: str, title: str = None):
        self.key = key
        self.title = title or key

        self.curr_val = 0.0
        self.invested_val = 0.0
        self.pnl = 0.0
        self.pnl_percent = 0.0

        self.expected_allocation_percent = 0.0  # TODO Input
        self.invested_allocation_percent = 0.0  # (investment_val/total_investment_val) * 100
        self.curr_allocation_percent = 0.0  # (curr_val/total_curr_val) * 100

    def update_values(self, invested_val: float, curr_val: float):
        self.invested_val += invested_val
        self.curr_val += curr_val
        self.pnl = self.curr_val - self.invested_val
        self.pnl_percent = (self.pnl * 100) / self.invested_val

    def update_allocations(self, portfolio_investment_val, portfolio_curr_val):
        self.invested_allocation_percent = (self.invested_val/portfolio_investment_val) * 100
        self.curr_allocation_percent = (self.curr_val/portfolio_curr_val) * 100

    @property
    def to_dict(self):
        return dict(
            key=self.key,
            title=self.title,
            curr_val=round(self.curr_val, 2),
            invested_val=round(self.invested_val, 2),
            pnl=round(self.pnl, 2),
            pnl_percent='{}%'.format(round(self.pnl_percent, 2)),
            expected_allocation_percent='{}%'.format(round(self.expected_allocation_percent, 2)),
            invested_allocation_percent='{}%'.format(round(self.invested_allocation_percent, 2)),
            curr_allocation_percent='{}%'.format(round(self.curr_allocation_percent, 2))
        )

    def __str__(self):
        return json.dumps(self.to_dict)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)


class Holding(object):
    def __init__(self, key: str, sector: Sector, quantity: int = 0, avg_price: float = 0.0, ltp: float = 0.0,
                 day_change_percent: float = 0.0, title: str = None):
        self.key = key
        self.title = title or key
        self.sector = sector
        self.quantity = quantity
        self.avg_price = avg_price
        self.ltp = ltp
        self.day_change_percent = day_change_percent
        self.curr_val = ltp * quantity
        self.invested_val = avg_price * quantity
        self.pnl = self.curr_val - self.invested_val
        self.pnl_percent = (self.pnl * 100) / self.invested_val

        self.expected_allocation_percent = 0.0  # TODO Input
        self.invested_allocation_percent = 0.0  # (investment_val/total_investment_val) * 100
        self.curr_allocation_percent = 0.0  # (curr_val/portfolio_curr_val) * 100

    @classmethod
    def to_holding(cls, holding_obj: Dict[str, Any]):
        sector: Sector = HOLDING_SECTOR_MAPPING.get(holding_obj['name'], Constants.UNKNOWN)
        holding: Holding = Holding(holding_obj['name'], sector, quantity=int(holding_obj['quantity']),
                                   avg_price=float(holding_obj['avg_price']), ltp=float(holding_obj['ltp']),
                                   day_change_percent=float(holding_obj['day_change_percent']))
        sector.update_values(holding.invested_val, holding.curr_val)
        return holding

    def update_allocations(self, portfolio_investment_val, portfolio_curr_val):
        self.invested_allocation_percent = (self.invested_val/portfolio_investment_val) * 100
        self.curr_allocation_percent = (self.curr_val/portfolio_curr_val) * 100

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)

    @property
    def to_dict(self):
        return dict(
            key = self.key,
            title = self.title,
            sector = self.sector.title or self.sector.key,
            quantity = self.quantity,
            avg_price = self.avg_price,
            ltp = self.ltp,
            curr_val=round(self.curr_val, 2),
            invested_val=round(self.invested_val, 2),
            pnl=round(self.pnl, 2),
            day_change_percent='{}%'.format(round(self.day_change_percent, 2)),
            pnl_percent='{}%'.format(round(self.pnl_percent, 2)),
            expected_allocation_percent='{}%'.format(round(self.expected_allocation_percent, 2)),
            invested_allocation_percent='{}%'.format(round(self.invested_allocation_percent, 2)),
            curr_allocation_percent='{}%'.format(round(self.curr_allocation_percent, 2))
        )

    def __str__(self):
        return json.dumps(self.to_dict)

    def __repr__(self):
        return self.__str__()

SECTORS: Dict[str, Sector] = {
    Constants.FMCG: Sector(Constants.FMCG, 'Fast moving consumer goods'),
    Constants.IT: Sector(Constants.IT, 'Information technology'),
    Constants.INTERNET: Sector(Constants.INTERNET, 'Internet'),
    Constants.BANKS: Sector(Constants.BANKS, 'Banks'),
    Constants.NBFC: Sector(Constants.NBFC, 'Non-banking financial companies'),
    Constants.INSURANCE: Sector(Constants.INSURANCE, 'Insurance'),
    Constants.AMC_AND_RT: Sector(Constants.AMC_AND_RT, 'Asset management companies and Registrar & transfer'),
    Constants.FMEG: Sector(Constants.FMEG, 'Fast moving electrical goods'),
    Constants.RETAIL: Sector(Constants.RETAIL, 'Retail'),
    Constants.FASHION_AND_LIFESTYLE: Sector(Constants.FASHION_AND_LIFESTYLE, 'Fashion & lifestyle'),
    Constants.CONSTRUCTION: Sector(Constants.CONSTRUCTION, 'Infra & construction'),
    Constants.PAINTS: Sector(Constants.PAINTS, 'Paints'),
    Constants.CHEMICAL: Sector(Constants.CHEMICAL, 'Chemical'),
    Constants.AGRO_CHEMICAL: Sector(Constants.AGRO_CHEMICAL, 'Agro-Chemical'),
    Constants.OIL_AND_GAS: Sector(Constants.OIL_AND_GAS, 'Oil & Gas'),
    Constants.PHARMA: Sector(Constants.PHARMA, 'Pharma'),
    Constants.AUTO_AND_EV: Sector(Constants.AUTO_AND_EV, 'Auto & EV')
}

HOLDING_SECTOR_MAPPING = {
    'AARTIIND': SECTORS[Constants.CHEMICAL],
    'ABBOTINDIA': SECTORS[Constants.PHARMA],
    'ALKYLAMINE': SECTORS[Constants.CHEMICAL],
    'ASIANPAINT': SECTORS[Constants.PAINTS],
    'ASTRAL': SECTORS[Constants.CONSTRUCTION],
    'ATUL': SECTORS[Constants.CHEMICAL],
    'BAJAJFINSV': SECTORS[Constants.NBFC],
    'BAJFINANCE': SECTORS[Constants.NBFC],
    'BERGEPAINT': SECTORS[Constants.PAINTS],
    'CAMS': SECTORS[Constants.AMC_AND_RT],
    'DABUR': SECTORS[Constants.FMCG],
    'DEEPAKNTR': SECTORS[Constants.CHEMICAL],
    'DIVISLAB': SECTORS[Constants.PHARMA],
    'DMART': SECTORS[Constants.RETAIL],
    'HAPPSTMNDS': SECTORS[Constants.IT],
    'HAVELLS': SECTORS[Constants.FMEG],
    'HCLTECH': SECTORS[Constants.IT],
    'HDFC': SECTORS[Constants.NBFC],
    'HDFCAMC': SECTORS[Constants.AMC_AND_RT],
    'HDFCBANK': SECTORS[Constants.BANKS],
    'HDFCLIFE': SECTORS[Constants.INSURANCE],
    'HINDUNILVR': SECTORS[Constants.FMCG],
    'ICICIBANK': SECTORS[Constants.BANKS],
    'IGL': SECTORS[Constants.OIL_AND_GAS],
    'INDIAMART': SECTORS[Constants.INTERNET],
    'INFY': SECTORS[Constants.IT],
    'JUBLFOOD': SECTORS[Constants.FMCG],
    'KOTAKBANK': SECTORS[Constants.BANKS],
    'MARICO': SECTORS[Constants.FMCG],
    'MARUTI': SECTORS[Constants.AUTO_AND_EV],
    'MINDAIND': SECTORS[Constants.AUTO_AND_EV],
    'MUTHOOTFIN': SECTORS[Constants.NBFC],
    'NAUKRI': SECTORS[Constants.INTERNET],
    'NAVINFLUOR': SECTORS[Constants.CHEMICAL],
    'NESTLEIND': SECTORS[Constants.FMCG],
    'PIDILITIND': SECTORS[Constants.CHEMICAL],
    'PIIND': SECTORS[Constants.AGRO_CHEMICAL],
    'POLYCAB': SECTORS[Constants.FMEG],
    'PRINCEPIPE': SECTORS[Constants.CONSTRUCTION],
    'RELAXO': SECTORS[Constants.FASHION_AND_LIFESTYLE],
    'RELIANCE': SECTORS[Constants.OIL_AND_GAS],
    'SBILIFE': SECTORS[Constants.INSURANCE],
    'SRF': SECTORS[Constants.CHEMICAL],
    'SUMICHEM': SECTORS[Constants.AGRO_CHEMICAL],
    'SUPREMEIND': SECTORS[Constants.CONSTRUCTION],
    'TATACONSUM': SECTORS[Constants.FMCG],
    'TATAPOWER': SECTORS[Constants.AUTO_AND_EV],
    'TCS': SECTORS[Constants.IT],
    'TITAN': SECTORS[Constants.FASHION_AND_LIFESTYLE],
    'VBL': SECTORS[Constants.FMCG],
    'VINATIORGA': SECTORS[Constants.CHEMICAL],
    'VOLTAS': SECTORS[Constants.FMEG],
    'WHIRLPOOL': SECTORS[Constants.FMEG]
}

HOLDINGS: Dict[str, Holding] = dict()

def parse_holdings(path):
    fieldnames = ['name', 'quantity', 'avg_price', 'ltp', 'curr_val', 'pnl', 'pnl_percent', 'day_change_percent']
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=fieldnames)
        next(reader)  # Field names
        yield from reader


def init_holdings():
    portfolio_invested_val = 0.0
    portfolio_curr_val = 0.0
    for holding_info in parse_holdings(exported_holdings_filepath):
        holding_info = dict(holding_info)
        holding_name = holding_info['name']
        if holding_name not in HOLDINGS:
            holding = Holding.to_holding(dict(holding_info))
            HOLDINGS[holding_name] = holding

        portfolio_invested_val += HOLDINGS[holding_name].invested_val
        portfolio_curr_val += HOLDINGS[holding_name].curr_val

    for holding in HOLDINGS.values():
        holding.update_allocations(portfolio_invested_val, portfolio_curr_val)

    for sector in SECTORS.values():
        sector.update_allocations(portfolio_invested_val, portfolio_curr_val)

    # print(HOLDINGS)
    # print(SECTORS.values())
    write_to_csv()

def write_to_csv():
    with open(holdings_analysis_filepath, 'w+', newline='') as f:
        fieldnames = list(list(HOLDINGS.values())[0].to_dict.keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for holding in HOLDINGS.values():
            writer.writerow(holding.to_dict)

    with open(sectors_analysis_filepath, 'w+', newline='') as f:
        fieldnames = list(list(SECTORS.values())[0].to_dict.keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for holding in SECTORS.values():
            writer.writerow(holding.to_dict)

if __name__ == '__main__':
    init_holdings()
