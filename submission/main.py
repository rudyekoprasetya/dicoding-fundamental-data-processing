from utils import transform_data, scrape_data, load_to_csv, load_to_spreadsheet
import pandas as pd

def main():
    BASE_URL = 'https://fashion-studio.dicoding.dev/page{}'
    all_data = scrape_data(BASE_URL)
    df = pd.DataFrame(all_data)

    # sebelum di transform
    print(df.head())
    print(df.info())

    #sesudah di transform
    clean_data = pd.DataFrame(transform_data(df))
    print(clean_data.head())
    print(clean_data.info()) 

    # load to CSV
    load_to_csv(clean_data)

    #load to spreadsheet
    load_to_spreadsheet(clean_data)

if __name__ == '__main__':
     main()