from api_client import APIClient
from data_processor import DataProcessor
from inspire_api import INSPIREHepAPI
from utils import get_date_range, str_to_obj, obj_to_str, calculate_period_diff
from data_visualiser import DataVisualiser
from typing import List, Dict, Any, Union, Set
import pandas as pd
from pandas import DataFrame
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class DataPipelineFacade:
    def __init__(self, api: APIClient, data_processor: DataProcessor):
        self.api = api
        self.data_processor = data_processor
        
        
    def construct_query(self, start_date_str: str, end_date_str: str, control_number_range: str) -> str:
        """
        Constructs the query based on the date range and control number.
        
        Args:
            months (int): The range of months for the date filter.
            control_number_range (str): The control number range for filtering results.
        
        Returns:
            str: The constructed query string.
        """
        query = f"date:[{start_date_str} TO {end_date_str}]&control_number%3A{control_number_range}"
        print(query)
        return query
    
    def execute(self, start_date: str, end_date: str, control_number_range: str = "10001->20000")-> DataFrame:
        """
        Executes the data pipeline: retrieving, processing, analyzing, and visualizing the data.
        
        Args:
            start_date (str): The start date for the date range filter.
            end_date (str): The end date for the date range filter.
            control_number_range (str): The control number range for filtering results.
        
        Returns:
            DataFrame: A DataFrame containing the processed data.
        """
        # Step 1: Construct the query
        query = self.construct_query(start_date, end_date, control_number_range)

        # Step 2: Set the query in the API
        self.api.set_query(query)
        # Step 3: Retrieve data
        raw_data = self.api.fetch_all_pages_concurrently()
        self.data_processor.pickle_json(raw_data)
        
        # Step 4: Process data
        processed_data = self.data_processor.extract_fields_concurrently(raw_data)

        rf_list: List[str] = self.data_processor.get_info_from_papers(processed_data)
        #rf_list: List[str] = self.data_processor.extract_parameters(processed_data)
        #print(rf_list)
        df = pd.DataFrame(rf_list).value_counts()
        df = df.reset_index()
        df.columns = ['DOI', f'{start_date}-{end_date}']
        print(df.head())
        return df
        # Step 5: Visualise data
        #self.data_visualiser.to_df(rf_list)

if __name__ == "__main__":

    fields = ['titles.title','dois.value', 'imprints.date',
              'citation_count', 'references.reference.dois','authors.recid']
    
    api = INSPIREHepAPI(fields=fields)
    data_processor = DataProcessor(fields)
        
    facade = DataPipelineFacade(api, data_processor)
    step: int = 90
    begin = str_to_obj("2020.07.01")
    end_date = datetime.now()
    df_periods = pd.DataFrame()
    
    while True:
        start_date = get_date_range(step, end_date)
        if start_date >= begin:
            df = facade.execute(obj_to_str(start_date),obj_to_str(end_date))
            if df_periods.empty:
                df_periods = df
            else:
                df_periods = pd.merge(df_periods, df, on='DOI', how='left')
            end_date = start_date - relativedelta(days=1)
        else: 
            break
    df_periods.to_csv("citations_evolution.csv")
    data_visualiser = DataVisualiser(df_periods)
    data_visualiser.bubble_plot()
