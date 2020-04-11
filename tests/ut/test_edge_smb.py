from unittest import mock

from cterasdk import exception
from cterasdk.common import Object
from cterasdk.edge import smb
from cterasdk.edge.enum import Mode, CIFSPacketSigning
from tests.ut import base_edge


class TestEdgeSMB(base_edge.BaseEdgeTest):

    def test_disable_smb(self):
        self._init_filer()
        smb.SMB(self._filer).disable()
        self._filer.put.assert_called_once_with('/config/fileservices/cifs/mode', Mode.Disabled)

    def test_enable_smb(self):
        self._init_filer()
        smb.SMB(self._filer).enable()
        self._filer.put.assert_called_once_with('/config/fileservices/cifs/mode', Mode.Enabled)

    def test_enable_abe(self):
        self._init_filer()
        smb.SMB(self._filer).enable_abe()
        self._filer.put.assert_called_once_with('/config/fileservices/cifs/hideUnreadable', True)

    def test_disable_abe(self):
        self._init_filer()
        smb.SMB(self._filer).disable_abe()
        self._filer.put.assert_called_once_with('/config/fileservices/cifs/hideUnreadable', False)

    def test_disable_packet_signing(self):
        self._init_filer()
        smb.SMB(self._filer).set_packet_signing(CIFSPacketSigning.Disabled)
        self._filer.put.assert_called_once_with('/config/fileservices/cifs/packetSigning', CIFSPacketSigning.Disabled)

    def test_packet_signing_if_client_agrees(self):
        self._init_filer()
        smb.SMB(self._filer).set_packet_signing(CIFSPacketSigning.IfClientAgrees)
        self._filer.put.assert_called_once_with('/config/fileservices/cifs/packetSigning', CIFSPacketSigning.IfClientAgrees)

    def test_required_packet_signing(self):
        self._init_filer()
        smb.SMB(self._filer).set_packet_signing(CIFSPacketSigning.Required)
        self._filer.put.assert_called_once_with('/config/fileservices/cifs/packetSigning', CIFSPacketSigning.Required)

    def test_set_packet_signing_raise_input_error(self):
        with self.assertRaises(exception.InputError) as error:
            smb.SMB(self._filer).set_packet_signing('Invalid argument')
        self.assertEqual('Invalid packet signing option', error.exception.message)

    def test_set_packet_signing_raise_error(self):
        expected_exception = exception.CTERAException()
        self._filer.put = mock.MagicMock(side_effect=expected_exception)
        with self.assertRaises(exception.CTERAException) as error:
            smb.SMB(self._filer).set_packet_signing(CIFSPacketSigning.Disabled)
        self.assertEqual('Invalid packet signing co', error.exception.message)

    def test_get_configuration(self):
        self._init_filer(get_response=TestEdgeSMB._get_cifs_configuration_response())
        ret = smb.SMB(self._filer).get_configuration()
        self._filer.get.assert_called_once_with('/config/fileservices/cifs')
        self._assert_equal_objects(ret, TestEdgeSMB._get_configuration_response())

    def test_modify_success(self):
        self._init_filer(get_response=TestEdgeSMB._get_cifs_configuration_response())
        smb.SMB(self._filer).modify(CIFSPacketSigning.Required, 20, True, False, False)
        self._filer.get.assert_called_once_with('/config/fileservices/cifs')
        self._filer.put.assert_called_once_with('/config/fileservices/cifs', mock.ANY)
        expected_param = TestEdgeSMB._get_cifs_configuration_response(CIFSPacketSigning.Required, 20, True, False, False)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_modify_raise(self):
        self._init_filer(get_response=TestEdgeSMB._get_cifs_configuration_response())
        self._filer.put = mock.MagicMock(side_effect=exception.CTERAException())
        with self.assertRaises(exception.CTERAException) as error:
            smb.SMB(self._filer).modify(CIFSPacketSigning.Required, 20, True, False, False)
        self._filer.get.assert_called_once_with('/config/fileservices/cifs')
        self._filer.put.assert_called_once_with('/config/fileservices/cifs', mock.ANY)
        expected_param = TestEdgeSMB._get_cifs_configuration_response(CIFSPacketSigning.Required, 20, True, False, False)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual('Failed to update SMB configuration.', error.exception.message)

    def test_modify_smb_disabled_raise(self):
        param = Object()
        param.mode = Mode.Disabled
        self._init_filer(get_response=param)
        with self.assertRaises(exception.CTERAException) as error:
            smb.SMB(self._filer).modify(CIFSPacketSigning.Required)
        self.assertEqual('SMB must be enabled in order to modify its configuration', error.exception.message)

    @staticmethod
    def _get_cifs_configuration_response(packet_signing=None, idle_disconnect_time=None, compatibility_mode=None,
                                         cifs_unix_extensions=None, abe_enabled=None):
        cifs = Object()
        cifs.mode = Mode.Enabled
        cifs.packetSigning = packet_signing if packet_signing else CIFSPacketSigning.Disabled
        cifs.idleDisconnectTime = idle_disconnect_time if idle_disconnect_time else 10
        cifs.compatibilityMode = compatibility_mode if compatibility_mode is not None else False
        cifs.cifsUnixExtensions = cifs_unix_extensions if cifs_unix_extensions is not None else True
        cifs.hideUnreadable = abe_enabled if abe_enabled is not None else True
        return cifs

    @staticmethod
    def _get_configuration_response():
        cifs = TestEdgeSMB._get_cifs_configuration_response()
        obj = Object()
        obj.mode = cifs.mode
        obj.packet_signing = cifs.packetSigning
        obj.idle_disconnect_time = cifs.idleDisconnectTime
        obj.compatibility_mode = cifs.compatibilityMode
        obj.cifs_unix_extensions = cifs.cifsUnixExtensions
        obj.abe_enabled = cifs.hideUnreadable
        return obj
