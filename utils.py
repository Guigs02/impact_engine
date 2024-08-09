from datetime import datetime, timedelta
import requests

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
            'fields': 'citation_count,titles,title'
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


def get_date_range(days:str = 60) -> tuple[str, str]:
        # Calculate the date range for the last two months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Format the dates in the required format (YYYY-MM-DD)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        # Construct the query
        return start_date_str, end_date_str