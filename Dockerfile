FROM python:3.8

ADD tappecue-monitor.py .
ADD requirements.txt .

EXPOSE 8000

HEALTHCHECK CMD curl --fail http://localhost:8000 || exit 1

RUN pip install --no-cache-dir -r requirements.txt

# CMD ["python", "./tappecue-monitor.py"]
ENTRYPOINT ["python", "./tappecue-monitor.py"]

VOLUME /config