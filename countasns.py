#!/usr/bin/env python3

import time
from _pybgpstream import BGPStream, BGPRecord, BGPElem

stream = BGPStream()
rec = BGPRecord()

stream.add_filter('record-type','ribs')
t = int(time.time())
stream.add_interval_filter((t-(3600*8)),t)

stream.start()

res = set()

def normalize_asns(ases):
    for r in ases:
        for a in r.strip('{}').split(','):
            try:
                yield int(a)
            except:
                pass

while(stream.get_next_record(rec)):
    elem = rec.get_next_elem()
    while(elem):
        # Get the prefix
        pfx = elem.fields['prefix']
        # Get the list of ASes in the AS path
        ases = elem.fields['as-path'].split(" ")
        res.update(list(normalize_asns(ases)))
        elem = rec.get_next_elem()

#for pfx in prefix_origin:
#    if len(prefix_origin[pfx]) > 1:
#        print(pfx, ",".join(prefix_origin[pfx]))

print(len(res))

