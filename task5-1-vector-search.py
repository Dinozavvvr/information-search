import numpy as np
from os import listdir


def read_lemmas(lemmas_file):
    lemmas = []
    with open(lemmas_file, 'r') as file:
        for line in file:
            parts = line.strip().split(':')
            lemma = parts[0].strip()
            lemmas.append(lemma)
    return lemmas


def save_file_order(files):
    with open('file_order.txt', 'w') as f:
        for i in range(len(files)):
            key = files[i].split('.')[0]
            f.write(f'{i}:{key}\n')


def calculate_vector_matrix(lemma_vocabulary, tfidf_directory):
    files = [file for file in listdir(tfidf_directory)]

    save_file_order(files)

    doc_lemma_matrix = np.zeros((len(files), len(lemma_vocabulary)))

    for i in range(len(files)):
        with open(f'{tfidf_directory}/{files[i]}', 'r') as f:
            for line in f:
                values = line.strip().split()
                lemma, tfidf = values[0], values[2]
                if lemma in lemma_vocabulary:
                    j = lemma_vocabulary.index(lemma)
                    doc_lemma_matrix[i, j] = tfidf

    return doc_lemma_matrix


if __name__ == '__main__':
    lemmas_map = read_lemmas('lemmas.txt')

    doc_lemma_matrix = calculate_vector_matrix(lemmas_map, 'lemmas_tf_idf')
    # нормализация
    doc_lemma_matrix_normalized = np.apply_along_axis(lambda x: x / np.linalg.norm(x), 1, doc_lemma_matrix)

    np.save('vectors.npy', doc_lemma_matrix_normalized)
