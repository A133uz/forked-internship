from django.db import models
from django.contrib.auth.models import User

class Document(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    processing_time = models.FloatField(null=True, blank=True)
    word_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Документ {self.id} загружен {self.uploaded_by.username}'

class Collection(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    documents = models.ManyToManyField(Document, related_name='collections')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Коллекция "{self.name}"  {self.owner.username}'

class Statistics(models.Model):
    word = models.CharField(max_length=100)
    tf = models.FloatField()  # Term Frequency in the document
    idf = models.FloatField() # Inverse Document Frequency in the collection
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='word_statistics')
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='word_statistics')

    class Meta:
        unique_together = ('word', 'document', 'collection')

    def __str__(self):
        return f'Статистика слова "{self.word}" в документе {self.document.id} / коллекции {self.collection.id}'



  

    

