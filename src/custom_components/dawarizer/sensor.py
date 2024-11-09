from datetime import datetime, timedelta
import logging

import aiohttp 
from homeassistant.helpers.entity import Entity 
import requests

from custom_components.dawarizer.const import NOMINATIM_URL
import matplotlib.pyplot as plt

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    api_url = hass.data["dawarizer"]["api_url"]
    api_key = hass.data["dawarizer"]["api_key"]
    verify_ssl = hass.data["dawarizer"].get("verify_ssl", True)

    sensors = [
        StatSensor(api_url, api_key, "totalDistanceKm", "Total Distance (Km)", verify_ssl),
        StatSensor(api_url, api_key, "totalPointsTracked", "Total Points Tracked", verify_ssl),
        StatSensor(api_url, api_key, "totalReverseGeocodedPoints", "Total Reverse Geocoded Points", verify_ssl),
        StatSensor(api_url, api_key, "totalCountriesVisited", "Total Countries Visited", verify_ssl),
        StatSensor(api_url, api_key, "totalCitiesVisited", "Total Cities Visited", verify_ssl),
        AreaCountSensor(api_url, api_key, "Area Count", verify_ssl),
        AreaNameSensor(api_url, api_key, "Area Names", verify_ssl),
        YearlyStatsSensor(api_url, api_key, "yearlyStats", "Yearly Stats", verify_ssl),
        PointsTotalSensor(api_url, api_key, "Total Points", verify_ssl),
        PointsLastDaySensor(api_url, api_key, "Points Last Day", verify_ssl),
        PointsLastMonthSensor(api_url, api_key, "Points Last Month", verify_ssl),
        PointsLastYearSensor(api_url, api_key, "Points Last Year", verify_ssl),
        HeatmapSensor(api_url, api_key, "Heatmap Last Day", "day", verify_ssl),
        HeatmapSensor(api_url, api_key, "Heatmap Last Week", "week", verify_ssl),
        HeatmapSensor(api_url, api_key, "Heatmap Last Month", "month", verify_ssl)
    ]
    add_entities(sensors, True)


class DawarizerSensor(Entity):

    def __init__(self, api_url, api_key, name, verify_ssl):
        self._api_url = api_url
        self._api_key = api_key
        self._verify_ssl = verify_ssl
        self._name = name
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def fetch_data(self, endpoint, params=None):
        url = f"{self._api_url}{endpoint}?api_key={self._api_key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=self._verify_ssl) as response:
                response.raise_for_status()
                return await response.json()

    
class StatSensor(DawarizerSensor):
    """Sensor for general statistics."""

    def __init__(self, api_url, api_key, stat_name, name, verify_ssl):
        super().__init__(api_url, api_key, name, verify_ssl)
        self._stat_name = stat_name

    async def async_update(self):
        try:
            data = await self.fetch_data("/api/v1/stats")
            self._state = data.get(self._stat_name)
        except Exception as e:
            _LOGGER.error(f"Error fetching data for {self._name}: {e}")
            self._state = None


class YearlyStatsSensor(DawarizerSensor):
    """Sensor for yearly statistics."""

    def __init__(self, api_url, api_key, stat_name, name, verify_ssl):
        super().__init__(api_url, api_key, name, verify_ssl)
        self._stat_name = stat_name

    async def async_update(self):
        try:
            data = await self.fetch_data("/api/v1/stats")
            self._state = len(data.get(self._stat_name, []))
            self._attributes = {
                "yearly_stats": data.get(self._stat_name, [])
            }
        except Exception as e:
            _LOGGER.error(f"Error fetching data for {self._name}: {e}")
            self._state = None


class AreaCountSensor(DawarizerSensor):
    """Sensor for the number of areas."""

    def __init__(self, api_url, api_key, name, verify_ssl):
        super().__init__(api_url, api_key, name, verify_ssl)

    async def async_update(self):
        try:
            data = await self.fetch_data("/api/v1/areas")
            self._state = len(data)
        except Exception as e:
            _LOGGER.error(f"Error fetching data for {self._name}: {e}")
            self._state = None


class AreaNameSensor(DawarizerSensor):
    """Sensor for the names of areas using geocoding."""

    def __init__(self, api_url, api_key, name, verify_ssl):
        super().__init__(api_url, api_key, name, verify_ssl)

    async def async_update(self):
        try:
            data = await self.fetch_data("/api/v1/areas")
            area_names = []
            for area in data:
                latitude = area["latitude"]
                longitude = area["longitude"]
                response = requests.get(
                    NOMINATIM_URL,
                    params={
                        "lat": latitude,
                        "lon": longitude,
                        "format": "json"
                    }
                )
                geocode_data = response.json()
                area_name = geocode_data.get("display_name", "Unknown")
                area_names.append({"id": area["id"], "name": area["name"], "geocode_name": area_name})
            self._state = len(area_names)
            self._attributes = {"areas": area_names}
        except Exception as e:
            _LOGGER.error(f"Error fetching data for {self._name}: {e}")
            self._state = None

            
