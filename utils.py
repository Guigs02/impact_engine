from datetime import datetime, timedelta

def get_date_range(days:str = 60) -> tuple[str, str]:
        # Calculate the date range for the last two months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Format the dates in the required format (YYYY-MM-DD)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        # Construct the query
        return start_date_str, end_date_str