import boto3
from botocore.exceptions import ClientError
from app.config import settings
from app.storage.media_storage_interface import IMediaStorage

class S3MediaStorage(IMediaStorage):
    def __init__(self):
        # Configurazione client S3
        # Se siamo in LocalStack, endpoint_url sarà valorizzato
        self.s3_client = boto3.client(
            's3',
            region_name=settings.AWS_REGION,
            endpoint_url=settings.AWS_ENDPOINT_URL # Fondamentale per LocalStack
            # Nota: Le credenziali vengono prese automaticamente dalle var d'ambiente standard AWS_ACCESS_KEY_ID
        )
        self.bucket_name = settings.S3_MEDIA_BUCKET

    def store_media(self, file_name: str, file_data: bytes, content_type: str) -> str:
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=file_data,
                ContentType=content_type
                # ACL='public-read' (Opzionale, dipende dalle policy del bucket)
            )
            
            # Costruzione URL
            if settings.AWS_ENDPOINT_URL:
                # URL stile LocalStack: http://localstack:4566/bucket/key
                return f"{settings.AWS_ENDPOINT_URL}/{self.bucket_name}/{file_name}"
            else:
                # URL stile AWS Production: https://bucket.s3.region.amazonaws.com/key
                return f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_name}"

        except ClientError as e:
            print(f"S3 Upload Error: {e}")
            raise e

    def delete_media(self, storage_path: str):
        try:
            # Estrazione della Key dall'URL
            # Esempio URL: http://.../mybucket/folder/img.png -> Key: folder/img.png
            if self.bucket_name in storage_path:
                key = storage_path.split(f"{self.bucket_name}/")[-1]
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
        except ClientError as e:
            print(f"S3 Delete Error: {e}")
            pass