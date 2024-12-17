# Dockerfile for development purposes only
# the --reload option should not be used in production because it makes the process very inefficient
# CMD can be overriden using the docker-compose file
# FROM tiangolo/uvicorn-gunicorn:python3.10

FROM tiangolo/uvicorn-gunicorn:python3.11

RUN apt-get update && apt-get install default-jdk ffmpeg libsm6 libxext6 libpq-dev gcc texlive-xetex texlive texlive-latex-extra pandoc -y
RUN apt-get install git -y
RUN apt-get update && apt-get install curl -y
WORKDIR /usr/local/
RUN mkdir /usr/local/sap
WORKDIR /usr/local/sap
COPY docker/nwrfc750P_14-70002752.zip ./nwrfcsdk.zip
RUN unzip nwrfcsdk.zip

RUN rm nwrfcsdk.zip
RUN export SAPNWRFC_HOME=/usr/local/sap/nwrfcsdk
RUN touch /etc/ld.so.conf.d/nwrfcsdk.conf
RUN echo "/usr/local/sap/nwrfcsdk/lib" >> /etc/ld.so.conf.d/nwrfcsdk.conf
RUN apt-get install g++ -y
WORKDIR /app

# <-- pip -->
# COPY requirements.txt .

# RUN pip install --upgrade pip
# RUN pip install --no-cache-dir --upgrade -r requirements.txt

# <-- poetry -->
COPY pyproject.toml .
COPY poetry.lock .
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

COPY ./app /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]