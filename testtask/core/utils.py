import re
import math
from collections import Counter
from .models import Collection


def clean_text(text: str) -> list[str]:
    # Убираем знаки препинания, приводим к нижнему регистру, разбиваем на слова
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()
    return words

def calculate_tf(words: list[str]) -> dict[str, float]:
    count = Counter(words)
    total = len(words)
    tf = {word: freq / total for word, freq in count.items()}
    return tf

def calculate_idf(collection: Collection, all_words: set) -> dict[str, float]:
    from .services import process_document_file
    # documents_word_sets — список множест слов каждого документа
    documents = collection.documents.all()
    documents_word_sets = [set(process_document_file(doc.file)) for doc in documents]
    N = len(documents_word_sets)
    idf = {}
    for word in all_words:
        doc_count = sum(1 for words in documents_word_sets if word in words)
        idf[word] = math.log((N / (1 + doc_count))) + 1  # сглаживание +1
    return idf


