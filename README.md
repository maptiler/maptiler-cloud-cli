# MapTiler Cloud CLI
This tool allows you [upload map data](https://documentation.maptiler.com/hc/en-us/articles/4408129705745-How-to-upload-MBTiles-or-GeoPackage-into-MapTiler-Cloud-using-API) into [MapTiler Cloud](https://www.maptiler.com/cloud/geodata-hosting/) using [upload API](https://docs.maptiler.com/cloud/admin-api/tileset_ingest/).

## Requirements

- Python *version >= 3.8*
- pip
- venv

## Installation

```shell
pip install maptiler-cloud-cli
```

## Authorization

You need an API token to be able to use the tool.
The token can be acquired from the
[Credentials](https://cloud.maptiler.com/account/credentials/)
section of your account administration pages in MapTiler Cloud.

Specify it either on the command line or as an environment variable.

```shell
maptiler-cloud --token=MY_TOKEN ...
```

```shell
MAPTILER_TOKEN=MY_TOKEN; maptiler-cloud ...
```

## Usage

### Create a new tileset

To create a new tileset, use the `tiles ingest` command.

```shell
maptiler-cloud tiles ingest v1.mbtiles
```

The command will print out the tileset ID on the last line.

> :information_source: The GeoPackage must have a tile matrix set. Read the
> [Vector tiles generating (basic)](https://documentation.maptiler.com/hc/en-us/articles/360020887038-Vector-tiles-generating-basic-)
> article to learn how to create a valid GeoPackage or MBTiles from the
> [MapTiler Engine application](https://www.maptiler.com/engine/).

> :bulb: If you reach the tileset limit for your account, you will not be able to upload new tilesets, and you will get an error.
> Check out our [plans](https://www.maptiler.com/cloud/plans/) to increase the number of tilesets you can have.

### Update a tileset

You can use the tileset ID to upload a new file to the same tileset.

```shell
maptiler-cloud tiles ingest --document-id=EXISTING_TILESET_ID v2.mbtiles
```

> :warning: This option **replaces** the tileset data with the data from the new file. It does **NOT** add the new data to the existing tileset.

To learn more about using this tool, read
[How to upload MBTiles or GeoPackage into MapTiler Cloud](https://documentation.maptiler.com/hc/en-us/articles/4408129705745-How-to-upload-MBTiles-or-GeoPackage-into-MapTiler-Cloud-using-API).

For more control over tileset management, you can use the
[Admin API](https://docs.maptiler.com/cloud/admin-api/).
The admin API allows you to create, update or delete a tileset among other actions.
