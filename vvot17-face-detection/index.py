import json
import boto3
import io
import requests
import base64


def handler(event, context):
    token = context.token['access_token']

    faces = get_faces(event, token)
    send_faces_to_queue(faces)

    return {
        'statusCode': 200,
        'body': ''
    }


def get_faces(event, token):
    session = boto3.session.Session(region_name='ru-central1')
    s3 = session.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net')

    bucket_id = event['messages'][0]['details']['bucket_id']
    object_id = event['messages'][0]['details']['object_id']

    image_bytes = io.BytesIO()
    s3.download_fileobj(bucket_id, object_id, image_bytes)

    image_base64 = base64.b64encode(image_bytes.getvalue())
    request_params = {
        "folderId": "b1g9qfipo2vd2oujpcjv",
        "analyze_specs": [{
            "content": image_base64.decode(),
            "features": [{
                "type": "FACE_DETECTION"
            }]
        }]
    }

    headers = {'Authorization': 'Bearer ' + token}
    yandex_vision_url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'

    response = requests.post(
        url=yandex_vision_url,
        headers=headers,
        json=request_params)

    content = json.loads(response.content.decode())

    faces = content['results'][0]['results'][0]['faceDetection']['faces']

    faces_result_objects = []
    for face in faces:
        face_coordinates = face['boundingBox']['vertices']
        face_rectangle = {
                             'top_left': {'point_coordinates': face_coordinates[0]},
                             'bottom_left': {'point_coordinates': face_coordinates[1]},
                             'bottom_right': {'point_coordinates': face_coordinates[2]},
                             'top_right': {'point_coordinates': face_coordinates[3]},
                         },
        face_result_map = {'photo_object_key': object_id, 'face_rectangle': face_rectangle}
        faces_result_objects.append(face_result_map)

    return faces_result_objects


def send_faces_to_queue(faces):
    session = boto3.session.Session()
    queue = session.client(
        service_name='sqs',
        endpoint_url='https://message-queue.api.cloud.yandex.net',
        region_name='ru-central1')

    for face in faces:
        body = json.dumps(face)

        queue.send_message(
            QueueUrl='https://message-queue.api.cloud.yandex.net/b1g71e95h51okii30p25/dj600000000b17jj02mk/vvot17-tasks',
            MessageBody=body,
        )
