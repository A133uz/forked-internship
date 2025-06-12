import re
import math
from collections import Counter
from dataclasses import dataclass, field
from .models import Collection
from typing import Dict, Optional
from heapq import heappop, heappush, heapify


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

#region Huffman's Algo implementation
@dataclass(order=True)
class HuffmanNode:
    freq: float
    word: Optional[str] = field(compare=False, default=None)
    left: Optional['HuffmanNode'] = field(compare=False, default=None)
    right: Optional['HuffmanNode'] = field(compare=False, default=None)
    
def build_huffman_tree(tf_dict: Dict[str, float]) -> Optional[HuffmanNode]:
    if not tf_dict:
        return 
    
    hq = [HuffmanNode(freq=tf, word=word) for word, tf in tf_dict.items()]
    heapify(hq)
    
    while len(hq) > 1:
        lnode = heappop(hq)
        rnode = heappop(hq)
        merged = HuffmanNode(freq=lnode.freq+rnode.freq, left=lnode, right=rnode)
        heappush(hq, merged)
        
    return hq[0]

def generate_huffman_codes(node: Optional[HuffmanNode], prefix: str='', codebook: Optional[Dict[str, str]]=None) -> Dict[str, str]:
    if codebook is None:
        codebook = {}
    if node is None:
        return codebook
    
    if node.word is not None:
        codebook[node.word] = prefix
    else:
        generate_huffman_codes(node.left, prefix+"0", codebook)
        generate_huffman_codes(node.right, prefix+"1", codebook)
    
    return codebook 
#endregion 