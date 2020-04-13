import sys
import re
import xml.etree.ElementTree as et
import numpy as np
import matplotlib.cm as cm
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

relay_band = {}
relays = []
exit_band = {}
exits = []
config_tree = et.parse("shadow.config.xml")
config_root = config_tree.getroot()
for elem in config_root:
  if 'id' in elem.attrib:
    hostname = elem.attrib['id']
    if re.match(r'relay\d+[a-z]*', hostname):
      band = int(elem.attrib['bandwidthup'])
      relay_band[hostname] = band
      relays.append(hostname)
      if 'exit' in hostname:
        exits.append(hostname)
        exit_band[hostname] = band

relay_band_sorted = [relay_band[e] for e in relay_band]
relay_band_sorted.sort()
plt.plot(relay_band_sorted)
plt.ylabel('capacity (kilobytes/s)')
plt.xlabel('Relay sorted by capacity')
plt.title('Distribution of relay capacities')
plt.savefig('relay_capacities.png')
plt.close()

exit_band_sorted = [exit_band[e] for e in exit_band]
exit_band_sorted.sort()
plt.plot(exit_band_sorted)
plt.ylabel('capacity (kilobytes/s)')
plt.xlabel('Exit Relay sorted by capacity')
plt.title('Distribution of exit relay capacities')
plt.savefig('exit_relay_capacities.png')
plt.close()

exits.sort()
exit_pub = {}
fname = sys.argv[1]
max_iter = 10000000
if len(sys.argv) > 2:
  max_iter = int(sys.argv[2])

f = open(fname, 'r')
for line in f:
  pub = re.search(r'(Published bandwidth) (relay\d+exit[a-z]*)=(\d+)', line)
  if pub:
    e = pub.groups()[1]
    if e not in exit_pub: exit_pub[e] = []
    exit_pub[e].append(int(pub.groups()[2]))
f.close()
  
max_iter = min(max_iter, len(exit_pub[exits[0]]))
err_mag_percents = {}
for e in exits:
  bands = list(exit_pub[e])
  del bands[1::2]
  ans = [exit_band[e]] * len(bands)
  print e + ' ' + str(exit_band[e])
  print e + ' ' + str(bands)
  err_mag_percents[e] = [100.0 * abs(float(bands[i] - ans[i])) / ans[i] for i in range(max_iter)]

  plt.ylim(0,max(exit_band[e], max(bands[1:max_iter])) * 1.1)
  plt.plot(ans[1:max_iter],'r', label='True capacity')
  plt.plot(bands[1:max_iter],'b', label='Estimated capacity')
  plt.ylabel('weight')
  plt.xlabel('round')
  plt.title(e + ' published weights')
  plt.legend(bbox_to_anchor=(0.5,-0.2), loc="lower center", ncol=  2)
  plt.savefig(e + '_publishedBW.png', bbox_inches='tight')
  plt.close()
  max_iter = min(max_iter, len(bands))

avg_err_mag_percents = []
for i in range(max_iter):
  avg_err_mag_percents.append(sum([err_mag_percents[a][i] for a in err_mag_percents]) / len(exits))
print "Average error %", avg_err_mag_percents
plt.plot(avg_err_mag_percents[1:])
plt.ylim(0, max(100, max(avg_err_mag_percents[1:])))
plt.xlabel('round')
plt.ylabel('percentage (%)')
plt.title('Average estimation error among all relays in each round')
plt.savefig('average_error.png')
plt.close()

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
