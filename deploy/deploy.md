# Инструкция по разворачиванию advm_etl, commands_ui, client_postgres 

Для запуска плейбука необходимо установить Ansible на свой компьютер. Ansible можно установить на компьютеры с Linux 
или MacOS. На компьютеры с Windows установить его нельзя, поэтому в этом случае необходим Linux-сервер с установленным 
Ansible, к которому можно подключиться и запустить нужные плейбуки.

В данной папке находится Ansible-плейбук *pb_deploy.yml*, который на сервере клиента разворачивает advm_etl, 
commands_ui, client_postgres, а так же настраивает их и серверное окружение.
 
## Порядок запуска:
1. Скопировать репозиторий на компьютер, с которого будет осуществлен запуск процесса развертки:  
   ```bash
   git clone https://github.com/adventum/advm_configs.git
   ```
     
2. Перейти в ветку клиента, предполагается что все нужные файлы модели для запуска и работы advm_etl уже есть в ветке 
   клиента

3. Для того чтобы запустить процесс развертывания софта на сервере клиента необходимо в папке клиента 
   создать три файла:
    * group_vars/CLIENT.yml (здесь вместо CLIENT нужно указать имя клиента)
    * deploy.sh
    * hosts.ini
    
    шаблоны этих файлов есть в папке *project_template* в ветке master. Файл *deploy.sh* нужно скопировать без каких либо 
    изменений.

4. Файл *hosts.ini* хранит параметры для запуска контейнеров и настройки окружения сервера. В файле *hosts.ini* есть 
   два раздела(см. пример) названия которых заключены в квадратные скобки([]). Первый должен 
   называться также как файл в *group_vars*(в шаблонах это *CLIENT*), второй -> название первого + *:vars*. В данном 
   файле надо задать следущие параметры:
    * Поменять IP-адрес на IP-адрес сервера клиента, указать ssh-порт в переменной *ansible_port*
    * В *airflow_image* указать необходимый тег docker-образа контейнера с airflow
    * В переменной *client_name* указать название клиента, должно совпадать с названием папки клиента в *advm_configs*
    * В переменной *data_base* указать используемую в *advm_etl* базу данных: *postgres* (если используется PostgreSQL), 
    *bq* (если используется Google BigQuery)
    * В переменной *local_advm_configs_dir* указать путь до директории *advm_configs* на локальной машине которая будет 
    скопирована на сервер
    * Указать значения параметров для контейнера с airflow
        - *airflow_container_name* - указать название контейнера с airflow 
        - *airflow_postgres_container_name* - название контейнера с базой для airflow
        - *airflow_port* - порт на котором будет доступен web интерфейс airflow
        - *advm_etl_log_level* - уровень логгирования advm_etl ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        - *advm_etl_logstash_logging* - отправлять ли логи в elk или нет, *true* - отправлять, иначе нет 
        - *airflow_smtp* - адрес smtp сервера будет использоваться для алертов от airflow
    * Указать значения параметров для контейнера с commands_ui
        - *commands_ui_container_name* - название контейнера с commands_ui
        - *commands_ui_image* - необходимый тег docker-образа контейнера с commands_ui
        - *commands_ui_postgres_user* - логин пользователя postgres
        - *commands_ui_db_name* - имя базы для commands_ui
        - *commands_ui_port* - порт на котором будет доступен web интерфейс commands_ui
        - *commands_ui_log_directory* - директория в которую commands_ui будет писать лог
        - *commands_ui_log_level* - уровень логгирования commands_ui(CRITICAL, ERROR, WARNING, INFO, DEBUG)
        - *commands_ui_logstash_logging* - отправлять ли логи в elk или нет, *true* - отправлять, иначе нет
    * При необходимости, указать значения параметров для контейнера с клиентским postgres  
        - *client_postgres_version* - версия postgres
        - *client_postgres_container_name* - название контейнера с клиенским postgres
        - *client_postgres_user* - имя создаваемого пользователя БД для клиенского postgres
        - *postgres_port* - порт сервера на котором будет доступна база с клиенским postgres
    * При необходимости, в переменной *postgres_shared_buffers_ratio* указать % от всей оперативной памяти сервера, 
    выделенный под Shared Buffers PostgreSQL
    * Указать переменные airflow

