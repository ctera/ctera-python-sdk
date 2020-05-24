import json


class Object:  # pylint: disable=too-many-instance-attributes
    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=5)
