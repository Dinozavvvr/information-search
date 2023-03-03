import uuid
from urllib.parse import urlparse
import re

import requests
from bs4 import BeautifulSoup as bs


def parse(url):
    contents = {}
    domain = urlparse(url).scheme + '://' + urlparse(url).netloc

    page_content = requests.get(url).text
    soap = bs(page_content, features="html.parser")
    contents[url] = page_content

    current = 0
    max = 200
    # получем все страницы с главной
    for a in soap.find_all('a', href=True):
        if current == max:
            return contents

        url = a['href']
        if not url.startswith("http"):
            if re.match("(.*#.*)|(.*(.svg|.jpg|.jpeg|.gif|.doc|.pdf|.docx)$)", url.lower()):
                continue
            url = domain + url

        contents[url] = requests.get(url).text
        current += 1

    return contents


def save(contents_map):
    with open(f"index.txt", "w") as index:
        for url, content in contents_map.items():
            filename = uuid.uuid4()
            # сохраняем контент
            with open(f"data/{filename}.html", "w") as file:
                file.write(bs(content, features="html.parser").prettify())
            # добавляем в index.txt
            index.write(f"{filename} : {url}\n")


if __name__ == '__main__':
    url = 'https://ru.wikipedia.org/wiki/%D0%98%D1%80%D0%B0%D0%BA%D1%81%D0%BA%D0%B0%D1%8F_%D0%B2%D0%BE%D0%B9%D0%BD%D0%B0#:~:text=%D0%98%D1%80%D0%B0%D0%BA%D1%81%D0%BA%D0%B0%D1%8F%20%D0%B2%D0%BE%D0%B9%D0%BD%D0%B0%20(%D1%81%2020%20%D0%BC%D0%B0%D1%80%D1%82%D0%B0,%D1%86%D0%B5%D0%BB%D1%8C%D1%8E%20%D1%81%D0%B2%D0%B5%D1%80%D0%B6%D0%B5%D0%BD%D0%B8%D1%8F%20%D0%BF%D1%80%D0%B0%D0%B2%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D1%81%D1%82%D0%B2%D0%B0%20%D0%A1%D0%B0%D0%B4%D0%B4%D0%B0%D0%BC%D0%B0%20%D0%A5%D1%83%D1%81%D0%B5%D0%B9%D0%BD%D0%B0.&text=%D0%9E%D1%81%D0%BD%D0%BE%D0%B2%D0%BD%D0%BE%D0%B9%20%D0%BA%D0%BE%D0%BD%D1%84%D0%BB%D0%B8%D0%BA%D1%82%3A,%D0%98%D1%80%D0%B0%D0%BA%D1%81%D0%BA%D0%B8%D0%B9%20%D0%BA%D0%BE%D0%BD%D1%84%D0%BB%D0%B8%D0%BA%D1%82'
    contents = parse(url)
    save(contents)
