#
# util_nbr.py
#
# ip neighbor (arp) related APIs.
#

from xml.etree import cElementTree as ET
from . import util_utl, util_method_tbl

#
# set functions
#


#
# get functions
#

# ex: nbr_name = 'Vlan4025:10.10.0.34'
#     nbr_info =  {'neigh':'80:a2:35:32:09:bb','family':'IPv4'}
def nbr_get_one(nbr_name, nbr_info):
    fld_map = [ {"fld" : "neigh",  "tag" : "mac" } ]

    if not nbr_name.startswith('Vlan'):
        return None

    if 'family' not in nbr_info or nbr_info['family'] != 'IPv4':
        return None

    nbr_elm = ET.Element('arp')
    vid_ip  = nbr_name.split(':', 1)
    vid_elm = ET.SubElement(nbr_elm, 'vlan')
    vid_elm.text = vid_ip[0].replace('Vlan', '')
    ip4_elm = ET.SubElement(nbr_elm, 'ip')
    ip4_elm.text = vid_ip[1]

    for fld in fld_map:
        tmp_elm = ET.SubElement(nbr_elm, fld["tag"])
        if fld["fld"] in nbr_info:
            tmp_elm.text = nbr_info[fld["fld"]]
        
    return nbr_elm    

@util_utl.utl_dbg
def nbr_get(ent_elm, db_args):
    nbrs_elm = ET.Element('arps')
    db       = db_args.appdb
    pattern  = util_utl.APPDB_TABLE_NAME_NBR + "*"
    nbr_keys = db_args.appdb.keys(db.APPL_DB, pattern)

    if nbr_keys != None:
        db_sep = db.get_db_separator(db.APPL_DB)

        # ex: nbr_keys = [ 'NEIGH_TABLE:Vlan4025:10.10.0.34' ]
        for nbr_key in nbr_keys:
            # ex: nbr_info = {'neigh':'80:a2:35:32:09:bb','family':'IPv4'}
            nbr_info = db.get_all(db.APPL_DB, nbr_key)

            nbr_one = nbr_get_one(nbr_key.split(db_sep,1)[1], nbr_info)

            if nbr_one != None:
               nbrs_elm.append(nbr_one)

        ent_elm.append(nbrs_elm) 
#
# register functions to method table
#
util_method_tbl.mtbl_register_method('get-arp', nbr_get)
