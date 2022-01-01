FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

# Necessary in order to install psycopg2
RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev

COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . ./

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "recipes_api.wsgi:application"]
