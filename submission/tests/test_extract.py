# my_project/test/test_extract.py

import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from datetime import datetime
import requests # Untuk penanganan exception requests
import sys
import os

# --- MODIFIKASI PATH DIMULAI DI SINI ---
# Mendapatkan direktori tempat 'test_extract.py' berada (yaitu 'my_project/test')
current_dir = os.path.dirname(os.path.abspath(__file__))
# Mendapatkan direktori induk ('my_project')
project_root = os.path.join(current_dir, '..')

# Menambahkan direktori 'my_project' ke path.
# Ini memungkinkan kita mengimpor 'extract' sebagai 'utils.extract'.
sys.path.insert(0, project_root)

# --- MODIFIKASI PATH BERAKHIR DI SINI ---

# Mengimpor fungsi dari file utils/extract.py
try:
    # Karena kita menambahkan 'my_project' ke path, kita harus mengimpornya sebagai 'utils.extract'
    from utils.extract import fetching_content, extract_data, scrape_data
except ImportError as e:
    print(f"Gagal mengimpor dari utils.extract. Pastikan Anda berada di direktori my_project saat menjalankan test: {e}")
    sys.exit(1)

# Sekarang, saat melakukan patching (Mocking), kita harus merujuk pada lokasi modul yang baru: 'utils.extract'

class TestExtractionFunctions(unittest.TestCase):

    # --- Pengujian fetching_content ---

    # Perhatikan: Patching sekarang menargetkan 'utils.extract.requests.Session'
    @patch('utils.extract.requests.Session') 
    def test_fetching_content_success(self, MockSession):
        """Menguji fetching_content untuk respons HTTP 200 yang sukses."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html>Mock Content</html>"
        mock_response.raise_for_status.return_value = None

        mock_session_instance = MockSession.return_value
        mock_session_instance.get.return_value = mock_response

        url = "http://mock-url.com"
        result = fetching_content(url)

        self.assertEqual(result, b"<html>Mock Content</html>")

    @patch('utils.extract.requests.Session')
    @patch('builtins.print')
    def test_fetching_content_http_error(self, mock_print, MockSession):
        """Menguji fetching_content untuk penanganan kesalahan HTTP (misalnya, 404)."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")

        mock_session_instance = MockSession.return_value
        mock_session_instance.get.return_value = mock_response

        url = "http://mock-url-404.com"
        result = fetching_content(url)

        mock_print.assert_called_once()
        self.assertIsNone(result)

    # --- Pengujian extract_data ---

    # Perhatikan: Patching sekarang menargetkan 'utils.extract.datetime'
    @patch('utils.extract.datetime') 
    def test_extract_data_complete(self, mock_datetime):
        """Menguji extract_data dengan data produk lengkap."""
        mock_now = datetime(2025, 1, 1, 10, 0, 0)
        mock_datetime.now.return_value = mock_now
        
        # HTML tiruan (Mock HTML) untuk produk lengkap
        html_product = """
        <div class="collection-card">
            <h3 class="product-title">T-Shirt Keren Terbaru</h3>
            <span class="price">$19.99</span>
            <p style="font-size: 14px">Rating: 4.5 ⭐ / 5</p>
            <p style="font-size: 14px">Colors: Black, White, Red</p>
            <p style="font-size: 14px">Size: S, M, L</p>
            <p style="font-size: 14px">Gender: Unisex</p>
        </div>
        """
        mock_product = BeautifulSoup(html_product, "html.parser").find('div')

        expected_data = {
            "Title": "T-Shirt Keren Terbaru",
            "Price": "19.99",
            "Rating": "4.5",
            "Colors": "Black, White, Red",
            "Size": "S, M, L",
            "Gender": "Unisex",
            "Timestamp": mock_now
        }

        result = extract_data(mock_product)
        self.assertEqual(result, expected_data)

    # ... (Anda dapat menyalin semua test case extract_data lainnya di sini) ...

    # --- Pengujian scrape_data ---

    # Perhatikan: Patching sekarang menargetkan 'utils.extract.time.sleep', 'utils.extract.fetching_content', dll.
    @patch('utils.extract.time.sleep', return_value=None)
    @patch('utils.extract.fetching_content')
    @patch('utils.extract.extract_data')
    def test_scrape_data_two_pages(self, mock_extract_data, mock_fetching_content, mock_sleep):
        """Menguji scrape_data untuk skenario 2 halaman sukses."""
        base_url = "https://fashion-studio.dicoding.dev/?page={}"
        
        # HTML Mock Halaman 1 (dengan tombol next)
        html_page_1 = """
        <html><body>
            <div class="collection-card">...Product 1...</div>
            <div class="pagination">
                <li class="page-item next"><a href="#">Next</a></li>
            </div>
        </body></html>
        """
        # HTML Mock Halaman 2 (tanpa tombol next)
        html_page_2 = """
        <html><body>
            <div class="collection-card">...Product 2...</div>
            <div class="pagination">
                </div>
        </body></html>
        """

        mock_fetching_content.side_effect = [
            html_page_1.encode('utf-8'),  # Halaman 1
            html_page_2.encode('utf-8')   # Halaman 2
        ]

        mock_extract_data.side_effect = [
            {"Title": "P1"},
            {"Title": "P2"}
        ]
            
        result = scrape_data(base_url, start_page=1, delay=0)

        self.assertEqual(mock_fetching_content.call_count, 2)
        self.assertEqual(mock_extract_data.call_count, 2)
        self.assertEqual(len(result), 2)


if __name__ == '__main__':
    unittest.main()