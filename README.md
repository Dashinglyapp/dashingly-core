This is a minimal and work-in-progress version of [Realize](http://www.realize.pe).

Setup:

```
cd realize-core
sudo xargs -a apt-packages.txt apt-get install
pip install -r requirements.txt
alembic upgrade head
python setup.py
```

Usage:

```
python app.py
```

Run migrations:

```
alembic revision --autogenerate -m "MESSAGE HERE"
```