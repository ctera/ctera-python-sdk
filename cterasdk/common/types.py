import re
from datetime import datetime
from collections import namedtuple

from .object import Object
from .utils import df_military_time, day_of_week
from .enum import FileCriteria, BooleanFunction, Application, ScheduleType


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


class IncludeOperator(Operator):
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


class PredefinedListCriteriaBuilder(CriteriaBuilder):

    def include(self, values):
        self.operator = IsOneOfOperator(values)
        return self


class CustomListCriteriaBuilder(CriteriaBuilder):

    def include(self, values):
        self.operator = IncludeOperator(values)
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
        self.schedule = None

    def to_server_object(self):
        param = Object()
        param._classname = 'SyncThrottlingSettings'  # pylint: disable=protected-access
        param.inKbitsPerSecond = self.download
        param.outKbitsPerSecond = self.upload
        param.schedule = self.schedule
        return param

    @staticmethod
    def from_server_object(param):
        r = ThrottlingRule()
        r.download = param.inKbitsPerSecond
        r.upload = param.outKbitsPerSecond
        r.schedule = param.schedule
        return r

    def __str__(self):
        return str(dict(upload_kbps=self.upload, download_kbps=self.download,
                        start=self.schedule.start, end=self.schedule.end, days=[day_of_week(day) for day in self.schedule.days]))


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

    def schedule(self, schedule):
        """
        Set the throttling rule schedule

        :param cterasdk.common.types.TimeRange schedule: Schedule
        """
        self.param.schedule = schedule
        return self

    def build(self):
        """
        Build the throttling rule
        """
        errors = [k for k, v in self.param.__dict__.items() if v is None]
        if errors:
            raise ValueError(f'No value for required field: {errors}')
        return self.param


class FileFilterBuilder:

    Type = 'File'

    @staticmethod
    def extensions():
        """Filter files by extension"""
        return PredefinedListCriteriaBuilder(FileFilterBuilder.Type, FileCriteria.Type)

    @staticmethod
    def names():
        """Filter files by names"""
        return PredefinedListCriteriaBuilder(FileFilterBuilder.Type, FileCriteria.Name)

    @staticmethod
    def name():
        """Filter files by name pattern"""
        return StringCriteriaBuilder(FileFilterBuilder.Type, FileCriteria.Name)

    @staticmethod
    def paths():
        """Filter files by path"""
        return PredefinedListCriteriaBuilder(FileFilterBuilder.Type, FileCriteria.Path)

    @staticmethod
    def path():
        """Filter files by path pattern"""
        return StringCriteriaBuilder(FileFilterBuilder.Type, FileCriteria.Path)

    @staticmethod
    def size():
        """Filter files by size"""
        return IntegerCriteriaBuilder(FileFilterBuilder.Type, FileCriteria.Size)

    @staticmethod
    def last_modified():
        """Filter files by last modification date"""
        return DateTimeCriteriaBuilder(FileFilterBuilder.Type, FileCriteria.Modified)


class DirectoryEntryFactory:

    @staticmethod
    def root(included):
        return DirEntry('root', included=included)


class FileEntry(Object):

    def __init__(self, name, display_name=None, included=None):
        self._classname = self.__class__.__name__  # pylint: disable=protected-access
        self.name = name
        self.displayName = display_name
        self.isIncluded = included


class DirEntry(FileEntry):

    def __init__(self, name, display_name=None, included=None, children=None):
        super().__init__(name, display_name, included)
        self.children = children


class BackupSet(Object):

    def __init__(self, name, directory_tree=None, filter_rules=None, defaults_dirs=None,
                 template_dirs=None, enabled=True, boolean_function=None, comment=None):
        self._classname = self.__class__.__name__  # pylint: disable=protected-access
        self.name = name
        self.isEnabled = enabled
        self.directoryTree = directory_tree if directory_tree else DirectoryEntryFactory.root(True)
        self.booleanFunction = boolean_function if boolean_function else BooleanFunction.AND
        self.templateDirectories = template_dirs
        self.defaultDirs = defaults_dirs
        self.comment = comment
        self.filterRules = filter_rules


class FilterBackupSet(BackupSet):
    pass


class ApplicationBackupSet(BackupSet):

    def __init__(self, apps):

        comment = 'Backup all the specified applications'
        name = 'Applications'

        if apps == Application.All:
            super().__init__(name=name, directory_tree=DirEntry(name, included=True), comment=comment)
        else:
            directory_tree = DirEntry(name, included=False, children=[DirEntry(app, included=True) for app in apps])
            super().__init__(name=name, directory_tree=directory_tree, comment=comment)

        self._classname = None


class TaskSchedule(Object):

    def __init__(self):
        self._classname = 'TaskSchedule'  # pylint: disable=protected-access
        self.mode = None


