## 第一次启动系统
    1. 安装python3
    2. 在有requirements.txt的目录下运行
    ```pip install -r requirements.txt```
    3. `python manage.py db init`
       `python manage.py db migrate`
       `python manage.py db upgrade`
       `python manage.py init_admin`
       `python manage.py init`
    4. `python run.py`