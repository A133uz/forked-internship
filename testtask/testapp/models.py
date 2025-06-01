from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.filename
    
class FileMetrics(models.Model):
    uploaded_file = models.OneToOneField(UploadedFile, on_delete=models.CASCADE)
    tfidf_data = models.JSONField(blank=True, null=True)  
    processing_time = models.FloatField(null=True, blank=True)
    word_count = models.PositiveIntegerField(default=0)
    max_time_processed = models.FloatField(null=True, blank=True)
    min_time_processed = models.FloatField(null=True, blank=True)
    avg_word_count = models.FloatField(null=True, blank=True)

  

    

