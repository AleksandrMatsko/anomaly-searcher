FROM python:3.12-slim

RUN apt-get update && apt-get install -y git
RUN apt-get update && apt-get install -y build-essential

# install rust compiler for river
RUN apt-get update && apt-get install -y \
    curl \
    build-essential

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

ENV PATH="/root/.cargo/bin:${PATH}"

RUN cargo --version

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

USER 2000

CMD ["python", "main.py", "-c", "/app/local/config.yaml"]
