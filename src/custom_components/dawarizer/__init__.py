from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv
import logging
import requests
import voluptuous as vol


_LOGGER = logging.getLogger(__name__)

DOMAIN = "dawarizer"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required("api_url"): str, 
                vol.Required("api_key"): str,
                vol.Optional("verify_ssl", default=True): cv.boolean,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Dawarizer integration."""
    conf = config[DOMAIN]
    hass.data[DOMAIN] = conf    

    discovery.load_platform(hass, "sensor", DOMAIN, {}, config)

    return True
