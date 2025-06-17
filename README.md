# hrstreamline
A Human Resource Management System (HRMS) designed to streamline core HR processes and improve employee management within organizations. This system focuses on managing employee data, tracking leave requests, and automating essential HR tasks to enhance operational efficiency and employee experience.


## Installation & Setup

### 1. Clone the Repository
```sh
git clone https://github.com/dthatprince/hrstreamline.git
cd hrstreamline
```

### 2. Create & Activate Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Run the Application
```sh
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5. Run the Application
```sh
flask --app app --debug run
```

The application will run at **`http://127.0.0.1:5000/`**




# Start the app with Docker Compose
```bash: 
docker-compose up --build
```
The app will be available at: http://localhost:5000


# Manual Development
### Start Redis (locally):
```bash: 
redis-server
```
### Start Celery Worker:
```bash: 
celery -A celery_worker.celery worker --loglevel=info
```
### Start Celery Beat:
```bash: 
celery -A celery_worker.celery beat --loglevel=info
```
### Or combined:
```bash: 
celery -A celery_worker.celery worker --beat --loglevel=info
```

