from bs4 import BeautifulSoup as bs
from selenium import webdriver
from fake_useragent import UserAgent
import pandas as pd
import requests
import time

proxy_list = [
    "50.168.210.238:80",
    "50.173.140.147:80",
    "50.169.62.109:80",
    "50.168.72.122:80",
    "50.207.199.86:80",
    "50.172.75.124:80",
    "50.168.163.176:80",
    "50.168.72.119:80",
    "50.174.145.15:80",
    "50.206.25.106:80",
    "50.170.90.30:80",
    "50.204.233.30:80",
    "68.185.57.66:80",
    "50.217.226.47:80",
    "198.49.68.80:80",
    "107.1.93.219:80",
    "107.1.93.218:80",
    "50.222.245.45:80",
    "50.174.145.8:80",
    "50.169.62.107:80",
    "50.221.74.130:80",
    "50.168.72.118:80",
    "50.168.72.114:80",
    "50.168.163.183:80",
    "50.171.32.226:80",
    "50.231.104.58:80",
    "50.207.199.82:80",
    "50.168.72.113:80",
    "50.228.83.226:80",
    "50.174.7.162:80",
    "50.204.219.227:80",
    "50.171.32.229:80",
    "50.228.141.96:80",
    "50.168.72.115:80",
    "50.173.140.151:80",
    "50.171.32.227:80",
    "107.1.93.212:80",
    "50.174.7.159:80",
    "138.68.225.200:80",
    "50.169.62.106:80",
    "50.173.140.150:80",
    "50.173.140.146:80",
    "209.97.150.167:3128",
    "50.172.75.123:80",
    "50.170.90.27:80",
    "50.168.72.116:80"
]

# Start a web driver (in this case, Chrome)
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

    # Choose a proxy from the list
    proxy = {'http': proxy_list[page_number % len(proxy_list)]}

    url = base_url + str(page_number)
    try:
        response = requests.get(url, headers=headers, proxies=proxy)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error accessing {url}: {e}")
        if response.status_code == 503:
            print("Retrying after a short delay...")
            time.sleep(5)  # Add a short delay before retrying
            continue
        else:
            break

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
    print(f"Scraping page {page_number}... with proxy '{proxy}'")

    for book in books:
            new_book = []

            book_url = book.get('href')
            print("-->", book_url)
            book_resp = requests.get(book_url, headers=headers)
            book_soup = bs(book_resp.text, 'html.parser')
            
            # Check for ISBN
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

            if info:
                # Find individual <li> elements
                li_pages = info.find('li', {'data-li': 'Número de páginas'})
                li_lang = info.find('li', {'data-li': 'Idioma'})
                li_date = info.find('li', {'data-li': 'Fecha de publicación'})

                # Extract information from <span> elements inside <li>
                pages = li_pages.find('span', class_='attr-data').text if li_pages else None
                lang = li_lang.find('span', class_='attr-data').text.strip() if li_lang else None
                date = li_date.find('span', class_='attr-data').text.strip() if li_date else None

                # Print the results
                new_book.append(pages)
                new_book.append(lang)
                new_book.append(date)
            else:
                break

            urls.append(book_url)
            scraped_books.append(new_book)
            time.sleep(0.1)

    page_number += 1
    if page_number % 20 == 0:
        time.sleep(15)
        ...
        # Change IPs and wait


# Close the web driver when you're done
driver.quit()

with open("output/urls.txt", "w") as file:
    for url in urls:
        file.write(url + "\n")

print(f"URLs have been written to urls.txt")

df = pd.DataFrame(scraped_books)
print(df.head())
df.to_csv("output/books_db.csv", index=False)