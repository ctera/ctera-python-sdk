class DayOfWeek:
    """
    Day of Week

    :ivar int Sunday: Sunday
    :ivar int Monday: Monday
    :ivar int Tuesday: Tuesday
    :ivar int Wednesday: Wednesday
    :ivar int Thursday: Thursday
    :ivar int Friday: Friday
    :ivar int Saturday: Saturday
    """
    Sunday = 0
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6
    Weekdays = [Monday, Tuesday, Wednesday, Thursday, Friday]
    Weekend = [Saturday, Sunday]
    All = [Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday]


class FileCriteria:
    """
    File Criteria

    :ivar str Name: File name
    :ivar str Path: File path
    :ivar str Type: File type
    :ivar str Size: File size
    :ivar str Modified: Last modified
    """
    Name = 'FileName'
    Path = 'PathName'
    Type = 'FileType'
    Size = 'FileSize'
    Modified = 'LastModified'


class BooleanFunction:
    """
    Boolean function

    :ivar str AND: AND
    :ivar str AND: OR
    """
    AND = 'AND'
    OR = 'OR'