class BackupScheduleBuilder:

    @staticmethod
    def interval(hours=None, minutes=None):
        """
        Schedule backup to periodically, defaults to 24 hours

        :param int hours: Hours
        :param int minutes: Minutes
        """
        param = TaskSchedule()
        param.mode = ScheduleType.Interval
        param.interval = Object()  # pylint: disable=attribute-defined-outside-init
        param.interval.hours = hours if hours is not None else 24
        param.interval.minutes = minutes if minutes is not None else 0
        return param

    @staticmethod
    def window(time_range):
        """
        Schedule backup to run at a specific time

        :param cterasdk.common.types.TimeRange time_range: Time range
        """
        param = TaskSchedule()
        param.mode = ScheduleType.Window
        param.window = time_range  # pylint: disable=attribute-defined-outside-init
        return param


class TimeRange:
    """ Class representing a task schedule """

    def __init__(self):
        self.param = Object()
        self.param._classname = 'TimeRange'  # pylint: disable=protected-access
        self.param.start = None
        self.param.end = None
        self.param.days = None
        self.param.termOnEnd = False

    def start(self, start):
        """
        Start time

        :param str start: A military time string 'hh:mm:ss' or a datetime object
        """
        self.param.start = TimeRange._infer_time_range(start)
        return self

    def end(self, end):
        """
        End time

        :param str end: A military time string 'hh:mm:ss' or a datetime object
        """
        self.param.end = TimeRange._infer_time_range(end)
        return self

    def days(self, days):
        """
        Set days

        :param list[cterasdk.common.enum.DayOfWeek] days: A list of days
        """
        self.param.days = days
        return self

    def terminate_at_endtime(self):
        """
        Terminate at end time, defaults to teminate on completion.
        """
        self.param.termOnEnd = True
        return self

    def build(self):
        """
        Build the time range
        """
        if self.param.termOnEnd and self.param.end is None:
            raise ValueError('End time required')
        if self.param.start is None:
            raise ValueError('Start time required')
        return self.param

    @staticmethod
    def _infer_time_range(time):
        if isinstance(time, datetime):
            return df_military_time(time)
        if isinstance(time, str):
            match = re.search('^[012][0-9]:[0-5][0-9]:[0-5][0-9]$', time)
            if match:
                return match.group(0)
            raise ValueError("Invalid time format. Expected 'hh:mm:ss'")
        raise ValueError("Invalid format. Expected 'datetime' or 'str'")

    def __str__(self):
        return str(self.param)


class ADDomainIDMapping(Object):
    """
    Base Class for Directory Service ID Mapping

    :ivar str domain: The domain flat name
    :param int start: The minimum id to use for mapping
    :param int end: The maximum id to use for mapping
    """
    def __init__(self, domain, start, end):
        self._classname = 'ADDomainIDMapping'
        self.domainFlatName = domain
        self.minID = start
        self.maxID = end


class SoftwareUpdatePolicyBuilder:
    """
    Software Update Policy Builder
    """

    def __init__(self):
        self.param = SoftwareUpdatesTopic(enabled=True, reboot_after_update=True, reboot_when=None)

    def download_and_install(self, download_and_install):
        """
        Download and install updates automatically.
        :param bool download_and_install: Set ``True`` to enable and ``False`` to disable.
        """
        self.param.download_and_install(download_and_install)
        return self

    def reboot_after_update(self, reboot_after_update):
        """
        Restart device automatically after installing new firmware

        :param bool reboot_after_update: Set ``True`` to enable and ``False`` to disable.
        """
        self.param.reboot_after_update(reboot_after_update)
        return self

    def schedule(self, schedule):
        """
        Set the throttling rule schedule

        :param cterasdk.common.types.TimeRange schedule: Schedule
        """
        self.param.schedule(schedule)
        return self

    def build(self):
        """
        Build the Software Update Policy
        """
        if self.param.rebootAfterUpdate is False:
            self.param.reboot_asap()
        return self.param


class SoftwareUpdatesTopic(Object):

    def __init__(self, enabled, reboot_after_update, reboot_when):
        self._classname = "SoftwareUpdatesSettings"
        self.enabled = enabled if enabled else None
        self.rebootAfterUpdate = reboot_after_update if reboot_after_update else None
        self.rebootWhen = reboot_when if reboot_when else None

    def download_and_install(self, enabled):
        self.enabled = enabled

    def reboot_after_update(self, enabled):
        self.rebootAfterUpdate = enabled

    def reboot_asap(self):
        self.rebootWhen = None

    def schedule(self, window):
        self.rebootWhen = Object()
        self.rebootWhen.mode = ScheduleType.Window
        self.rebootWhen.window = window


ConsentPage = namedtuple('ConsentPage', ('header', 'body'))
ConsentPage.__doc__ = 'Tuple holding the consent page header and body'
ConsentPage.header.__doc__ = 'The consent page header'
ConsentPage.body.__doc__ = 'The consent page body'
