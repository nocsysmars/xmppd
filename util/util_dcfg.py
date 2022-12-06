#
# util_dcfg.py
#
# default config related APIs.
#

from xml.etree import cElementTree as ET
from . import util_utl, util_method_tbl

CFG_TMPL_HOSTNAME_CMD = "config hostname {new_host}"
CFG_TMPL_DATE_CMD     = "date -s '{new_date_time}'"
CFG_TMPL_REBOOT_CMD   = "reboot"

#
# set functions
#

#
# ex: <entry><method>default-cfg</method><host>xmpp2</host>
#            <date>20211112 17:07:26</date></entry>
@util_utl.utl_dbg
def dcfg_default_cfg(ent_elm, db_args):
    is_host_ok = is_date_ok = False

    date_elm = ent_elm.find("date")
    if None not in [ date_elm, date_elm.text ]:
        exe_cmd = CFG_TMPL_DATE_CMD.format(new_date_time = date_elm.text)
        is_date_ok = util_utl.utl_execute_cmd(exe_cmd)

    host_elm = ent_elm.find("host")
    if None not in [ host_elm, host_elm.text ]:
        exe_cmd = CFG_TMPL_HOSTNAME_CMD.format(new_host = host_elm.text)
        is_host_ok = util_utl.utl_execute_cmd(exe_cmd)

    if not is_host_ok:
        util_method_tbl.mtbl_append_retmsg(ent_elm, "INVALID HOSTNAME")

    if not is_date_ok:
        util_method_tbl.mtbl_append_retmsg(ent_elm, "INVALID DATE")

    if is_date_ok and is_host_ok:
        util_method_tbl.mtbl_append_retmsg(ent_elm, "SUCCESS")

@util_utl.utl_dbg
def dcfg_reboot(ent_elm, db_args):
    # send msg back then reboot next round
    db_args.is_reboot = True
    util_method_tbl.mtbl_append_retmsg(ent_elm, "Reboot starts...")


def dcfg_reboot_nr(ent_elm, db_args):
    exe_cmd = CFG_TMPL_REBOOT_CMD
    util_utl.utl_execute_cmd(exe_cmd)

#
# get functions 
#


#
# register related functions to method table
#
util_method_tbl.mtbl_register_method('default-cfg', dcfg_default_cfg)
util_method_tbl.mtbl_register_method('reboot',      dcfg_reboot)
util_method_tbl.mtbl_register_method('reboot-nr',   dcfg_reboot_nr)
