import sys
import re

a = []
with open(sys.argv[1]) as f:
  lines = f.readlines()
  for l in lines:
    tote = re.search(r'(total-bytes-recv)=(\d+)', l)
    a.append(int(tote.groups()[1]))

a.sort()

#print a
    
bands = []
for i in range(len(a)):
  c = 'perfclient' + str(i)
  tgen_fname =  'shadow.data/hosts/perfclient' + str(i) + '/stdout-perfclient'+str(i)+'.tgen.1002.log'  
  onion_fname =  'shadow.data/hosts/perfclient' + str(i) + '/stdout-perfclient'+str(i)+'.oniontrace.1001.log'  
  with open(tgen_fname) as f:
    lines = f.readlines()
  for l in lines:
    if 'TIMEOUT' in l:
      tl = l
  with open(onion_fname) as f:
    lines = f.readlines()
  for l in lines:
    if 'CIRC 6 BUILT' in l:
      ol = l
  band = int(re.search(r'(total-bytes-recv)=(\d+)', tl).groups()[1])
  relays = re.findall(r'relay\d+[a-z]*' , ol)
  bands.append((float(band)/1024/300,relays))
bands.sort()
bands.reverse()
print bands
