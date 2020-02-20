import logging


def set_timezone(ctera_host, timezone):
    logging.getLogger().info("Updating timezone. %s", {'timezone' : timezone})

    ctera_host.put('/config/time/TimeZone', timezone)

    logging.getLogger().info("Timezone updated. %s", {'timezone' : timezone})
