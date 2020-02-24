import logging

from ..common import Object
from ..exception import CTERAException


def add_first_user(ctera_host, username, password, email):
    info = ctera_host.get('/nosession/logininfo')
    if info.isfirstlogin:
        user = Object()
        user.username = username
        user.password = password
        user.email = email
        ctera_host.post('/nosession/createfirstuser', user)
        logging.getLogger().info('User created. %s', {'user': username})
    else:
        logging.getLogger().info('Skipping. root account already exists.')
    ctera_host.login(username, password)


def add(ctera_host, username, password, fullName, email, uid):
    user = Object()
    user.username = username
    user.password = password
    user.fullName = fullName
    user.email = email
    user.uid = uid
    try:
        response = ctera_host.add('/config/auth/users', user)
        logging.getLogger().info("User created. %s", {'username': user.username})
        return response
    except CTERAException as error:
        logging.getLogger().error("User creation failed.")
        raise CTERAException('User creation failed', error)


def delete(ctera_host, username):
    try:
        response = ctera_host.delete('/config/auth/users/' + username)
        logging.getLogger().info("User deleted. %s", {'username': username})
        return response
    except Exception as error:
        logging.getLogger().error("User deletion failed.")
        raise CTERAException('User deletion failed', error)
