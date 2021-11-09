#
# util_utl.py
#
# Utility APIs.
#

import subprocess, json, logging, logging.handlers, inspect
import sys, os, time, functools, ConfigParser
from xml.etree import cElementTree as ET

CFGDB_TABLE_NAME_ACL            = 'ACL_TABLE'
CFGDB_TABLE_NAME_RULE           = 'ACL_RULE'
CFGDB_TABLE_NAME_VLAN           = 'VLAN'
CFGDB_TABLE_NAME_VLAN_MBR       = 'VLAN_MEMBER'
CFGDB_TABLE_NAME_MIRROR_SESSION = 'MIRROR_SESSION'
CFGDB_TABLE_NAME_PC             = 'PORTCHANNEL'
CFGDB_TABLE_NAME_NTP            = 'NTP_SERVER'

CFGDB_TABLE_NAME_TC2Q_MAP       = 'TC_TO_QUEUE_MAP'
CFGDB_TABLE_NAME_DSCP2TC_MAP    = 'DSCP_TO_TC_MAP'
CFGDB_TABLE_NAME_QUEUE          = 'QUEUE'
CFGDB_TABLE_NAME_SCHDLR         = 'SCHEDULER'
CFGDB_TABLE_NAME_TC2PG_MAP      = 'TC_TO_PRIORITY_GROUP_MAP'
CFGDB_TABLE_NAME_MAP_PFC_P2Q    = 'MAP_PFC_PRIORITY_TO_QUEUE'
CFGDB_TABLE_NAME_PORT_QOS_MAP   = 'PORT_QOS_MAP'
CFGDB_TABLE_NAME_WRED_PROFILE   = 'WRED_PROFILE'

CFGDB_TABLE_NAME_VXLAN_TUNNEL    = 'VXLAN_TUNNEL'
CFGDB_TABLE_NAME_VXLAN_TUNNEL_MAP= 'VXLAN_TUNNEL_MAP'

CFGDB_TABLE_NAME_INTF           = 'INTERFACE'
CFGDB_TABLE_NAME_PC_INTF        = 'PORTCHANNEL_INTERFACE'
CFGDB_TABLE_NAME_VLAN_INTF      = 'VLAN_INTERFACE'
CFGDB_TABLE_NAME_LBK_INTF       = 'LOOPBACK_INTERFACE'

APPDB_TABLE_NAME_LLDP           = 'LLDP_ENTRY_TABLE'
APPDB_TABLE_NAME_NBR            = 'NEIGH_TABLE'

STATDB_TABLE_NAME_FDB           = 'FDB_TABLE'

TAG_DBG_PERF                    = 'DBG_PERF'

DBG_FLG_TBL = {
    TAG_DBG_PERF : 1,
}

# for config.ini and log
LOG_FILE                        = 'xmppd.log'
LOG_DIR                         = '/var/log/'
LOG_FMT                         = '%(asctime)s %(levelname)-8s %(message)s'
LOG_FMT_DATE                    = '%y-%m-%d %H:%M:%S'

CFG_DIR                         = '/etc/xmppd/'
CFG_FILE                        = 'config.ini'

CFG_SECT_GEN                    = "general"

CFG_TBL = {
    "FAKE_DATA"         : 0,
    "INTERVAL_LLDP"     : 0,
    "INTERVAL_STATIS"   : 0,
    "START_LLDP"        : 7,
    "START_STATIS"      : 10,
    "CTRLER_IP"         : None,         # required for connection
    "CTRLER_PORT"       : 5269,
    "JID_SERVER"        : "xmpp.onosproject.org",
    "JID_DOMAIN"        : "edgecore.com",
    "CFG_PATH"          : None
}

def utl_is_flag_on(flg_name):
    return flg_name in DBG_FLG_TBL and DBG_FLG_TBL[flg_name] > 0

def utl_set_flag(flg_name, val):
    DBG_FLG_TBL[flg_name] = val

def utl_log(str, lvl = logging.DEBUG, c_lvl=1):
    f1 = sys._getframe(c_lvl)

    if f1:
        my_logger = logging.getLogger()
        if lvl < my_logger.getEffectiveLevel(): return
        rec = my_logger.makeRecord(
            'gnmi_svr',
            lvl,
            os.path.basename(f1.f_code.co_filename),
            f1.f_lineno,
            str,
            None,
            None,
            f1.f_code.co_name)

        my_logger.handle(rec)
    else:
        logging.log (lvl, str)

def utl_err(str):
    utl_log(str, logging.ERROR, 2)

