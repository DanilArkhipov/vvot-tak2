# ВВОТ задание 2
Архипов Данил 11-910

## Сервисные аккаунты необходимые для работы
- itis-2022-2023-vvot17-serverless-containers-invoker : serverless.containers.invoker
- itis-2022-2023-vvot17-face-cut-service-account : editor storage.viewer ydb.viewer container-registry.images.puller storage.uploader ydb.editor
- itis-2022-2023-vvot17-ai-vision-user : ai.vision.user
- itis-2022-2023-vvot17-face-detection-service-account : storage.viewer editor
- itis-2022-2023-vvot17-serverless-function-invoker : serverless.functions.invoker
- itis-2022-2023-vvot17-editor-service-account : editor
- itis-2022-2023-container-registry-images-puller : container-registry.images.puller
- itis-2022-2023-vvot17-boot-service-account : serverless.functions.invoker editor

## Бакеты
- itis-2022-2023-vvot17-photos
- itis-2022-2023-vvot17-photos

## Yandex Managed Service for YDB
- vvot17-db-photo-face
Для работы системы необходимо создать в базе данных таблицу photo-face с помощью скрипта:
CREATE TABLE photo_face (
    id String,
    photo_key String,
    face_key String,
    name String,
    PRIMARY KEY (id)
)

## Container Registry
- vvot17-container-registry

## Serverless Containers
- vvot17-face-cut установлен ервисный аккаунт itis-2022-2023-vvot17-face-cut-service-account, для аутентификации в boto3 используются статические ключи itis-2022-2023-vvot17-face-cut-service-account

## Cloud Functions
- vvot17-face-detection установлен ервисный аккаунт itis-2022-2023-vvot17-ai-vision-user, для аутентификации в boto3 используются статические ключи itis-2022-2023-vvot17-face-detection-service-account
- vvot17-boot установлен cервисный аккаунт itis-2022-2023-vvot17-boot-service-account, его же статические ключи используются для аутентификации boto3

## Триггеры
- vvot17-photo-trigger триггер создания объекта в бакете itis-2022-2023-vvot17-photos, вызывает функцию vvot17-face-detection, сервисный аккаунт 
itis-2022-2023-vvot17-serverless-function-invoker
- vvot17-task-trigger триггер получения сообщения в очереди vvot17-tasks, вызывает контейнер vvot17-face-cut, сервисные аккаунты: для очереди itis-2022-2023-vvot17-editor-service-account, для контейнера itis-2022-2023-vvot17-serverless-containers-invoker

## Message Queue
- vvot17-tasks

## API Gateway
- itis-2022-2023-vvot17-api
Спецификация: 
openapi: 3.0.0
info:
  title: Face Photo Api
  version: 1.0.0
servers:
- url: https://d5dr66gcjebi2sapbcvg.apigw.yandexcloud.net
paths:
  /face.jpg:
    get:
      x-yc-apigateway-integration:
        type: object_storage
        bucket: itis-2022-2023-vvot17-faces
        object: '{face}'
        error_object: error.html
        presigned_redirect: true
        service_account_id: ajeh5up8aaotm8spuro1
      parameters:
      - explode: true
        in: query
        name: face
        required: true
        schema:
          type: string
        style: form
      responses:
        '200':
          content:
            image/jpeg:
              schema:
                format: binary
                type: string
          description: OK
  /photo.jpg:
    get:
      x-yc-apigateway-integration:
        type: object_storage
        bucket: itis-2022-2023-vvot17-photos
        object: '{photo}'
        error_object: error.html
        presigned_redirect: true
        service_account_id: ajeh5up8aaotm8spuro1
      parameters:
      - explode: true
        in: query
        name: photo
        required: true
        schema:
          type: string
        style: form
      responses:
        '200':
          content:
            image/jpeg:
              schema:
                format: binary
                type: string
          description: OK
