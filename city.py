import math
import time

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
            if event.get("kind") == "open" :
                if (event["process"], event["remote_ip"]) in self.ip_to_cell:
                    cp = self.ip_to_cell[event["process"], event["remote_ip"]]
                    c = self.cell_dict[(cp)]
                    c.connections += 1
                else:
                    self.add_cell(event["process"], event["remote_ip"])
            elif event.get("kind") == "close":
                if (event["process"], event["remote_ip"]) in self.ip_to_cell:
                    cp = self.ip_to_cell[event["process"], event["remote_ip"]]
                    c = self.cell_dict[(cp)]
                    if c.connections != 0:
                        c.connections -= 1
                        if c.connections == 0:
                            c.state_changed_at = time.monotonic()
                            c.state = "dimming"

                    

    


if __name__ == "__main__":
    city = City()
    for i in range(25):
        city.add_cell(i, i)
    print(city.cell_dict)