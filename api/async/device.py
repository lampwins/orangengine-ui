
from api import celery as celery_app
from api.models import Device as DeviceModel
from api.async.base import DeviceTask
from api.async import celery_logger
from api import device_refresh_redis_conection
import orangengine


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

        if device_model.refresh_interval > 0:
            # only some devices wish to be periodically refreshed
            schedule_device_refresh(device_model.hostname, device_model.refresh_interval)


@celery_app.task(base=DeviceTask)
def refresh_device(hostname, reschedule=False):
    """Call the orangengine refresh method on the device"""
    device = refresh_device.device_factory.get_device(hostname)
    if reschedule:
        device_model = refresh_device.device_factory.get_device_model(hostname)
        schedule_device_refresh(hostname, device_model.refresh_interval)
    celery_logger.info('Refreshing device: %s', hostname)
    device.refresh()


def schedule_device_refresh(hostname, device_interval):
    """Set the device refresh interval for the given hostname and device_interval
    """
    device_key = REDIS_DEV_REF_INTV_COUNT_PREFIX + hostname
    unschedule_device_refresh(hostname)
    celery_logger.info('Scheduling device refresh interval for %s', hostname)
    interval = int(CELERY_BEAT_INTERVAL * round(float(device_interval)/CELERY_BEAT_INTERVAL))
    device_refresh_redis_conection.set(device_key, int(interval / CELERY_BEAT_INTERVAL) - 1)


def unschedule_device_refresh(hostname):
    """Remove the device from the refresh schedule
    """
    celery_logger.info("Unscheduling refresh for %s" % hostname)
    device_key = REDIS_DEV_REF_INTV_COUNT_PREFIX + hostname
    device_refresh_redis_conection.delete(device_key)


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

@celery_app.task(base=DeviceTask)
def deprovision_device(hostname):
    """End the lifecycle for the device with the given hostname

    Signal the factory, and unschedule the device
    """
    celery_logger.info("Deprovisioning device %s" % hostname)
    unschedule_device_refresh(hostname)
    deprovision_device.device_factory.delete_device(hostname)

@celery_app.task(base=DeviceTask)
def get_candidate_policy(hostname, profile_name, match_criteria):
    """Generate a candidate policy
    """
    celery_logger.debug("get_candidate_policy: match_criteria: %s", match_criteria)
    device = get_candidate_policy.device_factory.get_device(hostname)
    if isinstance(device, orangengine.drivers.PaloAltoPanoramaDriver):
        cp = device.candidate_policy_match(match_criteria, device_group=profile_name)
    else:
        cp = device.candidate_policy_match(match_criteria)
    return cp.serialize()

@celery_app.task(base=DeviceTask)
def apply_candidate_policy(hostname, candidate_policy, commit=False):
    """Apply the candidate policy to the device
    """
    celery_logger.debug("apply_candidate_policy: applying candidate policy: %s", candidate_policy)
    device = apply_candidate_policy.device_factory.get_device(hostname)
    passed = False
    #try:
    #    device.apply_candidate_policy(candidate_policy, commit)
    #    passed = True
    #except Exception as e:
    #    celery_logger.error(e)
    device.apply_candidate_policy(candidate_policy, commit)

    return passed
