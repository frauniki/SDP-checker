import sys
import json


def load_json():
    f = open("./exh.json", 'r')
    return json.load(f)


class Exh:
    def __init__(self, raw):
        self.raw_dict = raw
        self.index = {}
        self.target = None

        if self.raw_dict:
            self._index()

    def _index(self):
        for i in self.raw_dict:
            self.index[i['VLAN']] = i

    def search(self, vlan_id):
        self.target = self.index[vlan_id]
        return self

    def get(self, key):
        if self.target and key in self.target:
            return self.target[key]
        return


if __name__ == "__main__":
    exh = Exh(load_json())
    args = sys.argv
    if len(args) >= 3:
        output = exh.search(int(args[1])).get(str(args[2]))
        sys.stdout.write(str(output))
