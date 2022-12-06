#
# util_mirror.py
#
# port mirror related APIs.
#

from xml.etree import cElementTree as ET
from . import util_utl, util_method_tbl

CFG_TMPL_MIRROR_SPAN_ADD_EC  = "config mirror_session span add {sess_name}" \
                               " {dst_port} {src_port} {mode}"
CFG_TMPL_MIRROR_SPAN_ADD_BCM = "config mirror_session add span {sess_name}" \
                               " {dst_port} {src_port} {mode}"

CFG_TMPL_MIRROR_SPAN_ADD     = CFG_TMPL_MIRROR_SPAN_ADD_EC
CFG_TMPL_MIRROR_SPAN_REM     = "config mirror_session remove {sess_name}"

# setup the correct command according to the cfg
def mirror_cfg_ready_cb(cfg_tbl):
    global CFG_TMPL_MIRROR_SPAN_ADD

    if cfg_tbl["IS_EC"] == 1:
        CFG_TMPL_MIRROR_SPAN_ADD = CFG_TMPL_MIRROR_SPAN_ADD_EC
    else:
        CFG_TMPL_MIRROR_SPAN_ADD = CFG_TMPL_MIRROR_SPAN_ADD_BCM

#
# set functions
#

#
# ex: <entry><method>port-mirror</method><session>session_11_12_rx</session>
#            <action>add</action><source-port>Ethernet11</source-port>
#            <destination-port>Ethernet12</destination-port>
#            <direction>rx</direction></entry>
@util_utl.utl_dbg
def mirror_set_span(ent_elm, db_args):
    ses_elm = ent_elm.find("session")
    act_elm = ent_elm.find("action")

    is_bad_args = False
    if None in [ ses_elm, ses_elm.text, act_elm, act_elm.text ]:
        is_bad_args = True

    if not is_bad_args:
        if act_elm.text == 'add':
            sp_elm  = ent_elm.find("source-port")
            dp_elm  = ent_elm.find("destination-port")
            md_elm  = ent_elm.find("direction")

            if None in [ sp_elm, sp_elm.text, dp_elm, dp_elm.text, md_elm, md_elm.text ]:
                is_bad_args = True
            else:
                exe_cmd = CFG_TMPL_MIRROR_SPAN_ADD.format(
                            sess_name=ses_elm.text, dst_port=dp_elm.text,
                            src_port=sp_elm.text, mode=md_elm.text)
        else:
            exe_cmd = CFG_TMPL_MIRROR_SPAN_REM.format(sess_name=ses_elm.text)

    if is_bad_args:
        util_method_tbl.mtbl_append_retmsg(ent_elm, "WRONG PARAMETERS")
    else:
        if util_utl.utl_execute_cmd(exe_cmd):
            util_method_tbl.mtbl_append_retmsg(ent_elm, "SUCCESS")
        else:
            util_method_tbl.mtbl_append_retmsg(ent_elm, "FAIL")

#
# get functions
#


#
# register related functions to method table
#
util_method_tbl.mtbl_register_method('port-mirror', mirror_set_span)

#
# register cb function for CFG_TBL
#
util_utl.utl_register_cb_cfg_ready(mirror_cfg_ready_cb)

