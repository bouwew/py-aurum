"""Aurum Core module."""
import asyncio
import logging
from lxml import etree

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
        websession=None,
    ):
        """Set the constructor for this class."""

        if websession is None:

            async def _create_session():
                return aiohttp.ClientSession()

            loop = asyncio.get_event_loop()
            self.websession = loop.run_until_complete(_create_session())
        else:
            self.websession = websession

        self._endpoint = 'http://' + host + ':' + str(port)
        self._timeout = timeout

    async def collect_data(self, retry=2):
        """Connect to the Aurum meetstekker."""
        # pylint: disable=too-many-return-statements
        data = {}
        url = self._endpoint + AURUM_DATA

        try:
            with async_timeout.timeout(self._timeout):
                resp = await self.websession.get(url)
        except (asyncio.TimeoutError, aiohttp.ClientError):
            if retry < 1:
                _LOGGER.error("Error connecting to the Aurum meetstekker", exc_info=True)
                raise self.ConnectionFailedError
            return await self.connect(retry - 1)

        result = await resp.text()
        root = etree.fromstring(result)
        idx = 1
        for item in root:
            sensor = item.tag
            value = item.get("value")
            if sensor != "smartMeterTimestamp":
                if sensor == "powerElectricity":
                    value = int(float(value))
                elif abs(float(value)) > 10:
                    value = float("{:.1f}".format(round(float(value), 1)))
                else:
                    value = float("{:.2f}".format(round(float(value), 2)))
                
            data[idx] =  {sensor: value}
            idx += 1
        return data

    async def close_connection(self):
        """Close the Aurum connection."""
        await self.websession.close()


    class AurumError(Exception):
        """Aurum exceptions class."""


    class ConnectionFailedError(AurumError):
        """Raised when unable to connect."""
