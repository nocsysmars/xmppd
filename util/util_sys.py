#
# util_sys.py
#
# system related APIs.
#

import psutil
from xml.etree import cElementTree as ET
from . import util_utl, util_method_tbl

#
# set functions
#

#
# get functions 
#
@util_utl.utl_dbg
def sys_get_cpu(ent_elm, db_args):
    cpu_elm = ET.Element('cpu')
    stats_elm = ET.SubElement(cpu_elm, 'stats')
    usage_elm = ET.SubElement(stats_elm, 'usage')
    usage_elm.text = str(psutil.cpu_percent())
    ent_elm.append(cpu_elm)

@util_utl.utl_dbg
def sys_get_mem(ent_elm, db_args):
	# ex: svmem(total=103..., available=647..., percent=37.6, 
    #     used=818..., free=218..., active=474..., inactive=275..., 
    #     buffers=790..., cached=350..., shared=787..., slab=199...)
    #
    # used = total - free - cached - buffers
    # percent = total - avail/ total
    mem = psutil.virtual_memory()
    mem_elm = ET.Element('mem')
    stats_elm = ET.SubElement(mem_elm, 'stats')
    usage_elm = ET.SubElement(stats_elm, 'usage')
    usage_elm.text = str(mem.percent)
    ent_elm.append(mem_elm)

@util_utl.utl_dbg
def sys_get_disk(ent_elm, db_args):
    disk = psutil.disk_usage('/')
    disk_elm = ET.Element('disk')
    stats_elm = ET.SubElement(disk_elm, 'stats')
    usage_elm = ET.SubElement(stats_elm, 'usage')
    usage_elm.text = str(disk.percent)
    ent_elm.append(disk_elm)

#
# register functions to method table
#
util_method_tbl.mtbl_register_method('get-cpu-statistics', sys_get_cpu)
util_method_tbl.mtbl_register_method('get-mem-statistics', sys_get_mem)
util_method_tbl.mtbl_register_method('get-disk-statistics', sys_get_disk)

