from rest_framework import serializers
from testapp import models

class ProcessedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProcessedFile
        fields = '__all__'
