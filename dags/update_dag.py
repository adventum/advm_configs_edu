from datetime import timedelta, datetime

from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash_operator import BashOperator

default_args = {
    'owner': 'adventumpma',
    'depends_on_past': False,
    'start_date': datetime.fromisoformat(Variable.get("START_DATE")),
    'email': [i.strip() for i in Variable.get("EMAIL_RECIPIENTS").split(',')],
    'email_on_failure': True,
    # 'email_on_success': True,
    # 'email_on_retry': True,
    'retries': 1,
    'retries_delay': timedelta(minutes=5)
    }

dag = DAG(
    'update_dag',
    default_args=default_args,
    description='Update DAG',
    schedule_interval="30 3 * * *"
    )

work_directory = '/opt/advm_etl'

project = Variable.get("PROJECT_NAME")

project_bq_creds = Variable.get('PROJECT_BQ_CREDS')
project_bq_dataset = Variable.get('PROJECT_BQ_DATASET')
project_bq_adcost_table = Variable.get('PROJECT_BQ_ADCOST_TABLE')
project_bq_mediaplan_table = Variable.get('PROJECT_BQ_MEDIAPLAN_TABLE')
project_gcloud_storage_path = Variable.get('PROJECT_GCLOUD_STORAGE_PATH')
project_attribution_stages = Variable.get('PROJECT_ATTRIBUTION_STAGES')

project_bq_attribution_table = Variable.get('PROJECT_BQ_ATTRIBUTION_TABLE')
project_tableau_server = Variable.get('PROJECT_TABLEAU_SERVER')
project_tableau_login = Variable.get('PROJECT_TABLEAU_LOGIN')
project_tableau_pass = Variable.get('PROJECT_TABLEAU_PASS')


t0 = BashOperator(
    task_id='clear_fetch_folder',
    bash_command=f'(cd {work_directory};rm -rf fetch/*)',
    dag=dag
    )

t1 = BashOperator(
    task_id='update_and_truncate_stagings',
    bash_command=f'(cd {work_directory};python3 advm_etl.py {project} -S -I -T)',
    dag=dag
    )

t2 = BashOperator(
    task_id='update_and_truncate_raw',
    bash_command=f'(cd {work_directory};python3 advm_etl.py {project} -R -I -T)',
    dag=dag
    )

t3 = BashOperator(
    task_id='update_and_truncate_business',
    bash_command=f'(cd {work_directory};python3 advm_etl.py {project} -B -I -T -r ".*PIT")',
    dag=dag
    )

t4 = BashOperator(
    task_id='update_and_truncate_calc_full_union',
    bash_command=f'(cd {work_directory};python3 advm_etl.py {project} -B -I -T -r "Calc|Full|Union")',
    dag=dag
    )

t5 = BashOperator(
    task_id='fix_missing_fullgavisitstat',
    bash_command=f'(cd {work_directory};python3 advm_etl.py {project} -B -I -T -r '
                 f'"CalcAdSourceClear|CalcAdSourceDirtyUnion|CalcAdSourceDistinct|CalcAdSourcesDirty|FullGaVisitStat")',
    dag=dag
    )

t6 = BashOperator(
    task_id='update_and_truncate_graph',
    bash_command=f'(cd {work_directory};python3 advm_etl.py {project} -G -I -T)',
    dag=dag
    )

t7 = BashOperator(
    task_id='update_attribution',
    bash_command=f'(cd {work_directory};python3 attribution.py {project} {project_bq_creds} {project_bq_dataset} '
                 f'{project_bq_adcost_table} {project_bq_mediaplan_table} {project_gcloud_storage_path} '
                 f'--stages {project_attribution_stages})',
    dag=dag
    )

t8 = BashOperator(
    task_id='update_tableau',
    bash_command=f'(cd {work_directory};python3 tableau_updater.py {project} {project_bq_creds} {project_bq_dataset} '
                 f'{project_bq_attribution_table} {project_tableau_server} {project_tableau_login} '
                 f'{project_tableau_pass})',
    dag=dag
    )

t9 = BashOperator(
    task_id='update_and_truncate_stagings_for_click_fraud',
    bash_command=f"(cd  {work_directory};python3 advm_etl.py {project} -S -I -T -r 'Staging_.*_adcost' "
                 f"-s `date -d '-7day' +%Y-%m-%d` -e `date -d 'yesterday' +%Y-%m-%d`)",
    dag=dag
    )

t10 = BashOperator(
    task_id='update_and_truncate_raw_2',
    bash_command=f'(cd {work_directory};python3 advm_etl.py {project} -R -I -T)',
    dag=dag
    )


t0 >> t1 >> t2 >> t3 >> t4 >> t5 >> t6 >> t7 >> t8 >> t9 >> t10
