FROM python:3

ADD tappecue-monitor.py .
ADD requirements.txt .

EXPOSE 8000

RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir /config

CMD ["python", "./tappecue-monitor.py"]

VOLUME /config