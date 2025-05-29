FROM python:3.13-slim

RUN apt-get update && apt-get install -y curl libpq-dev
RUN curl -sSL https://install.python-poetry.org | python3

ENV PATH="/root/.local/bin:/app/.venv/bin:$PATH"
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

WORKDIR /app

COPY .env.docker .env
COPY . .

RUN poetry install --no-root

EXPOSE 3002

CMD ["poetry", "run", "start"]