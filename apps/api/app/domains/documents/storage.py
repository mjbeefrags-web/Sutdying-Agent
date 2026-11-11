from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit

from minio import Minio
from minio.error import MinioException, S3Error

from apps.api.app.core.config import get_settings


class StorageUnavailable(RuntimeError):
    pass


class ObjectStorage:
    def __init__(self) -> None:
        settings = get_settings()
        endpoint = urlsplit(settings.storage_endpoint_url)
        if endpoint.scheme not in {"http", "https"} or not endpoint.netloc:
            raise ValueError("STORAGE_ENDPOINT_URL must be an HTTP(S) endpoint.")
        if endpoint.path not in {"", "/"} or endpoint.query or endpoint.fragment:
            raise ValueError("STORAGE_ENDPOINT_URL cannot include a path, query, or fragment.")
        self._client = Minio(
            endpoint.netloc,
            access_key=settings.storage_access_key,
            secret_key=settings.storage_secret_key,
            secure=endpoint.scheme == "https",
            region=settings.storage_region,
        )
        self._bucket = settings.storage_bucket
        self._auto_create_bucket = settings.storage_auto_create_bucket

    def _ensure_bucket(self) -> None:
        try:
            if self._client.bucket_exists(self._bucket):
                return
            if not self._auto_create_bucket:
                raise StorageUnavailable("The configured document bucket does not exist.")
            self._client.make_bucket(self._bucket)
        except S3Error as exc:
            if exc.code in {"BucketAlreadyExists", "BucketAlreadyOwnedByYou"}:
                return
            raise StorageUnavailable("Document storage is unavailable.") from exc
        except MinioException as exc:
            raise StorageUnavailable("Document storage is unavailable.") from exc

    def put_file(self, object_key: str, file_path: Path, size_bytes: int) -> None:
        self._ensure_bucket()
        try:
            self._client.fput_object(
                self._bucket,
                object_key,
                str(file_path),
                length=size_bytes,
                content_type="application/pdf",
            )
        except (MinioException, OSError) as exc:
            raise StorageUnavailable("Document storage is unavailable.") from exc

    def get_bytes(self, object_key: str) -> bytes:
        try:
            response = self._client.get_object(self._bucket, object_key)
            try:
                return response.read()
            finally:
                response.close()
                response.release_conn()
        except (MinioException, OSError) as exc:
            raise StorageUnavailable("Document storage is unavailable.") from exc

    def delete(self, object_key: str) -> None:
        try:
            self._client.remove_object(self._bucket, object_key)
        except (MinioException, OSError) as exc:
            raise StorageUnavailable("Document storage is unavailable.") from exc


@lru_cache(maxsize=1)
def get_object_storage() -> ObjectStorage:
    return ObjectStorage()
