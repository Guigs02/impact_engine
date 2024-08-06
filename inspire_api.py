import os
import requests
import pandas as pd
from pathlib import Path
from pyinspirehep.contrib.clone import LiteratureClone


class INSPIREHepAPI:
    def __init__(self, record: str = "literature"):
        #Initialise
        self.base_url = f"https://inspirehep.net/api/{record}"
        self.headers = {
            "Accept": "application/json"  # Indicates that the client expects a JSON response
        }
    def search_papers(self, q :str = "", sort: str = "mostrecent", size :str = "10", fields: str= "") -> None:
        params = {
            'q': q,
            'sort': sort,
            'size': size,
            'fields': fields

        }
        
        response = requests.get(self.base_url, headers=self.headers, params = params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    def get_data(self, q :str = "", sort: str = "mostrecent", size :str = "10", fields: str= "") -> str:
        data = self.search_papers(q, sort, size, fields)

        for paper in data['hits']['hits']:
            metadata: str = paper['metadata']
            for field in fields:
                field_parts = field.split('.')
                print(metadata)
                value = metadata
                for part in field_parts:
                    #print(f"{field}")
                    value = value[part]
                    print(f"{field}: {value}")



  
  
  
  

if __name__ == "__main__":
    api = INSPIREHepAPI()
    query = 'topcite 1000+'
    fields = ['titles.title']
    data: str = api.get_data(q=query,fields=fields)
    print(data)

    
    
