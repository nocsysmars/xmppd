import time, logging, argparse, sys, os, socket, signal, pdb
from sleekxmpp import ClientXMPP, XMLStream, Iq

if __package__:
    # from systemd
    from .xmppclient import XmppClient
    from .util import util_utl, util_timer
else:
    from xmppclient import XmppClient
    from util import util_utl, util_timer

class XmppDaemon():

    def __init__(self, client_jid, server_jid, controller_ip, controller_port):
        self.peri_cb = util_timer.MyPeriodCb()
        self.jid = client_jid
        self.xmpp_agent = XmppClient(
            client_jid=client_jid, server_jid=server_jid, password='passwd', peri_cb = self.peri_cb)
        self.controller_ip   = controller_ip
        self.controller_port = controller_port
        self.ip_address = ""
        self.is_stopped = False

    def sigterm_handler(self, _signo, _stack_frame):
        logging.info("Received SIGTERM !")
        self.is_stopped = True

    def run(self):
        if self.xmpp_agent.connect(
            (self.controller_ip, int(self.controller_port)),
            use_tls=False, reattempt=False):
            self.xmpp_agent.process(block=False)
        else:
            logging.info("Connecting to server failed ...")
            sys.exit(1)

        try:
            while not self.is_stopped:
                time.sleep(1)
                self.peri_cb.timer_tick()

        except KeyboardInterrupt:
            self.is_stopped = True

        finally:
            logging.info("XMPPD Shutting down...")
            self.xmpp_agent.shutdown()

def main(daemon_flag = True):
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", help="emit debug messages")
    args = parser.parse_args()

    util_utl.utl_setup_log(daemon_flag, args.debug)
    util_utl.utl_setup_cfg(daemon_flag)

    exec_cmd = "sonic-cfggen -d -v DEVICE_METADATA.localhost.mac"
    (is_ok, output) = util_utl.utl_get_execute_cmd_output(exec_cmd)
    if is_ok:
        # localhost.mac ex : '00:11:22:33:44:55'
        # xmpp not allow ':' in jid
        client_jid = output.strip('\n').replace(':','') + \
                        '@' + util_utl.CFG_TBL["JID_DOMAIN"]
    else:
        logging.critical("Cannot get my mac address, exit !!!")
        sys.exit(1)

    if util_utl.CFG_TBL["CTRLER_IP"] in [None, ""]:
        logging.critical("No Controller IP found in {}, exit !!!".format(
                            util_utl.CFG_TBL["CFG_PATH"]))
        sys.exit(1)

    xmppd = XmppDaemon(
                client_jid, util_utl.CFG_TBL["JID_SERVER"],
                util_utl.CFG_TBL["CTRLER_IP"], util_utl.CFG_TBL["CTRLER_PORT"])

    signal.signal(signal.SIGTERM, xmppd.sigterm_handler)

    xmppd.run()

if __name__ == '__main__':
    main(daemon_flag = False)
