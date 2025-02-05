# airflow/dags/order_analytics_dag.py
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import psycopg2

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def extract_transform_load():
    # Koneksi ke PostgreSQL
    conn = psycopg2.connect(
        host="host.docker.internal",           # Sesuaikan dengan host database Anda
        database="postgres",        # Nama database
        user="postgres",            # Username
        password="password"         # Password
    )
    cur = conn.cursor()
    
    # 1. Buat tabel untuk menyimpan laporan analitik jika belum ada
    cur.execute("""
        CREATE TABLE IF NOT EXISTS product_performance (
            product VARCHAR(255),
            order_count INTEGER,
            total_sales NUMERIC,
            avg_sales NUMERIC,
            report_date DATE DEFAULT CURRENT_DATE
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_trends (
            order_date DATE,
            daily_orders INTEGER,
            daily_sales NUMERIC
        );
    """)
    conn.commit()
    
    # 2. Extract & Transform: Analisis performa produk
    performance_query = """
        SELECT product, COUNT(*) AS order_count, SUM(amount) AS total_sales, AVG(amount) AS avg_sales
        FROM "order"
        GROUP BY product;
    """
    cur.execute(performance_query)
    performance_results = cur.fetchall()
    
    print("Product Performance Report:")
    # Hapus data lama untuk report hari ini (jika ada)
    cur.execute("DELETE FROM product_performance WHERE report_date = CURRENT_DATE;")
    for row in performance_results:
        product, order_count, total_sales, avg_sales = row
        print(f"Product: {product}, Orders: {order_count}, Total Sales: {total_sales}, Avg Sales: {avg_sales}")
        # Insert hasil analitik ke tabel product_performance
        cur.execute("""
            INSERT INTO product_performance (product, order_count, total_sales, avg_sales, report_date)
            VALUES (%s, %s, %s, %s, CURRENT_DATE);
        """, (product, order_count, total_sales, avg_sales))
    conn.commit()
    
    # 3. Extract & Transform: Analisis tren harian
    trends_query = """
        SELECT DATE(created_at) AS order_date, COUNT(*) AS daily_orders, SUM(amount) AS daily_sales
        FROM "order"
        GROUP BY order_date
        ORDER BY order_date;
    """
    cur.execute(trends_query)
    trends_results = cur.fetchall()
    
    print("Daily Trends Report:")
    # Hapus data lama dari tabel daily_trends (opsional, tergantung kebutuhan)
    cur.execute("DELETE FROM daily_trends;")
    for row in trends_results:
        order_date, daily_orders, daily_sales = row
        print(f"Date: {order_date}, Daily Orders: {daily_orders}, Daily Sales: {daily_sales}")
        # Insert hasil tren harian ke tabel daily_trends
        cur.execute("""
            INSERT INTO daily_trends (order_date, daily_orders, daily_sales)
            VALUES (%s, %s, %s);
        """, (order_date, daily_orders, daily_sales))
    conn.commit()
    
    # Tutup koneksi
    cur.close()
    conn.close()

with DAG('order_analytics_dag',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dag:

    etl_task = PythonOperator(
        task_id='extract_transform_load',
        python_callable=extract_transform_load
    )
