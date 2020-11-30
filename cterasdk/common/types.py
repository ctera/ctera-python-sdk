from .object import Object


class PolicyRule:

    def __init__(self, assignment, criteria):
        self.assignment = assignment
        self.criteria = criteria


class PolicyRuleCoverter:

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
