FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY requirements.txt /tmp/
RUN pip3 install --requirement /tmp/requirements.txt
COPY ./app /app
