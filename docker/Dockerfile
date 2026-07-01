# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder

ENV POETRY_VERSION=2.2.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --without dev


FROM python:3.12-slim AS runtime

RUN groupadd --system app && useradd --system --gid app --create-home app

WORKDIR /app
COPY --from=builder /app/.venv ./.venv
ENV PATH="/app/.venv/bin:${PATH}"

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

RUN chown -R app:app /app
USER app

EXPOSE 8000

ENTRYPOINT ["entrypoint.sh"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
