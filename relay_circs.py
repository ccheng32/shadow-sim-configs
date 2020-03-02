import sys
import re
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import xml.etree.ElementTree as et

exit_band = {}
max_band= 0
config_tree = et.parse("shadow.config.xml")
config_root = config_tree.getroot()
for elem in config_root:
  if 'id' in elem.attrib:
    hostname = elem.attrib['id']
    if re.match(r'relay\d+exit[a-z]*', hostname):
      exit_band[hostname] = int(elem.attrib['bandwidthup'])
      max_band = max(exit_band[hostname], max_band)

file_list = sys.argv[1]

max_iter = int(sys.argv[2])
circs_per_iter = 1
iter_exits_map = []
for i in range(max_iter):
  iter_exits_map.append(dict())
iter_bw_map = []
for i in range(max_iter):
  iter_bw_map.append(dict())

fl = open(file_list, "r") 
for name in fl:
  f = open(name.strip(), "r")
  circ_exit_map = {}
  for line in f:
    built = re.search(r'(CIRC) (\d+) (BUILT)', line)
    if built:
      exit = re.findall(r'relay\d+exit[a-z]*', line)
      if len(exit) > 0:
        circ_exit_map[built.groups()[1]] = exit[0]
  f.close()
  
  line_cnt = 0
  f = open(name.strip(), "r")
  for line in f:
    remapped = re.search(r'(REMAP) (\d+)', line)
    if remapped:
      circ_num = remapped.groups()[1]
      if circ_num in circ_exit_map:
        exit = circ_exit_map[circ_num]
        mp = iter_exits_map[line_cnt / circs_per_iter]
        if exit not in mp:
          mp[exit] = 0
        mp[exit] += 1
      #else:
      #  print "Warning: CIRC ", circ_num, "'s exit is unknown."
      line_cnt += 1
    if line_cnt / circs_per_iter >= max_iter:
      break
  f.close()
fl.close()

for i in range(max_iter*2):
  if i % 2 == 1: continue
  fname = sys.argv[3] + "v3bw." + str(i)
  fbw = open(fname, "r")
  for line in fbw:
    nick = re.search(r'(nick=)(relay\d+exit[a-z]*)',line)
    if nick:
      relay_name = nick.groups()[1]
      bw = re.search(r'(bw=)(\d+)',line).groups()[1]
      iter_bw_map[i/2][relay_name] = int(bw)
  fbw.close()

exits = set()
for e in iter_bw_map[0]:
  exits.add(e)

sorted_exits = list(exits)
sorted_exits.sort()

for e in sorted_exits:
  cnts = []
  bws = []
  prod = []
  ans = [exit_band[e]] * max_iter
  for i in range(max_iter):
    if e in iter_exits_map[i]: cnts.append(iter_exits_map[i][e])
    else: cnts.append(0)
    if e in iter_bw_map[i]: bws.append(iter_bw_map[i][e])
    else: bws.append(0)
    prod.append( (1+cnts[-1]) * bws[-1] )

  print e,"num_circs",cnts
  print e,"observation",bws
  print e,"product",prod

  print "Creating figure..."
  color = 'r'
  fig,ax1 = plt.subplots()
  ax1.plot(bws,color=color)
  ax1.set_ylabel('bandwidth(KB/s)',color=color)
  ax1.tick_params(axis='y', labelcolor=color)
  ax1.set_xlabel('round')

  color = 'b'
  ax2 = ax1.twinx()
  ax2.plot(cnts,'b', color=color)
  ax2.set_ylabel('# of times chosen', color=color)
  ax2.tick_params(axis='y', labelcolor=color)

  plt.title(e + ' observations and times chosen')
  plt.savefig(e +'_observation.png')

  plt.close(fig)

  # Create bw*(num_circs + 1) figure
  plt.plot(ans, color='r')
  plt.plot(prod, color = 'b')
  plt.ylim(0,max_band*1.1)
  plt.xlabel('round')
  plt.ylabel('total bandwidth (KB/s)')
  plt.title('observation x (1+num_circs) at each round for ' + e)
  plt.savefig(e + '_product.png')
  plt.close()

colors = cm.rainbow(np.linspace(0, 1, len(exits)))
ps = []
prev_cnts = [0] * max_iter
r = range(max_iter)
ecnt = 0
exit_list = []
r_natural = []
for i in r:
  r_natural.append((i+1))
for e in sorted_exits:
  cnts = []
  for i in range(max_iter):
    if e in iter_exits_map[i]: cnts.append(iter_exits_map[i][e])
    else: cnts.append(0)
  pp = plt.bar(r_natural, cnts, align='center', bottom=prev_cnts, width = 0.35, color=colors[ecnt])
  for i in range(max_iter):
    prev_cnts[i] += cnts[i]
  ps.append(pp[0])
  exit_list.append(e)
  ecnt += 1

plt.ylabel('Times chosen')
plt.title('Total times chosen in each iteration for each relay')
plt.xlabel('round')
#plt.xticks(r_natural, r_natural)
ps.reverse()
exit_list.reverse()
plt.legend(ps, exit_list, loc='center left', bbox_to_anchor=(1, 0.5))
plt.savefig('total_relay_times.png', bbox_inches='tight')
plt.close()
