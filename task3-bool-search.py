from pymorphy2 import MorphAnalyzer
import json

morph = MorphAnalyzer()


def lemmatize(token):
    return morph.normal_forms(token)[0]


def search(query, inverted_index):
    operator = query.get("operator")
    left_query = query.get("left")
    right_query = query.get("right")

    if left_query:
        left_results = search(left_query, inverted_index)
    else:
        left_results = set()

    if right_query:
        right_results = search(right_query, inverted_index)
    else:
        right_results = set()

    if operator == "AND":
        results = left_results.intersection(right_results)
    elif operator == "OR":
        results = left_results.union(right_results)
    elif operator == "NOT":
        results = left_results.difference(right_results)
    else:
        term = query.get("val")
        results = inverted_index.get(lemmatize(term), set())

    return results


def read_index(filename):
    with open(filename, 'r') as f:
        d = {}
        for line in f:
            key, value = line.strip().split(': ')
            value_list = set(value.split())
            d[key] = value_list
        return d


if __name__ == '__main__':
    inverted_index = read_index('inverted_index.txt')

    # пример использования:
    #
    # одним not (двумя or (три and четыремя))

    # это наш search engine основанный на JSON, подобно ElasticSearch
    query = {
        "left": {
            "val": "одним"
        },
        "operator": "NOT",
        "right": {
            "left": {
                "val": "двумя"
            },
            "operator": "OR",
            "right": {
                "right": {
                    "val": "три"
                },
                "left": {
                    "val": "четыремя"
                },
                "operator": "AND",
            }
        }
    }

    results = search(query, inverted_index)
    print(results)
