import time, logging
from .utils import calculate_idf, calculate_tf
from .models import Document, Collection, Statistics
def get_top_rare_words(tf_dict, top_n=50):
    """
    Получить топ N слов с наименьшим TF (наиболее редкие слова в документе)
    """
    # Сортируем слова по возрастанию TF (наиболее редкие сверху)
    sorted_words = sorted(tf_dict.items(), key=lambda item: item[1])
    return dict(sorted_words[:top_n])

def process_document_file(file_obj):
    """
    Получить слова из файла.
    Например, можно считать текст, разделить по пробелам, очистить от знаков препинания, привести к нижнему регистру.
    """
    import re
    text = file_obj.read().decode('utf-8')
    words = re.findall(r'\b\w+\b', text.lower())
    return words

def save_document_with_stats(user, file_obj, collection=None):
    """
    Основная функция для:
    - Создания документа и сохранения файла
    - Расчёта TF
    - Добавления документа в коллекцию (если передана)
    - Пересчёта и сохранения статистики (TF/IDF)
    """
    start_time = time.time()
    
    # 1. Сохраняем документ
    document = Document.objects.create(file=file_obj, uploaded_by=user if user.is_authenticated else None)

    # 2. Получаем слова из файла
    words = process_document_file(document.file)

    # 3. Считаем TF для документа
    tf_all = calculate_tf(words)

    # 4. Выбираем 50 наиболее редких слов (минимальный TF)
    rare_words_tf = get_top_rare_words(tf_all, top_n=50)
    
    document.word_count = len(words)
    document.processing_time = time.time() - start_time
    document.save()

    if collection:
        # 5. Добавляем документ в коллекцию
        collection.documents.add(document)
        collection.save()

        # 6. Получаем IDF по коллекции для этих слов
        idf_values = calculate_idf(collection, set(rare_words_tf.keys()))

        # 7. Очищаем старую статистику для этого документа и коллекции
        Statistics.objects.filter(collection=collection, document=document).delete()

        # 8. Сохраняем статистику (TF и IDF) по 50 словам
        stats_objects = [
            Statistics(collection=collection, document=document, word=word, tf=tf, idf=idf_values.get(word, 0.0))
            for word, tf in rare_words_tf.items()
        ]
        Statistics.objects.bulk_create(stats_objects)
        
        stats_for_display = [
            {'word': word, 'tf': tf, 'idf': idf_values.get(word, 0.0)}
            for word, tf in rare_words_tf.items()
        ]

    else:
        
        # 7. Очищаем старую статистику для этого документа и коллекции
        Statistics.objects.filter(collection=None, document=document).delete()

        # 8. Сохраняем статистику (TF и IDF) по 50 словам
        stats_objects = [
            Statistics(collection=None, document=document, word=word, tf=tf, idf=1.0)
            for word, tf in rare_words_tf.items()
        ]
        Statistics.objects.bulk_create(stats_objects)
        
        stats_for_display = [
            {'word': word, 'tf': tf, 'idf': 1.0}  # idf = 1 если коллекции нет
            for word, tf in rare_words_tf.items()
        ]
        

    return document, stats_for_display
