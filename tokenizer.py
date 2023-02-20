from os import listdir

import re
from string import digits
from bs4 import BeautifulSoup as bs


# read collection of files in directory
def dir_reader(directory):
    files = [file for file in listdir(directory)]

    files_content = []
    for file in files:
        files_content.append(file_reader(f'{directory}/{file}'))

    return files_content


# read single file
def file_reader(filename):
    with open(filename, 'r') as file:
        return ''.join(file.readlines())


def extract_text(htmls):
    texts = []
    for html in htmls:
        texts.append(clean_html(html))

    return texts


def tokenize_collection(texts):
    tokens = set()

    for text in texts:
        tokens.update(tokenize(text))

    return tokens


def tokenize(text):
    # clear text
    t = re.sub(r'[^\w-]', ' ', text)
    t = re.sub(r'\d', '', t)
    t = re.sub(r'\s\w\s', '', t)
    t = re.sub(r'\s\s+', ' ', t)
    t = t.split(' ')

    return set(t)



def clean_html(html):
    soup = bs(html, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out

    # get text
    text = soup.find('body').get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text


def save_tokens(tokens):
    with open('tokens.txt', 'w') as file:
        for token in tokens:
            file.write(token + "\n")


if __name__ == '__main__':
    contents = dir_reader('data')
    texts = extract_text(contents)
    tokens = tokenize_collection(texts)
    save_tokens(tokens)