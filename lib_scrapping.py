from bs4 import BeautifulSoup as bs
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

response = requests.get("https://www.gandhi.com.mx/libros", headers=headers)

soup = bs(response.text, 'html.parser')

#print(soup.prettify())

#specific_a_tag = soup.find_all(class_='column main')
books = soup.find_all('li', class_='item product product-item')

print(books[0].prettify())

""" for book in books:
    book_url = book.find('a', class_='product photo product-item-photo')
    print(book)
    break """

""" if specific_a_tag:
    text = specific_a_tag.prettify() #get_text()
    print(text)
else:
    print('Tag not found') """