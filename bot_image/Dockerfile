FROM python:3.11-bookworm
WORKDIR /app
COPY requirements.txt .
COPY bot_tg_pg.py .
COPY .env .
RUN pip install -r requirements.txt
RUN mkdir -p /app/log
CMD ["python", "bot_tg_pg.py"]
