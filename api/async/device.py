
from api import celery as celery_app
from api.models import Device as DeviceModel
from api.async.base import DeviceTask
from api.async import celery_logger
from api import device_refresh_redis_conection


REDIS_DEV_REF_INTV_COUNT_PREFIX = 'dev:refresh:interval:count:'
CELERY_BEAT_INTERVAL = 5


@celery_app.task(base=DeviceTask)
def init_devices():
    """Do the first (for full) refresh on all devices and schedule their
    periodic refreshes
    """

    celery_logger.debug('Running device init')

    device_models = init_devices.device_factory.get_all_device_models()

    for device_model in device_models:
        # no delay here beceaue we should already be run as a task
        # and we do not want to schedule if the refresh fails
        refresh_device.delay(device_model.hostname)

        celery_logger.debug('Scheduling device refresh interval for %s', device_model.hostname)
        if device_model.refresh_interval > 0:
            # only some devices wish to be periodically refreshed
            schedule_device_refresh(device_model.hostname, device_model.refresh_interval)


@celery_app.task(base=DeviceTask)
def refresh_device(hostname):
    """Call the orangengine refresh method on the device"""
    device = refresh_device.device_factory.get_device(hostname)
    celery_logger.info('Refreshing device: %s', hostname)
    device.refresh()


def schedule_device_refresh(hostname, device_interval):
    """Set the device refresh interval for the given hostname and device_interval
    """
    interval = int(CELERY_BEAT_INTERVAL * round(float(device_interval)/CELERY_BEAT_INTERVAL))
    device_refresh_redis_conection.set(REDIS_DEV_REF_INTV_COUNT_PREFIX + hostname,
                                       int(interval / CELERY_BEAT_INTERVAL) - 1)


@celery_app.task(base=DeviceTask)
def beat_interval_runner():
    """Process the beat periodic task to check device refresh interval status

    Spin off the refresh task if called for.
    """
    celery_logger.info('Running beat interval checks')
    device_keys = device_refresh_redis_conection.keys(REDIS_DEV_REF_INTV_COUNT_PREFIX + "*")
    for hostname_key in device_keys:
        value = int(device_refresh_redis_conection.get(hostname_key))
        if value <= 0:
            # due for a refresh
            hostname = hostname_key.split(REDIS_DEV_REF_INTV_COUNT_PREFIX)[1]
            refresh_device.delay(hostname)
            device_interval = beat_interval_runner.device_factory.get_device_model(hostname)
            device_interval = device_interval.refresh_interval
            schedule_device_refresh(hostname, device_interval)
        else:
            # not due for a refresh, so just decrement the counter
            device_refresh_redis_conection.set(hostname_key, value - 1)
