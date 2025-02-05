# 📌 Backend API with NestJS, PostgreSQL, and Apache Airflow (Dockerized)

## 🏗️ Tech Stack
- **Backend:** NestJS (TypeScript)
- **Database:** PostgreSQL
- **Workflow Manager:** Apache Airflow
- **Containerization:** Docker & Docker Compose
- **Environment:** Node.js 18+

---

## 📦 1. Installation & Setup

### 🛠 Prerequisites
Make sure you have installed:
- [Node.js](https://nodejs.org/en) (v18 or later)
- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/)

### 📥 Clone Repository
```bash
git clone https://github.com/iniarif/order-service.git
cd order-service
```

### ⚙️ Setup Environment
Create a `.env` file based on `.env.example` and configure the environment variables.

```bash
cp .env.example .env
```

Adjust the **database** and **Airflow** configuration.

```ini
# Backend Config
NODE_ENV=development
PORT=3000

# Database Config
DB_HOST=db
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=mydatabase

# Airflow Config
AIRFLOW_URL=http://localhost:8080
```

---

## 🚀 2. Running the Application with Docker

Use **Docker Compose** to start all services.

```bash
docker-compose up -d
```

This will start:
1. **Backend API** (NestJS)
2. **PostgreSQL** (Database)
3. **Apache Airflow** (Workflow Scheduler)

Check if all containers are running:
```bash
docker ps
```

---

## 🔧 3. Project Structure
```plaintext
order-service/
│── src/                # Main NestJS code
│   ├── modules/        # Application modules
│   ├── controllers/    # API Controllers
│   ├── services/       # Business logic
│   ├── entities/       # Database Entities (TypeORM)
│   ├── config/         # Application Configuration
│   ├── main.ts         # NestJS Entry Point
│── dags/               # Airflow DAGs (Workflow)
│── docker/             # Docker Configuration
│── .env.example        # Environment Variables Example
│── docker-compose.yml  # Docker Compose File
│── package.json        # Dependencies
│── README.md           # Documentation
```

---

## 🏗️ 4. Docker Compose Configuration
The `docker-compose.yml` file manages the main services:

```yaml
version: '3.8'
services:
  backend:
    build: .
    container_name: nestjs_api
    ports:
      - "3000:3000"
    depends_on:
      - db
    env_file: .env
    networks:
      - app-network

  db:
    image: postgres:15
    container_name: postgres_db
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: mydatabase
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  airflow:
    image: apache/airflow:2.6.2
    container_name: airflow_scheduler
    restart: always
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://postgres:password@db:5432/mydatabase
    ports:
      - "8080:8080"
    depends_on:
      - db
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
```

---

## 🛠 5. Running & Using the Application

### 🎯 5.1 Backend API (NestJS)
Check if the backend is running correctly:
```bash
docker logs nestjs_api -f
```
Check the API in the browser or Postman:
```
http://localhost:3000/api
```

### 🎯 5.2 Database (PostgreSQL)
Check database connection:
```bash
docker exec -it postgres_db psql -U postgres -d mydatabase
```

### 🎯 5.3 Apache Airflow
Access the Airflow UI at:
```
http://localhost:8080
```
Default login credentials:
- **Username:** `airflow`
- **Password:** `airflow`

---

## 📌 6. API Endpoint
| Method | Endpoint     | Description       |
|--------|-------------|------------------|
| POST   | `/api/orders` | Create a new order |

Use **Postman** or **cURL** to test the API.

---

## 📌 7. Troubleshooting

### ❗ `Port already in use` Issue
Stop any process using port `3000`, `5432`, or `8080`:
```bash
sudo lsof -i :3000
kill -9 <PID>
```

### ❗ Database Connection Error
Check if the database is running:
```bash
docker logs postgres_db
```

### ❗ Airflow Not Accessible
Restart Airflow:
```bash
docker-compose restart airflow
```

---

## 🎯 8. Contributors & License
✍️ **Created by:** [Your Name](https://github.com/iniarif)  
📜 **License:** MIT License  
📧 **Contact:** your.email@example.com

🔥 Happy Coding! 🚀