class PointsTotalSensor(DawarizerSensor):
    """Sensor for the total number of points."""

    def __init__(self, api_url, api_key, name, verify_ssl):
        super().__init__(api_url, api_key, name, verify_ssl)

    async def async_update(self):
        try:
            data = await self.fetch_data("/api/v1/points")
            self._state = len(data)
        except Exception as e:
            _LOGGER.error(f"Error fetching data for {self._name}: {e}")
            self._state = None


class PointsLastDaySensor(DawarizerSensor):
    """Sensor for the number of points sent in the last day."""

    def __init__(self, api_url, api_key, name, verify_ssl):
        super().__init__(api_url, api_key, name, verify_ssl)

    async def async_update(self):
        try:
            end_at = datetime.utcnow().isoformat()
            start_at = (datetime.utcnow() - timedelta(days=1)).isoformat()
            data = await self.fetch_data("/api/v1/points", params={"start_at": start_at, "end_at": end_at})
            self._state = len(data)
        except Exception as e:
            _LOGGER.error(f"Error fetching data for {self._name}: {e}")
            self._state = None


class PointsLastMonthSensor(DawarizerSensor):
    """Sensor for the number of points sent in the last month."""

    def __init__(self, api_url, api_key, name, verify_ssl):
        super().__init__(api_url, api_key, name, verify_ssl)

    async def async_update(self):
        try:
            end_at = datetime.utcnow().isoformat()
            start_at = (datetime.utcnow() - timedelta(days=30)).isoformat()
            data = await self.fetch_data("/api/v1/points", params={"start_at": start_at, "end_at": end_at})
            self._state = len(data)
        except Exception as e:
            _LOGGER.error(f"Error fetching data for {self._name}: {e}")
            self._state = None


class PointsLastYearSensor(DawarizerSensor):
    """Sensor for the number of points sent in the last year."""

    def __init__(self, api_url, api_key, name, verify_ssl):
        super().__init__(api_url, api_key, name, verify_ssl)

    async def async_update(self):
        try:
            end_at = datetime.utcnow().isoformat()
            start_at = (datetime.utcnow() - timedelta(days=365)).isoformat()
            data = await self.fetch_data("/api/v1/points", params={"start_at": start_at, "end_at": end_at})
            self._state = len(data)
        except Exception as e:
            _LOGGER.error(f"Error fetching data for {self._name}: {e}")
            self._state = None


class HeatmapSensor(DawarizerSensor):
    """Sensor for generating heatmaps of the most frequented areas."""

    def __init__(self, api_url, api_key, name, period, verify_ssl):
        super().__init__(api_url, api_key, name, verify_ssl)
        self._period = period

    async def async_update(self):
        try:
            end_at = datetime.utcnow().isoformat()
            if self._period == "day":
                start_at = (datetime.utcnow() - timedelta(days=1)).isoformat()
            elif self._period == "week":
                start_at = (datetime.utcnow() - timedelta(weeks=1)).isoformat()
            elif self._period == "month":
                start_at = (datetime.utcnow() - timedelta(days=30)).isoformat()
            
            data = await self.fetch_data("/api/v1/points", params={"start_at": start_at, "end_at": end_at})

            # Filtrare i dati per ottenere solo valori numerici validi
            lats = [point["latitude"] for point in data if isinstance(point["latitude"], (int, float))]
            lons = [point["longitude"] for point in data if isinstance(point["longitude"], (int, float))]

            if lats and lons:  # Controlla se le liste non sono vuote
                plt.figure(figsize=(10, 6))
                plt.hist2d(lons, lats, bins=[100, 100], cmap='hot')
                plt.colorbar()
                plt.xlabel("Longitude")
                plt.ylabel("Latitude")
                plt.title(f"Heatmap for the last {self._period}")
                plt.savefig(f"/config/www/heatmap_{self._period}.png")
                plt.close()

                self._state = f"/local/heatmap_{self._period}.png"
            else:
                self._state = None
                _LOGGER.warn(f"No valid data points for generating heatmap for {self._name}")

        except Exception as e:
            _LOGGER.error(f"Error generating heatmap for {self._name}: {e}")
            self._state = None