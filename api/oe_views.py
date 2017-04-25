
from api import app, db
from api.models import ChangeRequest, Location, DeviceProfile, location_mapping_table
from api.models import Device, ZoneMapping
import logging
from api.auth import auth_token_required
from api.views import data_results
from orangengine.utils import is_ipv4, missing_cidr
from netaddr import IPNetwork, IPAddress, IPRange
from api.async.device import get_candidate_policy as device_candidate_policy
from api.async.device import apply_candidate_policy as device_apply_candidate_policy
from api.async.jobs import generate_job_id
from flask import jsonify, request, abort

logger = logging.getLogger(__name__)

@app.route('/v1.0/oe/change_request/<int:id>/score/', methods=['GET'])
@auth_token_required
def get_score(id):
    """Calculate an automation score for the given change request and return the
    criteria used to get a candidate policy object
    """
    # some weird session thing?
    change_request = ChangeRequest.query.filter_by(id=id, status='open').first_or_404()

    # start with a score of 10
    score = 10
    helping_hands = []

    # this is a mess
    device_profiles = DeviceProfile.query.join(
                            location_mapping_table, 
                            DeviceProfile.id==location_mapping_table.c.device_profile_id
                        ).join(
                            Location,
                            Location.id==location_mapping_table.c.location_id
                        ).filter(
                            Location.name.in_(
                                (change_request.source_location, change_request.destination_location)
                            )
                        ).all()

    if not device_profiles:
        helping_hands.append("Unable to identify a device profile to use.")
        score -= 5
        return data_results({'score': score, 'help': helping_hands})

    # now we have our profiles, so lets narrow down zones
    device_profiles_data = []
    for device_profile in device_profiles:

        zone_maps = ZoneMapping.query.filter_by(device_profile_id=device_profile.id).all()
        default_zone = None

        for zone in zone_maps:
            if zone.network == '0.0.0.0/0':
                default_zone = zone
        zone_maps.remove(default_zone)

        zones = {}

        for addr_type in ['source', 'destination']:

            if addr_type == 'source':
                a_type = change_request.sources
            else:
                a_type = change_request.destinations

            for s_addr in a_type:
                if s_addr.type == 'ipv4' or s_addr.type == 'ipv4_range':

                    if s_addr.type == 'ipv4_range':
                        value = IPRange(s_addr.value.split('-')[0],
                                        s_addr.value.split('-')[1])
                    elif s_addr.value == 'any':
                        value = IPNetwork('0.0.0.0/0')
                    else:
                        value = IPNetwork(s_addr.value)

                    zone_matchs = [zone_map for zone_map in zone_maps
                                   if value in IPNetwork(zone_map.network)]
                    if not zone_matchs:
                        zone_matchs = [default_zone]

                    zones[addr_type] = zone_matchs

        data = {
            'profile': device_profile.serialize(),
            'device': Device.query.filter_by(id=device_profile.device_id).first().serialize(),
            'zones': {
                'source': [z.zone_name for z in zones['source']],
                'destination': [z.zone_name for z in zones['destination']],
            }
        }
        device_profiles_data.append(data)

    return data_results({'score': score, 'environment': device_profiles_data})

@app.route('/v1.0/oe/candidate_policy/', methods=['POST'])
@auth_token_required
def get_candidate_policy():
    """Construct an orangengine.CandidatePolicy from the posted criteria
    """

    hostname = request.json['device']['hostname']
    profile_name = request.json['profile']['name']
    match_criteria = request.json['match_criteria']
    logger.debug(match_criteria)
    candidate_policy_json = device_candidate_policy.delay(hostname, profile_name, match_criteria).get()

    return data_results(candidate_policy_json)

@app.route('/v1.0/oe/apply_candidate_policy/', methods=['POST'])
@auth_token_required
def apply_candidate_policy():
    """Apply the candidate poliy to the device
    """

    hostname = request.json['device']['hostname']
    candidate_policy = request.json['candidate_policy']
    commit = request.json['commit']

    task_id = generate_job_id()
    logger.debug("apply_candidate_policy: candidate policy: %s", candidate_policy)
    device_apply_candidate_policy.apply_async((hostname, candidate_policy, commit), task_id=str(task_id))

    return data_results({'job_id': task_id})
