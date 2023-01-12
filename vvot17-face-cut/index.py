import io
import json
import os
import uuid

from PIL import Image
from sanic import Sanic, empty

import boto3
import ydb
import ydb.iam

END_POINT = 'grpcs://ydb.serverless.yandexcloud.net:2135'
DATA_BASE = '/ru-central1/b1g71e95h51okii30p25/etnbjvokdu8nmvvl36ef'
PHOTO_BUCKET = 'itis-2022-2023-vvot17-photos'
FACE_BUCKET = 'itis-2022-2023-vvot17-faces'


app = Sanic(__name__)

ydb_driver: ydb.Driver

PORT = os.getenv('PORT')


@app.after_server_start
async def after_server_start(app, loop):
    global ydb_driver
    ydb_driver = init_db_connection()
    ydb_driver.wait(timeout=5)


@app.post("/")
async def index(request):
    face_data = json.loads(request.json['messages'][0]['details']['message']['body'])
    face = get_face(face_data)
    face_id = save_face(face)
    save_data_to_db(face_id, face_data['photo_object_key'])

    return empty(status=200)


@app.after_server_stop
async def shutdown():
    ydb_driver.close()


def init_db_connection():
    endpoint = END_POINT
    path = DATA_BASE
    credentials = ydb.iam.MetadataUrlCredentials()
    driver_config = ydb.DriverConfig(
        endpoint, path, credentials=credentials
    )

    return ydb.Driver(driver_config)


def get_photo(photo_key):
    session = boto3.session.Session()
    s3 = session.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net'
    )

    print('Запрос фотки')
    response = s3.get_object(
        Bucket=PHOTO_BUCKET,
        Key=photo_key
    )
    print('Получили фотку')
    print(response)

    return response['Body'].read()


def get_face(face_data):
    photo_bytes = get_photo(face_data['photo_object_key'])
    print('Вырезаем лицо')
    image = Image.open(io.BytesIO(photo_bytes))
    face_rectangle = face_data['face_rectangle'][0]

    return image.crop((
        int(face_rectangle['top_left']['point_coordinates']['x']),
        int(face_rectangle['top_left']['point_coordinates']['y']),
        int(face_rectangle['bottom_right']['point_coordinates']['x']),
        int(face_rectangle['bottom_right']['point_coordinates']['y'])))


def save_face(face):
    face_bytes = io.BytesIO()
    face.save(face_bytes, format='JPEG')
    face_id = uuid.uuid4()

    print('Сохраняем лицо')
    session = boto3.session.Session()
    s3 = session.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net'
    )

    s3.put_object(
        Body=face_bytes.getvalue(),
        Bucket=FACE_BUCKET,
        Key=str(face_id) + '.jpg',
        ContentType='application/octet-stream'
    )
    print('Сохранили')
    return face_id


def save_data_to_db(face_id, photo_key):
    query = f"""
    PRAGMA TablePathPrefix("{DATA_BASE}");
    INSERT INTO photo_face (id, photo_key, face_key, name)
    VALUES ('{face_id}', '{photo_key}', '{face_id}.jpg', null);
    """

    print("Добавляем запись в БД")
    session = ydb_driver.table_client.session().create()
    session.transaction().execute(query, commit_tx=True)
    session.closing()

    print("Добавили")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(PORT), motd=False, access_log=False)