
import datetime
import jwt
from api import db, app, bcrypt, logger
from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import CIDR
from sqlalchemy.ext.declarative import DeclarativeMeta


# ORANGENGINE-UI MODELS


class Base(db.Model):
    """Base model

    Provides the basic attributes available in all models.
    """

    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified_at = db.Column(db.DateTime, default=db.func.current_timestamp(),
                            onupdate=db.func.current_timestamp())
    deleted = db.Column(db.Boolean, default=False)

    def serialize(self):
        """Default serializer

        May be overriden in subs, to modify behavior
        """
        my_keys = self.__dict__.keys()
        return_dict = {}
        for k in my_keys:
            if k.startswith('_'):
                continue
            value = self.__dict__.get(k)
            if hasattr(value, 'serialize'):
                value = value.serialize()
            return_dict[k] = value
        return return_dict


class ChangeRequest(Base):
    """Change Request model

    Represents firewall policy change requests. I.e. in the human form,
    "This server needs to talk to this other sever over this port."

    The implementation of a change request is what we are actually trying
    to automate here...
    """

    __tablename__ = 'change_request'
    summary = db.Column(db.String(255))
    requestor = db.Column(db.String(255))
    application = db.Column(db.String(255))
    source_location = db.Column(db.String(255))
    destination_location = db.Column(db.String(255))
    action = db.Column(db.String(255))
    status = db.Column(db.String(20), default='open')
    sources = db.relationship('Address', backref='change_request_sources', lazy='dynamic',
                              cascade="all,delete", foreign_keys='Address.change_request_source_id')
    destinations = db.relationship('Address', lazy='dynamic', backref='change_request_destinations',
                                   cascade="all,delete",
                                   foreign_keys='Address.change_request_destination_id')
    services = db.relationship('Service', backref='change_request', lazy='dynamic',
                               cascade="all,delete")

    def serialize(self):
        """Override to manually include relationsips"""
        data = super(ChangeRequest, self).serialize()
        data.update({
            'sources': [v.serialize() for v in self.sources],
            'destinations': [v.serialize() for v in self.destinations],
            'services': [v.serialize() for v in self.services],
        })
        return data


class Address(Base):
    """Address Model
    Used in the change request source and destination fields
    """

    __tablename__ = 'address'
    type = db.Column(db.String(20))  # dns/ipv4/ipv4_range
    value = db.Column(db.String(255))
    comments = db.Column(db.String(255))
    change_request_source_id = db.Column(db.Integer, db.ForeignKey('change_request.id'))
    change_request_destination_id = db.Column(db.Integer, db.ForeignKey('change_request.id'))


class Service(Base):
    """Service Model
    Used in the change request service/application fields
    """

    __tablename__ = 'service'
    type = db.Column(db.String(20))  # layer4/layer7
    layer4_protocol = db.Column(db.String(20))
    layer4_port = db.Column(db.Integer)
    layer7_value = db.Column(db.String(50))
    comments = db.Column(db.String(255))
    change_request_id = db.Column(db.Integer, db.ForeignKey('change_request.id'))


location_mapping_table = db.Table('location_mapping_table',
                                    db.Column('device_profile_id',
                                    db.Integer,db.ForeignKey('device_profile.id'), nullable=False),
                                  db.Column('location_id',db.Integer,db.ForeignKey('location.id'),
                                    nullable=False),
                                  db.PrimaryKeyConstraint('device_profile_id', 'location_id')
                                  )


class Device(Base):
    """Device model

    Represents the connection parameters user to instanciate a firewall
    device in orangengine.
    """

    __tablename__ = 'device'
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    apikey = db.Column(db.String(255), default=None)
    hostname = db.Column(db.String(255))
    driver = db.Column(db.String(30))
    refresh_interval = db.Column(db.Integer(), default=60)
    common_name = db.Column(db.String(255))
    device_profiles = db.relationship('DeviceProfile', backref='device', lazy='dynamic',
                                      cascade="all,delete")
    __table_args__ = (db.UniqueConstraint('hostname', name='_hostname_uc'),
                     )

    def serialize(self):
        """Override to leave out password and apikey as these are protected
        and manually include relationsips"""
        data = super(Device, self).serialize()
        data.pop('password')
        data.pop('apikey')
        data.update({'device_profiles': [v.serialize() for v in self.device_profiles]})
        return data


class DeviceProfile(Base):
    """Device Profile model
    The profile makes the location and zone mappings
    This allows us to interact with devices like Panorama
    which are management platforms that aggregate many devices
    """

    __tablename__ = 'device_profile'
    name = db.Column(db.String(255))
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    zone_mappings = db.relationship('ZoneMapping', backref='device_profile', lazy='dynamic',
                                    cascade="all,delete")
    zone_mapping_rules = db.relationship('ZoneMappingRule', backref='device_profile',
                                         lazy='dynamic', cascade="all,delete",)
    locations = db.relationship('Location', secondary=location_mapping_table,
                                backref='device_profile')

    def serialize(self):
        """Override to manually include relationsips"""
        data = super(DeviceProfile, self).serialize()
        data.update({
            'zone_mappings': [v.serialize() for v in self.zone_mappings],
            'zone_mapping_rules': [v.serialize() for v in self.zone_mapping_rules],
            'locations': [v.serialize() for v in self.locations],
        })
        return data


class Location(Base):
    """Location Model

    A location represents a region within a network. Locations allow us to map network
    locations to devices
    """

    __tablename__ = 'location'
    name = db.Column(db.String(255), nullable=False)
    __table_args__ = (db.UniqueConstraint('name', name='_name_uc'),
                     )


class ZoneMapping(Base):
    """Zone Mapping model

    Represents a zone mapping for a device. A zone mapping is key/value lookup
    for network to zone containment on a firewall.

    i.e., 10.0.0.0/24 -> untrust

    These mappings are used to figure out which zone a network or IP belongs to
    when generating a firewall policy on a zone based firewall.
    """

    __tablename__ = 'zone_mapping'
    device_profile_id = db.Column(db.Integer, db.ForeignKey('device_profile.id'))
    zone_name = db.Column(db.String(255), nullable=False)
    network = db.Column(CIDR, nullable=False)
    __table_args__ = (db.UniqueConstraint('device_profile_id', 'zone_name', 'network',
                                          name='_zone_network_mapping_uc'),
                     )


class ZoneMappingRule(Base):
    """Zone Mapping Rule model

    Prepresents a logical rule for mapping zones in special cases where
    routing on the firewall requires a specific destination zone to be used
    that would not normally be matched in this case.

    They come in the form of:
    source zone -> destination network = destination zone
    """

    __tablename__ = 'zone_mapping_rules'
    device_profile_id = db.Column(db.Integer, db.ForeignKey('device_profile.id'))
    source_zone_name = db.Column(db.String(255), nullable=False)
    destination_network = db.Column(CIDR, nullable=False)
    destination_zone_name = db.Column(db.String(255), nullable=False)
    __table_args__ = (db.UniqueConstraint('device_profile_id', 'source_zone_name',
                                          'destination_network', 'destination_zone_name'),
                     )


# USER MODELS FOR AUTHENTICATION


class User(Base):
    """ User Model for storing user related details """
    __tablename__ = "user"

    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, email, password, admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
        self.admin = admin

    def change_password(self, password):
        logger.debug("changing password for %s" % self.email )
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=0),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Validates the auth token
        :param auth_token:
        :return: integer|string
        """
        # logger.debug("decoding aut_token: %s" % auth_token)
        try:
            # strip any quotes
            auth_token = auth_token.strip('"')
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

    def serialize(self):
        pass


class BlacklistToken(Base):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_token'

    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False
