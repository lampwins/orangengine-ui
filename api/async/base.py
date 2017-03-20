
from celery import Task
from api.async import OEDeviceFactory


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
        if self._device_factory is None:
            self._device_factory = OEDeviceFactory()
        return self._device_factory
