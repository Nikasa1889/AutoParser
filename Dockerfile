FROM python:3.6

# RUN apk add --no-cache dcron
RUN apt-get update && apt-get install -y cron
COPY ./requirements.txt /workspace/
WORKDIR /workspace
RUN pip3 install -r /workspace/requirements.txt

COPY ./*.py /workspace/

RUN echo 'MAILTO="nikasa.1889@gmail.com,ttaique@gmail.com"\n\
PYTHONIOENCODING=utf8\n\
25 2 * * * /usr/local/bin/python3 /workspace/Parse.py\n\
' > /etc/cron.d/parse-cron

RUN cat /etc/cron.d/parse-cron
RUN crontab /etc/cron.d/parse-cron

# Create log file to be able to tail
RUN touch /var/log/cron.log
 
# Run the command on container startup
CMD cron && tail -f /var/log/cron.log

