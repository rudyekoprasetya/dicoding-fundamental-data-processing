import pandas as pd
import numpy as np
from datetime import datetime

def transform_data(df):
    try:
        # copy data sebelum di transform 
        df_transformed = df.copy()

        # isi data yang kosong atau tidak sesuai
        df_transformed = df_transformed.assign(
            Title=df_transformed['Title'].fillna('Unknown Product'),
            Rating=df_transformed['Rating'].fillna('Invalid Rating'),
            Price=df_transformed['Price'].fillna(0),
            Size=df_transformed['Size'].fillna('Not Specified')
        )

        #transformasi untuk kolom price
        df_transformed['Price'] = df_transformed['Price'].replace('Price Unavailable',0)
        df_transformed['Price'] = df_transformed['Price'].astype(np.float64) # konversi ke float64
        df_transformed.loc[df_transformed['Price'] < 0, 'Price'] = 0 # ubah nilai negatif ke 0
        df_transformed['Price'] = df_transformed['Price']*16000 # jadikan rupiah

        # transformasi kolom rating
        df_transformed['Rating'] = df_transformed['Rating'].replace('Invalid Rating',0)
        df_transformed['Rating'] = df_transformed['Rating'].replace('Not Rated',0)
        df_transformed['Rating'] = df_transformed['Rating'].round().astype(np.int64)

        # transformasi untuk kolom Colors
        df_transformed['Colors'] = df_transformed['Colors'].astype(np.int64)

        return df_transformed

    except Exception as e:
        print(f"An error occurred during transform data : {e}")