from api_client import APIClient
from typing import List, Dict, Any, Union, Set
import concurrent.futures
import pandas as pd
from pandas import DataFrame
import pickle
import json

class DataProcessor:
    def __init__(self, fields: List[str]):
        self.fields = fields
    
    def pickle_json(self, response: List[Dict], file_name: str = "response.pkl") -> None:
        
        with open(file_name, "wb") as f:
            pickle.dump(response, f)
        f.close()

    def depickle_to_json(self, file_name: str = "response.pkl") -> List[Dict]:
        with open(file_name, "rb") as f:
            json_data = pickle.load(f)
        f.close()
        return json_data

    def extract_fields_concurrently(self, raw_data: List[Dict]) -> List[Dict[str, Any]]:
        """
        Get specific data fields for papers concurrently.
        
        Args:
            papers (list[dict]): List of papers to process.
        
        Returns:
            A list of dictionaries with the extracted data fields.
        """
        result: str = ""
        all_pages_data = raw_data
        results = []
        # Validate and parse data
        papers = []
        for page_data in raw_data:
            # Check if page_data is a string and try to parse it
            if isinstance(page_data, str):
                try:
                    page_data = json.loads(page_data)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}. Skipping this entry.")
                    continue

            # Ensure page_data is a dictionary and contains the expected structure
            if isinstance(page_data, dict) and 'hits' in page_data and 'hits' in page_data['hits']:
                papers.extend(page_data['hits']['hits'])
            else:
                print("Unexpected data format in page_data. Skipping this entry.")
        
       
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.process_paper, paper) for paper in papers]
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        return results

    def extract_fields(self, raw_data: List[Dict]) -> List[Dict[str, Any]]:
        """
        Get specific data fields for papers sequentially.
        
        Args:
            papers (list[dict]): List of papers to process.
        
        Returns:
            A list of dictionaries with the extracted data fields.
        """
        result: str = ""
        data = raw_data
        results = []
        for page_data in data:
            for paper in page_data['hits']['hits']:
                result = self.process_paper(paper)
                results.append(result)
        
        return results
    def process_paper(self, paper: dict) -> dict[str,any]:
        """
        Process an individual paper to extract relevant fields.
        
        Args:
            paper (dict): The paper data to process.
        
        Returns:
            A dictionary with the extracted fields.
        """
        metadata = paper['metadata']
        result = {}
        for field in self.fields:
            value = self.extract_nested_field(metadata, field)
            if field == "references.reference.dois" and value:
                result[field] = self.extract_references_dois(metadata.get("references", []))
            else:
                result[field] = value
        return result
    
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
    
    """ def get_info_from_paper(self, paper: dict, info: str = "references.reference.dois")-> List[str]:
        info_list: list[str] = []
        if paper.get(info) is not None:
            return paper[info] """
    
    def get_info_from_papers(self, papers_data: List[Dict[str, Any]], info: str = "references.reference.dois") -> List[str]:
        ref_list: list[str] = []
        for paper in papers_data:
            if paper.get(info) is not None:
                ref_list.extend(paper[info])
        return ref_list
    
    # Define a function to normalize and extract information from the 'references' column
    def normalise_references(self, df: DataFrame, column_name: str):
        # Normalize the column
        normalised_df = pd.json_normalize(df[column_name].explode())
        
        return normalised_df
        