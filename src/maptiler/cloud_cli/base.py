import io
import re
from dataclasses import dataclass
from operator import attrgetter
from pathlib import Path
from time import sleep
from typing import Optional, Union
from urllib.parse import urljoin
from uuid import UUID

import click
import requests
import urllib3


@dataclass
class Error:
    message: str


@dataclass
class GoogleDriveUpload:
    url: str


@dataclass
class S3UploadPart:
    part_id: int
    url: str


@dataclass
class S3Upload:
    part_size: int
    parts: list[S3UploadPart]


@dataclass
class S3UploadResultPart:
    part_id: int
    etag: str


@dataclass
class S3UploadResult:
    parts: list[S3UploadResultPart]


@dataclass
class IngestResponse:
    id: UUID
    document_id: UUID
    state: str
    upload: Union[S3Upload, GoogleDriveUpload, None]
    errors: list[Error]


class ClientError(Exception):
    status_code: int
    errors: list[Error]

    def __init__(self, status_code: int, errors: list[Error]):
        self.status_code = status_code
        self.errors = errors


class Client:
    base_url: str
    session: requests.Session

    def __init__(self, token: str, base_url: Optional[str] = None):
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        if base_url is None:
            self.base_url = "https://service.maptiler.com"
        else:
            self.base_url = base_url.rstrip("/")

        retries = Retry(total=10, backoff_factor=0.5)
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Token {token}"})
        self.session.mount(self.base_url, HTTPAdapter(max_retries=retries))

    def check(self, response: requests.Response):
        if response.ok:
            return
        if 400 <= response.status_code < 500:
            data = response.json()
            errors = [Error(message=item["message"]) for item in data["errors"]]
        else:
            errors = [Error("Internal server error")]
        raise ClientError(response.status_code, errors)

    def ingest_response(self, data: dict) -> IngestResponse:
        if data.get("upload") is None:
            upload_url = data.get("upload_url")
            if upload_url is not None:
                upload = GoogleDriveUpload(url=upload_url)
            else:
                upload = None
        elif data["upload"]["type"] == "s3_multipart":
            upload = S3Upload(
                part_size=data["upload"]["part_size"],
                parts=[
                    S3UploadPart(part_id=item["part_id"], url=item["url"])
                    for item in data["upload"]["parts"]
                ],
            )
        elif data["upload"]["type"] == "google_drive_resumable":
            upload = GoogleDriveUpload(url=data["upload"]["url"])
        else:
            raise RuntimeError("Unknown upload type", data["upload"]["type"])

        if data.get("errors"):
            errors = [Error(item["message"]) for item in data["errors"]]
        else:
            errors = []

        return IngestResponse(
            id=UUID(data["id"]),
            document_id=UUID(data["document_id"]),
            state=data["state"],
            upload=upload,
            errors=errors,
        )

    def create_ingest(
        self, filename: str, size: int, document_id: Optional[UUID]
    ) -> IngestResponse:
        if document_id is None:
            url = urljoin(self.base_url, "/v1/tiles/ingest")
        else:
            url = urljoin(self.base_url, f"/v1/tiles/{document_id}/ingest")

        response = self.session.post(
            url,
            json={
                "filename": filename,
                "size": size,
                "supported_upload_types": [
                    "s3_multipart",
                    "google_drive_resumable",
                ],
            },
        )
        self.check(response)
        return self.ingest_response(response.json())

    def ingest(self, ingest_id: UUID) -> IngestResponse:
        response = self.session.get(
            urljoin(self.base_url, f"/v1/tiles/ingest/{ingest_id}")
        )
        self.check(response)
        return self.ingest_response(response.json())

    def process_ingest(
        self, ingest_id: UUID, upload_result: Optional[S3UploadResult]
    ) -> IngestResponse:
        if upload_result is None:
            json = None
        else:
            json = {
                "upload_result": {
                    "type": "s3_multipart",
                    "parts": [
                        {
                            "part_id": item.part_id,
                            "etag": item.etag,
                        }
                        for item in upload_result.parts
                    ],
                }
            }

        response = self.session.post(
            urljoin(self.base_url, f"/v1/tiles/ingest/{ingest_id}/process"),
            json=json,
        )
        self.check(response)
        return self.ingest_response(response.json())


