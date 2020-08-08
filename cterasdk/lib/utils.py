import base64


def merge(d1, d2):
    d1 = d1 if d1 else {}
    if d2:
        d1.update(d2)
    return d1


def b64decode(base64_message):
    base64_bytes = base64_message.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    return message_bytes.decode('ascii')
