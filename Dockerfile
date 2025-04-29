FROM python:3.11-slim

RUN apt-get update && apt-get install -y procps && apt-get clean

WORKDIR /app

COPY process_parser.py .

CMD ["python", "process_parser.py"]