
import datetime
import jwt
from api import db, app, bcrypt, logger
import enum
from sqlalchemy.dialects.postgresql import CIDR


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

    The implementation of a cahnge request is what we are actually trying
    to automate here...
    """

    class StateOptions(enum.Enum):
        """Enum options for state"""
        open = 'open'
        closed = 'closed'
        completed = 'completed'

    __tablename__ = 'change_request'
    summary = db.Column(db.String(255))
    requestor = db.Column(db.String(255))
    application = db.Column(db.String(255))
    source_location = db.Column(db.String(255))
    destination_location = db.Column(db.String(255))
    action = db.Column(db.String(255))
    status = db.Column(db.Enum(StateOptions), default=StateOptions.open)


class Device(Base):
    """Device model

    Represents the connection parameters user to instanciate a firewall
    device in orangengine.
    """

    class DriverOptions(enum.Enum):
        """Enum options for device_type for driver selection in orangengine"""
        juniper_srx = 'juniper_srx'
        palo_alto_panorama = 'palo_alto_panorama'

    __tablename__ = 'device'
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    apikey = db.Column(db.String(255), default=None)
    hostname = db.Column(db.String(255))
    driver = db.Column(db.Enum(DriverOptions))
    refresh_interval = db.Column(db.Integer(), default=60)
    common_name = db.Column(db.String(255))
    zone_mappings = db.relationship('ZoneMapping', backref='device', lazy='dynamic',
                                    cascade="all,delete")
    zone_mapping_rules = db.relationship('ZoneMappingRule', backref='device', lazy='dynamic',
                                         cascade="all,delete",)
    supplemental_device_params = db.relationship('SupplementalDeviceParam', backref='device',
                                                 lazy='dynamic', cascade="all,delete",)
    __table_args__ = (db.UniqueConstraint('hostname', name='_hostname_uc'),
                     )

    def serialize(self):
        """Override to leave out password and apikey as these are protected"""
        data = super(Device, self).serialize()
        data.pop('password')
        data.pop('apikey')
        return data


class SupplementalDeviceParam(Base):
    """Supplemental Device Param

    These get passed to the orangengine driver when dispatching a new device.
    They are the params that are specific to that driver.
    """

    __tablename__ = 'supplemental_device_param'
    name = db.Column(db.String(255), nullable=False)
    value = db.Column(db.String(255), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    __table_args__ = (db.UniqueConstraint('device_id', 'name', name='_device_param_uc'),
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
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    zone_name = db.Column(db.String(255), nullable=False)
    network = db.Column(CIDR, nullable=False)
    __table_args__ = (db.UniqueConstraint('device_id', 'zone_name', 'network',
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
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    source_zone_name = db.Column(db.String(255), nullable=False)
    destination_network = db.Column(CIDR, nullable=False)
    destination_zone_name = db.Column(db.String(255), nullable=False)
    __table_args__ = (db.UniqueConstraint('device_id', 'source_zone_name',
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
