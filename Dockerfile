FROM python:3.11
COPY certs/ink.crt /etc/ssl/ink.crt
COPY certs/ink.key /etc/ssl/ink.key
RUN chmod 644 /etc/ssl/ink.crt /etc/ssl/ink.key
WORKDIR /app
COPY requirements.txt .
COPY lib lib/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/
RUN pip install .
RUN chown -R www-data:www-data /app
USER www-data
EXPOSE 8000
CMD ["uvicorn", "inkserver:app", "--host", "0.0.0.0", "--port", "8000", "--root-path", "/ink/chat", "--ssl-keyfile=/etc/ssl/ink.key", "--ssl-certfile=/etc/ssl/ink.crt"]