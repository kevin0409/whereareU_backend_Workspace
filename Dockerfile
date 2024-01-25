FROM python:latest
RUN mkdir websvr/
ADD / websvr/
WORKDIR /websvr
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["sudo python -u", "run.py"]
