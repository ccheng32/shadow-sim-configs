import sys

N = int(sys.argv[1])

template ='''  <host bandwidthdown="1220700" bandwidthup="1220700" id="_CLIENT_HOLDER" >
    <process arguments="--Address _CLIENT_HOLDER --Nickname _CLIENT_HOLDER --DataDirectory shadow.data/hosts/_CLIENT_HOLDER --GeoIPFile ~/.shadow/share/geoip --defaults-torrc conf/tor.common.torrc -f conf/tor.perfclient.torrc" plugin="tor" preload="tor-preload" starttime="150" />
    <process arguments="Mode=log TorControlPort=9051 LogLevel=info Events=BW,ORCONN,CIRC,STREAM" plugin="oniontrace" starttime="150" />
    <process arguments="conf/tgen-perf.tgenrc.graphml" plugin="tgen" starttime="258" />
  </host>
'''

result = ""

for i in range(N):
  result += template.replace('_CLIENT_HOLDER', 'perfclient' + str(i))
  

print result
