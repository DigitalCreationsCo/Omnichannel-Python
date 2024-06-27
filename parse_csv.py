import pandas as pd

def parse_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        df.fillna('', inplace=True)
        return df
    except Exception as e:
        print(f"Error parsing CSV file: {e}")
        return None