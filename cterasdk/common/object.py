import json

class Object:
    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=5)
