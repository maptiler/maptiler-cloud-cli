# MapTiler Cloud CLI

## Installation

```shell
pip install maptiler-cloud-cli
```

## Authorization

You need an API token to be able to use the tool.
Specify it either on the command line or as an environment variable.
The token can be acquired from "Credentials" section of your account administration in MapTiler Cloud.

```shell
maptiler-cloud --token=MY_TOKEN ...
```

```shell
MAPTILER_TOKEN=MY_TOKEN; maptiler-cloud ...
```

## Usage

To create a new tileset, use the `tiles ingest` command.

```shell
maptiler-cloud tiles ingest v1.mbtiles
```

The command will print out the tileset ID on the last line.
You can use it to upload a new file to the same tileset.

```shell
maptiler-cloud tiles ingest --document-id=EXISTING_TILESET_ID v2.mbtiles
```
