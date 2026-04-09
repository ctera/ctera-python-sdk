from .uri import components, parse_qsl


def validate(uri):
    r = components(uri)

    assert r.scheme == "https", f"Error: Expected 'https' scheme, got '{r.scheme}'."
    assert r.netloc, "Error: Could not identify network location."
    assert r.path == "/invitations/", f"Error: Expected '/invitations/' path, got '{r.path}'."

    parameters = parse_qsl(r.query)

    if parameters and parameters[0][0] == "share":
        invite = parameters[0][1]

        assert invite, "Error: Invitation identifier not found."
        assert invite.isalnum(), f"Invitation identifier '{invite}' must be alphanumeric."

        return r.hostname, r.port, invite

    raise ValueError("Error: Could not find invitation identifer.")


def uri(invitation):
    return f'{invitation.clients.ctera.baseurl}/?share={invitation.invite}'
