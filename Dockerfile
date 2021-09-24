FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY . /app/
COPY ./requirements.txt /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

WORKDIR /app

# CMD ['uvicorn', 'src.main:app', '--host=0.0.0.0', '--reload']
