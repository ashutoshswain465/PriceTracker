import requests
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime

print("Book Price Tracker with database")
print("================================")

print("Initializing database...")
conn = sqlite3.connect('books.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        title TEXT,
        price REAL,
        availability TEXT
    )
''')

conn.commit()
print('Database ready: books.db\n')

url = "http://books.toscrape.com/"
response = requests.get(url)

if response.status_code == 200:
    print("\nScraping book information...")

soup = BeautifulSoup(response.content, 'html.parser')

books = soup.find_all('article', class_='product_pod')

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
scraped_data = []

for book in books[:20]:
    title = book.h3.a['title']
    price_text = book.find('p', class_='price_color').text
    price = float(price_text.replace('£', ''))
    availability = book.find('p', class_='instock availability').text.strip()

    scraped_data.append((timestamp, title, price, availability))

print(f'Scraped {len(scraped_data)} books successfully!\n')

print('Checking for price changes...\n')

price_changes = []
prices_down = 0
prices_up = 0
prices_same = 0

for timestamp, title, new_price, availability in scraped_data:
    cursor.execute('''
        SELECT price from books
        WHERE title = ?
        ORDER BY timestamp DESC
        LIMIT 1
    ''', (title,))

    result = cursor.fetchone()

    if result:
        old_price = result[0]
        if new_price < old_price:
            price_changes.append(f"📉 {title}: £{old_price:.2f} → £{new_price:.2f} (DOWN £{diff:.2f})")
            prices_down += 1
        elif new_price > old_price:
            diff = new_price - old_price
            price_changes.append(f"📈 {title}: £{old_price:.2f} → £{new_price:.2f} (UP £{diff:.2f})")
            prices_up += 1
        else:
            prices_same += 1

    cursor.execute('''
        INSERT INTO books (timestamp, title, price, availability)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, title, new_price, availability))

conn.commit()

if price_changes:
    print("Price Changes Detected:")
    print("-----------------------")
    for change in price_changes[:10]:
        print(change)
    if len(price_changes) > 10:
        print(f"... and {len(price_changes) - 10} more changes")
    print()
else:
    print("No price changes detected (first run or all prices unchanged)\n")

print("Summary:")
print("--------")
print(f"Total books: {len(scraped_data)}")
print(f"Prices decreased: {prices_down}")
print(f"Prices increased: {prices_up}")
print(f"Prices unchanged: {prices_same}\n")

conn.close()
print("All data saved to database!")
