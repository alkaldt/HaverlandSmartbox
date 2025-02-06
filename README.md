# hass-smartbox
![hassfest](https://github.com/ajtudela/hass-smartbox/workflows/Validate%20with%20hassfest/badge.svg) [![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration) [![codecov](https://codecov.io/gh/ajtudela/hass-smartbox/branch/main/graph/badge.svg?token=C6J448TUQ8)](https://codecov.io/gh/ajtudela/hass-smartbox) [![Total downloads](https://img.shields.io/github/downloads/ajtudela/hass-smartbox/total)](https://github.com/ajtudela/hass-smartbox/releases) [![Downloads of latest version (latest by SemVer)](https://img.shields.io/github/downloads/ajtudela/hass-smartbox/latest/total?sort=semver)](https://github.com/ajtudela/hass-smartbox/releases/latest) [![Current version](https://img.shields.io/github/v/release/ajtudela/hass-smartbox)](https://github.com/ajtudela/hass-smartbox/releases/latest)




Home Assistant integration for Haverland (and other brands) heating smartboxes.

**NOTE**: The initial version of this integration was made by [graham33](https://github.com/graham33) but it was not maintained. I have taken over the project and will try to keep it up to date.

## Installation

### Using HACS (Recommended)

1. Add this repository to your custom repositories
1. Search for and install "Smartbox" in HACS.
1. Restart Home Assistant.
1. In the Home Assistant UI go to "Configuration" -> "Integrations" click "+" and search for "Smartbox"

### Manually Copy Files

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `smartbox`.
1. Download _all_ the files from the `custom_components/smartbox/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the Home Assistant UI go to "Configuration" -> "Integrations" click "+" and search for "Smartbox"

### Finally

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=smartbox)


## Configuration

You will need the following items of information:
* Name of your resailer
* Your username and password used for the mobile app/web app.

If there is an issue during the process or authentication, the errors will be displayed.

### Additional Options
You can also specify the following options (although they have reasonable defaults):

#### Consumption history
We are currently getting the consumption history of device throuw the API and we inject it in statistics and TotalConsumption sensor
* start : we will get the last 3 years of consumption and set the option to auto.
* auto : every hour, we get the last 24 hours.
* off : stop the automatic collect. We will still update the sensor every hour.

#### Resailer logo
By default, each sensor has in own icon depends on the type of the sensor.
You can activate this option to display the logo of the resailer instead.

#### Session options 
```
  session_retry_attempts: 8 # how many times to retry session REST operations
  session_backoff_factor: 0.1 # how much to backoff between REST retries
  socket_reconnect_attempts: 3 # how many times to try reconnecting the socket.io socket
  socket_backoff_factor: 0.1 # how much to backoff between initial socket connect attempts
```

## Supported Node types

### Heaters
These are modelled as Home Assistant Climate entities.

* `htr` and `acm` (accumulator) nodes
  * Supported modes: 'manual' and 'auto'
  * Supported presets: 'home and 'away'
* `htr_mod`
  * Supported modes: 'manual', 'auto', 'self_learn' and 'presence'
  * Supported presets: 'away', 'comfort', 'eco', 'ice' and 'away'

The modes and presets for htr_mod heaters are mapped as follows:

| htr\_mod mode | htr\_mod selected_temp | HA HVAC mode | HA preset   |
|---------------|------------------------|--------------|-------------|
| manual        | comfort                | HEAT         | COMFORT     |
|               | eco                    | HEAT         | ECO         |
|               | ice                    | HEAT         | ICE         |
| auto          | *                      | AUTO         | SCHEDULE    |
| self\_learn   | *                      | AUTO         | SELF\_LEARN |
| presence      | *                      | AUTO         | ACTIVITY    |

## Debugging

Debug logging can be enabled by increasing the log level for the smartbox custom
component and the underlying [smartbox] python module in the Home Assistant
`configuration.yaml`:

```
 logger:
   ...
   logs:
     custom_components.smartbox: debug
     smartbox: debug
   ...
```

**Warning: currently logs might include credentials, so please be careful when
sharing excerpts from logs**

See the [Home Assistant logger docs] for how to view the actual logs. Please
file a [Github issue] with any problems.

## TODO
* Graceful cleanup/shutdown of update task
* use a coordinator to update data (and use the websocket to propagate data)

[custom repository]: https://hacs.xyz/docs/faq/custom_repositories
[Github issue]: https://github.com/ajtudela/hass-smartbox/issues
[Home Assistant integration docs]: https://developers.home-assistant.io/docs/creating_integration_file_structure/#where-home-assistant-looks-for-integrations
[Home Assistant logger docs]: https://www.home-assistant.io/integrations/logger/#viewing-logs
[Home Assistant secrets management]: https://www.home-assistant.io/docs/configuration/secrets/
[smartbox]: https://github.com/ajtudela/smartbox
