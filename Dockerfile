FROM python:3.9-alpine3.16

COPY requairements.txt /temp/requairements.txt
RUN apk add postgresql-client build-base postgresql-dev
RUN pip install -r /temp/requairements.txt
COPY service /service
WORKDIR /service
EXPOSE 8000



RUN adduser --disabled-password service-user
#RUN chown service-user:service-user -R /service/


USER service-user
