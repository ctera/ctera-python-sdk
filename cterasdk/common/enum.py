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


class Application:
    """
    Application

    :ivar str All: All Applications
    :ivar str Exchange: Microsoft Exchange
    :ivar str SQL: Microsoft SQL Server
    :ivar str NTDS: Active Directory Users and Groups
    :ivar str DFS: DFS Replication Service
    :ivar str FRS: File Replication Service
    :ivar str System: System State
    :ivar str HyperV: Hyper-V
    :ivar str SharePoint_07: SharePoint 2007
    :ivar str SharePoint: SharePoint
    """
    Exchange = '{76fe1ac4-15f7-4bcd-987e-8e1acb462fb7}'
    SQL = '{a65faa63-5ea8-4ebc-9dbd-a0c4db26912a}'
    NTDS = '{b2014c9e-8711-4c5c-a5a9-3cf384484757}'
    DFS = '{2707761b-2324-473d-88eb-eb007a359533}'
    FRS = '{d76f5a28-3092-4589-ba48-2958fb88ce29}'
    System = '{db7f098c-121b-46fe-814b-58902de3a193}'
    HyperV = '{66841cd4-6ded-4f4b-8f17-fd23f8ddc3de}'
    SharePoint_07 = '{c2f52614-5e53-4858-a589-38eeb25c6184}'
    SharePoint = '{da452614-4858-5e53-a512-38aab25c61ad}'
    All = [Exchange, SQL, NTDS, DFS, FRS, System, HyperV, SharePoint_07, SharePoint]


class ScheduleType:
    """
    Schedule Type

    :ivar str Manual: Manual
    :ivar str Hourly: Hourly
    :ivar str Daily: Daily
    :ivar str Weekly: Weekly
    :ivar str Monthly: Monthly
    :ivar str Interval: Interval
    :ivar str Window: Window
    """
    Manual = 'manual'
    Hourly = 'hourly'
    Daily = 'daily'
    Weekly = 'weekly'
    Monthly = 'monthly'
    Interval = 'interval'
    Window = 'window'
