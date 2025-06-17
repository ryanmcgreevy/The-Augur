# syntax=docker/dockerfile:1
FROM python:3
RUN mkdir /app
#RUN mkdir /app/eso_news
WORKDIR /app
COPY requirements.txt /app/
RUN --mount=type=cache,target=/root/.cache pip install --upgrade pip
RUN --mount=type=cache,target=/root/.cache pip install -r requirements.txt
RUN playwright install
RUN playwright install-deps
RUN apt-get update && apt-get install -y cron
RUN echo "*/30   *   *   *   * /usr/local/bin/python /app/crawler_eso.py >> /var/log/cron.log 2>&1" > /etc/cron.d/crawler
# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/crawler
# Apply cron job
RUN crontab /etc/cron.d/crawler
# Create the log file to be able to run tail
RUN touch /var/log/cron.log
COPY elastic/elastic.py /app
COPY crawler_eso.py /app
# Run the command on container startup
CMD cron && tail -f /var/log/cron.log

