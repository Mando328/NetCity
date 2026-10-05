import random
import time
import queue
import threading
import traceback

from events import PacketEvent, ConnEvent, DnsEvent
from profiles import PROFILES, IP_POOL

def make_state(profile_config, now):
    rate_low, rate_high = profile_config["rate"]
    rate = random.uniform(rate_low, rate_high)
    next_rate_change = now + random.uniform(3,7)
    burst_end = 0
    ips = random.sample(IP_POOL, 5) #list of ip adresses the app talks to

    return {"rate" : rate, "next_rate_change": next_rate_change, "burst_end": burst_end, "ips": ips}

def make_packet(process_name, profile_config, state):
    size_low, size_high = profile_config["size"]
    time_s = time.time()
    remote_port = random.choice(profile_config["ports"])
    remote_ip = random.choice(state["ips"])
    protocol_names, protocol_weights = zip(*profile_config["protocol"])
    protocol = random.choices(protocol_names, weights=protocol_weights)[0]

    if random.random() > profile_config["in_ratio"]:
        direction = "out"
    else:
        direction = "in"

    r = random.random()
    if r < 0.45:
        size = random.randint(size_low, min(size_low + 40, size_high))       # małe (ACK)
    elif r < 0.80:
        size = random.randint(max(size_high - 100, size_low), size_high)      # pełne
    else:
        size = random.randint(size_low, size_high)                     # dowolne

    return PacketEvent(
        time_s=time_s,
        process=process_name,
        direction=direction,
        protocol=protocol,
        remote_ip=remote_ip,
        remote_port=remote_port,
        size=size,
    )

def make_dns(process_name, prof):
    time_s = time.time()
    domain = random.choice(prof["dns"])
    return DnsEvent(
        time_s = time_s,
        request_name = domain,
        process = process_name,
    )

def make_connection(process_name, prof):
    ip = random.choice(IP_POOL) 
    port = random.choice(prof["ports"])
    time_s = time.time()
    kind = random.choice(["open", "close"])

    return ConnEvent(
        time_s = time,
        kind = kind,
        process = process_name,
        remote_ip = ip,
        remote_port = port,
    )

def put(q, ev): #function puts event in queue, if q is full does nothing
    try:
        q.put_nowait(ev)
    except queue.Full:
        pass

def start_fake_collector(q):
    stop = threading.Event()
    threading.Thread(target=run, args=(q, stop), daemon=True).start()
    return stop

def run(q, stop):
    try:
        now = time.monotonic()
        states = {name: make_state(prof, now) for name, prof in PROFILES.items()}
        last = now
        while not stop.is_set():
            now = time.monotonic()
            dt = now - last
            last = now
            for name, prof in PROFILES.items():
                state = states[name]

                
                if now >= state["next_rate_change"]:
                    rate_low, rate_high = prof["rate"]
                    state["rate"] = random.uniform(rate_low, rate_high)
                    state["next_rate_change"] = now + random.uniform(3, 7)

                
                mult = 1
                burst = prof["burst"]
                if burst is not None:
                    if now >= state["burst_end"] and random.random() < burst["chance"] * dt:
                        state["burst_end"] = now + random.uniform(*burst["dur"])
                    if now < state["burst_end"]:
                        mult = burst["mult"]

                expected = state["rate"] * mult * dt #smoothening output beacuse time.sleep is shitty
                n = int(expected)
                if random.random() < (expected - n):
                    n = n + 1
                for _ in range(n):
                    put(q, make_packet(name, prof, state))

                if prof["dns"] and random.random() < 0.3 * dt:
                    put(q, make_dns(name, prof))

                if name is not None and random.random() < 0.2 * dt:
                    put(q, make_connection(name, prof))

            time.sleep(0.01)

    except Exception:
        traceback.print_exc()





