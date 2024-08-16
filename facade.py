from api_client import APIClient
from data_processor import DataProcessor
from inspire_api import INSPIREHepAPI
from utils import get_date_range
from data_visualiser import DataVisualiser
from typing import List, Dict, Any, Union, Set
import pandas as pd

class DataPipelineFacade:
    def __init__(self, api: APIClient, data_processor: DataProcessor, data_visualiser: DataVisualiser):
        self.api = api
        self.data_processor = data_processor
        self.data_visualiser = data_visualiser
        
    def construct_query(self, months: int, end_date: str, control_number_range: str) -> str:
        """
        Constructs the query based on the date range and control number.
        
        Args:
            months (int): The range of months for the date filter.
            control_number_range (str): The control number range for filtering results.
        
        Returns:
            str: The constructed query string.
        """
        start_date_str, end_date_str = get_date_range(months, end_date)
        query = f"date:[{start_date_str} TO {end_date_str}]&control_number%3A{control_number_range}"
        print(query)
        return query
    
    def execute(self, months: int = 3, end_date: str = "", control_number_range: str = "10001->20000"):
        """
        Executes the data pipeline: retrieving, processing, analysing, and visualising the data.
        
        Args:
            months (int): The number of months for the date range filter.
            control_number_range (str): The control number range for filtering results.
        """
        # Step 1: Construct the query
        query = self.construct_query(months, end_date, control_number_range)

        # Step 2: Set the query in the API
        self.api.set_query(query)
        # Step 3: Retrieve data
        raw_data = self.api.fetch_all_pages()
        
        # Step 4: Process data
        processed_data = self.data_processor.extract_fields_concurrently(raw_data)

        rf_list: List[str] = self.data_processor.get_info_from_papers(processed_data)
        #rf_list: List[str] = self.data_processor.extract_parameters(processed_data)
        #print(rf_list)

        # Step 5: Visualise data
        self.data_visualiser.to_df(rf_list)

if __name__ == "__main__":

    fields = ['titles.title','dois.value', 'imprints.date',
              'citation_count', 'references.reference.dois','authors.recid']
    
    api = INSPIREHepAPI(fields=fields)
    data_processor = DataProcessor(fields)
    data_visualiser = DataVisualiser()
        
    facade = DataPipelineFacade(api, data_processor, data_visualiser)
    facade.execute()
    facade.execute(end_date="2024-05-01")
