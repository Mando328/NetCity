import queue
import time
import threading
import fake
from aggregator import Aggregator

TICK = 0.1

if __name__ == "__main__":
    stop = threading.Event()
    now = time.monotonic()
    last = now
    q = queue.Queue(maxsize= 50000)
    t = threading.Thread(target= fake.run, args= (q, stop), daemon= True)
    agg = Aggregator(q)
    next_t = time.monotonic() + TICK
    t.start()
    
    try:
        while True:
            packets = 0
            b_in = 0
            b_out  = 0
            delay = next_t - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            now = time.monotonic()
            dt = now - last

            summ = agg.flush() # summ as in summary
            
            for row in summ["processes"].values():
                packets += row["packets"]
                b_in += row["bytes_in"] 
                b_out += row["bytes_out"]

            if dt > 0:
                b_in_ps = b_in / dt
                b_out_ps = b_out / dt

            print(f"processes={len(summ['processes'])} packets={packets} events={len(summ['events'])} in : {b_in_ps:.0f} B/s, out: {b_out_ps:.0f} B/s")
            next_t += TICK
            last = now

    except KeyboardInterrupt:
        pass

    finally:
        stop.set()

        





