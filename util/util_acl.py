#
# util_acl.py
#
# acl related APIs.
#

import util_utl, util_method_tbl, pdb
from xml.etree import cElementTree as ET

TMP_ACL_FILE        = '/tmp/set-ip-acl.json'
CFG_TMPL_UPD_ACL    = 'config acl update full {filename}'

CFG_TMPL_BIND_ACL_EC    = 'config acl add table {aclname} L3 --ports "{inflist}" --stage {stage}'
CFG_TMPL_UNBIND_ACL_EC  = 'config acl remove table {aclname}'

# for bcm
CFG_TMPL_BIND_ACL_BCM   = 'config acl table add {aclname} L3 --ports "{inflist}" --stage {stage}'
CFG_TMPL_UNBIND_ACL_BCM = 'config acl table delete {aclname}'

CFG_TMPL_BIND_ACL   = CFG_TMPL_BIND_ACL_EC
CFG_TMPL_UNBIND_ACL = CFG_TMPL_UNBIND_ACL_EC

# setup the correct command according to the cfg
def acl_cfg_ready_cb(cfg_tbl):
    global CFG_TMPL_BIND_ACL, CFG_TMPL_UNBIND_ACL

    if cfg_tbl["IS_EC"] == 1:
        CFG_TMPL_BIND_ACL   = CFG_TMPL_BIND_ACL_EC
        CFG_TMPL_UNBIND_ACL = CFG_TMPL_UNBIND_ACL_EC
    else:
        CFG_TMPL_BIND_ACL   = CFG_TMPL_BIND_ACL_BCM
        CFG_TMPL_UNBIND_ACL = CFG_TMPL_UNBIND_ACL_BCM

#
# set functions
#

def acl_bind_ex(is_add, ent_elm):
    acl_elm = ent_elm.find('acl')
    port_elm= ent_elm.find('port')
    dir_elm = ent_elm.find('direction')

    if None in [ acl_elm, port_elm, dir_elm, acl_elm.text, port_elm.text, dir_elm.text ]:
        util_method_tbl.mtbl_append_retmsg(ent_elm, "WRONG PARAMETERS")
    else:
        if is_add:
            exe_cmd = CFG_TMPL_BIND_ACL.format(
                        aclname=acl_elm.text, inflist=port_elm.text, stage=dir_elm.text)
        else:
            exe_cmd = CFG_TMPL_UNBIND_ACL.format(
                        aclname=acl_elm.text)

        if util_utl.utl_execute_cmd(exe_cmd):
            util_method_tbl.mtbl_append_retmsg(ent_elm, "SUCCESS")
        else:
            util_method_tbl.mtbl_append_retmsg(ent_elm, "FAIL")

# ex: <entry><method>bind-acl</method><acl>IP_15_INGRESS</acl>
#            <port>Ethernet15</port><direction>INGRESS</direction></entry>
@util_utl.utl_dbg
def acl_bind(ent_elm, db_args):
    acl_bind_ex(True, ent_elm)

# ex: <entry><method>unbind-acl</method><acl>IP_16_INGRESS</acl>
#            <port>Ethernet16</port><direction>INGRESS</direction></entry>
@util_utl.utl_dbg
def acl_unbind(ent_elm, db_args):
    acl_bind_ex(False, ent_elm)

@util_utl.utl_dbg
def acl_update(ent_elm, db_args):

    file_elm = ent_elm.find('file')
    if file_elm is not None:
        with open(TMP_ACL_FILE, 'w') as acl_file:
            acl_file.write(file_elm.text)

        exe_cmd = CFG_TMPL_UPD_ACL.format(filename=TMP_ACL_FILE)

        if util_utl.utl_execute_cmd(exe_cmd):
            util_method_tbl.mtbl_append_retmsg(ent_elm, "SUCCESS")
        else:
            util_method_tbl.mtbl_append_retmsg(ent_elm, "FAIL")
    else:
        util_method_tbl.mtbl_append_retmsg(ent_elm, "WRONG PARAMETERS")

#
# get functions
#

#
# register functions to method table
#
util_method_tbl.mtbl_register_method('bind-acl',   acl_bind)
util_method_tbl.mtbl_register_method('unbind-acl', acl_unbind)
util_method_tbl.mtbl_register_method('update-acl', acl_update)

#
# register cb function for CFG_TBL
#
util_utl.utl_register_cb_cfg_ready(acl_cfg_ready_cb)
