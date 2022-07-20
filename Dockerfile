FROM python:3.9


WORKDIR /app
COPY apis/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn

COPY ./apis /app/

ENV FLASK_APP=app
ENTRYPOINT [ "gunicorn", "-c", "gunicorn.config.py", "--bind=0.0.0.0", "--reload", "--timeout", "600", "wsgi:app" ]
EXPOSE 5000