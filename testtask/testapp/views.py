from django.shortcuts import render
from .utils import process_file, save_file_with_metrics

def upload_and_show(request):
    if request.method == 'POST' and request.FILES['file']:
        file_obj = request.FILES['file']
        data = process_file(file_obj)
        uploaded, metrics = save_file_with_metrics(file_obj, data)

        return render(request, 'words.html', {'file': uploaded, 'metrics': metrics})
    return render(request, 'uploadform.html')

    
        