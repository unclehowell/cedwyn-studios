#!/usr/bin/env python3
"""Print the next piece of work: python3 tools/next.py [--lang en] [--scene F002] [--all]
Walks studio/queue/queue.json in order, then each scene's shots in order, then cy/en/es; prints the first unit that is
not done with the step it needs (still | line | take | move | i2v | card | qa). --all lists every open unit. — Tab agent"""
import json, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0]); import studio as S
a = sys.argv[1:]; opt = lambda n: a[a.index(n) + 1] if n in a else None
if '--all' in a:
    order, skip = S.scene_order()
    for sid in order:
        sc = S.load_scene(sid)
        if sc.get('status') in skip: continue
        for shid in sc['shots']:
            sh = S.load_shot(sid, shid)
            for name, u in S.units(sh):
                st = S.step_for(sh, name, u)
                if st: print(f'{sid}/{shid}\t{name}\t{sh["type"]}\t{u.get("status")}\t{st}')
else:
    print(json.dumps(S.next_unit(opt('--lang'), opt('--scene')) or {'next': None, 'why': 'every unit is done'}))
