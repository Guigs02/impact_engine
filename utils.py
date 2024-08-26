from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  # Helps to subtract months accurately
import requests
from pandas import DataFrame
import pandas as pd
from typing import List
import re

def extract_recid_from_url(url: str) -> str:
    """
    Extract the recid from a given URL.

    Args:
        url (str): The URL containing the recid.

    Returns:
        str: The extracted recid.
    """
    return url.split('/')[-1]
def extract_matching_string(input_string, pattern):
    match = re.search(pattern, input_string)
    if match:
        return match.group()
    else:
        return None

def get_date_range(month: int, end_date_obj: datetime) -> datetime:
    # Subtract the number of months from the end_date
    start_date_obj = end_date_obj - relativedelta(days= 1, months=month)
    print(start_date_obj)
    print(end_date_obj)
    
    # Replace day and time to only keep the year and month
    start_date_obj = start_date_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_date_obj = end_date_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0)-relativedelta(days= 1)
    
    print(start_date_obj)
    print(end_date_obj)
    
    # Return the start and end dates as datetime objects
    return start_date_obj, end_date_obj

def str_to_obj(date_str: str) -> datetime:
    return datetime.strptime(date_str, '%Y-%m')

def obj_to_str(date_obj: datetime) -> str:
    return date_obj.strftime('%Y-%m')

def wrap_labels(labels: List, width: int):
    return [label[:width] + '\n' + label[width:] for label in labels]

def remove_non_ascii(df):
    df = df.applymap(lambda x: x.encode('ascii', 'ignore').decode('ascii') if isinstance(x, str) else x)
    return df

def escape_unicode(text: str) -> str:
    try:
        return text.encode('ascii', 'ignore').decode('ascii')
    except UnicodeEncodeError:
        return text
def replace_latex_symbols(text: str) -> str:
    # Replace specific LaTeX unicode with plain text equivalents
    replacements = {
        r"$\unicode{x2013}$": "-",  # En dash
        # Add more replacements if needed
    }
    for latex_symbol, replacement in replacements.items():
        text = text.replace(latex_symbol, replacement)
    return text
def convert_date_to_names(date: str) -> str:
    # Get the month names and years
    month_year = date.strftime('%B %Y')
    
    # Return the formatted Month-Year to Month-Year string
    return month_year
def concatenate_name_dates(start_date: str, end_date: str):
    start_name = convert_date_to_names(start_date)
    end_name = convert_date_to_names(end_date)
    return f"{start_name}-{end_name}"

def get_periods_for_year(year: int, step: int):
    # Define the 6 periods of the year
    periods = []
    for month in range(1, 13, step):  # Start at month 1, increment by step
        start_date = datetime(year, month, 1)
        end_date = (start_date + relativedelta(months=step)) - relativedelta(days=1)
        periods.append((start_date, end_date))
    return periods
def get_period_for_date(date_obj: datetime, step: int = 2):
    # Determine the year and month from the date object
    year = date_obj.year
    month = date_obj.month
    
    # Calculate periods
    periods = get_periods_for_year(year, step)
    
    # Find the period that contains the date
    for start_date, end_date in periods:
        if start_date <= date_obj and date_obj <= end_date:
            return start_date, end_date
    
    return None




