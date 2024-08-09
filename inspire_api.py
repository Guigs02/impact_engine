import os
import requests
import json
import pandas as pd
from pathlib import Path
from pyinspirehep.contrib.clone import LiteratureClone
from utils import get_date_range


class INSPIREHepAPI:
    def __init__(self, record: str = "literature", q: str = "", sort: str = None, size: str = "5", fields: list[str] = []):
        # Initialise
        self.base_url = f"https://inspirehep.net/api/{record}"
        self.headers = {
            "Accept": "application/json"  # Indicates that the client expects a JSON response
        }
        self.q: str = q
        self.sort: str = sort
        self.size: str = size
        self.fields: list[str] = fields

    def set_query(self, q: str) -> None:
        self.q = q

    def set_fields(self, fields: list[str]) -> None:
        self.fields = fields

    def search_papers(self) -> dict:
        """
        Search for papers based on the query.
        """
        params = {
            'q': self.q,
            'sort': self.sort,
            'size': self.size,
        }
        
        response = requests.get(self.base_url, headers=self.headers, params=params)
        print(response.url)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def extract_references_dois(self, references: list[dict]) -> list[str]:
        """
        Extracts the 'dois' from each reference in the references list.
        
        Args:
            references (list[dict]): List of reference dictionaries.
        
        Returns:
            List of DOIs found in all references.
        """
        dois_list = []
        for reference in references:
            dois = self.extract_nested_field(reference, 'reference.dois')
            if dois:
                dois_list.extend(dois)
        return dois_list

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
        data = self.search_papers()
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

    fields = ['titles.title','references.reference.dois'
              ,'publication_info.artid','dois.value','authors.recid', 'imprints.date','citation_count']
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