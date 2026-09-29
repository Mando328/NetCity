#This is simply a list of fake but realistic traffic that can be used
#for testing or demos when sudo permissions are not available.
#Some of the info was AI generated since i dont want to mannualy search the interent
#for typical spotify packet sizes


PROFILES = {
    "chrome.exe": {
        "rate" : (40, 200), # rate lo/hi
        "size" : (54, 1514), # size lo/hi
        "in_ratio": 0.75, # incoming ratio
        "protocol": [("tcp", 0.9), ("udp", 0.1)], #weighted protocol chooser
        "ports" : [443, 443, 443, 80], #ports
        "burst": {"chance": 0.15, "duration": (1,4), "mult": 5}, #burst are sudden spikes in traffic: rate * mult
        "dns": ["youtube.com", "google.com", "github.com", "wikipedia.org"], #dns list
    },

    "discord.exe":{
        "rate" : (20, 70),
        "size" : (90, 250),
        "in_ratio": 0.5,
        "protocol": [("udp", 1.0)],
        "ports" : [443, 50001, 50002],
        "burst": {"chance": 0.02, "duration": (2,3), "mult": 2},
        "dns": ["discord.com", "gateway.discord.gg"],
    },

    "steam.exe": {
        "rate" : (1, 10),
        "size" : (54, 1514),
        "in_ratio": 0.95,
        "protocol": [("tcp", 1.0)],
        "ports" : [443, 27015, 27036],
        "burst": {"chance": 0.05, "duration": (10,40), "mult": 100},
        "dns": ["steamcontent.com", "steampowered.com"],
    },

        "spotify.exe": {
        "rate": (5, 25),
        "size": (54, 1514),
        "in_ratio": 0.9,
        "protos": [("tcp", 1.0)],
        "ports": [443, 4070],
        "burst": {"chance": 0.04, "dur": (2, 4), "mult": 8},
        "dns": ["spclient.wg.spotify.com", "scdn.co"],
    },

    "svchost.exe": {
        "rate": (2, 15),
        "size": (54, 700),
        "in_ratio": 0.6,
        "protos": [("tcp", 0.7), ("udp", 0.3)],
        "ports": [443, 123, 53],
        "burst": {"chance": 0.01, "dur": (10, 30), "mult": 20},
        "dns": ["windowsupdate.com", "microsoft.com", "time.windows.com"],
    },

    "game.exe": {
        "rate": (30, 120),
        "size": (50, 250),
        "in_ratio": 0.5,
        "protos": [("udp", 1.0)],
        "ports": [27015, 27016, 27020],
        "burst": None,
        "dns": [],
    },

    "OneDrive.exe": {
        "rate": (0, 5),
        "size": (54, 1514),
        "in_ratio": 0.3,
        "protos": [("tcp", 1.0)],
        "ports": [443],
        "burst": {"chance": 0.01, "dur": (5, 15), "mult": 30},
        "dns": ["onedrive.live.com"],
    },

    None: {                          # unknown process
        "rate": (0, 10),
        "size": (54, 400),
        "in_ratio": 0.5,
        "protos": [("tcp", 0.6), ("udp", 0.4)],
        "ports": [443, 80, 5353],
        "burst": None,
        "dns": [],
    },
    
}

IP_POOL = ( #those ip adresses are from the safe testing pool and are unclaimed
    [f"203.0.113.{i}" for i in range(1, 30)]
    + [f"198.51.100.{i}" for i in range(1, 30)]
    + [f"192.0.2.{i}" for i in range(1, 30)]
)