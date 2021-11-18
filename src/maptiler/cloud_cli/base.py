import urllib.parse
import re

from uuid import UUID
from pathlib import Path
from time import sleep
from typing import Optional

import click
import requests


class URLGenerator:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def tiles_ingest(self) -> str:
        return urllib.parse.urljoin(self.base_url, "ingest")

    def tiles_ingest_detail(self, ingest_id: UUID) -> str:
        return urllib.parse.urljoin(self.base_url, f"ingest/{ingest_id}")

    def tiles_process(self, ingest_id: UUID) -> str:
        return f"{self.tiles_ingest_detail(ingest_id)}/process"

    def tiles_ingest_new(self, document_id: UUID) -> str:
        return urllib.parse.urljoin(self.base_url, f"{document_id}/ingest")


@click.group()
@click.option("--token", envvar="MAPTILER_TOKEN", type=str, required=True)
@click.pass_context
def cli(context: click.Context, token: str):
    api_session = requests.Session()
    api_session.headers.update({"Authorization": "Token {}".format(token)})
    context.obj = {"api_session": api_session}


@cli.group()
def tiles():
    pass


@tiles.command("ingest")
@click.option("--document-id", type=UUID)
@click.argument("container", type=Path)
@click.pass_context
def ingest_tiles(context: click.Context, document_id: Optional[UUID], container: Path):
    url_generator = URLGenerator("https://service.maptiler.com/v1/tiles/")
    http = context.obj["api_session"]

    if document_id is not None:
        request_url = url_generator.tiles_ingest_new(document_id)
    else:
        request_url = url_generator.tiles_ingest()

    click.echo("Starting")
    response = http.post(
        request_url,
        json={
            "size": container.stat().st_size,
            "filename": container.name,
        },
    )
    response.raise_for_status()
    response_data = response.json()
    upload_url = response_data["upload_url"]
    ingest_id = response_data["id"]
    task_url = url_generator.tiles_ingest_detail(ingest_id)
    process_url = url_generator.tiles_process(ingest_id)

    click.echo("Uploading")
    upload_file(container, upload_url)

    click.echo("Processing")
    http.post(process_url)
    response = http.get(task_url)
    response.raise_for_status()
    response_data = response.json()

    delay = 1
    while (
        response_data["status"] != "failed" and response_data["status"] != "completed"
    ):
        sleep(delay)
        if delay < 60:
            delay += 1
        response = http.get(task_url)
        response.raise_for_status()
        response_data = response.json()

    if response_data["status"] == "failed":
        click.echo("Ingest failed, errors:")
        for error in response_data["errors"]:
            click.echo(f"\t message: {error['message']}")
    elif response_data["status"] == "completed":
        click.echo("Finished")
        click.echo(response_data["document_id"])


def upload_file(file: Path, url: str):
    http = requests.Session()
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
            response = http.put(url, data=chunk, headers={"Content-Range": range})
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
                timeout = 2 ** retries
                sleep(timeout)
                retries += 1
                offset = None
                chunk = None
            else:
                response.raise_for_status()
