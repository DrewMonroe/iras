#!/usr/bin/env python3


bgpstream_interval = (60*60*8) # seconds
roa_export = '/home/thlavacek/export.csv'

import ipaddress
import time
import iptree
import csv
import multiprocessing



class Announcement(object):
    def __init__(self, pfx, aspath):
        self.pfx = ipaddress.ip_network(pfx)
        self.aspath = aspath

    def getOrigin(self):
        if self.aspath and len(self.aspath) >= 1:
            return self.aspath[-1]
        else:
            return None

    def __str__(self):
        return '<%s %s>' % (str(self.pfx), str(self.aspath))

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash((self.pfx, tuple(self.aspath)))

    def __eq__(self, other):
        return (self.pfx, self.aspath) == (other.pfx, other.aspath)


def read_announcements(csvfile):
    with open(csvfile, 'r') as fh:
        reader = csv.reader(fh)
        for row in reader:
            for asn in row[1].split(';'):
                try:
                    asni = int(asn)
                    yield Announcement(row[0], [asni])
                except:
                    pass


class Roa(object):
    def __init__(self, pfx, asn, maxlen, trust_anchor):
        self.pfx = ipaddress.ip_network(pfx)
        self.asn = int(asn)
        self.maxlen = int(maxlen)

    def __str__(self):
        return '<%s-%d %s>' % (str(self.pfx), self.maxlen, str(self.asn))

    def __repr__(self):
        return str(self)


def build_roa_trees(filename):
    def normalize_asn(asn):
        return int(asn[2:])
    
    def read_roas(filename):
        fh = open(filename, 'r')
        csvr = csv.reader(fh)
        next(csvr)
        for row in csvr:
            # ASN,IP Prefix,Max Length,Trust Anchor
            yield Roa(row[1], normalize_asn(row[0]), row[2], row[3])


    t4 = iptree.IPLookupTree()
    t6 = iptree.IPLookupTree(ipv6=True)
    for roa in read_roas(filename):
        if isinstance(roa.pfx, ipaddress.IPv6Network):
            t = t6
        else:
            t = t4

        e = t.lookupNetExact(roa.pfx)
        if e:
            e.append(roa)
        else:
            t.add(roa.pfx,[roa])

    return (t4, t6)



def match(ann, roa_tree):
    def match_one_roa(ann, roa):
        #print("Matching ROA %s with announcement %s" % (str(roa), str(ann)))
        if not ann.pfx.overlaps(roa.pfx):
            raise Exception("match_one_roa with non-matching announcement and ROA called")

        if ann.pfx.prefixlen > roa.maxlen:
            return 2

        if ann.getOrigin() == roa.asn:
            return 1
        else:
            return 2

    invalid = False
    for rl in roa_tree.lookupAllLevels(ann.pfx):
        for r in rl:
            m = match_one_roa(ann, r)
            if m == 1:
                return 1
            elif m == 2:
                invalid = True
            else:
                raise Exception("Unknown match_roa result %d" % m)

    if invalid:
        return 2

    return 0


def main():
    def match_ext(ann, t4, t6):
        if isinstance(ann.pfx, ipaddress.IPv6Network):
            return match(ann, t6)
        else:
            return match(ann, t4)

    print("Building ROA tree")
    (t4,t6) = build_roa_trees(roa_export)
    print("Done building ROA tree")

    print("Matching BGP to ROAs")
    unknown = set()
    valid = set()
    invalid = set()
    with open("outfile.txt", 'w') as out:
        for ann in read_announcements("origins.csv"):
            res = match_ext(ann, t4, t6)
            out.write("%s %s %d\n" % (ann.pfx, str(ann.aspath), res))
            if res == 0:
                if ann.pfx in valid or ann.pfx in invalid:
                    continue
                unknown.update([ann.pfx])
            elif res == 1:
                valid.update([ann.pfx])
                if ann.pfx in unknown:
                    unknown.remove(ann.pfx)
                if ann.pfx in invalid:
                    invalid.remove(ann.pfx)
            elif res == 2:
                if ann.pfx in valid:
                    continue
                invalid.update([ann.pfx])
                if ann.pfx in unknown:
                    unknown.remove(ann.pfx)
            else:
                raise Exception("Unknown match result %d" % res)
    print("Done matching BGP to ROAs")
    print("unknown=%d valid=%d invalid=%d" % (len(unknown), len(valid), len(invalid)))

    with open("invalid.txt", 'w') as outi:
        for ipfx in invalid:
            if isinstance(ipfx, ipaddress.IPv4Network):
                outi.write("%s\n" % str(ipfx))
            else:
                print(type(ipfx))


if __name__ == '__main__':
    main()