@click.group()
@click.option("--token", type=str, envvar="MAPTILER_TOKEN", required=True)
@click.option("--base-url", type=str, hidden=True)
@click.pass_context
def cli(context: click.Context, token: str, base_url: str):
    context.obj = Client(token=token, base_url=base_url)


@cli.group()
def tiles():
    pass


@tiles.command("ingest")
@click.option("--document-id", type=UUID)
@click.argument("container", type=Path)
@click.pass_context
def ingest_tiles(context: click.Context, document_id: Optional[UUID], container: Path):
    client: Client = context.obj

    click.echo("Starting")
    try:
        ingest = client.create_ingest(
            filename=container.name,
            size=container.stat().st_size,
            document_id=document_id,
        )
    except ClientError as ex:
        click.echo("Could not create ingest", err=True)
        for error in ex.errors:
            click.echo(error.message, err=True)
        raise click.Abort()

    click.echo("Uploading")
    if isinstance(ingest.upload, S3Upload):
        upload_result = upload_to_s3(container, ingest.upload)
    elif isinstance(ingest.upload, GoogleDriveUpload):
        upload_to_google_drive(container, ingest.upload.url)
        upload_result = None
    else:
        raise RuntimeError

    click.echo("Processing")
    try:
        ingest = client.process_ingest(ingest.id, upload_result)
    except ClientError as ex:
        click.echo("Could not start processing", err=True)
        for error in ex.errors:
            click.echo(error.message, err=True)
        raise click.Abort()

    delay = 5
    while ingest.state not in {"completed", "canceled", "failed"}:
        sleep(delay)
        if delay < 60:
            delay += 1
        ingest = client.ingest(ingest.id)

    if ingest.state == "completed":
        click.echo("Finished")
        click.echo(ingest.document_id)
    elif ingest.state == "canceled":
        click.echo("Canceled")
    elif ingest.state == "failed":
        click.echo("Failed", err=True)
        for error in ingest.errors:
            click.echo(error.message, err=True)
        raise click.Abort()


def upload_to_s3(file: Path, upload: S3Upload) -> S3UploadResult:
    from urllib3.util.retry import Retry

    # The requests library does not work with body iterator.
    http = urllib3.PoolManager(retries=Retry(total=5, backoff_factor=0.5))

    parts = []
    file_size = file.stat().st_size
    buffer = memoryview(bytearray(8 * 1024 * 1024))

    def read(length: int):
        while length > 0:
            if length >= len(buffer):
                target = buffer
            else:
                target = buffer[:length]

            num_read = fp.readinto(target)
            yield target[:num_read]
            length -= num_read

    with file.open("rb") as fp:
        for part in sorted(upload.parts, key=attrgetter("part_id")):
            lower = (part.part_id - 1) * upload.part_size
            upper = min(lower + upload.part_size, file_size)
            length = upper - lower

            fp.seek(lower)

            response = http.request(
                method="PUT",
                url=part.url,
                headers={"Content-Length": str(length)},
                body=read(length),
            )
            if response.status >= 400:
                raise RuntimeError(response.status, response.read())

            parts.append(
                S3UploadResultPart(part_id=part.part_id, etag=response.headers["ETag"])
            )

    return S3UploadResult(parts=parts)


def upload_to_google_drive(file: Path, url: str):
    session = requests.Session()
    file_size = file.stat().st_size
    chunk_size = 10 * 1024 * 1024
    with file.open("rb") as fp:
        retries = 0
        offset = 0
        chunk = fp.read(chunk_size)
        while True:
            if chunk is not None:
                range = "bytes {}-{}/{}".format(
                    offset, offset + len(chunk) - 1, file_size
                )
            else:
                range = "bytes */{}".format(file_size)
            response = session.put(url, data=chunk, headers={"Content-Range": range})
            if response.status_code in {200, 201}:
                return
            elif response.status_code == 308:
                retries = 0
                match = re.fullmatch(r"bytes=\d+-(\d+)", response.headers["Range"])
                offset = int(match.group(1)) + 1
                fp.seek(offset)
                chunk = fp.read(chunk_size)
            elif response.status_code == 403 or response.status_code >= 500:
                if retries > 5:
                    response.raise_for_status()
                timeout = 2**retries
                sleep(timeout)
                retries += 1
                offset = None
                chunk = None
            else:
                response.raise_for_status()
