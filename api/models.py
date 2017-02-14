
from api import db

# A base model for other database tables to inherit
class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified_at = db.Column(db.DateTime, default=db.func.current_timestamp(),
                            onupdate=db.func.current_timestamp())

#added
class ChangeRequest(Base):
    summary = db.Column(db.String(255))
    requestor = db.Column(db.String(255))
    application = db.Column(db.String(255))
    source_location = db.Column(db.String(255))
    destination_location = db.Column(db.String(255))
    action = db.Column(db.String(255))



    def __init__(self, summary, requestor, application, source_location, destination_location, action):
        self.summary = summary
        self.requestor = requestor
        self.application = application
        self.source_location = source_location
        self.destination_location = destination_location
        self.action = action

#endAdded