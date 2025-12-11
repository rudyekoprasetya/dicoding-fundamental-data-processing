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
    time_stamp = datetime.now() 
    product_detail_element=product.find('div', class_='product-details')
    title = product_detail_element.find('h3', class_='product-title').text
    product_element = product_detail_element.find('div', class_='price_countainer')
    price_usd = product_element.find('span', class_='price').text
   

    details = product_detail_element.find_all('p')
    rating_text = details[0].text.strip()
    rating = float(rating_text.split("⭐")[1].split("/")[0].strip()) if "⭐" in rating_text else None
    
    colors = int(details[1].text.strip().split()[0])
    size = details[2].text.strip().split(":")[1].strip()
    gender = details[3].text.strip().split(":")[1].strip()
 
    
 
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
 
 
def scrape_data(base_url, start_page=1, delay=2):
    try:
        #Fungsi utama untuk mengambil keseluruhan data, mulai dari requests hingga menyimpannya dalam variabel data.
        data = []
        page_number = start_page
    
        while True:
            url = base_url.format(page_number)
            print(f"Scraping halaman: {url}")
    
            content = fetching_content(url)
            if content:
                soup = BeautifulSoup(content, "html.parser")
                products_element = soup.find_all('div', class_='collection_card')
                for product in products_element:
                    book = extract_data(product)
                    data.append(book)
    
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
 
