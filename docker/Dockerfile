# Dockerfile for development purposes only
# the --reload option should not be used in production because it makes the process very inefficient
# CMD can be overriden using the docker-compose file

FROM tiangolo/uvicorn-gunicorn:python3.10

WORKDIR /app

RUN apt-get update

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
