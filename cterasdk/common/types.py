import re
from datetime import datetime

from .object import Object
from .utils import df_military_time, day_of_week


class PolicyRule:

    def __init__(self, assignment, criteria):
        self.assignment = assignment
        self.criteria = criteria


class PolicyRuleConverter:

    @staticmethod
    def convert(rule, classname, property_name, assignment=None):
        param = Object()
        param._classname = classname  # pylint: disable=protected-access
        setattr(param, property_name, assignment if assignment else rule.assignment)
        param.filterRule = rule.criteria
        return param


class Operator(Object):

    def __init__(self, right):
        self._classname = self.__class__.__name__  # pylint: disable=protected-access
        self.right = right


class IsOperator(Operator):
    pass


class BeginsWithOperator(Operator):
    pass


class EndsWithOperator(Operator):
    pass


class ContainsOperator(Operator):
    pass


class IsOneOfOperator(Operator):
    pass


class LessThanOperator(Operator):
    pass


class MoreThanOperator(Operator):
    pass


class BeforeOperator(Operator):
    pass


class AfterOperator(Operator):
    pass


class AdvancedFilterRule(Object):

    def __init__(self, classname, field, operator):
        self._classname = self.__class__.__name__  # pylint: disable=protected-access
        self.className = classname
        self.fieldName = field
        self.operator = operator


class CriteriaBuilder:

    def __init__(self, criteria_type, criteria_field):
        self.criteria_type = criteria_type
        self.criteria_field = criteria_field
        self.operator = None

    def build(self):
        return AdvancedFilterRule(self.criteria_type, self.criteria_field, self.operator)


class ListCriteriaBuilder(CriteriaBuilder):

    def include(self, values):
        self.operator = IsOneOfOperator(values)
        return self


class IntegerCriteriaBuilder(CriteriaBuilder):

    def less_than(self, value):
        self.operator = LessThanOperator(value)
        return self

    def more_than(self, value):
        self.operator = MoreThanOperator(value)
        return self


class DateTimeCriteriaBuilder(CriteriaBuilder):

    def before(self, value):
        self.operator = BeforeOperator(value)
        return self

    def after(self, value):
        self.operator = AfterOperator(value)
        return self


class StringCriteriaBuilder(CriteriaBuilder):

    def equals(self, value):
        self.operator = IsOperator(value)
        return self

    def startswith(self, value):
        self.operator = BeginsWithOperator(value)
        return self

    def endswith(self, value):
        self.operator = EndsWithOperator(value)
        return self

    def contains(self, value):
        self.operator = ContainsOperator(value)
        return self

    def isoneof(self, values):
        self.operator = IsOneOfOperator(values)
        return self


class ThrottlingRule:
    """
    Throttling Rule

    :ivar int upload: Throttling rate upstream (Kilobits)
    :ivar int download: Throttling rate downstream (Kilobits)
    :ivar str start: Start time
    :ivar str end: End time
    :ivar list[str] days: Days
    """

    def __init__(self):
        self.upload = None
        self.download = None
        self.start = None
        self.end = None
        self.days = None

    def to_server_object(self):
        param = Object()
        param._classname = 'SyncThrottlingSettings'  # pylint: disable=protected-access
        param.inKbitsPerSecond = self.download
        param.outKbitsPerSecond = self.upload
        param.schedule = Object()
        param.schedule._classname = 'TimeRange'  # pylint: disable=protected-access
        param.schedule.start = self.start
        param.schedule.end = self.end
        param.schedule.days = self.days
        param.termOnEnd = False
        return param

    @staticmethod
    def from_server_object(param):
        r = ThrottlingRule()
        r.download = param.inKbitsPerSecond
        r.upload = param.outKbitsPerSecond
        r.start = param.schedule.start
        r.end = param.schedule.end
        r.days = param.schedule.days
        return r

    def __str__(self):
        return str(dict(upload_kbps=self.upload, download_kbps=self.download,
                        start=self.start, end=self.end, days=[day_of_week(day) for day in self.days]))


class ThrottlingRuleBuilder:
    """
    Bandwidth Throttling Rule Builder
    """

    def __init__(self):
        self.param = ThrottlingRule()

    def upload(self, kbps):
        """
        Throttle bandwidth upstream

        :param int kbps: Kilobits per second
        """
        self.param.upload = kbps
        return self

    def download(self, kbps):
        """
        Throttle bandwidth downstream

        :param int kbps: Kilobits per second
        """
        self.param.download = kbps
        return self

    def start(self, start):
        """
        Start throttling

        :param str start: A military time string 'hh:mm:ss' or a datetime object
        """
        self.param.start = ThrottlingRuleBuilder._infer_time(start)
        return self

    def end(self, end):
        """
        End throttling

        :param str end: A military time string 'hh:mm:ss' or a datetime object
        """
        self.param.end = ThrottlingRuleBuilder._infer_time(end)
        return self

    @staticmethod
    def _infer_time(time):
        if isinstance(time, datetime):
            return df_military_time(time)
        if isinstance(time, str):
            match = re.search('^[012][0-9]:[0-5][0-9]:[0-5][0-9]$', time)
            if match:
                return match.group(0)
            raise ValueError("Invalid time format. Expected 'hh:mm:ss'")
        raise ValueError("Invalid format. Expected 'datetime' or 'str'")

    def days(self, days):
        """
        Throttle on days

        :param list[cterasdk.common.enum.DayOfWeek] days: A list of days
        """
        self.param.days = days
        return self

    def build(self):
        """
        Build the throttling rule
        """
        errors = [k for k, v in self.param.__dict__.items() if v is None]
        if errors:
            raise ValueError('No value for required field: %s' % errors)
        return self.param
