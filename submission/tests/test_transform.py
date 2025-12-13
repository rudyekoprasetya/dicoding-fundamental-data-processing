# my_project/test/test_transform.py

import unittest
import pandas as pd
import numpy as np
import sys
import os 
from datetime import datetime

# --- MODIFIKASI PATH DIMULAI DI SINI ---
# Mendapatkan direktori induk ('my_project')
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
# --- MODIFIKASI PATH BERAKHIR DI SINI ---

# Mengimpor fungsi dari file utils/transform.py
try:
    from utils.transform import (
        clean_price,
        clean_rating,
        clean_colors,
        clean_size,
        clean_gender,
        transform_data
    )
except ImportError as e:
    print(f"Gagal mengimpor dari utils.transform. Pastikan Anda berada di direktori my_project saat menjalankan test: {e}")
    sys.exit(1)

# Konstanta kurs yang digunakan dalam clean_price
IDR_RATE = 16000

class TestTransformationFunctions(unittest.TestCase):

    def setUp(self):
        """Menyiapkan data mentah untuk pengujian."""
        self.raw_data = [
            # Data valid dan lengkap
            {"Title": "Hoodie A", "Price": "$10.50", "Rating": "4.5", "Colors": "Black, White", "Size": "M", "Gender": "Unisex", "Timestamp": datetime(2025, 1, 1, 10, 0, 0)},
            # Data dengan nilai hilang/tidak valid
            {"Title": "Baju B", "Price": "Price Unavailable", "Rating": None, "Colors": "Red", "Size": "L", "Gender": None, "Timestamp": datetime(2025, 1, 1, 11, 0, 0)},
            # Data duplikat dari Hoodie A
            {"Title": "Hoodie A", "Price": "$10.50", "Rating": "4.5", "Colors": "Black, White", "Size": "M", "Gender": "Unisex", "Timestamp": datetime(2025, 1, 1, 10, 0, 0)},
            # Data yang akan dihapus oleh filter awal
            {"Title": "Unknown Product", "Price": "5", "Rating": "2", "Colors": "Blue", "Size": "S", "Gender": "Female", "Timestamp": datetime(2025, 1, 1, 12, 0, 0)},
            # Data dengan format price yang berbeda
            {"Title": "Sepatu C", "Price": "$20,000", "Rating": "3.8", "Colors": "2 Colors", "Size": "XL", "Gender": "Male", "Timestamp": datetime(2025, 1, 1, 13, 0, 0)},
        ]
        self.raw_df = pd.DataFrame(self.raw_data)


    # --- Pengujian Fungsi clean_price ---

    def test_clean_price_standard(self):
        """Menguji harga standar dengan simbol $ dan konversi kurs."""
        s = pd.Series(["$10.00", "$5.50"])
        expected = pd.Series([10.00 * IDR_RATE, 5.50 * IDR_RATE], dtype='float64')
        result = clean_price(s)
        pd.testing.assert_series_equal(result, expected, check_names=False)

    def test_clean_price_unavailable_and_format(self):
        """Menguji 'Price Unavailable' dan format dengan koma."""
        s = pd.Series(["Price Unavailable", "$1,000.50", None])
        # Harga harus menjadi 1000.50 * 16000
        expected_values = [np.nan, 1000.50 * IDR_RATE, np.nan]
        expected = pd.Series(expected_values, dtype='float64')
        result = clean_price(s)
        pd.testing.assert_series_equal(result, expected, check_names=False)
        self.assertTrue(pd.api.types.is_float_dtype(result))

    # --- Pengujian Fungsi clean_rating ---

    def test_clean_rating_success(self):
        """Menguji ekstraksi angka dari string Rating."""
        s = pd.Series(["4.5", "3.8 / 5", "Rating: 5.0 ⭐", None])
        expected = pd.Series([4.5, 3.8, 5.0, np.nan], dtype='float64')
        result = clean_rating(s)
        pd.testing.assert_series_equal(result, expected, check_names=False)

    def test_clean_rating_invalid(self):
        """Menguji rating yang tidak valid."""
        s = pd.Series(["Not Rated", ""])
        expected = pd.Series([np.nan, np.nan], dtype='float64')
        result = clean_rating(s)
        pd.testing.assert_series_equal(result, expected, check_names=False)

    # --- Pengujian Fungsi clean_colors ---

    def test_clean_colors_success(self):
        """Menguji ekstraksi jumlah warna dan penanganan nilai hilang."""
        s = pd.Series(["2 Colors", None])
        # None -> 0 (setelah fillna)
        expected = pd.Series([2, 0], dtype='int32')
        result = clean_colors(s)
        pd.testing.assert_series_equal(result, expected, check_names=False)

    # --- Pengujian Fungsi clean_size dan clean_gender ---

    def test_clean_size(self):
        """Menguji penghapusan string 'Size:' dan trimming."""
        s = pd.Series(["Size: M", " XL ", "Unknown"])
        expected = pd.Series(["M", "XL", "Unknown"], dtype='object')
        result = clean_size(s)
        # Check Series equal harus membandingkan index dan tipe data juga
        pd.testing.assert_series_equal(result, expected, check_names=False, check_dtype=False)

    def test_clean_gender(self):
        """Menguji penghapusan string 'Gender:' dan trimming."""
        s = pd.Series(["Gender: Unisex", " Female", "Unknown"])
        expected = pd.Series(["Unisex", "Female", "Unknown"], dtype='object')
        result = clean_gender(s)
        pd.testing.assert_series_equal(result, expected, check_names=False, check_dtype=False)


    # --- Pengujian Fungsi transform_data (Fungsi Utama) ---

    def test_transform_data_success(self):
        """Menguji alur transformasi penuh dengan data yang kompleks."""
        
        result_df = transform_data(self.raw_data)

        # 1. Memastikan kolom 'Unknown Product' terfilter (1 baris hilang)
        # 2. Memastikan duplikat terfilter (1 baris hilang)
        # 3. Memastikan baris dengan NaN di Price/Rating terfilter ('Baju B' hilang karena Price Unavailable)
        # Total baris awal: 5. Hilang: 1 (Unknown) + 1 (Duplikat A) + 1 (Baju B/NaN) = 3 baris
        self.assertEqual(len(result_df), 2) 

        # Memeriksa data yang tersisa (Hoodie A dan Sepatu C)
        
        # Hoodie A (Index 0)
        self.assertAlmostEqual(result_df.loc[0, "Price"], 10.50 * IDR_RATE)
        self.assertEqual(result_df.loc[0, "Rating"], 4.5)
        self.assertEqual(result_df.loc[0, "Colors"], 0) # Karena 'Black, White' tidak diekstrak angka
        self.assertEqual(result_df.loc[0, "Size"], "M")
        self.assertEqual(result_df.loc[0, "Gender"], "Unisex")
        
        # Sepatu C (Index 1)
        self.assertAlmostEqual(result_df.loc[1, "Price"], 20000.00 * IDR_RATE)
        self.assertEqual(result_df.loc[1, "Rating"], 3.8)
        self.assertEqual(result_df.loc[1, "Colors"], 2)
        self.assertEqual(result_df.loc[1, "Size"], "XL")
        self.assertEqual(result_df.loc[1, "Gender"], "Male")

        # Memastikan tipe data sudah benar
        self.assertTrue(pd.api.types.is_float_dtype(result_df["Price"]))
        self.assertTrue(pd.api.types.is_float_dtype(result_df["Rating"]))
        self.assertTrue(pd.api.types.is_integer_dtype(result_df["Colors"]))
        self.assertTrue(pd.api.types.is_object_dtype(result_df["Size"]))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result_df["Timestamp"]))


    def test_transform_data_empty_input(self):
        """Menguji transform_data dengan input list kosong."""
        result_df = transform_data([])
        self.assertTrue(result_df.empty)
        # Memastikan kolom tetap ada meskipun kosong
        self.assertListEqual(list(result_df.columns), ["Title","Price","Rating","Colors","Size","Gender","Timestamp"])

    def test_transform_data_only_unknown_products(self):
        """Menguji transform_data dengan input hanya Unknown Product."""
        raw_data = [{"Title": "Unknown Product", "Price": "5", "Rating": "2", "Colors": "Blue", "Size": "S", "Gender": "Female", "Timestamp": datetime.now()}]