from lib.core import check, to_json
from lib.env import NIC


if __name__ == "__main__":
    sinoa = check(NIC)
    print(to_json(sinoa, indent=4))