# decorator to get function execution time
def utl_timeit(f):
    @functools.wraps(f)
    def timed(*args, **kw):
        if utl_is_flag_on(TAG_DBG_PERF):
            t_beg = time.time()
            result = f (*args, **kw)
            t_end = time.time()
            utl_log("Time spent %s : %s %s" %  ((t_end - t_beg), f.__name__, args), logging.CRITICAL, 2)
        else:
            result = f (*args, **kw)

        return result
    return timed

# decorator to add separation line in logs
def utl_log_outer(f):
    @functools.wraps(f)
    def wrapped(*args, **kw):
        if utl_is_flag_on(TAG_DBG_PERF):
            utl_log("beg ==================", logging.CRITICAL, 3)
            result = f (*args, **kw)
            utl_log("end ==================", logging.CRITICAL, 3)
        else:
            result = f (*args, **kw)

        return result
    return wrapped

@utl_timeit
def utl_execute_cmd(exe_cmd):
    p = subprocess.Popen(exe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    ## Wait for end of command. Get return code ##
    returncode = p.wait()

    if returncode != 0:
        # if no decorator, use inspect.stack()[1][3] to get caller
        utl_log("Failed to [%s] by %s !!! (%s)" % (exe_cmd, inspect.stack()[2][3], err), logging.ERROR)
        return False

    return True

@utl_timeit
def utl_get_execute_cmd_output(exe_cmd):
    p = subprocess.Popen(exe_cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    ## Wait for end of command. Get return code ##
    returncode = p.wait()

    if returncode != 0:
        # if no decorator, use inspect.stack()[1][3] to get caller
        utl_log("Failed to [%s] by %s !!!" % (exe_cmd, inspect.stack()[2][3]), logging.ERROR)
        return (False, None)

    return (True, output)

# decorator to print debug info
def utl_dbg(f):
    @functools.wraps(f)
    def dbg_msg(*args, **kw):
        logging.debug("%s : %s " %  (f.__name__, ET.tostring(args[0])))
        result = f (*args, **kw)

        return result
    return dbg_msg


# ex: port_lst = [ {} ]
def utl_build_xml_ports(port_list):
    root_et = ET.Element('entry')
    prts_et = ET.SubElement(root_et, 'ports')
    #cnt = 0
    for port in port_list:
    #    cnt += 1
        port_data = utl_build_xml_item(port, 'port')
        prts_et.append(port_data)
    #    if cnt == 2:
    #        break

    return root_et

# ex: info : { "a" : "x",
#              "b" : "y" }
def utl_build_xml_item(info, root_tag = 'entry'):
    root_et = ET.Element(root_tag)
    for key in info.keys():
        child_et = ET.SubElement(root_et, key)
        child_et.text = info[key]

    return root_et

def utl_setup_cfg(daemon_flag):
    cfg_path = ['./misc/', CFG_DIR] [daemon_flag] + CFG_FILE
    CFG_TBL["CFG_PATH"] = cfg_path
    cfg = ConfigParser.RawConfigParser()
    cfg.read(cfg_path)

    cmap_tbl = [ { "fld" : "FAKE_DATA",       "tag" : "fake_data",       "type" : "int" },
                 { "fld" : "INTERVAL_LLDP",   "tag" : "interval_lldp",   "type" : "int" },
                 { "fld" : "INTERVAL_STATIS", "tag" : "interval_statis", "type" : "int" },
                 { "fld" : "CTRLER_IP",       "tag" : "controller_ip"                   },
                 { "fld" : "CTRLER_PORT",     "tag" : "controller_port", "type" : "int" },
                 { "fld" : "JID_DOMAIN",      "tag" : "jid_domain"                      },
                 { "fld" : "JID_SERVER",      "tag" : "jid_server"                      },
    ]

    for cmap in cmap_tbl:
        if cfg.has_option(CFG_SECT_GEN, cmap["tag"]):
            if "type" in cmap:
                CFG_TBL[cmap["fld"]] = int(cfg.get(CFG_SECT_GEN, cmap["tag"]))
            else:
                CFG_TBL[cmap["fld"]] = cfg.get(CFG_SECT_GEN, cmap["tag"])

def utl_setup_log(daemon_flag, debug_flag):
    log_path = ['./', LOG_DIR] [daemon_flag] + LOG_FILE
    log_lvl  = [logging.INFO, logging.DEBUG] [debug_flag]

    if debug_flag:
        # clear log file
        with open(log_path, 'w'):
            pass

    logging.basicConfig(level=log_lvl,
                        format=LOG_FMT,
                        datefmt=LOG_FMT_DATE)

    handler = logging.handlers.RotatingFileHandler(
                    log_path, maxBytes=1024000, backupCount=2)
    handler.setFormatter(logging.Formatter(
                    fmt=LOG_FMT, datefmt=LOG_FMT_DATE))
    logging.getLogger().addHandler(handler)
