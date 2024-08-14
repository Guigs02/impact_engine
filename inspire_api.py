import os
import requests
import json
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from utils import get_date_range


class INSPIREHepAPI:
    def __init__(self, record: str = "literature", q: str = "", sort: str = None, size: str = "1000", fields: list[str] = []):
        # Initialise
        self.base_url = f"https://inspirehep.net/api"
        self.record = record
        self.headers = {
            "Accept": "application/json"  # Indicates that the client expects a JSON response
        }
        self.set_params(q,sort,size,fields)
    
    def set_params(self, q: str = "", sort: str = None, size:str = None, fields: list[str] = [])-> None:
        self.q: str = q
        self.sort: str = sort
        self.size: str = size
        self.fields: list[str] = fields

    def set_record(self, record: str):
        self.record = record

    def set_query(self, q: str) -> None:
        self.q = q

    def set_fields(self, fields: list[str]) -> None:
        self.fields = fields

    def __fetch(self)-> dict:
        params = {
            'q': self.q,
            'sort': self.sort,
            'size': self.size,
        }
    
        response = requests.get(url=f'{self.base_url}/{self.record}', headers=self.headers, params=params)
        print(response.url)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    
    def get_paper(self, dois: str) -> dict:
        query :str = f'dois.value:{dois}'
        self.set_params(q=query)
        return self.__fetch()

    def extract_references_dois(self, references: list[dict]) -> list[str]:
        """
        Extracts the 'dois' from each reference in the references list.
        
        Args:
            references (list[dict]): List of reference dictionaries.
        
        Returns:
            List of DOIs found in all references.
        """
        dois_set: set[str] = set()
        for reference in references:
            dois = self.extract_nested_field(reference, 'reference.dois')
            if dois:
                dois_set.update(dois)
        return dois_set

    def extract_nested_field(self, data: dict, field: str) -> any:
        """
        Extracts the nested field from the data. Handles lists of dictionaries.
        
        Args:
            data (dict): The dictionary from which to extract the field.
            field (str): The field to extract, specified as a dot-separated string.
        
        Returns:
            The value of the nested field, or None if any part of the path is not found.
        """
        sub_fields = field.split(".")
        value = data
        for sub_field in sub_fields:
            if isinstance(value, list):
                value = [item.get(sub_field) for item in value if item.get(sub_field) is not None]
            else:
                value = value.get(sub_field, None)
            if value is None:
                break
        return value

    def get_data(self) -> list[dict[str, any]]:
        """
        Get specific data fields for papers based on the query.
        """
        data = self.__fetch()
        results = []
        for paper in data['hits']['hits']:
            metadata = paper['metadata']
            result = {}
            for field in self.fields:
                value = self.extract_nested_field(metadata, field)
                if field == "references.reference.dois" and value:
                    result[field] = self.extract_references_dois(metadata.get("references", []))
                else:
                    result[field] = value
            results.append(result)
            print(result)
            print('\n')
        return results


if __name__ == "__main__":

    fields = ['titles.title','dois.value', 'imprints.date',
              'citation_count', 'references.reference.dois','authors.recid']
    #'publication_info.artid'
    api = INSPIREHepAPI(fields=fields)
    # sort-order: mostrecent, mostcited
    # Construct the query
    start_date_str, end_date_str = get_date_range(days = 90)
    print(start_date_str)
    print(end_date_str)
    query = f"date:[{start_date_str} TO {end_date_str}]&citation_count_without_self_citations"
    print(query)
    api.set_query(query)
    data: list[dict[str]] = api.get_data()
    print(len(data))
    ref_list: list[str] = []
    for paper in data:
        if paper.get("references.reference.dois") is not None:
            #print(f'LEN: {len(paper["references.reference.dois"])}')
            ref_list.extend(paper["references.reference.dois"])
        #else:
            #print('LEN: 0')
    #print(f'LENGTH: {len(ref_list)}\n {ref_list}')
    
    series = pd.Series(ref_list).value_counts()
    print(series)
    print(f'LENGTH: {len(ref_list)}')
    # Limit to top 5 categories
    top_n = 15
    limited_series = series.nlargest(top_n).sort_values(ascending=True)
    limited_series.plot.barh()
    plt.title(f'Top {top_n} Citations')

    # Adjust layout to show full y labels
    plt.tight_layout()
    plt.show()
    
    # REPEATING PAPERS!
 