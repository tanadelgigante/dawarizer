# dawarizer

**Dawarizer** is a simple Home Assistant custom component that loads from a Dawarich installation the informations about:

- Stats
- Number of points (last day, last week, last month, and total)
- Number of areas (last day, last month, and total)
- Heath maps (ast day, last week, last month)

by interrogating the Dawarich APIs.

##setup

Simply download the content of the `dawarizer` directory and place under your `custom_components` directory of Home Assistant.
Then edit your `configuration.yaml` by adding the Dawarizer section:

	dawarizer:
	api_url: "https://<dawarich_server>"
	api_key: "<api_key>"
	validate_ssl: True/False [True]

The API token could be copied from the _Account_ section of your user.

Then restart your Home Assistant instance.

This component is not affiliated or related to Dawarich developers and is used for study of the Dawarich and Home Assistant capabilities. This component is intended "as-is" and the author is not responsible for malfunctioning or damaging of your systems. Any collaboration is welcome.
