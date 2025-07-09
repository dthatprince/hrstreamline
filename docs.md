Mysql Server
host: localhost
user:
password: 
database: hrstreamlinedb








# Run Celery Services for Leave Balance Accrual
#### Terminal 1: Start Redis
```bash: 
redis-server
```

### Terminal 2: Start Celery worker
```bash: 
celery -A celery_worker.celery worker --loglevel=info
```

### Terminal 3: Start Celery Beat
```bash: 
celery -A celery_worker.celery beat --loglevel=info
```

### Or combine beat + worker:
```bash: 
celery -A celery_worker.celery worker --beat --loglevel=info
```



