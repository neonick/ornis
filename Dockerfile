FROM python:3.12-slim

WORKDIR app

RUN pip install requests

COPY . .

CMD ["python3", "-m", "orni"]
