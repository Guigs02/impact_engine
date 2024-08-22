from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  # Helps to subtract months accurately
import requests
from pandas import DataFrame
import pandas as pd
from typing import List

class INSPIREHepAPI:
    def __init__(self):
        self.base_url = "https://inspirehep.net/api/literature"
        self.headers = {
            "Accept": "application/json"  # Indicates that the client expects a JSON response
        }

    def get_author_citations(self, recid: str):
        """
        Fetches the total citations for all papers authored by the given recid.
        """
        query = f"author.recid:{recid}"
        params = {
            'q': query,
            'size': '1000',  # Adjust as necessary, or paginate
            'fields': 'citation_count,titles.title'
        }
        
        response = requests.get(self.base_url, headers=self.headers, params=params)
        if response.status_code == 200:
            data = response.json()
            total_citations = 0
            for paper in data['hits']['hits']:
                citations = paper['metadata'].get('citation_count', 0)
                total_citations += citations
                title = paper['metadata']['titles'][0]['title']
                print(f"Title: {title}, Citations: {citations}")
            print(f"\nTotal Citations for Author (recid: {recid}): {total_citations}")
        else:
            response.raise_for_status()

if __name__ == "__main__":
    api = INSPIREHepAPI()
    recid = "1981989"  # Replace with the actual recid of the author
    api.get_author_citations(recid)


def get_date_range(days: int, end_date_obj: datetime) -> datetime:
    # If end_date is not provided, use the current date
    
    # Subtract the number of months from the end_date
    start_date_obj = end_date_obj - relativedelta(days=days)
    
    # Format the dates in the required format (YYYY-MM-DD)
    #start_date_str = start_date_obj.strftime('%Y-%m-%d')
    #end_date_str = end_date_obj.strftime('%Y-%m-%d')
    
    # Return the start and end dates as strings
    return start_date_obj

def str_to_obj(date_str: str) -> datetime:
    return datetime.strptime(date_str, '%Y-%m-%d')

def obj_to_str(date_obj: datetime) -> str:
    return date_obj.strftime('%Y-%m-%d')

def calculate_period_diff(df: DataFrame)->DataFrame:
    periods = df.columns[1:].tolist()
    diffs = []
    for i in range(len(periods) - 1):
        diff_col = f'{periods[i]}vs{periods[i+1]}'
        df[diff_col] = (df[periods[i]]) / (df[periods[0]])
        #df[diff_col] = (df[periods[i]] - df[periods[i+1]]) / (df[periods[0]] - df[periods[1]])
        diffs.append(diff_col)
    return df

def wrap_labels(labels: List, width: int):
    return [label[:width] + '\n' + label[width:] for label in labels]


