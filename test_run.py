from events import *

ev = PacketEvent(time_s=0.0, process="chrome", direction="out",
                 protocol="tcp", remote_ip="1.2.3.4",
                 remote_port=443, size=100)
print(ev.process)   # 100