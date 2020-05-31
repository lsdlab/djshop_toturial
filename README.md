# djshop

![Language](https://img.shields.io/badge/language-Python-blue.svg?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)

电商系统后端 API

- Python 3.8.2
- PostgreSQL 12.1
- Redis 5.0.7
- rabbitmq 3.8.2
- django 3.0
- django-rest-framework 3.10.3
- celery 4.3.0

## PostgreSQL

**创建数据库/用户**

```sql
CREATE USER djshop_development WITH PASSWORD 'djshop_development';
GRANT ALL PRIVILEGES ON DATABASE djshop_development to djshop_development;
ALTER DATABASE djshop_development OWNER TO djshop_development;
```

## celery with rabbitmq as broker

**rabbitmq 配置**

```shell
sudo rabbitmqctl add_user djshop Ae2V6v7FzrR9UWyANQJR
sudo rabbitmqctl set_user_tags djshop administrator
sudo rabbitmqctl set_permissions -p / djshop ".*" ".*" ".*"
```

**celery flower 监控**

```shell
flower -A apps.celeryconfig --basic_auth=Ae2V6v7FzrR9UWyANQJR:Ae2V6v7FzrR9UWyANQJR
```

**cloc 统计代码行数**

```shell
cloc --exclude-lang=JavaScript,CSS .
```

## pytest 单元测试

python manage.py test -v 2

## django_extension 生成 model er 图

```shell
python manage.py graph_models -a -g -X TimestampedModel -o er.png
```

## 生产环境

- debian or ubuntu, 1c2g machine is the minimum setup
- PostgreSQL 12.2
- Redis 5.0.8
- rabbitmq 3.8.3
- Python 3.8.2
- nginx
- gunicorn
- redis for celery result backend
- rabbitmq for celery broker
- supervisor for manage gunicorn and celery process
- pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

生产环境配置在 `conf/production` 下，supervisor 以及 nginx 配置文件，修改复制到生产环境对应位置即可。
nginx 接受请求，gunicorn 转发，django 处理，supervisor 管理一个
gunicorn 以及两个 celery 进程，gunicorn worker 数量为 CPU 乘 2 加 1，celery worker 数量开到 4 个
