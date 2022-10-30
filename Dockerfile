FROM python:3.10.6-slim-bullseye

WORKDIR /usr/src/app
RUN pip install --no-cache-dir poetry
COPY . .
RUN poetry install
CMD ["poetry", "run", "peekl", "-c", "config.yaml"]
