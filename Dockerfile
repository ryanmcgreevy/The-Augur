# syntax=docker/dockerfile:1
FROM python:3
RUN mkdir /app
WORKDIR /app
COPY . /app
RUN --mount=type=cache,target=/root/.cache pip install --upgrade pip
RUN --mount=type=cache,target=/root/.cache pip install -r requirements.txt
CMD ["python", "augur_discord.py"]
