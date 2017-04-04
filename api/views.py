
import logging
import subprocess
from flask import jsonify, request, abort
from api import app, db
from api.auth import auth_token_required
from api.models import ChangeRequest, Device, ZoneMapping, ZoneMappingRule
from api.models import SupplementalDeviceParam, Location
import netaddr
from api.async.device import refresh_device, deprovision_device
from api.async.jobs import generate_job_id, get_job_status


# Setup
logger = logging.getLogger(__name__)

def data_results(data):
    # wrap the data in a standard response and jsonify it
    if isinstance(data, basestring):
        data = {'message': data}
    return jsonify({"data": data}, )

# Info method, Return Request Data back to client as JSON
@app.route('/v1.0/info', methods=['POST', 'GET'])
@auth_token_required
def app_getinfo():
    """ Returns Flask API Info """
    response = dict()
    response['message'] = "Flask API Data"
    response['status'] = "200"
    response['method'] = request.method
    response['path'] = request.path
    response['remote_addr'] = request.remote_addr
    response['user_agent'] = request.headers.get('User-Agent')

    # GET attributes
    for key in request.args:
        response['GET ' + key] = request.args.get(key, '')
    # POST Attributes
    for key in request.form.keys():
        response['POST ' + key] = request.form[key]

    return data_results(response)

@app.route('/')
def app_index():
    """Index identifying the server"""
    response = {"message": "orangeninge-ui api server: Authentication required for use",
                "status": "200"}
    return data_results(response)

@app.route('/v1.0/change_requests/', methods=['POST', 'GET'])
@auth_token_required
def change_requests():

    if request.method == 'POST':
        new_request = ChangeRequest(**request.json)
        db.session.add(new_request)
        db.session.commit()
        return data_results("success")

    elif request.method == 'GET':
        status = request.args.get('status')
        deleted = request.args.get('deleted', False)
        if status:
            # only with a specified state
            result_set = ChangeRequest.query.filter_by(deleted=deleted, status=getattr(
                                                    ChangeRequest.StateOptions, status)).all()
        else:
            # all change requests
            result_set = ChangeRequest.query.filter_by(deleted=deleted).all()
        serialized_list = []
        for obj in result_set:
            serialized_list.append(obj.serialize())
        return data_results(serialized_list)

