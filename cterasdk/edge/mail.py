import logging

from ..common import Object


def enable(ctera_host, SMTPServer, port, username, password, useTLS):
    settings = ctera_host.get('/config/logging/alert')
    settings.useCustomServer = True
    settings.SMTPServer = SMTPServer

    if settings.port != port:
        settings.port = port

    if username is not None and password is not None:
        settings.useAuth = True
        settings.auth = Object()
        settings.auth.username = username
        settings.auth.password = password

    if settings.useTLS != useTLS:
        settings.useTLS = useTLS

    logging.getLogger().info('Enabling mail server.')

    ctera_host.put('/config/logging/alert', settings)

    logging.getLogger().info(
        'Updated mail server settings. %s',
        {'SMTPServer': SMTPServer, 'port': port, 'username': username, 'useTLS': useTLS}
    )


def disable(ctera_host):
    logging.getLogger().info('Disabling mail server.')
    ctera_host.put('/config/logging/alert/useCustomServer', False)
    logging.getLogger().info('Mail server disabled.')
