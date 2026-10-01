from typing import NamedTuple

class PacketEvent(NamedTuple):
    time_s: float
    process: str | None
    direction : str # in or out
    protocol : str # tcp or udp
    remote_ip: str
    remote_port : int
    size: int

class ConnEvent(NamedTuple):
    time_s: float
    kind: str   # open or close
    process: str
    remote_ip: str
    remote_port : int

class DnsEvent(NamedTuple):
    time_s : float
    process : str | None
    request_name : str
