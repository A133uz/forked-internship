from sklearn.feature_extraction.text import TfidfVectorizer
from .models import UploadedFile, FileMetrics
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
    
def save_file_with_metrics(file_obj, processed):
    uploaded = UploadedFile.objects.create(file=file_obj, filename=file_obj.name)
    
    metrics = FileMetrics.objects.create(
        uploaded_file=uploaded,
        tfidf_data=processed['tfidf_data'],
        processing_time=processed['processing_time'],
        word_count=processed['word_count'],
        max_time_processed=processed.get('max_time_processed'),
        min_time_processed=processed.get('min_time_processed'),
        avg_word_count=processed.get('avg_word_count')
    )
    return uploaded, metrics

