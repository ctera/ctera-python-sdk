import logging

from . import session


def login(ctera_host, username, password):
    ctera_host.form_data('/login', {'j_username' : username, 'j_password' : password})

    logging.getLogger().info("User logged in. %s", {'host' : ctera_host.host(), 'user': username})

    session.activate(ctera_host)


def logout(ctera_host):
    ctera_host.form_data('/logout', {})

    logging.getLogger().info("User logged out. %s", {'host' : ctera_host.host()})

    session.terminate(ctera_host)
