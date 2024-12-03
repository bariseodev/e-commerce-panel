import time
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Load product links from the file
with open('product_links.txt', 'r') as f:
    product_links = [line.strip() for line in f]

# Setup Selenium WebDriver
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Remove or comment this line to disable headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_service = Service("C:/chromedriver.exe")  # Replace with the path to your ChromeDriver
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# Prepare the Excel file and the dataframe for incremental saving
columns = ['Ürün Adı', 'Fiyat', 'Satıcı', 'Kategori', 'Kategori ID', 'Ürün Kodu', 'Görseller']
df = pd.DataFrame(columns=columns)

# Start iterating over product links
j = 0
for product_link in product_links:
    try:
        print(f"Çekilen Ürün: {j}")
        print(f"Ürün Bilgileri Çekiliyor: {product_link}")
        driver.get(product_link)
        time.sleep(3)  # Wait for the page to load fully

        # Extract the JSON-LD data from the <script type="application/ld+json"> tag
        try:
            script_tag = driver.find_element(By.XPATH, '//script[@type="application/ld+json"]')
            json_data = script_tag.get_attribute('innerHTML')

            # Print the raw JSON data to debug
            print("Raw JSON Data:", json_data)

            # Parse the JSON data
            try:
                product_data = json.loads(json_data)
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                continue  # Skip this product if JSON is invalid

            # Print the structure of the JSON data to debug
            print("Parsed JSON Data:", product_data)

            # Ensure the parsed data is a dictionary and access its details
            if isinstance(product_data, dict):
                # Extract product details from the parsed JSON
                product_name = product_data.get('name', 'Not Available')
                price = product_data.get('offers', {}).get('price', 'Not Available')
                price_currency = product_data.get('offers', {}).get('priceCurrency', 'Not Available')

                # Try to extract images from JSON (different structure might apply)
                images = product_data.get('image', [])
                image_urls = []

                # Handle cases where 'image' is a list of strings (direct URLs)
                if isinstance(images, list):
                    image_urls = [str(img) for img in images if isinstance(img, str)]
                # Handle case where 'image' is a dictionary with a 'contentUrl' key
                elif isinstance(images, dict) and 'contentUrl' in images:
                    image_urls.append(str(images['contentUrl']))

                # If no images found from JSON-LD, attempt to find images in HTML (for fallback)
                if not image_urls:
                    try:
                        image_elements = driver.find_elements(By.XPATH, '//img')
                        image_urls = [img.get_attribute('src') for img in image_elements if img.get_attribute('src')]
                    except Exception as img_e:
                        print(f"Error retrieving images from HTML: {img_e}")

                # Join the image URLs as a string separated by commas
                image_urls_str = ', '.join(image_urls)

                # Extract other product details (merchant, category, etc.)
                merchant = product_data.get('offers', {}).get('seller', {}).get('name', 'Not Available')
                category = product_data.get('category', 'Not Available')
                category_id = product_data.get('offers', {}).get('categoryID', 'Not Available')
                product_code = product_data.get('sku', 'Not Available')

                # Create a DataFrame for the current product
                product_details = pd.DataFrame([{
                    'Ürün Adı': product_name,
                    'Fiyat': f"{price} {price_currency}",
                    'Satıcı': merchant,
                    'Kategori': category,
                    'Kategori ID': category_id,
                    'Ürün Kodu': product_code,
                    'Görseller': image_urls_str  # Save image URLs as a comma-separated string
                }])

                # Concatenate the new product details with the existing DataFrame
                df = pd.concat([df, product_details], ignore_index=True)

                # Save the dataframe to Excel after each iteration
                df.to_excel('product_details.xlsx', index=False, engine='openpyxl')
                print(f"Ürün {product_name} kaydedildi ve Excel dosyasına yazıldı.")
            else:
                print("The JSON data is not in the expected format.")

        except Exception as e:
            print(f"Error extracting JSON data: {e}")
            continue  # Skip this product if JSON data extraction fails

        # Increment the counter j to track the number of products processed
        j += 1

    except Exception as e:
        print(f"Error retrieving product details for {product_link}: {e}")

# Close the WebDriver after scraping is done
driver.quit()

# Final message
print(f"Toplam ürün detayları çekildi: {j}")
print("Ürünler Excel dosyasına kaydedildi.")
