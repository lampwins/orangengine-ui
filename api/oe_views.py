
from api import app, db
from api.models import ChangeRequest
import logging
from api.auth import auth_token_required

logger = logging.getLogger(__name__)

@app.route('/v1.0/oe/candidate_policy/change_request/<int:id>/')
@auth_token_required
def get_candidate_policy(id):
    """Calculate an automation score for the given change request and return an
    orangengine.ChangeRequest object
    """
    # some weird session thing?
    change_request = ChangeRequest.query.filter_by(id=id, status='open').first_or_404()

    # start with a score of 10
    score = 10

    

