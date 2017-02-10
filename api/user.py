#!/usr/bin/env python
#
# Copyright (c) 2016 Jonathan Yantis
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# pylint: disable=E1101
"""
API User Functions
"""
import sys
import logging
import time
from passlib.hash import sha256_crypt
from api import db, app
from api.models import Base
from flask_security import (http_auth_required, auth_token_required,
                            Security, RoleMixin, UserMixin, SQLAlchemyUserDatastore)
from flask_security.utils import encrypt_password

logger = logging.getLogger(__name__)


roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(),
                                 db.ForeignKey('auth_user.id')),
                       db.Column('role_id', db.Integer(),
                                 db.ForeignKey('auth_role.id')))


class Role(Base, RoleMixin):
    __tablename__ = 'auth_role'
    name = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.String(255))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Role %r>' % self.name


class User(Base, UserMixin):
    __tablename__ = 'auth_user'
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(45))
    current_login_ip = db.Column(db.String(45))
    login_count = db.Column(db.Integer)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<User %r>' % self.email

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


def add_user(username, passwd):
    """
    Add a new user to the database
    """
    if not User.query.first():
        user_datastore.create_user(email=username, password=encrypt_password(passwd))
        db.session.commit()
        return True
    return False

def del_user(username):
    """ Delete a user from the database """

    user = User.query.filter_by(email=username).first()

    if user:
        logger.info("Deleting user: %s", username)

        db.session.delete(user)
        db.session.commit()

        return True
    else:
        logger.error("Error: User does not exists in DB")
        exit(1)
