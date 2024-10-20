FROM python:3.13-slim

WORKDIR /app
ADD requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ADD . .

EXPOSE 8000
ENTRYPOINT ["uvicorn"]
CMD ["mimipi:app", "--port", "8000", "--host", "0.0.0.0", "--no-server-header"]
