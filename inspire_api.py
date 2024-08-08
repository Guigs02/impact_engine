import os
import requests
import json
import pandas as pd
from pathlib import Path
from pyinspirehep.contrib.clone import LiteratureClone
from utils import get_date_range


class INSPIREHepAPI:
    def __init__(self, record: str = "literature", q: str = "", sort: str = None, size: str = "2", fields: list[str] = []):
        #Initialise
        self.base_url = f"https://inspirehep.net/api/{record}"
        self.headers = {
            "Accept": "application/json"  # Indicates that the client expects a JSON response
        }
        self.q :str= q
        self.sort :str = sort
        self.size :str = size
        self.fields :list[str] = fields

    def set_query(self, q: str) -> None:
        self.q = q
    
    def set_fields(self, fields: list[str])->None:
        self.fields = fields

    def search_papers(self) -> None:
        """
        Search for papers based on the query.
        """
        params = {
            'q': self.q,
            'sort': self.sort,
            'size': self.size,
            #'fields': self.fields,

        }
        
        response = requests.get(self.base_url, headers=self.headers, params = params)
        print(response.url)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def extract_nested_field(self, data: dict, field: str) -> str:
        """
        Extracts the nested field from the data. Handles lists of dictionaries.
        """
        sub_fields = field.split(".")
        value = data
        for sub_field in sub_fields:
            if sub_field != None:
                if isinstance(value, list):
                    # True subfield
                    print(len(value))
                    values: set = set()
                    for i in range(0, len(value)):
                        values.add(value[i][sub_field])
                    return values if values else None
                else:
                    if sub_field in value:
                        value = value[sub_field]
                    else:
                        return None
        return value         
            
    def get_data(self) -> list[dict[str]]:
        """
        Get specific data fields for papers based on the query.
        """
        data = self.search_papers()
        results: list = []
        for paper in data['hits']['hits']:
            metadata: str = paper['metadata']
            result: dict = {}
     #       print(metadata)
     #       print('\n')
            for field in fields:
                try:
                    result[field] = self.extract_nested_field(metadata, field)
                except (KeyError,IndexError, TypeError) as e:
                    result[field] = None
            results.append(result) 
            print(result)
            print('\n')

        return results                 
  
  

if __name__ == "__main__":

    fields = ['publication_info.artid','dois.value','titles.title', 'imprints.date','citation_count']
    api = INSPIREHepAPI(fields=fields)
    # sort-order: mostrecent, mostcited
    # Construct the query
    start_date_str, end_date_str = get_date_range(days = 90)
    print(start_date_str)
    print(end_date_str)
    query = f"date:[{start_date_str} TO {end_date_str}]"
    print(query)
    api.set_query(query)
    data: list[dict[str]] = api.get_data()
    #for i in range(0, len(data)):
        #print(data[i])

    
    
