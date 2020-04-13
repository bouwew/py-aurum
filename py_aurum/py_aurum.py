"""Aurum Core module."""
import requests
import logging
from lxml import etree

AURUM_DATA = "/measurements/output.xml"

_LOGGER = logging.getLogger(__name__)


class Aurum:
    """Define the Aurum object."""

    def __init__(self, host, port=80):
        """Set the constructor for this class."""
        self._session = requests.Session()
        self._endpoint = 'http://' + host + ':' + str(port)

    def collect_data(self):
        data = {}
        xml = None
        url = self._endpoint + AURUM_DATA

        try:
            xml = self._session.get(url)
            xml.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            #_LOGGER.error("Http Error:",errh)
            print("Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            #_LOGGER.error("Error Connecting:",errc)
            print("Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            #_LOGGER.error("Timeout Error:",errt)
            print("Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            #_LOGGER.error("OOps: Something Else",err)
            print("OOps: Something Else",err)

        if xml is not None:
            result = xml.text
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
                    
                if value != 0:
                    data[idx] =  {sensor: value}
                idx += 1
            return data
