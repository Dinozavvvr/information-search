import re
from os import listdir

from bs4 import BeautifulSoup as bs
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from pymorphy2 import MorphAnalyzer

morph = MorphAnalyzer()
lemmatizer = WordNetLemmatizer()
ru_stopwords = stopwords.words('russian')


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
    text = text.lower()
    t = re.sub(r'[^А-Яа-я-]', ' ', text)
    t = re.sub(r'\d', '', t)
    # t = re.sub(r'\s\w\s', '', t)
    t = re.sub(r'\s\s+', ' ', t)
    t = t.split(' ')

    return set(t)


def remove_stopwords(tokens):
    return [word for word in tokens if not word in ru_stopwords]


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


def get_lemmas(tokens):
    lemmas = {}

    for token in tokens:
        token_lem = morph.normal_forms(token)[0]
        if not token_lem in lemmas:
            lemmas[token_lem] = [token]
        else:
            lemmas[token_lem].append(token)

    return lemmas


def save_lemmas(lemmas):
    with open('lemmas.txt', 'w') as file:
        for lemma, forms in lemmas.items():
            file.write(f'{lemma}: {" ".join(forms)}\n')


if __name__ == '__main__':
    contents = dir_reader('data')
    texts = extract_text(contents)
    tokens = tokenize_collection(texts)
    tokens = remove_stopwords(tokens)

    save_tokens(tokens)

    lemmas = get_lemmas(tokens)
    save_lemmas(lemmas)
