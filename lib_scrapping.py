from bs4 import BeautifulSoup as bs
from selenium import webdriver
from fake_useragent import UserAgent
import pandas as pd
import requests
import time

# Start a web driver (in this case, Chrome) 989988
driver = webdriver.Chrome()

base_url = "https://www.gandhi.com.mx/libros?p="  # Base URL
page_number = 1

urls = []
scraped_books = []
while True:
    ua = UserAgent()
    user_agent = ua.random
    headers = {
    'User-Agent': user_agent,
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
}
    url = base_url + str(page_number)
    response = requests.get(url, headers=headers)
    print(response)
    if response.status_code != 200:
        break

    # Navigate to the generated URL
    driver.get(url)

    # Wait for the page to load
    time.sleep(3)  # You can adjust the delay as needed

    # Get the page source
    page_source = driver.page_source
    soup = bs(page_source, 'html.parser')
    books = soup.find_all('a', class_='product photo product-item-photo')
    print(f"Scraping page {page_number}...")

    for book in books:
            new_book = []

            book_url = book.get('href')
            print("-->", book_url)
            book_resp = requests.get(book_url, headers=headers)
            book_soup = bs(book_resp.text, 'html.parser')
            
            isbn = book_soup.find('div', class_='isbn')
            if isbn:
                new_book.append(isbn.text.split(": ")[1])
            else:
                break

            #Check for title
            title = book_soup.find('span', class_='base')
            if title:
                new_book.append(title.text)
            else:
                new_book.append(None)
            
            #Check for author
            author = book_soup.find('div', class_='autor')
            if author:
                new_book.append(author.text.split(": ")[1])
            else:
                new_book.append(None)

            # Check for price
            price = book_soup.find('span', class_='price')
            if price:
                new_book.append(price.text)
            else:
                new_book.append(None)

            # Check for editorial
            editorial = book_soup.find('div', class_='editoriales')
            if editorial:
                new_book.append(editorial.text.split(": ")[1])
            else:
                new_book.append(None)

            counter = 0
            info = book_soup.find('div', class_='additional-attributes-wrapper table-wrapper')
            for i in info.find_all('span', class_='attr-data'):
                book_info = i.text.strip()
                new_book.append(book_info)
                counter += 1
                if counter == 3:
                    break
            
            urls.append(book_url)
            scraped_books.append(new_book)
            time.sleep(0.1)

    page_number += 1

# Close the web driver when you're done
driver.quit()


with open("urls.txt", "w") as file:
    for url in urls:
        file.write(url + "\n")

print(f"URLs have been written to urls.txt")

df = pd.DataFrame(scraped_books)
print(df.head())
df.to_csv("books_db.csv", index=False)