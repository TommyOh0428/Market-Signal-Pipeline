FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup -S app && adduser -S app -G app \
    && apk add --no-cache libstdc++

COPY pyproject.toml ./
COPY src ./src
COPY examples ./examples

RUN pip install --upgrade pip \
    && pip install --only-binary=:all: .

USER app

CMD ["msp-quant-example", "--ticker", "NVDA", "--news-score", "0"]
