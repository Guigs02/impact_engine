import requests
from typing import List, Dict, Any
import pandas as pd
from pandas import DataFrame
from utils import *
from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_records_info(fields: str, query: str, sort: str = 'mostcited', size: str = '200'):
    url = 'https://inspirehep.net/api/literature'
    url += f'?sort={sort}'
    url += f'&size={size}'
    url += f'&fields={fields}'
    url += f'&q={query}'

    headers = {
            "Accept": "application/json"  # Indicates that the client expects a JSON response
        }
    response = requests.get(url=url, headers=headers)
        #response = requests.get(url=f'{self.base_url}/{self.record}', headers=self.headers, params=params)
    print(response.url)
    if response.status_code == 200:
        result = response.json()
        return result["hits"]["hits"], result["hits"]["total"]
    else:
        response.raise_for_status()

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
    """ print(papers_list[0])
    print("")
    print("")
    print("NEW PAPER")
    print("")
    print("")
    print(papers_list[1]) """
    refs = [
    ref for paper in papers_list if 'references' in paper 
    for ref in paper['references']
]
    return refs
    """ for paper in papers_list:
        refs.append(paper['references'][0])
 """

def process_single_timeframe(fields: str, start_date_str: str, end_date_str: str) -> DataFrame:
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
    pd.DataFrame(papers_list).drop(columns=['references']).to_csv(f"top200_{start_date_str}_{end_date_str}.csv", index=False)
    
    # Extract references and count them
    refs_list = get_refs_list(papers_list)
    df = pd.DataFrame(refs_list).value_counts().reset_index()
    
    # Rename columns appropriately
    column_date = concatenate_name_dates(str_to_obj(start_date_str), str_to_obj(end_date_str))
    df.columns = ['recid', column_date]
    
    return df
def process_timeframe_series(fields: str, last_timeframe: datetime, first_timeframe: datetime, step: int = 2) -> DataFrame:
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
    last_timeframe_start, last_timeframe_end = get_period_for_date(last_timeframe)
    timeframe_start, timeframe_end = get_period_for_date(first_timeframe)
    while True:
        if timeframe_start >= last_timeframe_start:
            start_date_str = obj_to_str(timeframe_start)
            end_date_str = obj_to_str(timeframe_end)
            
            df = process_single_timeframe(fields, start_date_str, end_date_str)
            
            if df_periods.empty:
                df_periods = df
            else:
                df_periods = pd.merge(df_periods, df, on='recid', how='left')
                
            # Move to the previous period
            timeframe_end -= relativedelta(months=step)
            timeframe_start -= relativedelta(months=step)
        else:
            break
    
    return df_periods

if __name__ == "__main__":
    api_fields = 'titles.title,recid,citation_count,references.record'
    
    # Define the range of dates
    start_date = datetime(2020, 4, 1)
    end_date = datetime.now()
    
    # Choose whether to process one timeframe or the entire series of timeframes
    process_single_timeframe_only = True  # Change to True to process only one timeframe
    
    if process_single_timeframe_only:
        start_period_start, start_period_end = get_period_for_date(end_date)
        start_date_str = obj_to_str(start_period_start)
        end_date_str = obj_to_str(start_period_end)
        
        df = process_single_timeframe(api_fields, start_date_str, end_date_str)
        df.to_csv("out_single_timeframe.csv", index=False)
    else:
        citation_evolution_df = process_timeframe_series(api_fields, start_date, end_date, step=2)
        citation_evolution_df.to_csv("out_cit_evo.csv", index=False)



""" if __name__ == "__main__":
    fields = 'titles.title,recid,citation_count,references.record'
    step: int = 2
    begin_obj = datetime(2020,4,1)
    begin_period_start, begin_period_end = get_period_for_date(begin_obj)
    end_obj = datetime.now()
    end_period_start, end_period_end = get_period_for_date(end_obj)
    print(end_period_end)
    print(end_period_start)
    df_periods = pd.DataFrame()
    while True:
        if end_period_start >= begin_period_start:
            start_date_str = obj_to_str(end_period_start)
            end_date_str = obj_to_str(end_period_end)

            papers_list= get_papers_list(fields, start_date_str,end_date_str)
            pd.DataFrame(papers_list).drop(columns = ['references']).to_csv(f"top200_{start_date_str}_{end_date_str}.csv", index=False)

            refs_list = get_refs_list(papers_list)
            df = pd.DataFrame(refs_list).value_counts()
            df = df.reset_index()
            column_date = concatenate_name_dates(end_period_start, end_period_end)
            df.columns = ['recid', column_date]
            
            if df_periods is not None:
                if df_periods.empty:
                    df_periods = df
                else:
                    df_periods= pd.merge(df_periods, df, on='recid', how='left')
            end_period_end -= relativedelta(months=2)
            end_period_start -= relativedelta(months=2)
        else: 
            break
    df_periods.to_csv("out_cit_evo.csv", index= False) """
   

   