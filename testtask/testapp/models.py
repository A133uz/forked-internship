from django.db import models

class ProcessedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    tfidf_data = models.JSONField(blank=True, null=True)  
    processing_time = models.FloatField(null=True, blank=True)
    word_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.filename

  

    

