FROM python:3.9-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

FROM base AS development
COPY ./media /temporary_media
EXPOSE 8000
CMD ["sh", "entrypoint.development.sh"]

FROM base AS pre-production
CMD [ "sh", "entrypoint.pre-production.sh" ]

FROM base AS production
CMD [ "sh", "entrypoint.production.sh" ]