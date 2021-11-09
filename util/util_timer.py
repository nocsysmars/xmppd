#
# util_timer.py
#
# timer related APIs.
#

import util_utl, util_method_tbl, pdb
from collections import deque


# { "interval"  :
#   "cb_f"      :
#   "time_left" :  }
#
# interval == 0 -> once
#           > 0 -> repeat
class MyPeriodCb(object):
    def __init__(self):
        self.total_time = 0
        self.cb_q = deque()

    def register_period_cb(self, t_start, t_interval, cb_f):
        new_rec = { "interval" : t_interval,
                    "cb_f"     : cb_f }

        if t_start > self.total_time:
            # put new_rec to the tail
            new_rec["time_left"] = t_start - self.total_time
            self.total_time = t_start
            self.cb_q.append( new_rec )
        else:
            tmp_total = 0
            for idx in range(len(self.cb_q)):
                if tmp_total + self.cb_q[idx]["time_left"] > t_start:
                    # put new_rec to left
                    self.cb_q[idx]["time_left"] += (tmp_total - t_start)
                    new_rec["time_left"] = t_start - tmp_total
                    self.cb_q.insert(idx, new_rec)
                else:
                    tmp_total += self.cb_q[idx]["time_left"]

    def timer_tick(self):
        if self.total_time > 0:
            self.total_time -= 1
            self.cb_q[0]["time_left"] -= 1
            while self.cb_q[0]["time_left"] == 0:
                old_rec = self.cb_q.popleft()
                old_rec["cb_f"]()
                if old_rec["interval"] != 0:
                    self.register_period_cb(
                        old_rec["interval"], old_rec["interval"], old_rec["cb_f"])
