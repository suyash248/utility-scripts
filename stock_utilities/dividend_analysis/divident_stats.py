from typing import List, Dict, Tuple, Any

import xlrd
from datetime import date, datetime
import traceback

from xlrd.sheet import Cell, Sheet

loc = input('Enter account statement file(xls) path: ')
DATE_FORMAT = '%d/%m/%y'

def parse_date(date_str):
    try:
        datetime_obj = datetime.strptime(date_str, DATE_FORMAT)
        return datetime_obj
    except Exception as ValueError:
        pass


def get_boundaries(sheet: Sheet) -> Tuple[int, int]:
    start_row_num: int = -1
    end_row_num: int = -1
    row_idx: int = 0

    for row in sheet.get_rows():
        is_boundary: bool = True
        for cell in row:
            is_boundary = type(cell.value) == str and cell.value.startswith('*')
            if not is_boundary:
                break

        if is_boundary:
            if start_row_num < 0:
                start_row_num = row_idx
            elif end_row_num < 0:
                end_row_num = row_idx
        row_idx += 1
    return start_row_num + 1, end_row_num - 1


def get_headers(sheet: Sheet):
    row_idx: int = 0
    for row in sheet.get_rows():
        is_header_row: bool = True
        if type(row[0].value) == str and row[0].value.startswith('*'):
            for cell in row[1:]:
                if type(cell.value) == str and len(cell.value) == 0:
                    is_header_row = is_header_row and True
                else:
                    is_header_row = False
        else:
            is_header_row = False

        row_idx += 1
        if is_header_row:
            break
    header_names: Tuple[str, ...] = tuple(
        map(lambda cell: cell.value.replace('.', '').replace('/', '_').replace(' ', '_').lower(), sheet.row(row_idx)))
    return header_names


def get_dividend_rows(sheet: Sheet) -> List[Dict[str, Any]]:
    start_row_num, end_row_num = get_boundaries(sheet)
    header_names: Tuple[str, ...] = get_headers(sheet)
    # headers: Dict[str, int] = {header_names[idx]: idx for idx in range(0, len(header_names))}

    dividend_rows: List[Dict[str, Any]] = []

    row_num = 1
    for row_idx in range(start_row_num, end_row_num):
        row: Dict[str, Any] = dict(zip(header_names, map(lambda cell: cell.value, sheet.row(row_idx))))
        row['index'] = row_num
        row_num += 1
        # print(row)

        if row['narration'].find('ACH') >= 0 or row['narration'].find('DIV') >= 0:
            dividend_rows.append(row)

    return dividend_rows

def extract_org_name(div_details: str):
    div_details_limit: int = 45
    div_details: str = div_details.replace('ACH C- ', '')
    div_details = div_details[
                  :len(div_details) - 1 if len(div_details) <= div_details_limit else div_details_limit] + '...'
    return div_details

def print_dividend_stats(sheet: Sheet):
    dividend_rows: List[Dict[str, Any]] = get_dividend_rows(sheet)
    # print(dividend_rows)
    total_div: float = 0.0
    print("{:<15} {:<50} {:<10}".format('Date', 'Company', 'Amount(INR)'))
    print(''.join(['-'] * 80))
    for dividend_row in dividend_rows:
        total_div += float(dividend_row['deposit_amt'])
        print("{:<15} {:<50} {:<10}".format(dividend_row['date'], extract_org_name(dividend_row['narration']), dividend_row['deposit_amt']))
    print(''.join(['-'] * 80))
    print('Total dividend({}-{}): INR {}'.format(dividend_rows[0]['date'], dividend_rows[-1]['date'],
                                                   round(total_div, 2)))


if __name__ == '__main__':
    wb = xlrd.open_workbook(loc)
    sheet: Sheet = wb.sheet_by_index(0)
    print_dividend_stats(sheet)
