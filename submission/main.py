from utils.extract import scrape_data
import pandas as pd

def main():
    BASE_URL = 'https://fashion-studio.dicoding.dev/'
    all_data = scrape_data(BASE_URL)
    df = pd.DataFrame(all_data)
    print(df)

if __name__ == '__main__':
     main()