FROM nginx:alpine

COPY ./html /usr/share/nginx/html

EXPOSE 80

FROM python:3.12.6-slim 

ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip 
RUN pip install -r requirements.txt

COPY . .


EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
