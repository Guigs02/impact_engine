import os
import concurrent.futures
import requests
import json
import matplotlib.pyplot as plt
import pandas as pd
from api_client import APIClient
from utils import get_date_range


class INSPIREHepAPI(APIClient):
    def __init__(self, record: str = "literature", q: str = "", sort: str = None, size: str = "5", fields: list[str] = []):
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

    def _fetch(self, page: int = 1)-> dict:
        params = {
            'q': self.q,
            'sort': self.sort,
            'size': self.size,
            'page': page
        }
    
        response = requests.get(url=f'{self.base_url}/{self.record}', headers=self.headers, params=params)
        print(response.url)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def fetch_all_pages(self) -> list[dict]:
        page: int = 1
        all_responses: list[dict] = []
        while True:
            if page == 2:
                break
            response_page = self._fetch(page=page)
            #print(response_page)
            hits = response_page.get('hits', {}).get('hits', [])
            if not hits:
                break
            all_responses.append(response_page)
            #print(all_responses)
            page += 1
        #print(f'Page {page} fetched, total results: {len(all_responses)}')

        return all_responses
    
    def get_paper(self, dois: str) -> dict:
        query :str = f'dois.value:{dois}'
        self.set_params(q=query)
        return self._fetch()
   ################################################################################### 
    # In DataProcessor class

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
    
    def get_data_concurrently(self) -> list[dict[str, any]]:
        """
        Get specific data fields for papers based on the query.
        """
        result: str = ""
        all_pages_data = self.fetch_all_pages()
        results = []
        papers = [paper for page_data in all_pages_data for paper in page_data['hits']['hits']]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.process_paper, paper) for paper in papers]
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        return results

    def get_data(self) -> list[dict[str, any]]:
        """
        Get specific data fields for papers based on the query.
        """
        result: str = ""
        data = self.fetch_all_pages()
        results = []
        for page_data in data:
            for paper in page_data['hits']['hits']:
                result = self.process_paper(paper)
                results.append(result)
        
        return results
    def process_paper(self, paper: dict) -> dict[str,any]:
        metadata = paper['metadata']
        result = {}
        for field in self.fields:
            value = self.extract_nested_field(metadata, field)
            if field == "references.reference.dois" and value:
                result[field] = self.extract_references_dois(metadata.get("references", []))
            else:
                result[field] = value
        return result
 