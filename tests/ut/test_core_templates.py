# pylint: disable=protected-access
from unittest import mock

from cterasdk.common import Object
from cterasdk.core import templates
from tests.ut import base_core


class TestCoreTemplates(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._template = 'Template'
        self._template_classname = 'DeviceTemplate'

    def test_get_template_default_attrs(self):
        get_multi_response = self._get_template_object(name=self._template)
        self._init_global_admin(get_multi_response=get_multi_response)
        ret = templates.Templates(self._global_admin).get(self._template)
        self._global_admin.get_multi.assert_called_once_with('/deviceTemplates/' + self._template, mock.ANY)
        expected_include = ['/' + attr for attr in templates.Templates.default]
        actual_include = self._global_admin.get_multi.call_args[0][1]
        self.assertEqual(len(expected_include), len(actual_include))
        for attr in expected_include:
            self.assertIn(attr, actual_include)
        self.assertEqual(ret.name, self._template)

    def test_list_templates_default_attrs(self):
        with mock.patch("cterasdk.core.templates.query.iterator") as query_iterator_mock:
            templates.Templates(self._global_admin).list_templates()
            query_iterator_mock.assert_called_once_with(self._global_admin, '/deviceTemplates', mock.ANY)
            expected_query_params = base_core.BaseCoreTest._create_query_params(include=templates.Templates.default,
                                                                                start_from=0, count_limit=50)
            actual_query_params = query_iterator_mock.call_args[0][2]
            self._assert_equal_objects(actual_query_params, expected_query_params)

    def test_delete_template(self):
        delete_response = 'Success'
        self._init_global_admin(delete_response=delete_response)
        ret = templates.Templates(self._global_admin).delete(self._template)
        self._global_admin.delete.assert_called_once_with('/deviceTemplates/' + self._template)
        self.assertEqual(ret, delete_response)

    def test_set_default_template_no_wait(self):
        execute_response = 'Success'
        self._init_global_admin(execute_response=execute_response)
        ret = templates.Templates(self._global_admin).set_default(self._template)
        self._global_admin.execute.assert_has_calls([
            mock.call('/deviceTemplates/' + self._template, 'setAsDefault'),
            mock.call('', 'applyAutoAssignmentRules')
        ])
        self.assertEqual(ret, execute_response)

    def test_remove_default_template_no_wait(self):
        execute_response = 'Success'
        get_multi_response = self._get_template_object(name=self._template, isDefault=True)
        self._init_global_admin(get_multi_response=get_multi_response, execute_response=execute_response)
        ret = templates.Templates(self._global_admin).remove_default(self._template)
        self._global_admin.get_multi.assert_called_once_with(f'/deviceTemplates/{self._template}', mock.ANY)
        self._global_admin.execute.assert_has_calls([
            mock.call('', 'removeDefaultDeviceTemplate'),
            mock.call('', 'applyAutoAssignmentRules')
        ])
        self.assertEqual(ret, execute_response)

    def _get_template_object(self, **kwargs):
        template_object = Object()
        template_object._classname = self._template_classname  # pylint: disable=protected-access
        for key, value in kwargs.items():
            setattr(template_object, key, value)
        return template_object
