from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import logging
import psycopg2
from psycopg2.extras import execute_values

# Default arguments for DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Get database credentials from Airflow Variables (or use Airflow Connections)
DB_CONFIG = {
    'host': Variable.get("db_host", default_var="host.docker.internal"),
    'database': Variable.get("db_name", default_var="postgres"),
    'user': Variable.get("db_user", default_var="postgres"),
    'password': Variable.get("db_password", default_var="password"),
}

def get_db_connection():
    """Create a new database connection."""
    return psycopg2.connect(**DB_CONFIG)

def create_tables():
    """Ensure necessary tables exist."""
    queries = [
        """
        CREATE TABLE IF NOT EXISTS product_performance (
            product VARCHAR(255) PRIMARY KEY,
            order_count INTEGER,
            total_sales NUMERIC,
            avg_sales NUMERIC,
            report_date DATE DEFAULT CURRENT_DATE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS daily_trends (
            order_date DATE PRIMARY KEY,
            daily_orders INTEGER,
            daily_sales NUMERIC
        );
        """
    ]

    with get_db_connection() as conn, conn.cursor() as cur:
        for query in queries:
            cur.execute(query)
        conn.commit()

def fetch_query_results(query):
    """Fetch results from a given SQL query."""
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

def upsert_product_performance():
    """Extract, transform, and load product performance data."""
    query = """
        SELECT product, COUNT(*) AS order_count, SUM(amount) AS total_sales, AVG(amount) AS avg_sales
        FROM "order"
        GROUP BY product;
    """
    results = fetch_query_results(query)

    logging.info("Product Performance Report:")
    data = []
    for row in results:
        product, order_count, total_sales, avg_sales = row
        logging.info(f"Product: {product}, Orders: {order_count}, Total Sales: {total_sales}, Avg Sales: {avg_sales}")
        data.append((product, order_count, total_sales, avg_sales))

    if data:
        upsert_query = """
            INSERT INTO product_performance (product, order_count, total_sales, avg_sales, report_date)
            VALUES %s
            ON CONFLICT (product) DO UPDATE SET 
                order_count = EXCLUDED.order_count,
                total_sales = EXCLUDED.total_sales,
                avg_sales = EXCLUDED.avg_sales,
                report_date = CURRENT_DATE;
        """
        with get_db_connection() as conn, conn.cursor() as cur:
            execute_values(cur, upsert_query, data)
            conn.commit()

def upsert_daily_trends():
    """Extract, transform, and load daily trends data."""
    query = """
        SELECT DATE(created_at) AS order_date, COUNT(*) AS daily_orders, SUM(amount) AS daily_sales
        FROM "order"
        GROUP BY order_date
        ORDER BY order_date;
    """
    results = fetch_query_results(query)

    logging.info("Daily Trends Report:")
    data = []
    for row in results:
        order_date, daily_orders, daily_sales = row
        logging.info(f"Date: {order_date}, Daily Orders: {daily_orders}, Daily Sales: {daily_sales}")
        data.append((order_date, daily_orders, daily_sales))

    if data:
        upsert_query = """
            INSERT INTO daily_trends (order_date, daily_orders, daily_sales)
            VALUES %s
            ON CONFLICT (order_date) DO UPDATE SET 
                daily_orders = EXCLUDED.daily_orders,
                daily_sales = EXCLUDED.daily_sales;
        """
        with get_db_connection() as conn, conn.cursor() as cur:
            execute_values(cur, upsert_query, data)
            conn.commit()

def extract_transform_load():
    """Main ETL function to run all steps."""
    logging.info("Starting ETL Process")
    create_tables()
    upsert_product_performance()
    upsert_daily_trends()
    logging.info("ETL Process Completed Successfully")

# Define DAG
with DAG('order_analytics_dag',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dag:

    etl_task = PythonOperator(
        task_id='extract_transform_load',
        python_callable=extract_transform_load
    )
