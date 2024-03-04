#Deriving the latest base image
FROM python:latest


#Labels as key value pair
#LABEL Maintainer="Philip.H"

COPY Scraper.py ./
COPY EduCert.p12 ./
COPY database.db ./
COPY requirements.txt ./
COPY crontab ./

RUN apt-get update && apt-get -y install cron
RUN pip install --upgrade pip

RUN python3 -m venv /opt/venv
RUN . /opt/venv/bin/activate && pip install -r requirements.txt


RUN chmod a+x ./Scraper.py
RUN touch /var/log/cron.log



RUN crontab crontab

CMD ["cron", "-f", "/var/log/cron.log"]