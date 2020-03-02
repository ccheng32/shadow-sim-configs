import sys
import re
import xml.etree.ElementTree as et
import numpy as np
import matplotlib.cm as cm
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

exit_band = {}
exit_ip = {}
exits = []
max_band= 0
config_tree = et.parse("shadow.config.xml")
config_root = config_tree.getroot()
for elem in config_root:
  if 'id' in elem.attrib:
    hostname = elem.attrib['id']
    if re.match(r'relay\d+exit[a-z]*', hostname):
      exits.append(hostname)
      exit_ip[hostname] = elem.attrib['iphint']
      exit_band[hostname] = int(elem.attrib['bandwidthup'])
      max_band = max(exit_band[hostname], max_band)

exits.sort()
exit_pub = {}
for e in exits:
  relay_name = e
  ip = exit_ip[e]
  band = exit_band[e]
  max_iter = int(sys.argv[1])
  fname = sys.argv[2]
  print relay_name, band
  
  arr = ip.split('.')
  assert len(arr) == 4
  c = (int(arr[0]) << 24) + (int(arr[1]) << 16) + (int(arr[2]) << 8) + int(arr[3])
  c_str = hex(c)[2:]
  
  f = open(fname, 'r')
  found_relay = False
  bands = []
  c_str_cnt = 0
  for line in f:
    if c_str in line:
      found_relay = True
    if found_relay:
      pub = re.search(r'(published bandwidth:) (\d+)', line)
      if pub:
        found_relay = False
        if c_str_cnt % 2 == 0:
          bands.append(int(pub.groups()[1]))
      c_str_cnt += 1
    if len(bands) >= max_iter:
      break
  f.close()
  print relay_name,bands
  exit_pub[relay_name] = list(bands)
  
  ans = [band]*(max_iter)

  plt.ylim(0,max_band * 1.1)
  plt.plot(ans,'r')
  plt.plot(bands,'b')
  plt.ylabel('weight')
  plt.xlabel('round')
  plt.title(relay_name + ' published weights')
  plt.savefig(relay_name + '_publishedBW.png')
  plt.close()


max_iter = min(max_iter, len(exit_pub[exits[0]]))
pub_sums = [0] * max_iter
for e in exits:
  for i in range(max_iter):
    pub_sums[i] += exit_pub[e][i] 

colors = cm.rainbow(np.linspace(0, 1, len(exits)))
ps = []
prev_cnts = [0] * max_iter
r = range(max_iter)
ecnt = 0
exit_list = []
r_natural = []
for i in r:
  r_natural.append((i+1))
for e in exits:
  cnts = []
  for i in range(max_iter):
    if e in exit_pub: cnts.append(float(exit_pub[e][i]) / pub_sums[i])
  pp = plt.bar(r_natural, cnts, align='center', bottom=prev_cnts, width = 0.35, color=colors[ecnt])
  for i in range(max_iter):
    prev_cnts[i] += cnts[i]
  ps.append(pp[0])
  exit_list.append(e)
  ecnt += 1

plt.ylabel('weights')
plt.title('Normalized published weights in each iteration for each relay')
plt.xlabel('round')
#plt.xticks(r_natural, r_natural)
ps.reverse()
exit_list.reverse()
plt.legend(ps, exit_list, loc='center left', bbox_to_anchor=(1, 0.5))
plt.savefig('relative_relay_weights.png', bbox_inches='tight')
plt.close()
