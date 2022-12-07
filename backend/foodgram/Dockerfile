FROM python:3.7-slim
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY ./ .
RUN python manage.py makemigrations users api
RUN python manage.py migrate
RUN python manage.py collectstatic
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
