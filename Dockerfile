FROM python:3.10-slim

RUN apt update && apt install -y gcc libpq-dev bash && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install -r ./requirements.txt
 
WORKDIR /DBfinal/final_project

CMD ["bash", "-c", "tail -f /dev/null"]
