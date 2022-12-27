FROM python:3.11.1-alpine

WORKDIR /app
COPY ./pyreminder/requirements.txt /app
RUN pip install -r requirements.txt
COPY ./pyreminder/pyreminder.py .

CMD python3 pyreminder.py && tail -f /dev/null