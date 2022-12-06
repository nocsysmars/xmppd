#
# util_fdb.py
#
# fdb related APIs.
#

from xml.etree import cElementTree as ET
from . import util_utl, util_method_tbl

#
# set functions
#


#
# get functions
#

# ex: fdb_name = 'Vlan4039:34:ef:b6:74:88:38'
#     fdb_info = {'type': 'dynamic', 'port': 'Ethernet48'}
def fdb_get_one(fdb_name, fdb_info):
    fld_map = [ {"fld" : "type",   "tag" : "type" },
                {"fld" : "port",   "tag" : "port" } ]

    if not fdb_name.startswith('Vlan'):
        return None

    fdb_elm = ET.Element('mac')
    vid_mac = fdb_name.split(':', 1)
    vid_elm = ET.SubElement(fdb_elm, 'vlan')
    vid_elm.text = vid_mac[0].replace('Vlan', '')
    adr_elm = ET.SubElement(fdb_elm, 'address')
    adr_elm.text = vid_mac[1]

    for fld in fld_map:
        tmp_elm = ET.SubElement(fdb_elm, fld["tag"])
        if fld["fld"] in fdb_info:
            tmp_elm.text = fdb_info[fld["fld"]]
        
    return fdb_elm

@util_utl.utl_dbg
def fdb_get(ent_elm, db_args):
    db      = db_args.statdb
    pattern = util_utl.STATDB_TABLE_NAME_FDB + "*"

    fdbs_elm = ET.Element('macs')

    fdb_keys = db_args.statdb.keys(db.STATE_DB, pattern)

    if fdb_keys != None:
        db_sep = db.get_db_separator(db.STATE_DB)
        # ex: fdb_keys = [ 'FDB_TABLE|Vlan4039:34:ef:b6:74:88:38' ]
        for fdb_key in fdb_keys:
            # ex: fdb_info = {'type': 'dynamic', 'port': 'Ethernet48'}
            fdb_info = db.get_all(db.STATE_DB, fdb_key)

            fdb_one = fdb_get_one(fdb_key.split(db_sep)[1], fdb_info)

            if fdb_one != None:
               fdbs_elm.append(fdb_one)

    ent_elm.append(fdbs_elm)
#
# register functions to method table
#
util_method_tbl.mtbl_register_method('get-mac', fdb_get)
