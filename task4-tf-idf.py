import math
import os
import re
import nltk
from pathlib import Path
from os import listdir
from bs4 import BeautifulSoup as bs
from nltk.corpus import stopwords, words

nltk.download('stopwords')

words = set(words.words())
en_stopwords = stopwords.words('russian')


def dir_reader(directory):
    files = [file for file in listdir(directory)]
    files_content = []
    for file in files:
        files_content.append(clean_html(file_reader(f'{directory}/{file}')))
    return files_content, files


def file_reader(filename):
    with open(filename, 'r') as file:
        return ''.join(file.readlines())


def extract_text(htmls):
    print('Extracting text')
    texts = []
    for html in htmls:
        texts.append(clean_html(html))
    return texts


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

    # clear text
    text = text.lower()
    t = re.sub(r'[^А-Яа-я-]', ' ', text)
    t = re.sub(r'\d', '', t)
    t = re.sub(r'\s\w\s', '', t)
    t = re.sub(r'\s\s+', ' ', t)
    t = t.split(' ')

    return t


def tokenize_with_count(text):
    token_count_dict = {}
    for token in text:
        if token in token_count_dict:
            token_count_dict[token] += 1
        else:
            token_count_dict[token] = 1
    return token_count_dict


def count_tokens(texts):
    token_count_dicts = []
    for i, text in enumerate(texts):
        token_count_dicts.append(tokenize_with_count(text))
    return token_count_dicts


def load_termins(termins_file):
    termins_set = set()
    with open(termins_file, 'r') as file:
        for line in file:
            termins_set.add(line.strip())
    return termins_set


def load_lemmas(lemmas_file):
    lemma_form_dict = {}
    with open(lemmas_file, 'r') as file:
        for line in file:
            parts = line.strip().split(':')
            word = parts[0].strip()
            forms = [form.strip() for form in parts[1].split()]
            lemma_form_dict[word] = forms
    return lemma_form_dict


def count_lemma_forms(lemma_form_dict, token_count_dicts):
    lemma_count_dicts = []
    for token_count_dict in token_count_dicts:
        lemma_count_dict = {}
        for lemma, forms in lemma_form_dict.items():
            count = 0
            for form in forms:
                if form in token_count_dict:
                    count += token_count_dict[form]
            if count != 0:
                lemma_count_dict[lemma] = count
        lemma_count_dicts.append(lemma_count_dict)
    return lemma_count_dicts


def calculate_doc_word_sums(token_count_dicts):
    sums = []
    for token_count_dict in token_count_dicts:
        sums.append(sum(token_count_dict.values()))
    return sums


def calculate_tf_idf(result_dir, files, word_count_dicts, termins_set, doc_word_sums):
    Path(result_dir).mkdir(parents=True, exist_ok=True)

    for file in listdir(result_dir):
        os.remove(os.path.join(result_dir, file))
    doc_count = len(word_count_dicts)

    for i, word_count_dict in enumerate(word_count_dicts):
        with open(f'{result_dir}/{files[i].split(".")[0]}.txt', 'a') as file:
            for word, count in word_count_dict.items():
                if word not in termins_set:
                    continue
                tf = count / doc_word_sums[i]
                idf = math.log(doc_count / sum(1 for d in word_count_dicts if word in d))
                tf_idf = tf * idf
                if idf == 0.0:
                    file.write(f'{word} 0.0 0.0\n')
                else:
                    file.write(f'{word} {idf:.20f} {tf_idf:.20f}\n')


if __name__ == '__main__':
    texts, files = dir_reader('data')

    termins_set = load_termins('tokens.txt')
    token_count_dicts = count_tokens(texts)

    lemma_form_dict = load_lemmas('lemmas.txt')
    lemma_count_dicts = count_lemma_forms(lemma_form_dict, token_count_dicts)
    doc_word_sums = calculate_doc_word_sums(token_count_dicts)

    calculate_tf_idf('tokens_tf_idf', files, token_count_dicts, termins_set, doc_word_sums)
    calculate_tf_idf('lemmas_tf_idf', files, lemma_count_dicts, termins_set, doc_word_sums)