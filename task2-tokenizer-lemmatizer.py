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
    filenames = []
    for file in files:
        filenames.append(file)
        files_content.append(file_reader(f'{directory}/{file}'))

    return files_content, filenames


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
    tokens_list = []

    for text in texts:
        tokens_list.append(tokenize(text))

    return tokens_list


def tokenize(text):
    # clear text
    text = text.lower()
    t = re.sub(r'[^А-Яа-я-]', ' ', text)
    t = re.sub(r'\d', '', t)
    # t = re.sub(r'\s\w\s', '', t)
    t = re.sub(r'\s\s+', ' ', t)
    t = t.split(' ')

    return set(t)


def remove_stopwords(tokens_list):
    removed_stopwords = []
    for token_list in tokens_list:
        removed_ = []
        for token in token_list:
            if token not in ru_stopwords:
                removed_.append(token)

        removed_stopwords.append(removed_)

    return removed_stopwords


def merge(tokens_list):
    tokens_set = set()

    for token_list in tokens_list:
        tokens_set.update(token_list)

    return tokens_set


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
        if token_lem not in lemmas:
            lemmas[token_lem] = [token]
        else:
            lemmas[token_lem].append(token)

    return lemmas


def save_lemmas(lemmas):
    with open('lemmas.txt', 'w') as file:
        for lemma, forms in lemmas.items():
            file.write(f'{lemma}: {" ".join(forms)}\n')


def create_inverted_index(tokens_list, filenames):
    inverted_index = {}

    for i, token_list in enumerate(tokens_list):
        for token in token_list:
            token_lem = morph.normal_forms(token)[0]
            if token_lem not in inverted_index:
                inverted_index[token_lem] = [filenames[i]]
            else:
                inverted_index[token_lem].append(filenames[i])

    return inverted_index


def save_inverted_index(inverted_index):
    with open('inverted_index.txt', 'w') as file:
        for inverted_item, docs in inverted_index.items():
            file.write(f'{inverted_item}: {" ".join(docs)}\n')


if __name__ == '__main__':
    contents, filenames = dir_reader('data')
    texts = extract_text(contents)

    tokens_list = tokenize_collection(texts)
    tokens_list = remove_stopwords(tokens_list)
    tokens_set = merge(tokens_list)
    lemmas = get_lemmas(tokens_set)
    inverted_index = create_inverted_index(tokens_list, filenames)

    save_tokens(tokens_set)
    save_lemmas(lemmas)
    save_inverted_index(inverted_index)
