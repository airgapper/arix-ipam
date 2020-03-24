import pymongo
import ipaddress


class IPAMDatabase:
    def __init__(self, mongo_uri):
        # Core datastores
        self._client = pymongo.MongoClient(mongo_uri)
        self._db = self._client["arix-ipam"]

        # Collections
        self.prefixes = self._db["prefixes"]
        self.config = self._db["config"].find_one({})

        self.aggregate = ipaddress.ip_network(self.config["prefix"])
        if self.aggregate.prefixlen >= 48:
            print("Aggregate prefix is smaller than a /48")
            exit(1)

        self.available = []
        self.sync()

    def sync(self):
        self.available = list(self.aggregate.subnets(prefixlen_diff=(48 - self.aggregate.prefixlen)))
        for _prefix in self.prefixes.find({}):
            self.available.remove(ipaddress.ip_network(_prefix["inet6num"]))

    def assign(self, netname, descr):
        inet6num = str(self.available[0])

        self.prefixes.insert({
            "inet6num": inet6num,
            "netname": netname,
            "descr": descr
        })
        self.available.remove(ipaddress.ip_network(inet6num))

        _new = {
            "inet6num": inet6num,
            "netname": netname,
            "descr": descr,
            "country": self.config["country"],
            "org": self.config["org"],
            "admin-c": self.config["admin-c"],
            "tech-c": self.config["tech-c"],
            "mnt-by": self.config["mnt"],
            "status": "ASSIGNED"
        }

        out = ""
        for key in _new.keys():
            out += "{: <10} {}\n".format(*[key + ":", _new[key]])
        out = out.strip()

        return out

    def get(self):
        return self.prefixes.find({})

    def delete(self, inet6num):
        self.prefixes.delete_one({"inet6num": inet6num})
        self.sync()
