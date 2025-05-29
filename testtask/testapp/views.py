from django.shortcuts import render
from .models import ProcessedFile
from .utils import process_file

def upload_and_show(request):
    if request.method == 'POST' and request.FILES['file']:
        file_obj = request.FILES['file']
        data = process_file(file_obj)

        processed = ProcessedFile.objects.create(
            file=file_obj,
            filename=file_obj.name,
            tfidf_data=data['tfidf_data'],
            processing_time=data['processing_time'],
            word_count=data['word_count']
        )

        return render(request, 'words.html', {'file': processed})
    return render(request, 'uploadform.html')

    
        