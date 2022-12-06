#
# util_lldp.py
#
# lldp related APIs.
#

from xml.etree import cElementTree as ET
from . import util_utl, util_method_tbl

#
# set functions
#


#
# get functions
#
lldp_info_fake = [
    { "lldp_rem_port_id_subtype"      : "2",
      "lldp_rem_port_id"              : "20",
      "lldp_rem_chassis_id_subtype"   : "4",
      "lldp_rem_chassis_id"           : "00:11:22:33:44:55",
      "lldp_rem_index"                : "1" },

    { "lldp_rem_port_id_subtype"      : "2",
      "lldp_rem_port_id"              : "21",
      "lldp_rem_chassis_id_subtype"   : "4",
      "lldp_rem_chassis_id"           : "00:11:22:33:44:55",
      "lldp_rem_index"                : "2" }
]



def lldp_get_info_one_port(inf_name, lldp_info):
    fld_map = [ {"fld" : "lldp_rem_port_id_subtype",   "tag" : "remPortIdSubType" },
                {"fld" : "lldp_rem_port_id",           "tag" : "remPortId" },
                {"fld" : "lldp_rem_chassis_id_subtype","tag" : "remChassSubType" },
                {"fld" : "lldp_rem_chassis_id",        "tag" : "remChassSubId" },
                {"fld" : "lldp_rem_index",             "tag" : "id"} ]

    lldp_elm = ET.Element('lldp')
    if_elm   = ET.SubElement(lldp_elm, 'ifName')
    if_elm.text = inf_name

    for fld in fld_map:
        tmp_elm = ET.SubElement(lldp_elm, fld["tag"])
        if fld["fld"] in lldp_info:
            tmp_elm.text = lldp_info[fld["fld"]]

    return lldp_elm

@util_utl.utl_dbg
def lldp_get(ent_elm, db_args):
    lldps_elm = ET.Element('lldps')

    lldp_keys = db_args.appdb.keys(
        db_args.appdb.APPL_DB, util_utl.APPDB_TABLE_NAME_LLDP + "*")

    if lldp_keys != None:
        db_sep = db_args.appdb.get_db_separator(db_args.appdb.APPL_DB)

        for lldp_key in lldp_keys:
            lldp_info = db_args.appdb.get_all(db_args.appdb.APPL_DB, lldp_key)

            inf_name = lldp_key.split(db_sep)[1]

            lldp_one = lldp_get_info_one_port(inf_name, lldp_info)

            lldps_elm.append(lldp_one)

    if util_utl.CFG_TBL["FAKE_DATA"] > 0:
        # fake data
        inf_fake_lst = [ "Ethernet1", "Ethernet2" ]
        for idx in range(len(inf_fake_lst)):
            lldp_one = lldp_get_info_one_port(inf_fake_lst[idx], lldp_info_fake[idx])
            lldps_elm.append(lldp_one)

    ent_elm.append(lldps_elm)

#
# register functions to method table
#
util_method_tbl.mtbl_register_method('get-lldp', lldp_get)
