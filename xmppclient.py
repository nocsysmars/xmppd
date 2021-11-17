import time, logging, pdb, uuid
from sleekxmpp import ClientXMPP, XMLStream, Iq, StanzaPath, Callback
from xml.etree import cElementTree as ET
from util import *


class MyArgs: pass

class XmppClient(ClientXMPP):
    def __init__(self, client_jid, server_jid, password, peri_cb):
        self.session_started = False

        super(XmppClient, self).__init__(server_jid, password)

        self.register_plugin('xep_0030')
        self.register_plugin('xep_0059')
        self.register_plugin('xep_0060')

        # try to reconnect if server is disconnected
        self.auto_reconnect = True

        self.client_jid = client_jid
        self.stream_header = "<stream:stream to='%s' %s %s %s %s %s>" % (
            self.boundjid.host,
            "from='%s'" % self.client_jid,
            "xmlns:stream='%s'" % self.stream_ns,
            "xmlns='%s'" % self.default_ns,
            "xml:lang='%s'" % self.default_lang,
            "version='1.0'")

        self.add_event_handler("connected", self.connected)
        self.add_event_handler("session_start", self.session_start, threaded=False)
        self.add_event_handler("message", self.message_handler)
        self.add_event_handler("disconnected", self.disconnected)
        self.add_event_handler("socket_error", self.socket_err)

        self.register_handler(
            Callback('message',
                     StanzaPath('message'),
                     lambda msg: self.event('message', msg)))

        self.db_args = MyArgs()
        self.db_args.appdb  = util_db.db_connect_by_name('APPL')
        self.db_args.cntrdb = util_db.db_connect_by_name('COUNTER')
        #self.db_args.asicdb = db_connect_by_name('ASIC')
        self.db_args.statdb = util_db.db_connect_by_name('STATE')
        self.db_args.cfgdb  = util_db.db_connect_by_name('CFG')

        # flag to execute reboot
        self.db_args.is_reboot = False

        self.peri_cb = peri_cb

        # check if port table is ready
        is_ready = False
        chk_cnt = 0
        while True:
            pstate = self.db_args.appdb.get(
                        self.db_args.appdb.APPL_DB, 'PORT_TABLE:PortInitDone', 'lanes')

            is_ready = pstate != None

            chk_cnt += 1

            if is_ready or chk_cnt % 3 == 1:
                logging.info(
                    "PORT TABLE was%sready...(%s)" % ([" not ", " "][is_ready], chk_cnt))

            if is_ready: break

            time.sleep(10)

    def start_stream_handler(self, xml):
        self.event('session_start')

    def connected(self, event):
        logging.info('xmppd {} CONNECTED !'.format(self.client_jid))

    def socket_err(self, event):
        self.reconnect_delay *= 2

    def disconnected(self, event):
        logging.info('xmppd {} DISCONNECTED !'.format(self.client_jid))

    def session_start(self, event):
        logging.info("Session started")
        self.session_started = True
        self.session_started_event.set()

        self.session_main()

    def session_main(self):
        # send platform message
        self.publish_platform()

        # send port message
        self.publish_all_ports()

        if util_utl.CFG_TBL['INTERVAL_LLDP'] > 0:
            self.peri_cb.register_period_cb(
                util_utl.CFG_TBL['START_LLDP'],
                util_utl.CFG_TBL['INTERVAL_LLDP'],
                self.period_msg_lldp)

        if util_utl.CFG_TBL['INTERVAL_STATIS'] > 0:
            self.peri_cb.register_period_cb(
                util_utl.CFG_TBL['START_STATIS'],
                util_utl.CFG_TBL['INTERVAL_STATIS'],
                self.period_msg_port_statis)

    def shutdown(self):
        self.auto_reconnect = False
        self.set_stop()
        self.disconnect()

    def message_handler(self, msg):
        logging.info("XMPP Message received!")
        payload = msg.get_payload()
        xml = payload[0]

        ent_elm = xml.find('./items/item/entry')

        if ent_elm is not None:
            met_elm = ent_elm.find('method')

            method_str = None
            if met_elm is not None:
                method_str = met_elm.text

            # call method.text
            ent_elm = util_method_tbl.mtbl_execute_method(method_str, ent_elm, self.db_args)

        else:
            # no entry found
            ent_elm = xml
            util_method_tbl.mtbl_append_retmsg(ent_elm, "NO ENTRY FOUND")

        # send result
        self.send_result(ent_elm)

        if self.db_args.is_reboot:
            time.sleep(2)
            self.db_args.is_reboot = False
            util_method_tbl.mtbl_execute_method('reboot-nr', ent_elm, self.db_args)

    def send_result(self, ent_elm):
        msg = self.Message(sto=self.boundjid.host, stype='chat', sfrom=self.client_jid)
        msg.appendxml(ent_elm)
        msg.send()

    def publish_msg(self, node, data):
        ret_val = False

        self.node = node
        id_data = str(uuid.uuid4())

        # need to wait for the response
        try:
            result = self['xep_0060'].publish(
                         self.boundjid.host, self.node, id=id_data,
                         payload=data, ifrom=self.client_jid, block=True)

            if result['type'] == 'result' and str(result).find(id_data) > 0:
                logging.info('Published at item id: %s' % id_data)
                ret_val = True
        except:
            logging.error('Could not publish to: %s' % self.node)

        finally:
            return ret_val

    # ex:
    #     <entry>
    #        <serial>571254X1622099</serial>
    #        <sw>SONiC-OS-3.1.1-Enterprise_Base</sw>
    #        <hw>x86_64-accton_as5712_54x-r0</hw>
    #     </entry>
    def publish_platform(self):
        pf_info = util_platform.platform_get_info()
        self.publish_msg('platform', util_utl.utl_build_xml_item(pf_info))

    def publish_all_ports(self):
        all_port_data = util_interface.interface_get_port_info(self.db_args)
        self.publish_msg('port', util_utl.utl_build_xml_ports(all_port_data))

    def period_msg_lldp(self):
        ent_elm = util_utl.utl_build_xml_item( {'method' : 'get-lldp'} )
        ent_elm = util_method_tbl.mtbl_execute_method('get-lldp', ent_elm, self.db_args)
        self.send_result(ent_elm)

    def period_msg_port_statis(self):
        ent_elm = util_utl.utl_build_xml_item( {'method' : 'get-statistics'} )
        ent_elm = util_method_tbl.mtbl_execute_method('get-statistics', ent_elm, self.db_args)
        self.send_result(ent_elm)

