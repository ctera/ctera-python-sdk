from unittest import mock

from cterasdk import exception
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
