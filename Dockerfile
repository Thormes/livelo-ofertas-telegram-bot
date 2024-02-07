FROM python:3.10
LABEL authors="Thormes"

ENV TZ America/Sao_Paulo

RUN apt-get update

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

#COPY . .

RUN chmod -R o+s+w /app

ENTRYPOINT ["python", "bot_telegram.py"]