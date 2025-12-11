import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
 
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    )
}
 
 
def fetching_content(url):
    #Mengambil konten HTML dari URL yang diberikan
    session = requests.Session()
    response = session.get(url, headers=HEADERS)
    try:
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan ketika melakukan requests terhadap {url}: {e}")
        return None
 
 
def extract_data(product):
    try:
        time_stamp = datetime.now() 
        t = product.find("h3", class_="product-title")
        title = t.get_text(strip=True) if t else "Unknown Product"
        p = product.find("span", class_="price") or product.find("p", class_="price")
        price = p.get_text(strip=True) if p else "Price Unavailable"
        price_usd = price.replace("$", "").strip()
        details = product.find_all("p", style=lambda v: v and "font-size: 14px" in v)
        rating = colors = size = gender = None
        for x in details:
            text = x.get_text(strip=True)
            if text.startswith("Rating:"):
                rating = text.replace("Rating:", "").replace("⭐","").replace(" / 5","").strip()
            elif "Colors" in text:
                colors = text.replace("Colors", "").strip()
            elif text.startswith("Size:"):
                size = text.replace("Size: ","").strip()
            elif text.startswith("Gender:"):
                gender =  text.replace("Gender: ","").strip()

        list_product = {
            "Title": title,
            "Price": price_usd,
            "Rating": rating,
            "Colors":colors,
            "Size":size,
            "Gender":gender,
            "Timestamp":time_stamp
        }
    
        return list_product
    except Exception as e:
        print(f"An error occurred to save dataframe : {e}") 
 
def scrape_data(base_url, start_page=1, delay=1):
    try:
        #Fungsi utama untuk mengambil keseluruhan data, mulai dari requests hingga menyimpannya dalam variabel data.
        data = []
        page_number = start_page
    
        while True:
            if (page_number==1):
                url = 'https://fashion-studio.dicoding.dev/'
            else:
                url = base_url.format(page_number)
            print(f"Scraping halaman: {url}")
    
            content = fetching_content(url)
            if content:
                soup = BeautifulSoup(content, "html.parser")
                products_element = soup.find_all('div', class_='collection-card')
                for product in products_element:
                    product_data = extract_data(product)
                    data.append(product_data)
    
                next_button = soup.find('li', class_='page-item next')
                if next_button:
                    page_number += 1
                    time.sleep(delay) # Delay sebelum halaman berikutnya
                else:
                    break # Berhenti jika sudah tidak ada next button
            else:
                break # Berhenti jika ada kesalahan
    
        return data
    except Exception as e:
        print(f"An Error Occured During Scraping Data : {e}")
 
