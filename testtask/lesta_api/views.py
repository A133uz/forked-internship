from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.decorators import api_view
from testapp import models, utils
from .serializers import ProcessedFileSerializer

class UploadFileAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        data = utils.process_file(file_obj)

        processed = models.ProcessedFile.objects.create(
            file=file_obj,
            filename=file_obj.name,
            tfidf_data=data['tfidf_data'],
            processing_time=data['processing_time'],
            word_count=data['word_count']
        )

        return Response(ProcessedFileSerializer(processed).data, status=status.HTTP_201_CREATED)
    
@api_view(["GET"])
def display_version(request):
    return Response({"version" : "1.0"}, status=status.HTTP_200_OK)

