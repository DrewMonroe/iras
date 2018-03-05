#!/usr/bin/env python3


bgpstream_interval = (60*60*8) # seconds

import time
from _pybgpstream import BGPStream, BGPRecord, BGPElem
import csv
import multiprocessing


def bgpstream_worker(project, collector, dumptime):
    def normalize_asns(ases):
        for r in ases:
            for a in r.strip('{}').split(','):
                try:
                    yield int(a)
                except:
                    pass

    stream = BGPStream()

    stream.add_filter('record-type','ribs')
    stream.add_filter('project', project)
    stream.add_filter('collector',collector)
    stream.add_interval_filter(dumptime,dumptime+3600)

    stream.start()

    rec = BGPRecord()

    drec = 0
    delem = 0

    while(stream.get_next_record(rec)):
        drec += 1
        while(True):
            elem = rec.get_next_elem()
            if not elem:
                break

            delem += 1

            pfx = elem.fields['prefix']
            aspath = list(normalize_asns(elem.fields['as-path'].split(" ")))
            yield (pfx, (aspath[-1] if aspath else None))

    print("drec=%d delem=%d" % (drec, delem))

def bgpstream_get_origins():
    outt = {}
    for ann in bgpstream_worker('ris', 'rrc11', 1519977600):
        if ann[0] not in outt:
            outt[ann[0]] = set()
        outt[ann[0]].update([ann[1]])
    return outt


def main():
    ot = bgpstream_get_origins()
    with open("origins.csv", 'w') as out:
        outw = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
        for k in ot:
            outw.writerow([k, ';'.join([str(asn) for asn in ot[k]])])


if __name__ == '__main__':
    main()

