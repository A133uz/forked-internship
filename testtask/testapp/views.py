from django.shortcuts import render
from collections import Counter
import string
import math

doc_freqs = Counter()
total_docs = 0

# Create your views here.
def upload_file(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]

        
        if not uploaded_file.name.endswith((".txt", ".md", ".csv", ".json", ".docx", ".pdf")):
            return render(request, "uploadform.html", {"error": "Неверный формат файла. Загрузите текстовый файл или документ"})

       
        try:
            file_content = uploaded_file.read().decode("utf-8")
        except UnicodeDecodeError:
            return render(request, "uploadform.html", {"error": "Не смогли распознать файл"})
        
        extra_punctuation = "«»“”‘’—…<>"

        file_content = file_content.translate(str.maketrans("", "", string.punctuation + extra_punctuation))
        words = file_content.split()
        total_words = len(words)
        
        
        tf_scores = Counter(words)
        tf_scores = {word: count / total_words for word, count in tf_scores.items()}

        
        document_frequencies = Counter()
        document_count = 1  

        for word in set(words):
            document_frequencies[word] += 1

        idf_scores = {word: math.log((document_count + 1) / (df + 1)) + 1 for word, df in document_frequencies.items()}

       
        sorted_words = sorted(idf_scores.keys(), key=lambda w: idf_scores[w], reverse=True)[:50]

        return render(request, "words.html", {
            "tf_scores": tf_scores,
            "idf_scores": idf_scores,
            "sorted_words": sorted_words,
        })

    return render(request, "uploadform.html")
    
        