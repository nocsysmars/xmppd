#
# util_platform.py
#
# APIs for processing platform info.
#

import subprocess, json, re, pdb, util_utl

# ex: get "571254X1625041" from 
#         "Serial Number        0x23  14 571254X1625041"
def platform_get_syseeprom_output_val(sys_output, tag_str, pos):
    ret_val = None

    for idx in range(len(sys_output)):
        if tag_str in sys_output[idx]:
            ret_val = sys_output[idx].split()[pos]
            break

    return ret_val

#  get platform, serial, sw version
def platform_get_info():
    ret_val = {
        "hw"     : "unknown",
        "serial" : "unknown",
        "sw"     : "unknown"
    }

    # show platform syseeprom
    #  ex:  Command: sudo decode-syseeprom
    #       TlvInfo Header:
    #          Id String:    TlvInfo
    #          Version:      1
    #          Total Length: 169
    #       TLV Name             Code Len Value
    #       -------------------- ---- --- -----
    #       Manufacture Date     0x25  19 06/16/2016 14:01:49
    #       Diag Version         0x2E   7 2.0.1.4
    #       Label Revision       0x27   4 R01J
    #       Manufacturer         0x2B   6 Accton
    #       Manufacture Country  0x2C   2 TW
    #       Base MAC Address     0x24   6 CC:37:AB:EC:D9:B2
    #       Serial Number        0x23  14 571254X1625041
    #       Part Number          0x22  13 FP1ZZ5654002A
    #       Product Name         0x21  15 5712-54X-O-AC-B
    #       MAC Addresses        0x2A   2 74
    #       Vendor Name          0x2D   8 Edgecore
    #       Platform Name        0x28  27 x86_64-accton_as5712_54x-r0
    #       ONIE Version         0x29  14 20170619-debug
    #       CRC-32               0xFE   4 0x5B1B4944
    show_cmd_pf = 'show platform syseeprom'
    oc_comp = None
    (is_ok, output) = util_utl.utl_get_execute_cmd_output(show_cmd_pf)
    if is_ok:
        output = output.splitlines()
        fld_map = [ {"fld" : "hw",     "tag" : "Platform", "pos" : 4 },
                    {"fld" : "serial", "tag" : "Serial",   "pos" : 4 } ]

        for idx in range(len(fld_map)):
            val = platform_get_syseeprom_output_val(output, fld_map[idx]["tag"], fld_map[idx]["pos"])
            if val:
                ret_val[fld_map[idx]["fld"]] = val

    # show version
    #  ex: SONiC Software Version: SONiC.HEAD.434-dirty-20171220.093901
    #      Distribution: Debian 8.1
    #      Kernel: 3.16.0-4-amd64
    #      Build commit: ab2d066
    #      Build date: Wed Dec 20 09:44:56 UTC 2017
    #      Built by: johnar@jenkins-worker-3
    show_cmd_ver = 'show version'
    (is_ok, output) = util_utl.utl_get_execute_cmd_output(show_cmd_ver)
    if is_ok:
        output = output.splitlines()
        for idx in range(len(output)):
            if 'Software Version' in output[idx]:
                ret_val["sw"] = output[idx].split(': ')[1]
                break

    return ret_val