5. Файл *group_vars/CLIENT.yml* хранит секретные параметры, нужно скопировать *CLIENT.yml* и переименовать названием 
    клиента, также переименновать разделы в *hosts.ini*. В данном файле надо задать следущие параметры:
    * *ansible_user* - пользователь для доступа по SSH к серверу клиента   
    * *ansible_password* - пароль для доступа по SSH к серверу клиента
    * *ansible_sudo_pass* - sudo-пароль от сервера клиента (обычно такой же как ansible_password)
    * при необходимости, *dockerhub_pass* - пароль от DockerHub Adventum (если его меняли)
    * *postgreSQL_db_pass* - пароль пользователя бд для клиентского postgres  
    * *PROJECT_TABLEAU_PASS* - пароль пользователя табло
    * при необходимости, *SMTP_PASSWORD* - пароль от smtp сервера Adventum (если его меняли)
    * *airflow_pg_pass* - пароль пользователя бд для airflow
    * *airflow_admin_password* - пароль админа для авторизации в ui airflow
    * *commands_ui_pg_pass* - пароль пользователя бд для commands_ui
    * *commands_ui_secret_key* - рандомная строка, чем больше тем лучше            
    * *commands_ui_admin_pass* - пароль админа для авторизации в commands_ui
    * *logstash_ip_address* - ip адрес logstash, куда будут отправляться логи в elk
    * *logstash_port* - порт logstash, обязательно в кавычках иначе ansible будет ругаться ("5000")

   Открытие и редактирование файла *group_vars/CLIENT.yml*:
   ```bash
   ansible-vault edit group_vars/CLIENT.yml
   # Далее, ввести пароль (см. Teampass -> ansible-vault), отредактировать файл, сохранить
   ```
6. Запуск deploy.sh.
   Данный скрипт принимает все аргументы коммандной строки комманды *ansible-playbook*, в частности аргумент *--tags* 
   или *-t*. Данный аргумент принимает в качестве значения строку в которой мы можем передавать один или несколько 
   тегов перечисленных через запятую. Теги нужны для того чтобы можно было запускать разные наборы задач, для 
   нашего плейбука есть следующие теги:
   
        airflow - переустанавливает контейнер с airflow, все задачи из роли keybunch_airflow
            update_airflow - задачи перезапуска контейнеров airflow и commands_ui без создания баз и пользователей 
                             баз для airflow и commands_ui так как они выполняются один раз при первом запуске, 
                             если необходимо обновить и данные баз, то нужно удалить файлы баз и запустить деплой 
                             с тегом airflow
            commands_ui - задачи перезапуска контейнера commands_ui
        client_postgres - переустанавливает контейнер с клиентским постгресс, все задачи из роли clients_postgres
            update_client_postgres - задачи перезапуска контейнера client_postgres за исключением создания базы,
                                     создания пользователя и некоторых функций которые сохраняются в файлах базы 
                                     на диске
   
   При первом деплое софта на сервер нужно запускать *deploy.sh* без тегов, так как там выполняются дополнительные 
   задачи настройки окружения. 
  
   Пример запуска                 
   ```bash
   bash deploy.sh --tags "airflow,client_postgres" 
   ``` 
   Также можно передать аргумент *--list-tasks* для того чтобы получить список задач отфильтрованный согласно тегу
   ```bash
   bash deploy.sh --tags "airflow,client_postgres --list-tasks" 
   ``` 
   После запуска скрипт попросит ввести Vault password (см. Teampass -> ansible-vault).

   Скрипт в домашнем каталоге пользователя на сервере клиента создаст папку *advm_configs*, в которую уже должны быть
   скопированны все необходимые файлы если все было настроено правильно.   

   Если используется БД PostgreSQL, то так же в домашнем каталоге будет создан файл *pg_server.json*. Это креденшалсы 
   для подключения к созданной и настроенной клиентской БД PostgreSQL. 
   Этот файл нужно будет переместить в папку креденшаласов проекта.