#
# util_db.py
#
#  

import swsssdk


def db_connect_by_name(db_name):
    if db_name not in ['APPL', 'COUNTER', 'ASIC', 'STATE', 'CFG' ]:
        return None

    if db_name == 'CFG':
        ret_db = swsssdk.ConfigDBConnector()
        ret_db.connect()
        return ret_db

    ret_db = swsssdk.SonicV2Connector(host='127.0.0.1')
    if ret_db is None:
        return None

    if db_name == 'APPL':
        db_id = ret_db.APPL_DB
    elif db_name == 'COUNTER':
        db_id = ret_db.COUNTERS_DB
    elif db_name == 'ASIC':
        db_id = ret_db.ASIC_DB
    elif db_name == 'STATE':
        db_id = ret_db.STATE_DB

    ret_db.connect(db_id)
    return ret_db

