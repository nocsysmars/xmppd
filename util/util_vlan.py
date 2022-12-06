#
# util_vlan.py
#
# vlan related APIs.
#

from xml.etree import cElementTree as ET
from . import util_utl, util_method_tbl

CFG_TMPL_VLAN_CMD     = "config vlan {action} {vid}"
CFG_TMPL_VLAN_MBR_CMD = "config vlan member {action} {tag_mode} {vid} {inf_name}"

#
# set functions
#

#
# ex: <entry><method>create-vlan</method><vlanid>6</vlanid></entry>
def vlan_cfg(ent_elm, act):
    vid_elm = ent_elm.find("vlanid")
    if vid_elm is not None:
        exe_cmd = CFG_TMPL_VLAN_CMD.format(action = act, vid = vid_elm.text)
        if util_utl.utl_execute_cmd(exe_cmd):
            util_method_tbl.mtbl_append_retmsg(ent_elm, "SUCCESS")
        else:
            util_method_tbl.mtbl_append_retmsg(ent_elm, "FAIL")
    else:
        util_method_tbl.mtbl_append_retmsg(ent_elm, "VID NOT FOUND")

@util_utl.utl_dbg
def vlan_create(ent_elm, db_args):
    vlan_cfg(ent_elm, "add")

@util_utl.utl_dbg
def vlan_remove(ent_elm, db_args):
    vlan_cfg(ent_elm, "del")


def vlan_mbr_cfg(ent_elm, act_str, vid_str, tag_str, inf_str):
    exe_cmd = CFG_TMPL_VLAN_MBR_CMD.format(
                action = act_str, tag_mode = tag_str, vid = vid_str, inf_name = inf_str)

    if util_utl.utl_execute_cmd(exe_cmd):
        util_method_tbl.mtbl_append_retmsg(ent_elm, "SUCCESS")
    else:
        util_method_tbl.mtbl_append_retmsg(ent_elm, "FAIL")

#
# ex: <entry><tag>true</tag><port>Ethernet17</port><action>add</action>
#            <method>vlan-member</method><vlanid>6</vlanid></entry>
@util_utl.utl_dbg
def vlan_mbr(ent_elm, db_args):
    vid_elm = ent_elm.find("vlanid")
    tag_elm = ent_elm.find("tag")
    port_elm= ent_elm.find("port")
    act_elm = ent_elm.find("action")
        
    if None in ( vid_elm, tag_elm, port_elm, act_elm ):
        util_method_tbl.mtbl_append_retmsg(ent_elm, "WRONG PARAMETERS")
    else:
        if act_elm.text == "add":
            act_str = "add"
            tag_str = ["-u",  ""] [tag_elm.text == "true"]
        else:            
            act_str = "del"
            tag_str = ""
       
        vlan_mbr_cfg(ent_elm, act_str, vid_elm.text, tag_str, port_elm.text)

#
# get functions 
#
@util_utl.utl_dbg
def vlan_get(ent_elm, db_args):
    # ex: {'Vlan10': {'vlanid': '10', 'members': ['Ethernet9']}}
    vlan_lst     = db_args.cfgdb.get_table(util_utl.CFGDB_TABLE_NAME_VLAN)
    # ex: {('Vlan10', 'Ethernet9'): {'tagging_mode': 'tagged'}}
    vlan_mbr_lst = db_args.cfgdb.get_table(util_utl.CFGDB_TABLE_NAME_VLAN_MBR)

    vlans_elm = ET.Element('vlans')
    for vlan in vlan_lst:
        vlan_elm = ET.Element('vlan')
        vid_elm  = ET.SubElement(vlan_elm, 'id')
        vid_elm.text = vlan_lst[vlan]['vlanid']
        tag_elm  = ET.SubElement(vlan_elm, 'tag-mbrs')
        utag_elm = ET.SubElement(vlan_elm, 'utag-mbrs')

        tag_lst = []
        utag_lst = []

        for mbr_vlan, mbr_port in vlan_mbr_lst.keys():
            if mbr_vlan == vlan:
                if vlan_mbr_lst[vlan, mbr_port]['tagging_mode'] == 'tagged':
                    tag_lst.append(mbr_port)
                else:
                    utag_lst.append(mbr_port)

        tag_elm.text  = ",".join(tag_lst)
        utag_elm.text = ",".join(utag_lst)

        vlans_elm.append(vlan_elm)

    ent_elm.append(vlans_elm)


#
# register vlan related functions to method table
#
util_method_tbl.mtbl_register_method('create-vlan', vlan_create)
util_method_tbl.mtbl_register_method('remove-vlan', vlan_remove)
util_method_tbl.mtbl_register_method('get-vlan',    vlan_get)
util_method_tbl.mtbl_register_method('vlan-member', vlan_mbr)
