FROM python:3.8-alpine
WORKDIR /code
RUN apk add --no-cache gcc musl-dev linux-headers libffi-dev openssl-dev rust cargo build-base
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip & pip install -r requirements.txt
COPY . .
RUN poetry install
CMD ["poetry", "run" , "python", "main.py"]