
from celery import Task
from api.async import OEDeviceFactory
from api.async import celery_logger


class DeviceTask(Task):
    """Base task for all tasks related to devices

    Provides access to the device factory
    """

    _device_factory = None

    @property
    def device_factory(self):
        """Property for the device factory

        Returns a singleton instance of the factory
        """
        if DeviceTask._device_factory is None:
            DeviceTask._device_factory = OEDeviceFactory()
        return DeviceTask._device_factory
