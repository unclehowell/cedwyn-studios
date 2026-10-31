#!/usr/bin/env python3
"""IPFS CIDv1 for a file, pure Python (no packages): the CID `ipfs add --cid-version=1` (Kubo defaults: raw leaves,
fixed 256 KiB chunks, balanced DAG, 174 links per node, sha2-256, base32) gives for the same bytes. Computing a CID does not
put the file on IPFS; pinning is a separate step (see STUDIO.md "Media store").
Usage: python3 tools/ipfs_cid.py <file> [<file> ...]   ->  "<cid>  <file>" per line.   Self-test: python3 tools/ipfs_cid.py --selftest
— Sion's Tab agent, 31 Oct 2026"""
import hashlib, sys, base64
CHUNK = 262144; MAXLINKS = 174

def _varint(n):
    out = bytearray()
    while True:
        b = n & 0x7f; n >>= 7
        if n: out.append(b | 0x80)
        else: out.append(b); return bytes(out)
def _field(num, wire, payload):
    key = _varint((num << 3) | wire)
    return key + (_varint(payload) if wire == 0 else _varint(len(payload)) + payload)
def _cid(codec, digest):           # CIDv1 bytes: version, codec, multihash(sha2-256)
    return _varint(1) + _varint(codec) + b'\x12\x20' + digest
def cid_str(cid_bytes):
    return 'b' + base64.b32encode(cid_bytes).decode().lower().rstrip('=')

class _Leaves:
    def __init__(self, f): self.f = f; self.buf = f.read(CHUNK); self.first = True
    def done(self): return not self.buf and not self.first
    def next(self):
        data = self.buf; self.first = False; self.buf = self.f.read(CHUNK)
        return (_cid(0x55, hashlib.sha256(data).digest()), len(data), len(data))   # (cid, filesize, tsize)

def _node(children):                # children: [(cid, filesize, tsize)] -> dag-pb UnixFS File node
    fsize = sum(c[1] for c in children)
    unixfs = _field(1, 0, 2) + _field(3, 0, fsize) + b''.join(_field(4, 0, c[1]) for c in children)
    links = b''.join(_field(2, 2, _field(1, 2, c[0]) + _field(2, 2, b'') + _field(3, 0, c[2])) for c in children)
    blob = links + _field(1, 2, unixfs)
    return (_cid(0x70, hashlib.sha256(blob).digest()), fsize, len(blob) + sum(c[2] for c in children))

def _fill(lv, depth, first=None):
    kids = [first] if first else []
    while len(kids) < MAXLINKS and not lv.done():
        kids.append(lv.next() if depth == 1 else _fill(lv, depth - 1))
    return _node(kids)

def cid_of_fileobj(f):
    lv = _Leaves(f); root = lv.next(); depth = 1
    while not lv.done():
        root = _fill(lv, depth, first=root); depth += 1
    return cid_str(root[0])
def cid_of_file(path):
    with open(path, 'rb') as f: return cid_of_fileobj(f)

def selftest():
    import io
    # published vectors: the empty file and b"hello world" as single raw leaves (CIDv1, sha2-256)
    assert cid_of_fileobj(io.BytesIO(b'')) == 'bafkreihdwdcefgh4dqkjv67uzcmw7ojee6xedzdetojuzjevtenxquvyku'
    assert cid_of_fileobj(io.BytesIO(b'hello world')) == 'bafkreifzjut3te2nhyekklss27nh3k72ysco7y32koao5eei66wof36n5e'
    print('selftest ok')

if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']: selftest()
    else:
        for p in sys.argv[1:]: print(cid_of_file(p) + '  ' + p)
