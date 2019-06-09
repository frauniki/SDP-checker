from shownet.dropcheck import DropCheck


NIC_NAME = "en7"
FUNCTION = {
    "srx4600": {
        "ip": [
            "10.129.176.2"
        ]
    }
}


class ShowNet(DropCheck):
    console_out = True
    debug = True
    nic_name = NIC_NAME
    ping_test_count = 1
    v4target = "ipv4.google.com"
    v6target = "ipv6.google.com"
    function = FUNCTION


if __name__ == "__main__":
    shownet = ShowNet()
    shownet.all_check()
