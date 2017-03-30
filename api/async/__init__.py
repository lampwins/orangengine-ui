
import logging
import orangengine
from  api.models import Device as DeviceModel
from celery.utils.log import get_task_logger
from api import debug


celery_logger = get_task_logger(__name__)
if debug:
    celery_logger.setLevel(logging.DEBUG)
    celery_logger.debug('Enabled Debug mode')


class OEDeviceFactory(object):
    """Device Factory for the orangengine device instances

    The factory is responsible for maintaining singlton instances for each device.
    It contains public methods for updating (refreshing) the api device models from
    the database, and the respective orangengine device instances.
    """

    def __init__(self):
        self._devices = {}
        self._device_models = {}

        self._refresh_all_device_models()

    @staticmethod
    def _dispatch_device(device_model):
        """use the device model to dispatch an orangengine device and store it"""

        if device_model:

            conn_params = {
                'host': device_model.hostname,
                'username': device_model.username,
                'password': device_model.password,
                'device_type': device_model.driver.value,  # this is an enum so we need the value
                'apikey': device_model.apikey,
            }

            celery_logger.info("Dispatching device: %s", device_model.hostname)

            return orangengine.dispatch(**conn_params)

    def _refresh_device_model(self, hostname):
        """load and override the device model from the database for the given hostname"""

        device_model = DeviceModel.query.filter_by(deleted=False, hostname=hostname).first()
        if device_model:
            self._device_models[hostname] = device_model

        return device_model

    def _refresh_all_device_models(self):
        """replace all device models and refrsh them"""

        self._device_models = {}
        device_models = DeviceModel.query.filter_by(deleted=False).all()
        if device_models:
            for device_model in device_models:
                self._device_models[device_model.hostname] = device_model

    def _init_device(self, hostname):
        device_model = self._device_models.get(hostname)
        if device_model is None:
            device_model = self._refresh_device_model(hostname)
        device = self._dispatch_device(device_model)
        self._devices[hostname] = device
        return device

    def get_device(self, hostname, refresh_none=True):
        """Return the orangengine device singlton instance for the given hostname.

        Optionally (by default) refresh the device (and model) if it is not found
        """

        device = self._devices.get(hostname)
        if not device and refresh_none:
            device = self._init_device(hostname)

        return device

    def get_all_device_models(self):
        """Return a list of all device models currently stored
        """
        return self._device_models.values()

    def get_device_model(self, hostname):
        """Return the device model for a given hostname
        """
        return self._device_models.get(hostname)

    def delete_device(self, hostname, include_model=True):
        """Delete the orangengine device instance and optionally the model
        """
        self._devices.pop(hostname)
        if include_model:
            self._device_models.pop(hostname)

