#
# util_method_tbl.py
#
# method table related APIs.

from xml.etree import cElementTree as ET

method_table = {}

def mtbl_append_retmsg(ent_elm, msg):
    ret_elm = ent_elm.find('ret')
    if ret_elm == None:
        ret_elm = ET.SubElement(ent_elm, 'ret')

    if ret_elm.text == None:
        ret_elm.text = msg
    else:
        ret_elm.text += ' ' + msg

def mtbl_register_method(name, func_p):
    if name not in method_table:
        method_table[name] = func_p

def mtbl_execute_method(name, ent_elm, db_args):
    if name in method_table:
        method_table[name](ent_elm, db_args)
    else:
        mtbl_append_retmsg(ent_elm, "INVALID METHOD")

    return ent_elm
