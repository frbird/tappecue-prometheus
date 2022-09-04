FROM python:3.9.13-buster

ADD tappecue-monitor.py .
ADD requirements.txt .

EXPOSE 8000

RUN pip install -r requirements.txt
RUN mkdir /config

CMD ["python", "./tappecue-monitor.py"]

VOLUME /config