from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import api_view, action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from core.services import save_document_with_stats, encode_document_with_huffman
from core.models import Collection, Statistics, Document

from django.db.models import Avg, Min, Max
from django.db import transaction
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import get_object_or_404
from .serializers import (
    DocumentUploadSerializer, 
    DocumentSerializer, 
    StatisticsSerializer,
    PasswordUpdateSerializer,
    RegisterSerializer,
    UserSerializer,
    LoginSerializer,
    CollectionSerializer
    )

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import os
#region Document Operations
class DocumentUploadAPI(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        request_body=DocumentUploadSerializer,
        operation_description="Загрузка документа с возможной привязкой к коллекции",
        responses={201: openapi.Response("Document created")},
    )
    def post(self, request):
        serializer = DocumentUploadSerializer(data=request.data)
        if serializer.is_valid():
            file_obj = serializer.validated_data['file']
            collection_id = serializer.validated_data.get('collection_id')
            user = request.user or AnonymousUser()
           

            collection = None
            if collection_id:
                try:
                    collection = Collection.objects.get(id=collection_id)
                except Collection.DoesNotExist:
                    return Response({"error": "Коллекция не найдена."}, status=404)

            # ✅ Обработка и сохранение
            document, stats = save_document_with_stats(user=user, file_obj=file_obj, collection=collection)

            return Response({
                "document_id": document.id,
                "filename": os.path.basename(document.file.name),
                "message": "Документ успешно загружен и обработан.",
            }, status=201)

        return Response(serializer.errors, status=400)
   
class DocumentViewSet(ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Защита от генерации схемы swagger
        if getattr(self, 'swagger_fake_view', False):
            return Document.objects.none()

        user = self.request.user
        if not user.is_authenticated:
            return Document.objects.none()
        
        return Document.objects.filter(uploaded_by=self.request.user)

    @swagger_auto_schema(
        operation_description="Получить список документов (id : название) текущего пользователя",
        responses={
            200: openapi.Response(
                description="Словарь с id и названием документов",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    additional_properties=openapi.Schema(type=openapi.TYPE_STRING, description='Название документа')
                )
            )
        }
    )
    def list(self, request):
        docs = self.get_queryset()
        data = {doc.id: doc.file.name.split('/')[-1] for doc in docs}
        return Response(data)

    @swagger_auto_schema(
        operation_description="Получить содержимое документа",
        responses={
            200: openapi.Response(
                description="Содержимое документа",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'doc_id': openapi.Schema(type=openapi.TYPE_NUMBER, description='ID документа'),
                        'content': openapi.Schema(type=openapi.TYPE_STRING, description='Содержимое документа')
                    }
                )
            ),
            404: "Документ не найден"
        }
    )
    def retrieve(self, request, pk=None):
        doc = get_object_or_404(Document, id=pk, uploaded_by=request.user)
        doc.file.open()
        content = doc.file.read()
        doc.file.close()
        return Response({"doc_id": pk, "content": content})

    @swagger_auto_schema(
        operation_description="Удалить документ по ID, загруженный текущим пользователем",
        responses={
            204: openapi.Response(description="Документ успешно удалён"),
            404: "Документ не найден"
        }
    )
    def destroy(self, request, pk=None):
        doc = get_object_or_404(Document, id=pk, uploaded_by=request.user)
        doc.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_description="Получить статистику (TF и IDF) по документу для текущего пользователя.",
        responses={
            200: openapi.Response(
                description="Статистика по документу",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    additional_properties=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'tf': openapi.Schema(type=openapi.TYPE_NUMBER, description='TF слова в документе'),
                            'collections': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                description='Коллекции и соответствующие IDF значения',
                                additional_properties=openapi.Schema(type=openapi.TYPE_NUMBER),
                            )
                        }
                    )
                )
            ),
            404: "Документ не найден"
        }
    )
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        doc = get_object_or_404(Document, id=pk, uploaded_by=request.user)
        stats = Statistics.objects.filter(document=doc)
        result = {}
        for stat in stats:
            word = stat.word
            if word not in result:
                result[word] = {
                    "tf": stat.tf,
                    "collections": {}
                }
            collection_id = str(stat.collection.id) if stat.collection else "none"
            result[word]["collections"][collection_id] = stat.idf

        return Response(result)
    
    @action(detail=True, methods=["get"], url_path="huffman")
    def huffman_encode(self, request, pk=None):
        document = get_object_or_404(Document, id=pk, uploaded_by=request.user)
        try:
            encoded_text = encode_document_with_huffman(document.file)
        except IOError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(encoded_text)
   
