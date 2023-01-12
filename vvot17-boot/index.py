import os
import ydb
import ydb.iam
import json
import requests
import six


def init_db_connection():
    endpoint = END_POINT
    path = DATA_BASE
    credentials = ydb.iam.MetadataUrlCredentials()
    driver_config = ydb.DriverConfig(
        endpoint, path, credentials=credentials
    )

    return ydb.Driver(driver_config)


def get_unnamed_face(chat_id):
    query = f"""
    PRAGMA TablePathPrefix("{DATA_BASE}");
    SELECT * FROM photo_face WHERE name is NULL LIMIT 1;
    """
    session = driver.table_client.session().create()
    result = session.transaction().execute(query, commit_tx=True)
    session.closing()
    print(result)

    for row in result[0].rows:
        face_key = row.face_key.decode("utf-8")
        photo_url = GATEWAY_PREFIX + '/face.jpg/?face=' + face_key
        send_photo(chat_id, photo_url)


def set_name_to_photo(name):
    query = f"""
        PRAGMA TablePathPrefix("{DATA_BASE}");
        SELECT * FROM photo_face WHERE name is NULL LIMIT 1;
        """
    session = driver.table_client.session().create()
    result_sets = session.transaction().execute(query, commit_tx=True)

    face_key = ''
    for row in result_sets[0].rows:
        face_key = row.face_key.decode("utf-8")
    if face_key == '':
        return

    query = f"""
    PRAGMA TablePathPrefix("{DATA_BASE}");
    UPDATE photo_face SET name = '{name}' WHERE face_key = '{face_key}';
    """
    session.transaction().execute(query, commit_tx=True)
    session.closing()


def find(chat_id, name):
    query = f"""
    PRAGMA TablePathPrefix("{DATA_BASE}");
    SELECT DISTINCT photo_key, name FROM photo_face WHERE name = '{name}';
    """
    session = driver.table_client.session().create()
    result_sets = session.transaction().execute(query, commit_tx=True)
    session.closing()

    if len(result_sets[0].rows) == 0:
        send_message(chat_id, f'Нет фотографии с именем {name}')
    for row in result_sets[0].rows:
        photo_key = row.photo_key.decode("utf-8")
        photo_url = GATEWAY_PREFIX + '/photo.jpg/?photo=' + photo_key
        send_photo(chat_id, photo_url)


def handler(event, context):
    global TOKEN
    global GATEWAY_PREFIX
    global OBJECT_LINK_TEMPLATE
    global END_POINT
    global DATA_BASE
    global driver

    TOKEN = os.getenv("TG_TOKEN")

    GATEWAY_PREFIX = 'https://d5dr66gcjebi2sapbcvg.apigw.yandexcloud.net'
    OBJECT_LINK_TEMPLATE = os.getenv("OBJECT_LINK_TEMPLATE")
    END_POINT = 'grpcs://ydb.serverless.yandexcloud.net:2135'
    DATA_BASE = '/ru-central1/b1g71e95h51okii30p25/etnbjvokdu8nmvvl36ef'

    driver = init_db_connection()
    driver.wait(timeout=5)

    body = json.loads(event['body'])
    chat_id = body['message']['from']['id']
    command = body['message']['text']

    print(f'body: {body}')
    print(f'command: {command}')

    if command == '/start':
        send_message(chat_id, 'Bot started')
        return
    if command == '/getface':
        get_unnamed_face(chat_id)
        return
    if command.startswith('/find'):
        args = command.split(' ')
        find(chat_id, args[1])
        return

    set_name_to_photo(command)
    send_message(chat_id, f'Добавлено новое имя {command}')


def send_message(chat_id, text):
    url = 'https://api.telegram.org/bot' + TOKEN + '/' + 'sendMessage'
    data = {'chat_id': chat_id, 'text': text}
    requests.post(url, data=data)


def send_photo(chat_id, photo):
    url = 'https://api.telegram.org/bot' + TOKEN + '/' + 'sendPhoto'
    print(f'url: {url}')
    data = {'chat_id': chat_id, 'photo': photo}
    requests.post(url, data=data)