@app.route('/v1.0/change_requests/<int:id>/', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@auth_token_required
def change_request(id):

    # some weird session thing?
    change_request = ChangeRequest.query.filter(ChangeRequest.id==id).first_or_404()

    if request.method == 'GET':
        return data_results(change_request.serialize())

    elif request.method == 'PUT':
        # not implemented
        abort(501)

    elif request.method == 'PATCH':
        for key in request.json.keys():
            if key != 'created_at' or key != 'modified_at' or key != 'id':
                setattr(change_request, key, request.json[key])
        db.session.commit()
        return data_results('Patched change_request %d' % id)

    elif request.method == 'DELETE':
        change_request.deleted = True
        db.session.commit()
        return data_results('Deleted change_request %d' % id)

@app.route('/v1.0/devices/', methods=['POST', 'GET', 'PUT'])
@auth_token_required
def devices():

    # one-to-many relationships
    if request.method == 'POST' or request.method == 'PUT':

        zone_mappings_list = request.json.pop('zone_mappings', [])
        zone_mapping_rules_list = request.json.pop('zone_mapping_rules', [])
        supplemental_device_params_list = request.json.pop('supplemental_device_params', [])
        location_mappings_list = request.json.pop('locations', [])

        if zone_mappings_list:
            request.json['zone_mappings'] = []
            for mapping in zone_mappings_list:
                zone_mapping = ZoneMapping(**mapping)
                db.session.add(zone_mapping)
                request.json['zone_mappings'].append(zone_mapping)

        if zone_mapping_rules_list:
            request.json['zone_mapping_rules'] = []
            for mapping_rule in zone_mapping_rules_list:
                zone_mapping_rule = ZoneMappingRule(**mapping_rule)
                db.session.add(zone_mapping_rule)
                request.json['zone_mapping_rules'].append(zone_mapping_rule)

        if supplemental_device_params_list:
            request.json['supplemental_device_params'] = []
            for instance in supplemental_device_params_list:
                supplemental_device_param = SupplementalDeviceParam(**instance)
                db.session.add(supplemental_device_param)
                request.json['supplemental_device_params'].append(supplemental_device_param)

        if location_mappings_list:
            logger.debug('getting location instances from db for mapping')
            request.json['locations'] = []
            for location in location_mappings_list:
                # locations already exist, we are just addeding them to the relationship
                _location = Location.query.filter_by(id=location).first_or_404()
                request.json['locations'].append(_location)

    # request methods
    if request.method == 'POST':
        new_device = Device(**request.json)
        db.session.add(new_device)
        db.session.commit()
        return data_results("success")

    elif request.method == 'GET':
        deleted = request.args.get('deleted', False)
        result_set = Device.query.filter_by(deleted=deleted).all()
        serialized_list = []
        for obj in result_set:
            serialized_list.append(obj.serialize())
        return data_results(serialized_list)

    elif request.method == 'PUT':
        device = Device.query.filter_by(hostname=request.json.get('hostname')).first()
        if device:
            for key in request.json.keys():
                if key != 'created_at' or key != 'modified_at' or key != 'id':
                    setattr(device, key, request.json[key])
            if not request.json.get('deleted'):
                setattr(device, 'deleted', False)
        else:
            device = Device(**request.json)
            db.session.add(device)

        db.session.commit()
        refresh_device.delay(device.hostname, True)
        return data_results({'status':'success', 'object_id': device.id})

@app.route('/v1.0/devices/<int:id>/', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@auth_token_required
def device(id):

    # some weird session thing?
    device = Device.query.filter(Device.id==id).first_or_404()

    if request.method == 'GET':
        return data_results(device.serialize())

    elif request.method == 'PUT':
        # not implemented
        abort(501)

    elif request.method == 'PATCH':
        for key in request.json.keys():
            if key == 'locations':
                for location_id in request.json[key]:
                    location = Location.query.filter_by(id=location_id).first_or_404()
                    device.locations.append(location)
            elif key != 'created_at' or key != 'modified_at' or key != 'id':
                setattr(device, key, request.json[key])
        db.session.commit()
        return data_results('Patched device %d' % id)

    elif request.method == 'DELETE':
        hostname = device.hostname
        if request.args.get('hard', False):
            # hard delete (delete from db)
            db.session.delete(device)
        else:
            # soft delete (set the deleted flag)
            device.deleted = True
        db.session.commit()
        deprovision_device.delay(hostname)
        return data_results('Deleted device %d' % id)

@app.route('/v1.0/locations/', methods=['POST', 'GET'])
@auth_token_required
def locations():

    if request.method == 'POST':
        new_location = Location(**request.json)
        db.session.add(new_location)
        db.session.commit()
        return data_results("success")

    elif request.method == 'GET':
        deleted = request.args.get('deleted', False)
        result_set = Location.query.filter_by(deleted=deleted).all()
        serialized_list = []
        for obj in result_set:
            serialized_list.append(obj.serialize())
        return data_results(serialized_list)

@app.route('/v1.0/locations/<int:id>/', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@auth_token_required
def location(id):

    # some weird session thing?
    location = Location.query.filter(Location.id==id).first_or_404()

    if request.method == 'GET':
        return data_results(location.serialize())

    elif request.method == 'PUT':
        # not implemented
        abort(501)

    elif request.method == 'PATCH':
        for key in request.json.keys():
            if key != 'created_at' or key != 'modified_at' or key != 'id':
                setattr(location, key, request.json[key])
        db.session.commit()
        return data_results('Patched location %d' % id)

    elif request.method == 'DELETE':
        if request.args.get('hard', False):
            # hard delete (delete from db)
            db.session.delete(location)
        else:
            # soft delete (set the deleted flag)
            location.deleted = True
        db.session.commit()
        return data_results('Deleted location %d' % id)

@app.route('/v1.0/zone_mappings/', methods=['POST', 'GET'])
@auth_token_required
def zone_mappings():

    if request.method == 'POST':
        try:
            netaddr.IPNetwork(request.json.get('network'))
            new_zone_mapping = ZoneMapping(**request.json)
            db.session.add(new_zone_mapping)
            db.session.commit()
        except Exception:
            abort(400)

        return data_results("success")

    elif request.method == 'GET':
        result_set = ZoneMapping.query.all()
        serialized_list = []
        for obj in result_set:
            serialized_list.append(obj.serialize())
        return data_results(serialized_list)

@app.route('/v1.0/zone_mappings/<int:id>/', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@auth_token_required
def zone_mapping(id):

    # some weird session thing?
    zone_mapping = ZoneMapping.query.filter(ZoneMapping.id==id).first_or_404()

    if request.method == 'GET':
        return data_results(zone_mapping.serialize())

    elif request.method == 'PUT':
        # not implemented
        abort(501)

    elif request.method == 'PATCH':
        for key in request.json.keys():
            if key != 'created_at' or key != 'modified_at' or key != 'id' or key != 'deleted':
                setattr(zone_mapping, key, request.json[key])
        db.session.commit()
        return data_results('Patched zone mapping %d' % id)

    elif request.method == 'DELETE':
        db.session.delete(zone_mapping)
        db.session.commit()
        return data_results('Deleted zone mapping %d' % id)

@app.route('/v1.0/zone_mappings/device/<int:id>/', methods=['GET', 'DELETE'])
@auth_token_required
def zone_mapping_by_device(id):

    # some weird session thing?
    device = Device.query.filter(Device.id==id).first_or_404()

    if request.method == 'GET':
        result_set = ZoneMapping.query.filter_by(device_id=id)
        serialized_list = []
        for obj in result_set:
            serialized_list.append(obj.serialize())
        return data_results(serialized_list)

    elif request.method == 'DELETE':
        ZoneMapping.query.filter_by(device_id=id).delete()
        db.session.commit()
        return data_results('successfully deleted all zone_mappings for device %s' % id)

@app.route('/v1.0/zone_mapping_rules/', methods=['POST', 'GET'])
@auth_token_required
def zone_mapping_rules():

    if request.method == 'POST':
        try:
            netaddr.IPNetwork(request.json.get('destination_network'))
            new_zone_mapping_rule = ZoneMappingRule(**request.json)
            db.session.add(new_zone_mapping_rule)
            db.session.commit()
        except Exception:
            abort(400)

        return data_results("success")

    elif request.method == 'GET':
        result_set = ZoneMappingRule.query.all()
        serialized_list = []
        for obj in result_set:
            serialized_list.append(obj.serialize())
        return data_results(serialized_list)

@app.route('/v1.0/zone_mapping_rules/<int:id>/', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@auth_token_required
def zone_mapping_rule(id):

    # some weird session thing?
    zone_mapping_rule = ZoneMappingRule.query.filter(ZoneMappingRule.id==id).first_or_404()

    if request.method == 'GET':
        return data_results(zone_mapping_rule.serialize())

    elif request.method == 'PUT':
        # not implemented
        abort(501)

    elif request.method == 'PATCH':
        for key in request.json.keys():
            if key != 'created_at' or key != 'modified_at' or key != 'id' or key != 'deleted':
                setattr(zone_mapping_rule, key, request.json[key])
        db.session.commit()
        return data_results('Patched zone mapping %d' % id)

    elif request.method == 'DELETE':
        db.session.delete(zone_mapping_rule)
        db.session.commit()
        return data_results('Deleted zone mapping %d' % id)

@app.route('/v1.0/zone_mapping_rules/device/<int:id>/', methods=['GET', 'DELETE'])
@auth_token_required
def zone_mapping_rule_by_device(id):

    # some weird session thing?
    device = Device.query.filter(Device.id==id).first_or_404()

    if request.method == 'GET':
        result_set = ZoneMappingRule.query.filter_by(device_id=id)
        serialized_list = []
        for obj in result_set:
            serialized_list.append(obj.serialize())
        return data_results(serialized_list)

    elif request.method == 'DELETE':
        ZoneMappingRule.query.filter_by(device_id=id).delete()
        db.session.commit()
        return data_results('successfully deleted all zone_mapping_rules for device %s' % id)

@app.route('/v1.0/jobs/<uuid:id>/', methods=['GET'])
@auth_token_required
def jobs(id):
    """Get Status/Result for a job ID
    """
    status = get_job_status(id) or abort(404)
    return data_results({'status': status, 'job_id': str(id)})
