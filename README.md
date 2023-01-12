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
