
import uuid
from api import jobs_redis_conection


STATUS_PENDING = "PENDING"

def generate_job_id():
    """Generate a new Job ID and store the entry in the redis store
    """
    job_id = uuid.uuid4()
    jobs_redis_conection.set(job_id, STATUS_PENDING)
    return job_id



