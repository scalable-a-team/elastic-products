FROM python:3.9


WORKDIR /app
COPY apis/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn

COPY ./apis /app/

ENV FLASK_APP=app

ENTRYPOINT [ "python" ]
CMD [ "main.py" ]
EXPOSE 5000