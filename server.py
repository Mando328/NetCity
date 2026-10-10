import asyncio
import websockets
import json
import queue
import threading
import time
from aggregator import Aggregator
import fake


TICK = 0.1


async def handler(websocket, agg):
    try:
        now = time.monotonic()
        last = now
        next_t = now + TICK
        print("Conn open")

        while True:
            delay = next_t - time.monotonic()
            if delay > 0:
                await asyncio.sleep(delay)

            now = time.monotonic()
            dt = now - last
            last = now
            summ = agg.flush()
            summ["dt"] = dt
            payload = json.dumps(summ)

            await websocket.send(payload)

            next_t += TICK


    except websockets.ConnectionClosed:
        print("Conn closed")


async def main():
    q = queue.Queue(maxsize= 50000)
    stop_event = threading.Event()
    t = threading.Thread(target=fake.run, args=(q, stop_event), daemon=True)
    t.start()
    agg = Aggregator(q)
    async with websockets.serve(lambda ws: handler(ws, agg), "127.0.0.1", 8765):
        print("Server running at ws://127.0.0.1:8765")
        await asyncio.Future() # keeps the server alive


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopping server...")
