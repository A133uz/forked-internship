from rest_framework import serializers
from testapp import models

class MetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FileMetrics
        fields = [
            'tfidf_data',
            'processing_time',
            'word_count',
            'max_time_processed',
            'min_time_processed',
            'avg_word_count'
        ]
        
class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UploadedFile
        fields = ['id', 'filename', 'file', 'uploaded_at']
