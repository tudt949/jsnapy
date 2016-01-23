import unittest
import yaml
from jnpr.jsnapy.snap import Parser
from jnpr.jsnapy import SnapAdmin
import jnpr.junos.device
from mock import patch, mock_open, ANY, call
from contextlib import nested


class TestSnap(unittest.TestCase):

    def setUp(self):
        self.diff = False
        self.hostname = "10.216.193.114"
        self.db = dict()
        self.db['store_in_sqlite'] = False
        self.db['check_from_sqlite'] = False
        self.db['db_name'] = ""
        self.db['first_snap_id'] = None
        self.db['second_snap_id'] = None
        self.output_file = "abc"

    @patch('jnpr.junos.device.Device')
    @patch('jnpr.jsnapy.snap.etree')
    def test_snap(self, mock_etree, mock_dev):
        prs = Parser()
        test_file = "configs/delta.yml"
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="user",
            passwd="xyz")
        dev.open()
        m_op = mock_open()
        with patch('jnpr.jsnapy.snap.open', m_op, create=True) as m_open:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db)
            self.assertEqual(prs.command_list, ['show chassis fpc'])
            self.assertEqual(prs.rpc_list, [])
            self.assertEqual(prs.test_included, ['check_chassis_fpc'])
        dev.close()

    @patch('sys.exit')
    @patch('argparse.ArgumentParser.print_help')
    @patch('jnpr.junos.device.Device')
    @patch('jnpr.jsnapy.snap.etree')
    def test_snap_2(self, mock_etree, mock_dev, mock_parser, mock_exit):
        js = SnapAdmin()
        conf_file = "configs/main.yml"
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="user",
            passwd="xyz")
        dev.open()
        m_op = mock_open()
        with patch('jnpr.jsnapy.snap.open', m_op, create=True) as m_open:
            js.generate_rpc_reply(dev, self.output_file, "10.216.193.114", js.main_file)
            self.assertTrue(m_open.called)
        dev.close()


    @patch('jnpr.jsnapy.snap.Parser._write_file')
    @patch('jnpr.jsnapy.snap.etree')
    def test_snap_3(self, mock_etree, mock_parse):
        prs = Parser()
        test_file = "configs/delta.yml"
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="xyz",
            passwd="abc")
        with patch('jnpr.junos.rpcmeta._RpcMetaExec.cli') as mock_cli:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db)
            mock_cli.assert_called_once_with('show chassis fpc', format='xml')

    @patch('jnpr.jsnapy.snap.Parser._write_file')
    @patch('jnpr.jsnapy.snap.etree')
    def test_snap_4(self, mock_etree, mock_parse):
        prs = Parser()
        test_file = "configs/delta_text.yml"
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="xyz",
            passwd="abc")
        with patch('jnpr.junos.rpcmeta._RpcMetaExec.cli') as mock_cli:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db)
            mock_cli.assert_called_once_with('show chassis fpc', format='text')

    @patch('jnpr.jsnapy.snap.Parser._write_file')
    @patch('jnpr.jsnapy.snap.etree')
    def test_snap_5(self, mock_etree, mock_parse):
        prs = Parser()
        test_file = "configs/delta_error.yml"
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="xyz",
            passwd="abc")
        with patch('logging.Logger.error') as mock_log:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db)
            c = mock_log.call_args_list[0]
            self.assertNotEqual(c[0][0].find("ERROR occurred"), -1)

    @patch('jnpr.junos.device.Device')
    @patch('jnpr.jsnapy.snap.etree')
    def test_rpc_1(self, mock_etree, mock_dev):
        prs = Parser()
        test_file = "configs/test_rpc.yml"
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="user_mock",
            passwd="xyz")
        dev.open()
        m_op = mock_open()
        with patch('jnpr.jsnapy.snap.open', m_op, create=True) as m_open:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db)

            self.assertEqual(prs.command_list, [])
            self.assertEqual(
                prs.rpc_list, [
                    'get-config', 'get-interface-information'])
            self.assertEqual(
                prs.test_included, [
                    'test_rpc_version', 'test_interface'])
        dev.close()

    @patch('jnpr.jsnapy.snap.Parser._write_file')
    @patch('jnpr.jsnapy.snap.etree')
    def test_rpc_2(self, mock_etree, mock_parse):
        prs = Parser()
        test_file = "configs/test_rpc.yml"
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="xyz",
            passwd="abc")
        with nested(
                patch('jnpr.junos.rpcmeta._RpcMetaExec.__getattr__'),
                patch('jnpr.junos.rpcmeta._RpcMetaExec.get_config')
        ) as (mock_rpc, mock_config):
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db)
            mock_rpc.assert_called_once_with('get_interface_information')
            mock_config.assert_called_once_with(
                options={
                    'format': 'xml'},
                filter_xml=ANY)

    @patch('jnpr.junos.device.Device')
    @patch('jnpr.jsnapy.snap.Parser._write_file')
    @patch('jnpr.jsnapy.snap.etree')
    def test_rpc_3(self, mock_etree, mock_parse, mock_dev):
        prs = Parser()
        test_file = "configs/test_rpc_error.yml"
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="user",
            passwd="xyz")
        dev.open()
        with patch('logging.Logger.error') as mock_log:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db)
            c = mock_log.call_args_list[0]
            self.assertNotEqual(
                c[0][0].find("ERROR!!, filtering rpc works only for 'get-config' rpc"), -1)
        dev.close()

    @patch('jnpr.jsnapy.snap.Parser._write_file')
    @patch('jnpr.jsnapy.snap.etree')
    def test_rpc_4(self, mock_etree, mock_parse):
        prs = Parser()
        test_file = "configs/test_rpc_2.yml"
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="xyz",
            passwd="abc")
        with nested(
                patch('jnpr.junos.rpcmeta._RpcMetaExec.__getattr__'),
                patch('jnpr.junos.rpcmeta._RpcMetaExec.get_config')
        ) as (mock_rpc, mock_config):
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db)
            mock_rpc.assert_called_once_with('get_interface_information')
            mock_config.assert_called_once_with(options={'format': 'xml'})

    @patch('jnpr.jsnapy.snap.Parser._write_file')
    @patch('jnpr.jsnapy.snap.etree')
    def test_rpc_5(self, mock_etree, mock_parse):
        prs = Parser()
        test_file = "configs/test_rpc_error_2.yml"
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="xyz",
            passwd="abc")
        with patch('logging.Logger.error') as mock_log:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db)
            c = mock_log.call_args_list[0]

            self.assertNotEqual(c[0][0].find("ERROR occurred"), -1)

    @patch('jnpr.jsnapy.snap.Parser._write_file')
    @patch('jnpr.jsnapy.snap.etree')
    def test_rpc_6(self, mock_etree, mock_parse):
        prs = Parser()
        test_file = "configs/test_rpc_2_error.yml"
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="xyz",
            passwd="abc")
        with patch('logging.Logger.error') as mock_log:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db)
            c = mock_log.call_args_list[0]
            self.assertNotEqual(c[0][0].find("ERROR occurred"), -1)

    @patch('jnpr.junos.device.Device')
    @patch('jnpr.jsnapy.snap.etree')
    @patch('jnpr.jsnapy.snap.JsnapSqlite')
    def test_snap_sqlite_1(self, mock_sqlite, mock_etree, mock_dev):
        prs = Parser()
        test_file = "configs/delta.yml"
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="user",
            passwd="xyz")
        dev.open()
        m_op = mock_open()
        self.db['store_in_sqlite'] = True
        self.db['db_name'] = "abc.db"
        with patch('jnpr.jsnapy.snap.open', m_op, create=True) as m_open:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db)
            mock_sqlite.assert_called_once_with('10.216.193.114', 'abc.db')
        dev.close()

    @patch('jnpr.junos.device.Device')
    @patch('jnpr.jsnapy.snap.etree')
    @patch('jnpr.jsnapy.snap.JsnapSqlite.__init__')
    @patch('jnpr.jsnapy.snap.JsnapSqlite.insert_data')
    def test_snap_sqlite_2(self, mock_insert, mock_init, mock_etree, mock_dev):
        mock_init.return_value = None
        prs = Parser()
        test_file = "configs/delta.yml"
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="user",
            passwd="xyz")
        dev.open()
        m_op = mock_open()
        with patch('jnpr.jsnapy.snap.open', m_op, create=True) as m_open:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "01.216.193.114",
                self.db)
            self.assertFalse(mock_insert.called)
            self.assertFalse(mock_init.called)
        dev.close()

    @patch('jnpr.junos.device.Device')
    @patch('jnpr.jsnapy.snap.etree')
    @patch('jnpr.jsnapy.snap.JsnapSqlite.__init__')
    @patch('jnpr.jsnapy.snap.Parser._check_reply')
    @patch('jnpr.jsnapy.snap.JsnapSqlite.insert_data')
    def test_snap_sqlite_3(self, mock_insert, mock_reply, mock_init, mock_etree, mock_dev):
        mock_init.return_value = None
        prs = Parser()
        test_file = "configs/delta.yml"
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="user",
            passwd="xyz")
        dev.open()
        m_op = mock_open()
        self.db['store_in_sqlite'] = True
        self.db['db_name'] = "abc.db"
        with patch('jnpr.jsnapy.snap.open', m_op, create=True) as m_open:
            prs.generate_reply(
                test_file,
                dev,
                "snap_mock",
                "10.216.193.114",
                self.db)

            db_dict = dict()
            db_dict['cli_command'] = 'show_chassis_fpc'
            db_dict['snap_name'] = "snap_mock"
            db_dict['filename'] = "10.216.193.114" +"_" "snap_mock" + "_" + "show_chassis_fpc" + "." + "xml"
            db_dict['format'] = "xml"
            db_dict['data'] = mock_reply()
            mock_insert.assert_called_once_with(db_dict)
        dev.close()


    @patch('jnpr.junos.device.Device')
    @patch('jnpr.jsnapy.snap.etree')
    @patch('jnpr.jsnapy.snap.JsnapSqlite.__init__')
    @patch('jnpr.jsnapy.snap.Parser._check_reply')
    @patch('jnpr.jsnapy.snap.JsnapSqlite.insert_data')
    def test_snap_sqlite_4(self, mock_insert, mock_reply, mock_init, mock_etree, mock_dev):
        mock_init.return_value = None
        prs = Parser()
        calls =[]
        test_file = "configs/test_rpc.yml"
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="user",
            passwd="xyz")
        dev.open()
        m_op = mock_open()
        self.db['store_in_sqlite'] = True
        self.db['db_name'] = "abc.db"
        with patch('jnpr.jsnapy.snap.open', m_op, create=True) as m_open:
            prs.generate_reply(
                test_file,
                dev,
                "snap_mock",
                "10.216.193.114",
                self.db)
            db_dict = dict()
            db_dict['cli_command'] = 'get-config'
            db_dict['snap_name'] = "snap_mock"
            db_dict['filename'] = "10.216.193.114" + "_" + "snap_mock" + "_" + "get-config" + "." + "xml"
            db_dict['format'] = 'xml'
            db_dict['data'] = mock_reply()
            calls.append(call(db_dict))
            db_dict2 = db_dict.copy()
            db_dict2['cli_command'] = 'get-interface-information'
            db_dict2['filename']= "10.216.193.114" + "_" + "snap_mock" + "_" + "get-interface-information" + "." + "xml"
            calls.append(call(db_dict2))
            print "\n 888888888 calls:", calls
            print "\n 9999986755 call list:", mock_insert.call_args_list
            print "\n 0000000000000mock_insert.mock_calls", mock_insert.mock_calls
            mock_insert.assert_has_calls(calls)
        dev.close()

with patch('logging.Logger.info') as mock_logger:
    if __name__ == "__main__":
        suite = unittest.TestLoader().loadTestsFromTestCase(TestSnap)
        unittest.TextTestRunner(verbosity=2).run(suite)
