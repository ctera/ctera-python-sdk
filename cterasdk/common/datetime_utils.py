import datetime


class DateTimeUtils():
    @staticmethod
    def get_expiration_date(expiration):
        """
        Get a datetime.date representation of the expiration date

        :param variable,optional expiration:
            The expiration value.
            Pass datetime.date for a specific date, integer for days from now, or True for immediate (yesterday)
        :return datetime.date: datetime.date representation of the expiration date
        """
        if isinstance(expiration, bool):
            expiration_date = datetime.date.today() - datetime.timedelta(days=1)
        elif isinstance(expiration, int):
            expiration_date = datetime.date.today() + datetime.timedelta(days=expiration)
        elif isinstance(expiration, datetime.date):
            expiration_date = expiration
        return expiration_date
