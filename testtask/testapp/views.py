from django.shortcuts import render
import core.services
from .forms import UploadForm

def upload_and_show(request):
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            user = request.user
            collection = None  # Или достать нужную коллекцию, если надо

            document, stats = core.services.save_document_with_stats(user, file, collection)

            return render(request, 'words.html', {
                'stats': stats,
                'document': document,
            })
    else:
        form = UploadForm()

    return render(request, 'uploadform.html', {'form': form})

    
        