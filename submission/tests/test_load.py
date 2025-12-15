import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import pandas as pd
from datetime import datetime

# --- MODIFIKASI PATH UNTUK IMPOR YANG TEPAT ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
# --- AKHIR MODIFIKASI PATH ---

# Mengimpor fungsi dari file utils/load.py
try:
    from utils.load import load_to_csv, load_to_spreadsheet
except ImportError as e:
    print(f"Gagal mengimpor dari utils.load. Pastikan Anda berada di direktori my_project saat menjalankan test: {e}")
    sys.exit(1)

class TestLoadingFunctions(unittest.TestCase):
    PANDAS_PD_MODULE_PATH = 'utils.load.pd'

    def setUp(self):
        self.mock_df = pd.DataFrame({
            "Title": ["Product A", "Product B"],
            "Price": ["10.00", "20.00"],
            "Timestamp": [datetime(2025, 1, 1, 10, 0, 0), datetime(2025, 1, 1, 11, 0, 0)]
        })


    # --- Pengujian load_to_csv  ---

    @patch('pandas.DataFrame.to_csv')
    def test_load_to_csv_success(self, mock_to_csv):
        path = "test_output.csv"
        load_to_csv(self.mock_df, path)
        mock_to_csv.assert_called_once_with(path, index=False)

    @patch('utils.load.print')
    @patch('pandas.DataFrame.to_csv')
    def test_load_to_csv_failure(self, mock_to_csv, mock_print):
        mock_to_csv.side_effect = Exception("Permission denied")
        load_to_csv(self.mock_df, "protected_path.csv")
        mock_print.assert_called_once()


    # --- Pengujian load_to_spreadsheet ---

    @patch('utils.load.gspread')
    @patch('utils.load.print')
    def test_load_to_spreadsheet_success(self, mock_print, mock_gspread):
        """Menguji load_to_spreadsheet untuk proses yang berhasil."""

        mock_gc = mock_gspread.service_account.return_value
        mock_sh = mock_gc.open_by_key.return_value
        mock_worksheet = mock_sh.sheet1
        
        mock_data_copy = MagicMock() 
        
        # Kita harus men-mock nilai return di setiap langkah rantai
        mock_data_copy.columns.values.tolist.return_value = ["Title", "Price", "Timestamp"]
        
        # Menyiapkan nilai untuk .values.tolist
        mock_data_copy.values.tolist.return_value = [
            ["Product A", "10.00", "2025-01-01 10:00:00"], 
            ["Product B", "20.00", "2025-01-01 11:00:00"]
        ]
        
        mock_data_copy.__getitem__.return_value.astype.return_value = "Mocked String Timestamp Series"
        

        # Patch metode copy() dari input DataFrame nyata
        with patch.object(self.mock_df, 'copy', return_value=mock_data_copy):
            load_to_spreadsheet(self.mock_df)

        # Assertions
        mock_gspread.service_account.assert_called_once_with(filename='highmaps-157309-95f84e1a26b5.json')
        mock_worksheet.clear.assert_called_once()
        
        mock_worksheet.update.assert_called_once()
        args, _ = mock_worksheet.update.call_args
        self.assertEqual(args[0], 'A1')
        
        mock_print.assert_called_once_with("Data berhasil disimpan ke Google Sheets!")

    @patch('utils.load.gspread')
    @patch('utils.load.print')
    def test_load_to_spreadsheet_auth_failure(self, mock_print, mock_gspread):
        """Menguji load_to_spreadsheet ketika autentikasi gagal."""
        
        mock_gspread.service_account.side_effect = Exception("Authentication Failed")
        
        load_to_spreadsheet(self.mock_df)

        mock_print.assert_called_once()
        args, _ = mock_print.call_args
        self.assertIn("Authentication Failed", args[0])
        self.assertIn("Terjadi kesalahan ketika melakukan load to spreadsheet", args[0])


if __name__ == '__main__':
    unittest.main()