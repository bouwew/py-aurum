"""Aurum Core module."""
import asyncio
import logging
from defusedxml import ElementTree as etree

import aiohttp
import async_timeout

AURUM_DATA = "/measurements/output.xml"

DEFAULT_TIMEOUT = 20

_LOGGER = logging.getLogger(__name__)


class Aurum:
    """Define the Aurum object."""

    def __init__(
        self,
        host,
        port=80,
        timeout=DEFAULT_TIMEOUT,
        websession: aiohttp.ClientSession = None,
    ):
        """Set the constructor for this class."""

        if not websession:

            async def _create_session() -> aiohttp.ClientSession:
                return aiohttp.ClientSession()

            loop = asyncio.get_event_loop()
            if loop.is_running():
                self.websession = aiohttp.ClientSession()
            else:
                self.websession = loop.run_until_complete(_create_session())
        else:
            self.websession = websession

        self._aurum_data = {}
        self._endpoint = f"http://{host}:{str(port)}"
        self._timeout = DEFAULT_TIMEOUT

    async def connect(self, retry=2):
        """Connect to the Aurum meetstekker."""
        # pylint: disable=too-many-return-statements
        url = f"{self._endpoint}{AURUM_DATA}"

        try:
            with async_timeout.timeout(self._timeout):
                resp = await self.websession.get(url)
        except (asyncio.TimeoutError, aiohttp.client_exceptions.ClientConnectorError):
            if retry < 1:
                _LOGGER.error(
                    "Error connecting to the Aurum meetstekker", exc_info=True
                )
                raise self.ConnectionFailedError("Error connecting")
                return False
            return await self.connect(retry - 1)

        try:
            result = await resp.text()
        except asyncio.TimeoutError:
            _LOGGER.error("Timed out reading response from the Aurum meetstekker")
            raise self.DeviceTimeoutError

        # Command accepted gives empty body with status 202
        if resp.status == 202:
            _LOGGER.debug(resp.status)
            return

        if not result or "error" in result:
            _LOGGER.error("Something's not right: %s", result)
            _LOGGER.error(resp.status)
            raise self.ResponseError

        root = etree.fromstring(result)
        for item in root:
            sensor = item.tag
            if sensor == "smartMeterTimestamp":
                _LOGGER.debug("Connected to the Aurum meetstekker")
                return True

    async def close_connection(self):
        """Close the Aurum connection."""
        await self.websession.close()

    async def update_data(self, retry=2):
        """Connect to the Aurum meetstekker."""
        # pylint: disable=too-many-return-statements
        url = f"{self._endpoint}{AURUM_DATA}"

        try:
            with async_timeout.timeout(self._timeout):
                resp = await self.websession.get(url)
        except asyncio.TimeoutError:
            if retry < 1:
                _LOGGER.error("Timed out getting data from the Aurum meetstekker")
                raise self.DeviceTimeoutError
            return await self.update_data(retry - 1)

        try:
            result = await resp.text()
        except asyncio.TimeoutError:
            _LOGGER.error("Timed out reading response from the Aurum meetstekker")
            raise self.DeviceTimeoutError

        # Command accepted gives empty body with status 202
        if resp.status == 202:
            _LOGGER.debug(resp.status)
            return

        if not result or "error" in result:
            _LOGGER.error("Something's not right: %s", result)
            _LOGGER.error(resp.status)
            raise self.ResponseError

        self._aurum_data = etree.fromstring(result)

    def get_aurum_data(self):
        """Connect to the Aurum meetstekker."""
        new_data = {}
        idx = 1
        sensor = value = None
        for item in self._aurum_data:
            sensor = item.tag
            value = item.get("value")
            if sensor != "smartMeterTimestamp":
                if sensor == "powerElectricity":
                    value = int(float(value))
                    if sensor == "counterGas":
                        value = float("{:.3f}".format(round(float(value), 3)))
                    else:
                        if abs(float(value)) > 10:
                            value = float("{:.1f}".format(round(float(value), 1)))
                        else:
                            value = float("{:.2f}".format(round(float(value), 2)))

            new_data[idx] = {sensor: value}
            idx += 1

        if new_data == {}:
            _LOGGER.error("Aurum data missing")
            raise self.XMLDataMissingError
        return new_data

    class AurumError(Exception):
        """Aurum exceptions class."""

    class ConnectionFailedError(AurumError):
        """Raised when unable to connect."""

    class DeviceTimeoutError(AurumError):
        """Raised when device is not supported."""

    class ResponseError(AurumError):
        """Raised when empty or error in response returned."""

    class XMLDataMissingError(AurumError):
        """Raised when xml data is empty."""
