# syntax=docker/dockerfile:1
FROM python:3
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
RUN --mount=type=cache,target=/root/.cache pip install --upgrade pip
RUN --mount=type=cache,target=/root/.cache pip install -r requirements.txt
COPY augur_discord.py /app
COPY augur.py /app
CMD ["python", "augur_discord.py"]