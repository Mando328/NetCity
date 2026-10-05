import time
import queue
from fake import *
from events import PacketEvent, ConnEvent, DnsEvent

MAX_PER_TICK = 20000

class Aggregator:
    def __init__(self, q):
        self.q = q

    def flush(self):
        p = {} #PROCESSES
        eve = [] #EVENTS
        i = 0
        while i < MAX_PER_TICK:
            i = i + 1
            try :
                x = self.q.get_nowait()

            except queue.Empty:
                i = i - 1
                break


            if isinstance(x, PacketEvent):
                process = x.process
                if process is None:
                    process = "unknown"

                if process not in p:
                   p[process] = {"bytes_in": 0, "bytes_out": 0, "packets" : 0}
                p[process]["packets"] += 1
                if x.direction == "in":
                    p[process]["bytes_in"] += x.size
                elif x.direction == "out":
                    p[process]["bytes_out"] += x.size

            elif isinstance(x, ConnEvent):
                process = x.process
                if process is None:
                    process = "unknown"

                eve.append({
                    "type": "conn",
                    "kind": x.kind,
                    "process": process,
                    "remote_ip": x.remote_ip,
                    "remote_port": x.remote_port,
                })

            elif isinstance(x, DnsEvent):
                process = x.process
                if process is None:
                    process = "unknown"
                eve.append({
                    "type": "dns",
                    "process": process,
                    "request_name": x.request_name,
                })

            else:
                pass
        
        return{
            "t" : time.time(),
            "processes": p,
            "events": eve,
        }

