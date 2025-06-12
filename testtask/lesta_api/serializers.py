from rest_framework import serializers
from core.models import  Document, Collection, Statistics
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

#region User Serializers
"""
Сериализаторы, предназначенные для операций над моделью (сущностью) пользователя
"""
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # стандартные поля User
        read_only_fields = ['id']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        
    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data['username'],
                                        password=validated_data['password'],
                                        email=validated_data.get('email', '')
                                        )
        return user
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class PasswordUpdateSerializer(serializers.ModelSerializer):
    new_pass = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_pass = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        if data['new_pass'] != data['confirm_pass']:
            raise serializers.ValidationError('Пароли не совпадают')
        return data
    
    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_pass'])
        instance.save()
        return instance
        
    
#endregion

class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.ReadOnlyField(source='uploaded_by.username')
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'file', 'file_url', 'uploaded_by', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None
    
class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)
    collection_id = serializers.IntegerField(required=False)

    def validate_collection_id(self, value):
        from core.models import Collection
        if not Collection.objects.filter(id=value).exists():
            raise serializers.ValidationError("Collection does not exist.")
        return value
    
class DocumentContentSerializer(serializers.Serializer):
    doc_id = serializers.IntegerField()
    content = serializers.CharField()
    


class CollectionSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    name = serializers.CharField(required=False, allow_blank=True)
    documents = DocumentSerializer(many=True, read_only=True)
    documents_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Document.objects.all(),
        write_only=True,
        required=False,
        source='documents'
    )

    class Meta:
        model = Collection
        fields = ['id', 'name', 'owner', 'documents', 'documents_ids', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at']

    def create(self, validated_data):
        documents = validated_data.pop('documents', [])
        collection = Collection.objects.create(**validated_data)
        collection.documents.set(documents)
        return collection

    def update(self, instance, validated_data):
        documents = validated_data.pop('documents', None)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        if documents is not None:
            instance.documents.set(documents)
        return instance

class StatisticsSerializer(serializers.ModelSerializer):
    document_id = serializers.ReadOnlyField(source='document.id')
    collection_id = serializers.ReadOnlyField(source='collection.id')
    collection = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all(),
        allow_null=True, required=False
    )

    class Meta:
        model = Statistics
        fields = ['id', 'word', 'tf', 'idf', 'document_id', 'collection_id', 'collection']
        read_only_fields = ['id', 'document_id', 'collection_id']

