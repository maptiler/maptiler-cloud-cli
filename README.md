<img src="https://raw.githubusercontent.com/maptiler/maptiler-sdk-kotlin/main/Examples/maptiler-logo.png" alt="Company Logo" height="32"/>

# MapTiler Cloud CLI

This tool allows you [upload map data](https://docs.maptiler.com/guides/map-tiling-hosting/data-hosting/how-to-upload-mbtiles-or-geopackage-into-maptiler-cloud-using-api/) into [MapTiler](https://www.maptiler.com/cloud/geodata-hosting/) using [upload API](https://docs.maptiler.com/cloud/admin-api/tileset_ingest/).

![](https://img.shields.io/badge/python-%E2%89%A53.8-f2f6ff?style=for-the-badge&labelColor=D3DBEC&logo=python&logoColor=333359)

---

📖 [Documentation](https://docs.maptiler.com/guides/map-tiling-hosting/data-hosting/how-to-upload-mbtiles-or-geopackage-into-maptiler-cloud-using-api/) &nbsp; 🌐 [Website](https://www.maptiler.com/) &nbsp; 🔑 [Get Service token](https://cloud.maptiler.com/account/credentials/)

---

<br>

<details> <summary><b>Table of Contents</b></summary>
<ul>
<li><a href="#-installation">Installation</a></li>
<li><a href="#-basic-usage">Basic Usage</a></li>
<li><a href="#-support">Support</a></li>
<li><a href="#-contributing">Contributing</a></li>
<li><a href="#-license">License</a></li>
<li><a href="#-acknowledgements">Acknowledgements</a></li>
</ul>
</details>

## 📦 Installation

### Requirements

- Python _version >= 3.8_
- pip
- venv

```shell
pip install maptiler-cloud-cli
```

<br>

## 🚀 Basic Usage

### Authorization

You need an [Service token](https://docs.maptiler.com/cloud/api/authentication-token/) to be able to use the tool.
The token can be acquired from the
[Credentials](https://cloud.maptiler.com/account/credentials/)
section of your account administration pages in MapTiler.

Specify it either on the command line or as an environment variable.

```shell
maptiler-cloud --token=MY_TOKEN ...
```

```shell
MAPTILER_TOKEN=MY_TOKEN; maptiler-cloud ...
```

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

For more control over tileset management, you can use the
[MapTiler Service API](https://docs.maptiler.com/cloud/admin-api/).
The admin API allows you to create, update or delete a tileset among other actions.

<br>

## 💬 Support

- 📚 [Documentation](https://docs.maptiler.com/guides/map-tiling-hosting/data-hosting/how-to-upload-mbtiles-or-geopackage-into-maptiler-cloud-using-api/) - Comprehensive guides and API reference
- ✉️ [Contact us](https://maptiler.com/contact) - Get in touch or submit a request
- 🐦 [Twitter/X](https://twitter.com/maptiler) - Follow us for updates

<br>

---

<br>

## 🤝 Contributing

We love contributions from the community! Whether it's bug reports, feature requests, or pull requests, all contributions are welcome:

- Fork the repository and create your branch from `main`
- If you've added code, add tests that cover your changes
- Ensure your code follows our style guidelines
- Give your pull request a clear, descriptive summary
- Open a Pull Request with a comprehensive description

<br>

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](./LICENSE) file for details.

<br>

## 🙏 Acknowledgements

This project is built on the shoulders of giants:

- [MapTiler Service API](https://docs.maptiler.com/cloud/admin-api/) – MapTiler Service API gives you full access to your account including write operations
- [Python](https://www.python.org/) – A programming language that lets you work quickly
  and integrate systems more effectively

<br>

<p align="center" style="margin-top:20px;margin-bottom:20px;"> <a href="https://cloud.maptiler.com/account/keys/" style="display:inline-block;padding:12px 32px;background:#F2F6FF;color:#000;font-weight:bold;border-radius:6px;text-decoration:none;"> Get Your API Key <sup style="background-color:#0000ff;color:#fff;padding:2px 6px;font-size:12px;border-radius:3px;">FREE</sup><br /> <span style="font-size:90%;font-weight:400;">Start building with 100,000 free map loads per month ・ No credit card required.</span> </a> </p>

<br>

<p align="center"> 💜 Made with love by the <a href="https://www.maptiler.com/">MapTiler</a> team <br />
<p align="center">
  <a href="https://www.maptiler.com/">Website</a> •
  <a href="https://docs.maptiler.com/guides/map-tiling-hosting/data-hosting/how-to-upload-mbtiles-or-geopackage-into-maptiler-cloud-using-api/">Documentation</a> •
  <a href="https://github.com/maptiler/maptiler-cloud-cli/">GitHub</a>
</p>
