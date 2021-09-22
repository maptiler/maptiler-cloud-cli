import uuid

import pytest
import requests

from click.testing import CliRunner

from maptiler.cloud_cli.cli import ingest_tiles, URLGenerator


class MockedCliRunner(CliRunner):
    def __init__(self, session, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)

    def invoke(self, *args, **kwargs):
        return super().invoke(obj={"api_session": self.session}, *args, **kwargs)


class TestUploadCLI:
    ingest_id = uuid.uuid4()
    document_id = uuid.uuid4()
    upload_url = "https://upload_to.foo"
    url_generator = URLGenerator("https://service.maptiler.com/v1/tiles/")

    @pytest.fixture(scope="session")
    def cli_runner(self, requests_session):
        cli_runner = MockedCliRunner(requests_session)
        return cli_runner

    @pytest.fixture(scope="session")
    def dummy_file(self, cli_runner):
        with cli_runner.isolated_filesystem():
            with open("test.mbtiles", "w") as f:
                f.write("Bar")
            yield "test.mbtiles"

    @pytest.fixture(scope="session")
    def requests_session(self):
        import requests_mock

        api_session = requests.Session()
        api_session.headers.update({"Authorization": "Token Foo"})
        with requests_mock.Mocker(session=api_session) as session_mock:
            session_mock.post(
                self.url_generator.tiles_ingest(),
                json={"upload_url": self.upload_url, "id": str(self.ingest_id)},
                status_code=200,
            )
            session_mock.post(
                self.url_generator.tiles_ingest_new(self.document_id),
                json={"upload_url": self.upload_url, "id": str(self.ingest_id)},
                status_code=200,
            )
            session_mock.get(
                self.url_generator.tiles_process(self.ingest_id),
                status_code=200,
            )
            session_mock.get(
                self.url_generator.tiles_ingest_detail(self.ingest_id),
                json={"status": "completed", "progress": 100},
                status_code=200,
            )
            yield api_session

    def test_success_ingest_no_document_id(self, cli_runner, requests_mock,
                                           dummy_file):
        requests_mock.put(
            self.upload_url,
            text="ok",
            status_code=200,
        )

        result = cli_runner.invoke(ingest_tiles, [dummy_file])
        assert result.exit_code == 0

    def test_success_upload_with_document_id(
        self, cli_runner, requests_mock, dummy_file
    ):
        requests_mock.put(
            self.upload_url,
            text="ok",
            status_code=200,
        )

        result = cli_runner.invoke(
            ingest_tiles, [f"--document-id={self.document_id}", dummy_file]
        )
        assert result.exit_code == 0
