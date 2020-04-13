import sys
import re
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm

file_list = sys.argv[1]
rounds = int(sys.argv[2])
fl = open(file_list, "r") 

perf_list = []
for i in range(rounds):
  perf_list.append([])
for name in fl:
  round_cnt = 0
  f = open(name.strip(), "r")
  for line in f:
    built = re.search(r'TIMEOUT', line)
    if built:
      recv_line = re.search(r'(total-bytes-recv)=(\d+)', line)
      perf_list[round_cnt].append(int(recv_line.groups()[1]))
      round_cnt += 1
    if round_cnt >= rounds:
      break
  f.close()
fl.close()

ten_avgs = []
five_avgs = []
one_avgs = []
for rnd in range(rounds):
  perf_list[rnd].sort()
  plt.plot(perf_list[rnd])
  plt.title('Client performance distribution in round ' + str(rnd))
  plt.xlabel('Clients (sorted by performance)')
  plt.ylabel('Number of bytes downloaded')
  plt.yscale('log')
  plt.savefig('client_performance_' + str(rnd) + '.png')
  plt.close()
  one_per = int(len(perf_list[rnd]) * 0.01)
  five_per = int(len(perf_list[rnd]) * 0.05)
  ten_per = int(len(perf_list[rnd]) * 0.1)
  one_avg = np.mean(perf_list[rnd][0:one_per])
  five_avg = np.mean(perf_list[rnd][0:five_per])
  ten_avg = np.mean(perf_list[rnd][0:ten_per])
  ten_avgs.append(ten_avg)
  five_avgs.append(five_avg)
  one_avgs.append(one_avg)
  print 'minimum: ' + str(min(perf_list[rnd])) + ', smallest 1% avg: ' + str(one_avg) + ', smallest 5% avg: ' + str(five_avg) + ', smallest 10% avg: ' + str(ten_avg)

plt.plot(ten_avgs, label='Slowest 10%')
plt.plot(five_avgs, label='Slowest 5%')
plt.plot(one_avgs, label='Slowest 1%')
plt.xlabel('round')
plt.ylabel('Number of bytes downloaded in a period')
plt.title('Average performance of the slowest clients')
plt.legend(bbox_to_anchor=(0.5,-0.2), loc="lower center", ncol=  3)
plt.savefig('avg_performance.png', bbox_inches='tight')
plt.close()
