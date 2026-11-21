import json
M={}
def both(base, r, l): M[base+'_r']=[str(r)]; M[base+'_l']=[str(l)]
for k,v in dict(frontal=52734,occipital=52735,sphenoid=52736,ethmoid=52740,vomer=9710,mandible=52748,hyoid=52749,sacrum=16202).items(): M[k]=[str(v)]
M['sternum']=['7486','7487','7488']
for b,(r,l) in dict(parietal=(52788,52789),temporal=(52738,52739),maxilla=(53649,53650),zygomatic=(52892,52893),nasal=(53647,53648),lacrimal=(53645,53646),palatine=(53655,53656),concha=(54737,54738),
  clavicle=(13322,13323),scapula=(13395,13396),humerus=(23130,23131),radius=(23464,23465),ulna=(23467,23468),
  scaphoid=(24435,24436),lunate=(24437,24438),triquetrum=(24439,24440),pisiform=(24441,24442),trapezium=(24443,24444),trapezoid=(23725,24445),capitate=(24446,24447),hamate=(24448,24449),
  os_coxae=(16586,16587),femur=(24474,24475),patella=(24486,24487),tibia=(24477,24478),fibula=(24480,24481),calcaneus=(24497,24498),talus=(24482,24483),navicular=(24500,24501),cuboid=(24528,24529),
  cuneiform_med=(24521,24522),cuneiform_int=(24523,24524),cuneiform_lat=(24525,24526)).items(): both(b,r,l)
for i,f in enumerate([12519,12520,12521,12522,12523,12524,12525],1): M[f'c{i}']=[str(f)]
for i,f in enumerate([9165,9187,9209,9248,9922,9945,9968,9991,10014,10037,10059,10081],1): M[f't{i}']=[str(f)]
for i,f in enumerate([13072,13073,13074,13075,13076],1): M[f'l{i}']=[str(f)]
ribR=[7857,7882,7909,7957,8066,8175,8229,8283,8364,8445,8531,8533]; ribL=[7987,8012,8039,8148,8093,8202,8256,8310,8391,8472,8532,8534]
ccR={1:7875,2:7886,3:7913,4:7976,5:8070,6:8194,7:8248}; ccL={1:8005,2:8031,3:8058,4:8167,5:8112,6:8221,7:8275}
for i in range(12):
    M[f'rib_{i+1}_r']=[str(ribR[i])]+([str(ccR[i+1])] if i+1 in ccR else [])
    M[f'rib_{i+1}_l']=[str(ribL[i])]+([str(ccL[i+1])] if i+1 in ccL else [])
for n,(r,l) in {1:(24464,24465),2:(24466,24467),3:(24468,24469),4:(24470,24471),5:(24472,24473)}.items(): both(f'mc_{n}',r,l)
for n,(r,l) in {1:(24507,24508),2:(24509,24510),3:(24511,24512),4:(24513,24514),5:(24515,24516)}.items(): both(f'mt_{n}',r,l)
for n,(r,l) in enumerate([(24450,65470),(24451,71915),(24452,71908),(24453,71916),(24454,66791)],1): both(f'hand_prox_{n}',r,l)
for n,(r,l) in zip(range(2,6),[(24455,23938),(24456,23940),(24457,23942),(24458,23944)]): both(f'hand_mid_{n}',r,l)
for n,(r,l) in enumerate([(24459,23951),(24460,23953),(24461,23955),(24462,23957),(24463,23959)],1): both(f'hand_dist_{n}',r,l)
for n,(r,l) in enumerate([(43253,43254),(32634,32635),(32636,32637),(32638,32639),(32640,32641)],1): both(f'foot_prox_{n}',r,l)
for n,(r,l) in zip(range(2,6),[(32642,32643),(32644,32645),(32646,32647),(230986,230988)]): both(f'foot_mid_{n}',r,l)
for n,(r,l) in enumerate([(32650,32651),(32652,32653),(32654,32655),(32656,32657),(32658,32659)],1): both(f'foot_dist_{n}',r,l)
