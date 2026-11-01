import sys, glob, os
for d in sys.argv[1:]:
    p = os.path.join(d, 'model.obj')
    if not os.path.exists(p): continue
    L = open(p).read().split('\n')
    V = [i for i, l in enumerate(L) if l.startswith('v ')]
    cur = None; used = {}
    for l in L:
        if l.startswith('usemtl'): cur = l.split()[1]
        elif l.startswith('f '):
            for t in l.split()[1:]: used.setdefault(int(t.split('/')[0]) - 1, set()).add(cur)
    img_mats = set()
    mtl = open(os.path.join(d, 'model.mtl')).read()
    blk = None
    for l in mtl.split('\n'):
        if l.startswith('newmtl'): blk = l.split()[1]
        if l.startswith('map_Kd'): img_mats.add(blk)
    zs = [float(L[V[i]].split()[3]) for i in range(len(V))]
    zmax = max(zs); moved = 0
    for vi, mats in used.items():
        if mats <= img_mats:
            a = L[V[vi]].split()
            z = float(a[3])
            if z > zmax - (zmax - min(zs)) * 0.6:    # front-facing image faces
                a[3] = f'{z + 0.12:.4f}'; L[V[vi]] = ' '.join(a); moved += 1
    open(p, 'w').write('\n'.join(L))
    print(d, 'image mats', img_mats, 'moved', moved)
