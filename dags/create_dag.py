from datetime import timedelta, datetime

from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator

default_args = {
    'owner': 'adventumpma',
    'depends_on_past': False,
    'start_date': datetime.fromisoformat(Variable.get("START_DATE")),
    'email': [i.strip() for i in Variable.get("EMAIL_RECIPIENTS").split(',')],
    'email_on_failure': True,
    'retries': 0,
    'retries_delay': timedelta(minutes=5)
    }

dag = DAG(
    'create_dag',
    default_args=default_args,
    description='Create DAG',
    schedule_interval='@once'
)

work_directory = '/opt/advm_etl'

project = Variable.get("PROJECT_NAME")

is_run = Variable.get("KEYBUNCH_DROP_ALL_TABLE")


t1 = BashOperator(
    task_id='create_all',
    bash_command=
    f'if [ "{is_run}" = "yes" ]; then\n'
    f'  cd {work_directory};python3 commands_executors/advm_etl.py {project} --airflow -C -S -R -B -G\n'
    f'else \n'
    f'  echo "ERROR! You are going to dropping all tales in project {project}, for this you should set '
    f'  KEYBUNCH_DROP_ALL_TABLE to yes"; exit 1\n'
    f'fi ',
    dag=dag,
)


def drop_keybunch_drop_all_table():
    Variable.set("KEYBUNCH_DROP_ALL_TABLE", "no")


t2 = PythonOperator(
    task_id='update_variable',
    python_callable=drop_keybunch_drop_all_table,
    dag=dag
)

t1 >> t2
