import gspread
import pandas as pd

def load_to_csv(df, path="products.csv"):
    try:
        df.to_csv(path, index=False)
    except Exception as e:
        print(f"An erro occurred an save to CSV : {e}")

def load_to_spreadsheet(df):
	try :
		# 1. Autentikasi dengan file JSON
		gc = gspread.service_account(filename='highmaps-157309-95f84e1a26b5.json')

		# 2. Buka spreadsheet
		spreadsheet_id = '1tDsvSwXu5q9F6TaggFsK4fje4FX0iMNRfIs1I859EGg' # Ganti dengan ID spreadsheet Anda
		sh = gc.open_by_key(spreadsheet_id)

		# 3. Pilih worksheet (tab)
		worksheet = sh.sheet1 # Atau sh.worksheet("NamaSheet")
		worksheet.clear()

		data = df.copy()
		data["Timestamp"] = data["Timestamp"].astype(str)

		# 4. Data dari DataFrame
		# df = pd.DataFrame({'KolomA': [1, 2, 3], 'KolomB': ['X', 'Y', 'Z']})

		# 5. Ubah DataFrame ke format list of lists
		data_to_write = [data.columns.values.tolist()] + data.values.tolist()

		# 6. Tulis ke Google Sheet (mulai dari sel A1)
		worksheet.update('A1', data_to_write)
		print("Data berhasil disimpan ke Google Sheets!")
	except Exception as e:
		print(f"Terjadi kesalahan ketika melakukan load to spreadsheet : {e}")
