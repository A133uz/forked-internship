from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.decorators import api_view
from testapp import utils, models
from .serializers import UploadedFileSerializer, MetricsSerializer
from django.db.models import Max, Min, Avg

class UploadFileAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        data = utils.process_file(file_obj)
        uploaded, metrics = utils.save_file_with_metrics(file_obj, data)
        return Response({"file": UploadedFileSerializer(uploaded).data, "tf-idf" : MetricsSerializer(metrics).data['tfidf_data']}, status=status.HTTP_201_CREATED)
    
class MetricsAPIView(APIView):
    def get(self, request):
        metrics = models.FileMetrics.objects.aggregate(mx_time=Max('processing_time'),
                                                    mn_time=Min('processing_time'),
                                                    avg_time=Avg('processing_time'),
                                                    avg_word_count=Avg('word_count'))
        
        return Response({"max_time_processed" : metrics['mx_time'],
                        "min_time_processed" : metrics['mn_time'],
                        "avg_time_processed" : metrics['avg_time'],
                        "avg_word_count" : metrics['avg_word_count']}, status=200)
    
@api_view(["GET"])
def display_version(request):
    return Response({"version" : "1.0"}, status=status.HTTP_200_OK)

@api_view(["GET"])
def get_status(request):
    
    return Response({"status" : "OK"}, status=200)

        

