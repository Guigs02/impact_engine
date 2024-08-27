import requests
from typing import List, Dict, Any
import pandas as pd
from pandas import DataFrame
from utils import *
from datetime import datetime
from dateutil.relativedelta import relativedelta

def make_api_request(url: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """
    Makes an API request to the given URL and returns the JSON response.

    Args:
        url (str): The full URL to make the request to.
        headers (Dict[str, str]): Headers to include in the request.

    Returns:
        Dict[str, Any]: Parsed JSON response from the API.

    Raises:
        Exception: If the API request fails.
    """
    response = requests.get(url, headers=headers)
    
    #print("Request URL:", response.url)  # Debugging

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")


def get_records_info(fields: str, query: str, sort: str = 'mostcited', size: str = '200'):
    url = 'https://inspirehep.net/api/literature'
    url += f'?sort={sort}'
    url += f'&size={size}'
    url += f'&fields={fields}'
    url += f'&q={query}'

    headers = {
            "Accept": "application/json"  # Indicates that the client expects a JSON response
        }
    # Make the API request and get the result
    result = make_api_request(url, headers)

    # Extract the relevant data
    return result["hits"]["hits"], result["hits"]["total"]

def get_paper_info(recid: str, fields: str) -> Dict:
    response,_ = get_records_info(fields=fields, query = recid)
    paper_info_dict = extract_field_dict(response)[0]
    return paper_info_dict

def get_citing_papers(recid: str, fields):
    response,_ = get_records_info(fields=fields, query = recid)
    citing_list: List = []
    paper_info_dict = extract_field_dict(response)
        
    return paper_info_dict


def extract_field_dict(data: List[Dict]) -> List[Dict[str, Any]]:
    """
    Get specific data fields for papers sequentially.
    
    Args:
        papers (list[dict]): List of papers to process.
    
    Returns:
        A list of dictionaries with the extracted data fields.
    """
    results = []
    result: Dict = {}
    for paper in data:
        result = flatten_dict(paper['metadata'])
        results.append(result)
    return results

def flatten_dict(paper: Dict) -> Dict:
    new_dict: Dict = {}
    references: List = []
    for key, value in paper.items():
        if isinstance(value, list):
            for sub_dict in value:
                if isinstance(sub_dict, dict):
                    for sub_sub_dict_key, sub_sub_dict_value in sub_dict.items():
                        if isinstance(sub_sub_dict_value, dict):
                            for last_level_key, last_level_value in sub_sub_dict_value.items():
                                references.append(last_level_value)
                            paper[key] = references
                new_dict = paper | sub_dict
                del new_dict[key]
    return new_dict

def construct_query(start_date_str: str, end_date_str: str) -> str:
    query = f'de {start_date_str}->{end_date_str}'
    return query

def get_papers_list(fields: str, start_date_str: str, end_date_str: str) -> List:
    query = construct_query(start_date_str, end_date_str)
    papers, total = get_records_info(fields, query)
    papers_list = extract_field_dict(papers)
    return papers_list

def get_refs_list(papers_list: List[Dict])->List:
    refs: List = []
    refs = [
    ref for paper in papers_list if 'references' in paper 
    for ref in paper['references']
]
    return refs

def process_single_timeframe(fields: str, start_date_str: str, end_date_str: str, generate_csv: bool) -> DataFrame:
    """
    Processes data for a single timeframe and returns a DataFrame with citation counts.

    Args:
        fields (str): Fields to retrieve from the API.
        start_date_str (str): Start date of the timeframe.
        end_date_str (str): End date of the timeframe.

    Returns:
        DataFrame: A DataFrame containing citation counts for the specified timeframe.
    """
    papers_list = get_papers_list(fields, start_date_str, end_date_str)
    
    # Save papers list to CSV
    if generate_csv:
        pd.DataFrame(papers_list).drop(columns=['references']).to_csv(f"top200_{start_date_str}_{end_date_str}.csv", index=False)
    
    # Extract references and count them
    refs_list = get_refs_list(papers_list)
    df = pd.DataFrame(refs_list).value_counts().reset_index()
    
    # Rename columns appropriately
    column_date = concatenate_name_dates(str_to_obj(start_date_str), str_to_obj(end_date_str))
    df.columns = ['recid_url', column_date]
    
    return df
def process_timeframe_series(fields: str, last_timeframe: datetime, first_timeframe: datetime, generate_csv: bool, step: int = 2) -> DataFrame:
    """
    Iterates over a series of timeframes and processes each one.

    Args:
        fields (str): Fields to retrieve from the API.
        last_timeframe (datetime): The latest date in the timeframe series.
        first_timeframe (datetime): The earliest date in the timeframe series.
        step (int): Number of months to step back for each iteration.

    Returns:
        DataFrame: A DataFrame containing merged citation counts across all timeframes.
    """
    df_periods = pd.DataFrame()
    last_timeframe_start, last_timeframe_end = get_period_for_date(last_timeframe, step)
    timeframe_start, timeframe_end = get_period_for_date(first_timeframe, step)
    while True:
        if timeframe_start >= last_timeframe_start:
            start_date_str = obj_to_str(timeframe_start)
            end_date_str = obj_to_str(timeframe_end)
            
            df = process_single_timeframe(fields, start_date_str, end_date_str, generate_csv)
            
            if df_periods.empty:
                df_periods = df
            else:
                df_periods = pd.merge(df_periods, df, on='recid_url', how='left')
                
            # Move to the previous period
            timeframe_end -= relativedelta(months=step)
            timeframe_start -= relativedelta(months=step)
        else:
            break
    
    return df_periods

def get_paper_details(recids: List[str], fields: str) -> DataFrame:
    """
    Fetches titles and preprint dates for the given recids.

    Args:
        recids (List[str]): List of recids for which to fetch data.

    Returns:
        DataFrame: DataFrame containing recid, title, and preprint date.
    """
    details: List[Dict] = []

    for recid in recids:
        paper_info = get_paper_info(recid=recid,fields=fields)
        details.append(paper_info)
    df: DataFrame = rename_dataframe_columns(pd.DataFrame(details), f'recid,{fields}')

    return df

def add_paper_details(df: DataFrame, details_df: DataFrame) -> DataFrame:
    """
    Add detailed information columns to the main DataFrame.
    """
    return pd.concat([details_df, df], axis = 1)

def parse_fields(fields_str: str) -> List[str]:
    fields = fields_str.split(',')
    columns = []
    for field in fields:
        if '.' in field:
            field_name = field.split('.')[-1]
        else:
            field_name = field
        columns.append(field_name)
    return columns

def rename_dataframe_columns(df: DataFrame, fields_str: str) -> DataFrame:
    columns = parse_fields(fields_str)
    df.columns = columns
    return df


if __name__ == "__main__":
    api_fields = 'titles.title,recid,preprint_date'
    dicti = get_citing_papers("refersto:recid:2774173", api_fields)
    print(dicti)
    """ api_fields = 'titles.title,recid,citation_count,references.record'
    details_fields = 'preprint_date,titles.title'
    
    # Define the range of dates
    start_date = datetime(2020, 4, 1)
    end_date = datetime.now()
    step_back = 3
    
    # Choose whether to process one timeframe or the entire series of timeframes
    process_single_timeframe_only = False  # Change to True to process only one timeframe
    
    
    if process_single_timeframe_only:
        start_period_start, start_period_end = get_period_for_date(end_date, step=step_back)
        start_date_str = obj_to_str(start_period_start)
        end_date_str = obj_to_str(start_period_end)
        
        df = process_single_timeframe(api_fields, start_date_str, end_date_str)
    else:
        df = process_timeframe_series(api_fields, start_date, end_date, step=step_back)

    # Fetch and include paper details for the first 20 records
    recid_urls = df['recid_url'].head(200).tolist()
    recids = [extract_recid_from_url(url) for url in recid_urls]
    details_df = get_paper_details(recids, details_fields)
    df = add_paper_details(df, details_df)

    # Save final DataFrame
    df.to_csv("final_output.csv", index=False) """


   