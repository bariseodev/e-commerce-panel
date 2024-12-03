import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Get input arguments
if len(sys.argv) < 3:
    print("Usage: python selenium_trendyol_link_extract.py <query_url> <page_count>")
    sys.exit(1)

query = sys.argv[1]
page_count = int(sys.argv[2])

if page_count > 200:
    print("200 sayfadan fazla çekilemez.")
    sys.exit()

all_product_links = []

# Setup Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0')
chrome_service = Service("C:/chromedriver.exe")  # Replace with the path to your ChromeDriver
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

try:
    # Iterate through pages
    for i in range(1, page_count + 1):
        print(f"Sayfa: {i}")
        page_url = f"{query}?pi={i}"
        driver.get(page_url)
        time.sleep(3)  # Wait for the page to load fully

        # Find product cards
        product_cards = driver.find_elements(By.CLASS_NAME, "p-card-wrppr")
        for card in product_cards:
            try:
                # Extract product link
                link_element = card.find_element(By.CSS_SELECTOR, "div.p-card-chldrn-cntnr.card-border a")
                link = link_element.get_attribute("href")
                all_product_links.append(link)
            except Exception as e:
                print(f"Bağlantı alınamadı: {e}")
finally:
    driver.quit()

# Remove duplicate links
unique_links = list(set(all_product_links))
print(f"Toplam ürün bağlantısı: {len(unique_links)}")

# Save product links to a file for later use
output_file = "product_links.txt"
with open(output_file, "w") as f:
    for link in unique_links:
        f.write(link + "\n")

print(f"Ürün bağlantıları alındı ve {output_file} dosyasına kaydedildi.")
