# base image
FROM python:3.9

# set work directory
WORKDIR /usr/src/app

# copy source code to work directory
COPY . .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# command to run on container start
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "2", "--max-requests", "1000", "-k", "sync", "run:app"]
