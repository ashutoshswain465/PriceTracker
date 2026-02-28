import requests
from bs4 import BeautifulSoup

url = "http://books.toscrape.com/"

print("Book Price Scraper")
print("==================")

response = requests.get(url)

if response.status_code == 200:
    print("\nScraping book information...")

soup = BeautifulSoup(response.content, 'html.parser')

books = soup.find_all('article', class_='product_pod')

counter = 0

for book in books[:3]:
    title = book.h3.a['title']
    price_text = book.find('p', class_='price_color').text
    price = float(price_text.replace('£',''))
    availability = book.find('p', class_='instock availability').text.strip()
    counter += 1

    print(f"Title: {title}")
    print(f"Price: {price}")
    print(f"Availability: {availability}\n")

print("\nScraping complete!")
print(f"Total books found: {counter}")
