
import uuid
from api import jobs_redis_conection


STATUS_PENDING = "PENDING"

def generate_job_id():
    """Generate a new Job ID and store the entry in the redis store
    """
    job_id = uuid.uuid4()
    jobs_redis_conection.set(job_id, STATUS_PENDING)
    return job_id


def get_job_status(job_id):
    """Return the job status for the given id
    """
    job_status = jobs_redis_conection.get(job_id)
    return job_status
