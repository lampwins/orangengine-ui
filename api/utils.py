
from flask import json
import enum


class OEUIJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, enum.Enum):
            return o.value
        return json.JSONEncoder.default(self, o)
