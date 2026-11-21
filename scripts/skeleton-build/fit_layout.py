"""Derive the true-proportion layout (layout.json) from the converted meshes.
Inputs: out/_manifest_bones.json (convert.py) and bones.json (authored bones dumped from the old data bundle).
Uniform scale K keeps the original body height; organs/nerves/shell get an affine + local warp (BT) so they stay registered."""
import json, numpy as np
man = json.load(open('/tmp/work/out/_manifest_bones.json')); bones = {b['id']: b for b in json.load(open('/tmp/work/bones.json'))}
ids = list(man); K = 1.93
R = np.array([man[i]['worldCenter'] for i in ids]); A = np.array([bones[i]['pos'] for i in ids])
ymin = min(man[i]['worldCenter'][1] - man[i]['bounds'][1] / 2 for i in ids)
t = np.array([0.0, -0.178 - K * ymin, 0.0]); t[2] = A[:, 2].mean() - K * R[:, 2].mean()
N = K * R + t
layout = {i: {'p': [round(float(x), 4) for x in N[n]], 's': [round(K * float(d), 4) for d in man[i]['bounds']]} for n, i in enumerate(ids)}
G = []
for ax in range(3):
    a = N[:, ax].std() / A[:, ax].std(); G.append((float(a), float(N[:, ax].mean() - a * A[:, ax].mean())))
BT = []
for i, v in layout.items():
    a = bones[i]['pos']; g = [a[0] * G[0][0] + G[0][1], a[1] * G[1][0] + G[1][1], a[2] * G[2][0] + G[2][1]]
    BT.append([round(a[0], 4), round(a[1], 4), round(a[2], 4)] + [round(v['p'][k] - g[k], 4) for k in range(3)])
for side, sx in (('r', -1), ('l', 1)):  # bones with no scan: place by hand inside/below neighbouring bones
    layout[f'malleus_{side}'] = {'p': [sx * 0.103, 2.758, -0.0066]}; layout[f'incus_{side}'] = {'p': [sx * 0.095, 2.758, -0.0126]}; layout[f'stapes_{side}'] = {'p': [sx * 0.087, 2.758, -0.0186]}
layout['coccyx'] = {'p': [0.003, 1.33, -0.075]}
json.dump({'K': K, 't': t.tolist(), 'G': G, 'layout': layout, 'BT': BT, 'SHELL_SX': 1.22}, open('/tmp/work/layout.json', 'w'))
