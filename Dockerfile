FROM python:3.6

# RUN apk add --no-cache dcron
RUN apt-get update && apt-get install -y cron
COPY ./requirements.txt /workspace/
WORKDIR /workspace
RUN pip3 install -r /workspace/requirements.txt

COPY ./*.py /workspace/
ADD crontab /etc/cron.d/autoparse
RUN chmod 644 /etc/cron.d/autoparse
RUN chown root:root /etc/cron.d/autoparse
RUN crontab /etc/cron.d/autoparse
RUN touch /var/log/cron.log
 
# Run the command on container startup
CMD service cron start && tail -f /dev/null
