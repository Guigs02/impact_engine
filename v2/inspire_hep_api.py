import requests
from typing import List, Dict, Any
import pandas as pd
from pandas import DataFrame
from utils import str_to_obj, obj_to_str, get_date_range
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


if __name__ == "__main__":
    fields = 'titles.title,recid,citation_count,references.record'
    step: int = 90
    begin_date = str_to_obj("2020-05-01")
    end_date = datetime.now()
    df_periods = pd.DataFrame()
    while True:
        start_date = get_date_range(step, end_date)
        if start_date >= begin_date:
            start_date_str = obj_to_str(start_date)
            end_date_str = obj_to_str(end_date)

            papers_list= get_papers_list(fields, start_date_str,end_date_str)
            pd.DataFrame(papers_list).drop(columns = ['references']).to_csv(f"top200_{start_date_str}_{end_date_str}.csv", index=False)

            refs_list = get_refs_list(papers_list)
            df = pd.DataFrame(refs_list).value_counts()
            df = df.reset_index()
            df.columns = ['recid', f'{start_date_str}_{end_date_str}']
            
            if df_periods is not None:
                if df_periods.empty:
                    df_periods = df
                else:
                    df_periods= pd.merge(df_periods, df, on='recid', how='left')
            end_date = start_date - relativedelta(days=1) 
        else: 
            break
    df_periods.to_csv("out_cit_evo.csv", index= False)
   

   