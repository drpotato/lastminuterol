#!/usr/bin/env python 
# -*- coding: utf-8 -*-

__author__ = 'Chris Morgan'

from main import generate_rol

import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote


class RolMessage(messages.Message):
    text = messages.StringField(1)


@endpoints.api(name='rol', version='v1')
class RolApi(remote.Service):
    """Reflection on Learning API v1."""
    @endpoints.method(message_types.VoidMessage, RolMessage, path='rol', http_method='GET', name='rol')
    def greetings_list(self, _):
        return RolMessage(text=generate_rol())

APPLICATION = endpoints.api_server([RolApi])