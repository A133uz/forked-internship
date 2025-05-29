from sklearn.feature_extraction.text import TfidfVectorizer
import time

def process_file(file_obj):
    content = file_obj.read().decode('utf-8')
    start = time.time()
    
    words = content.split()[:50]
    text = ' '.join(words)

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform([text])
    
    tfidf_scores = {
        word: round(score, 4)
        for word, score in zip(vectorizer.get_feature_names_out(), X.toarray()[0])
    }

    return {
        "tfidf_data": tfidf_scores,
        "processing_time": round(time.time() - start, 4),
        "word_count": len(words)
    }
