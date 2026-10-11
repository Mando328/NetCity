import math
import time

DIM_GRACE = 10

def getGridPosition(index):
    ring = math.ceil((math.sqrt(index + 2) - 1) / 2)
    firstIndexInRing = 4 * (ring - 1) * ring
    offset = index - firstIndexInRing
    side = ring * 2
    gx = 0
    gz = 0
    if offset < side:
        gx = -ring + 1 + offset
        gz = - ring
    elif offset < side * 2:
        gx = ring
        gz = - ring + 1 + offset - side
    elif offset < side * 3:
        gx = ring - 1 - offset + side * 2
        gz = ring
    else:
        gx = - ring
        gz = ring - 1 - offset + side * 3

    return gx , gz 


class Cell:
    def __init__(self, gx, gz, owner, ip, state="empty"):
        self.gx = gx
        self.gz = gz
        self.owner = owner
        self.ip = ip
        self.state = state
        self.state_changed_at = time.monotonic()
        self.connections = 0

    def __repr__(self):
        return f"Cell({self.gx}, {self.gz}) owner={self.owner} ip={self.ip} state={self.state} conn={self.connections}"

class City:
    def __init__(self):
        self.cell_dict = {}
        self.next_index = 0
        self.process_last_seen = {}
        self.ip_to_cell = {}

    
    def get_next_position(self):
        gx, gz = getGridPosition(self.next_index)
        return gx, gz


    def add_cell(self, owner, ip):
        gx, gz = self.get_next_position()
        c = Cell(gx, gz, owner, ip,)
        self.cell_dict[(gx, gz)] = c
        self.ip_to_cell[(owner, ip)] = (gx, gz)
        self.next_index += 1


        return c

    def update(self, snapshot):
        now = time.monotonic()
        for process in snapshot["processes"]:
            self.process_last_seen[process] = now
        for event in snapshot["events"]:
            kind = event.get("kind")
            key = (event["process"], event["remote_ip"])
            if kind == "open":
                if key in self.ip_to_cell:
                    c = self.cell_dict[self.ip_to_cell[key]]
                else:
                    c = self.add_cell(*key)
                c.connections += 1
                if c.state != "active":
                    c.state = "active"
                    c.state_changed_at = now
            elif kind == "close":
                if key in self.ip_to_cell:
                    c = self.cell_dict[self.ip_to_cell[key]]
                    if c.connections != 0:
                        c.connections -= 1
                        if c.connections == 0:
                            c.state = "dimming"
                            c.state_changed_at = now


    def tick(self):
      now = time.monotonic()
      for c in self.cell_dict.values():  
        if c.state == "dimming":
            if now - c.state_changed_at > DIM_GRACE:
                c.state = "ruin"
                c.state_changed_at = now
            

    


