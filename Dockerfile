FROM python:3.11.9-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y curl git wget unzip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# in addition to requirements.txt install package pandas-ta from repo
COPY pandas-ta.tar.gz .
RUN tar -xzf pandas-ta.tar.gz
RUN pip install ./pandas-ta

WORKDIR /app

# shared data folder
VOLUME ["/app/data"]

COPY . .

ARG DATAWAREHOUSE
ARG USE_TERRAFORM

CMD ["bash", "start_app.sh"]
