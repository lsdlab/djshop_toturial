FROM python:3.8.2-alpine3.11 as build1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE conf.production.settings
ENV TZ Asia/Shanghai
RUN mkdir /djshop

# add china mirrors
RUN echo 'http://mirrors.aliyun.com/alpine/v3.11/community/'>/etc/apk/repositories
RUN echo 'http://mirrors.aliyun.com/alpine/v3.11/main/'>>/etc/apk/repositories

# install psycopg2-binary
RUN apk update \
    && apk add tzdata \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install -U pip setuptools -i https://mirrors.aliyun.com/pypi/simple/ \
    && pip install psycopg2-binary -i https://mirrors.aliyun.com/pypi/simple/ \
    && apk del build-deps

# install requirements and copy code
COPY requirements.txt /djshop
RUN pip install -r /djshop/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

FROM python:3.8.2-alpine3.11
COPY --from=build1 / /
COPY . /djshop
WORKDIR /djshop
COPY ./wait-for /bin/wait-for
