from airflow.providers.standard.operators.python import PythonOperator
from table import main
import sys
import os
from datetime import datetime, timedelta
from airflow import DAG

# Thêm thư mục dags vào sys.path để import được file table.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


default_args = {
    'owner': 'nguyen',
    'retries': 2,
    'description': 'airlfow lấy thông tin từ api thời tiết',
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='lay_du_lieu_thoi_tiet',
    default_args=default_args,
    start_date=datetime(2026, 7, 7),
    schedule=timedelta(hours=1),
    catchup=False,
    tags=['nguyen']
) as dag:
    task1 = PythonOperator(
        task_id='lay_du_lieu',
        python_callable=main
    )
