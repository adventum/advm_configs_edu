from datetime import timedelta, datetime

from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash_operator import BashOperator

default_args = {
    'owner': 'adventumpma',
    'depends_on_past': False,
    'start_date': datetime.fromisoformat(Variable.get("START_DATE")),
    'email': [i.strip() for i in Variable.get("EMAIL_RECIPIENTS").split(',')],
    'retries': 0,
    'retries_delay': timedelta(minutes=5),
    'email_on_failure': True,
    }

dag = DAG(
    'create_commands_dag',
    default_args=default_args,
    description='Create commands DAG',
    schedule_interval='@once'
)

work_directory = '/opt/advm_etl'

project = Variable.get("PROJECT_NAME")


t1 = BashOperator(
    task_id='create_commands_dag',
    bash_command=f'cd {work_directory};python3 commands_generator/commands_generate.py {project}',
    email_on_failure=True,
    email='v.mikhaylov@adventum.ru',
    dag=dag
)
