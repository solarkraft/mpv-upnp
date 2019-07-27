from lib.ssdp import SSDPServer
from lib.upnp_http_server import UPNPHTTPServer
import uuid
import netifaces as ni
from time import sleep
import logging

NETWORK_INTERFACE = 'wlp1s0'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def setup_debugging():
    """
    Load PyCharm's egg and start a remote debug session.
    :return: None
    """
    import sys
    sys.path.append('/root/pycharm-debug-py3k.egg')
    import pydevd
    pydevd.settrace('192.168.4.47', port=5422, stdoutToServer=True, stderrToServer=True, suspend=False)


setup_debugging()


def get_network_interface_ip_address(interface='eth0'):
    """
    Get the first IP address of a network interface.
    :param interface: The name of the interface.
    :return: The IP address.
    """
    while True:
        if NETWORK_INTERFACE not in ni.interfaces():
            logger.error('Could not find interface %s.' % (interface,))
            exit(1)
        interface = ni.ifaddresses(interface)
        if (2 not in interface) or (len(interface[2]) == 0):
            logger.warning('Could not find IP of interface %s. Sleeping.' % (interface,))
            sleep(60)
            continue
        return interface[2][0]['addr']


device_uuid = uuid.uuid4()
local_ip_address = get_network_interface_ip_address(NETWORK_INTERFACE)

http_server = UPNPHTTPServer(8088,
    friendly_name="MPV Renderer",
    manufacturer="solarkraft",
    manufacturer_url='http://github.com/solarkraft/mpv-upnp/',
    model_description='Renders through MPV. ',
    model_name="MPV",
    model_number="1",
    model_url="http://github.com/solarkraft/mpv-upnp/",
    serial_number="1",
    uuid=device_uuid,
    presentation_url="http://{}:5000/".format(local_ip_address))
http_server.start()

ssdp = SSDPServer()
ssdp.register(
    'local',
    'uuid:{}::upnp:rootdevice'.format(device_uuid),
    'upnp:rootdevice',
    'http://{}:8088/device.xml'.format(local_ip_address))
ssdp.run()