class MetricsAPIView(APIView):
    
    
    @swagger_auto_schema(
        operation_description="Возвращает метрики по документам: среднее количество слов, минимальное и максимальное время обработки.",
        responses={
            200: openapi.Response(
                description="Метрики документов",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'average_word_count': openapi.Schema(type=openapi.TYPE_NUMBER, description='Среднее количество слов'),
                        'min_processing_time': openapi.Schema(type=openapi.TYPE_NUMBER, description='Минимальное время обработки (сек)'),
                        'max_processing_time': openapi.Schema(type=openapi.TYPE_NUMBER, description='Максимальное время обработки (сек)'),
                    }
                )
            )
        }
    )
    def get(self, request):
        docs = Document.objects.all()

        data = docs.aggregate(
            avg_word_count=Avg('word_count'),
            min_processing_time=Min('processing_time'),
            max_processing_time=Max('processing_time'),
            avg_processing_time=Avg('processing_time')
        )

        return Response(data)
#endregion 

#region Collection Operations
class CollectionViewSet(ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Защита от генерации схемы swagger
        if getattr(self, 'swagger_fake_view', False):
            return Document.objects.none()

        user = self.request.user
        if not user.is_authenticated:
            return Document.objects.none()
        
        return Collection.objects.filter(owner=self.request.user)
    @swagger_auto_schema(
    request_body=CollectionSerializer,
    responses={
        201: CollectionSerializer,
        400: "Bad Request"
    },
    operation_summary="Создать новую коллекцию",
    operation_description="Создает коллекцию с привязкой документов"
    )
    def create(self, request):
        serializer = CollectionSerializer(data=request.data, context={"request" : request})
        if serializer.is_valid():
            collection = serializer.save(owner=request.user)
            documents = self.request.data.get('documents')
            if documents:
                collection.documents.set(documents)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
    responses={200: openapi.Response(description="Список коллекций с документами")},
    operation_summary="Получить список коллекций пользователя"
    )
    def list(self, request):
        collections = self.get_queryset()
        data = [
            {
                'id': collection.id,
                'documents': DocumentSerializer(collection.documents.all(), many=True, context={'request': request}).data
            } for collection in collections
        ]
        return Response(data)
    
    @swagger_auto_schema(
    responses={
        200: DocumentSerializer(many=True),
        404: "Not Found"
    },
    operation_summary="Получить документы из коллекции"
    )
    def retrieve(self, request, pk=None):
        collection = get_object_or_404(self.get_queryset(), pk=pk)
        docs = collection.documents.all()
        serializer = DocumentSerializer(docs, many=True, context={'request': request})
        return Response(serializer.data)

    
    @swagger_auto_schema(
    method='get',
    responses={200: StatisticsSerializer(many=True)},
    operation_summary="Получить статистику коллекции"
    )   
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        collection = get_object_or_404(self.get_queryset(), pk=pk)
        stats = Statistics.objects.filter(collection=collection)
        serializer = StatisticsSerializer(stats, many=True)
        return Response(serializer.data) 
    
    @swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('pk', openapi.IN_PATH, description="ID коллекции", type=openapi.TYPE_INTEGER),
        openapi.Parameter('doc_id', openapi.IN_PATH, description="ID документа", type=openapi.TYPE_INTEGER),
    ],
    responses={200: "Документ добавлен", 404: "Not found"},
    operation_summary="Добавить документ в коллекцию"
    )
    @swagger_auto_schema(
    method='delete',
    manual_parameters=[
        openapi.Parameter('pk', openapi.IN_PATH, description="ID коллекции", type=openapi.TYPE_INTEGER),
        openapi.Parameter('doc_id', openapi.IN_PATH, description="ID документа", type=openapi.TYPE_INTEGER),
    ],
    responses={204: "Документ удален", 404: "Not found"},
    operation_summary="Удалить документ из коллекции"
    )
    @action(detail=True, methods=['post', 'delete'], url_path='(?P<doc_id>[^/.]+)')
    def modify_document(self, request, pk=None, doc_id=None):
        collection = get_object_or_404(self.get_queryset(), pk=pk)
        document = get_object_or_404(Document, pk=doc_id, uploaded_by=request.user)

        if request.method == 'POST':
            collection.documents.add(document)
            return Response({'msg': 'Документ добавлен'}, status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            collection.documents.remove(document)
            return Response({'msg': 'Документ удалён'}, status=status.HTTP_204_NO_CONTENT)
#endregion    

#region User Operations
User = get_user_model()

class UserViewSet(ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_queryset(self):
        return User.objects.all()
    
    @swagger_auto_schema(
    operation_description="Обновить пароль пользователя",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['password'],
        properties={
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Новый пароль'),
        }
    ),
    responses={
        200: openapi.Response(description='Пароль успешно обновлён'),
        403: openapi.Response(description='Нет доступа — можно менять только свой пароль'),
        400: openapi.Response(description='Некорректные данные')
    }
    )
    def partial_update(self, request, pk=None):
        if str(request.user.id) != pk:
            return Response({'msg' : 'Нет доступа!'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = PasswordUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        request.user.set_password(serializer.validated_data['password'])
        request.user.save()
        return Response({'msg' : 'Пароль обновлен'}, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
    operation_description="Удалить пользователя. Также удаляются все его файлы и коллекции.",
    responses={
        204: openapi.Response(description='Пользователь удалён'),
        403: openapi.Response(description='Нет доступа — можно удалить только свой аккаунт'),
        404: openapi.Response(description='Пользователь не найден')
    }
    )
    @transaction.atomic
    def destroy(self, request, pk=None):
        if str(request.user.id) != pk:
            return Response({'msg' : 'Нет доступа!'}, status=status.HTTP_403_FORBIDDEN)
        
        user = get_object_or_404(User, id=pk)
        user.delete()
        return Response({'msg' : 'Пользователь удален'}, status=status.HTTP_204_NO_CONTENT)

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
    operation_description="Регистрация нового пользователя по логину и паролю",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["username", "password"],
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING, description="Имя пользователя"),
            "password": openapi.Schema(type=openapi.TYPE_STRING, description="Пароль")
        }
    ),
    responses={
        201: openapi.Response(
            description="Пользователь успешно создан. Возвращаются access и refresh токены.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "msg": openapi.Schema(type=openapi.TYPE_STRING),
                    "access": openapi.Schema(type=openapi.TYPE_STRING),
                    "refresh": openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: "Ошибка валидации данных"
    }
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'msg' : "Пользователь создан",
            'access' : str(refresh.access_token),
            'refresh' : str(refresh)
        }, status=status.HTTP_201_CREATED)
        
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    
    @swagger_auto_schema(
    operation_description="Авторизация пользователя по логину и паролю",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["username", "password"],
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING, description="Имя пользователя"),
            "password": openapi.Schema(type=openapi.TYPE_STRING, description="Пароль")
        }
    ),
    responses={
        201: openapi.Response(
            description="Успешная авторизация. Возвращаются access и refresh токены.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "msg": openapi.Schema(type=openapi.TYPE_STRING),
                    "access": openapi.Schema(type=openapi.TYPE_STRING),
                    "refresh": openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        401: openapi.Response(
            description="Неверные логин или пароль",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "msg": openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        )
    }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'msg' : "Успешный вход",
                'access' : str(refresh.access_token),
                'refresh' : str(refresh)
            }, status=status.HTTP_201_CREATED)
        return Response({'msg' : 'Указаны неверные данные'}, status=status.HTTP_401_UNAUTHORIZED)
    
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
    operation_description="Выход пользователя. Refresh токен попадает в черный список.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["refresh"],
        properties={
            "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="Refresh токен для аннулирования")
        }
    ),
    responses={
        205: openapi.Response(
            description="Успешный выход. Токен добавлен в черный список.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "msg": openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: openapi.Response(
            description="Некорректный токен или отсутствует refresh",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        )
    }
    )
    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'msg' : 'Выход выполнен, токен добавлен в черный список'}, status=status.HTTP_205_RESET_CONTENT)
        except KeyError:
            return Response({'error' : 'Рефреш токен обязателен'}, status=status.HTTP_400_BAD_REQUEST)
        except TokenError as e:
            return Response({'error' : f'Некорректный токен {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
#endregion
@swagger_auto_schema( 
        method='get',
        operation_description="Возвращает текущую версию API.",
        responses={
            200: openapi.Response(
                description="Версия API",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'version': openapi.Schema(type=openapi.TYPE_STRING, description='Версия API'),
                    }
                )
            )
        }
    )   
@api_view(["GET"])
def get_version(request):
    return Response({"version" : "2.0.0"}, status=status.HTTP_200_OK)

@swagger_auto_schema(
        method='get',
        operation_description="Возвращает cтатус API. если ничего не возращается, значит присутствуют ошибки",
        responses={
            200: openapi.Response(
                description="Статус API",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, description='Статус API'),
                    }
                )
            )
        }
    ) 
@api_view(["GET"])
def get_status(request):
    
    return Response({"status" : "OK"}, status=status.HTTP_200_OK)

        

