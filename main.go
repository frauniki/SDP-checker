package main

import (
	"net"
	"os"
	"os/exec"
	"strconv"

	"github.com/common-nighthawk/go-figure"
	"github.com/olekukonko/tablewriter"
	"github.com/sparrc/go-ping"
	"github.com/spf13/viper"
)

type Ip struct {
	network net.IPNet
	address net.IP
	gateway net.IP
}

type Response struct {
	addresses []*Ip
	pingV4    *ping.Statistics
	pingV6    *ping.Statistics
	dnsA      net.IP
	dnsAAAA   net.IP
}

type DropCheck struct {
	interfaceName string
	v4target      string
	v6target      string
	pingCount     int
	response      Response
	exhibitor     *Exhibitor
	exhibitorOut  bool
}

type Exhibitor struct {
	vlan        int
	name        string
	space       string
	media       string
	tag         string
	bat         string
	addressType string
	ipV4Address string
	ipV6Address string
	dhcp        bool
}

func (dc *DropCheck) Ip() error {
	iface, err := net.InterfaceByName(dc.interfaceName)
	if err != nil {
		return err
	}
	addrs, err := iface.Addrs()
	if err != nil {
		return nil
	}
	for _, addr := range addrs {
		ip, ipNet, err := net.ParseCIDR(addr.String())
		if err != nil {
			return err
		}
		ipResult := Ip{
			address: ip,
			network: *ipNet,
			gateway: nil,
		}
		dc.response.addresses = append(dc.response.addresses, &ipResult)
	}

	return nil
}

func (dc *DropCheck) Ping() error {
	v4, err := ping.NewPinger(dc.v4target)
	if err != nil {
		return err
	}
	v6, err := ping.NewPinger(dc.v6target)
	if err != nil {
		return nil
	}
	v4.Count = dc.pingCount
	v6.Count = dc.pingCount
	v4.Run()
	v6.Run()
	dc.response.pingV4 = v4.Statistics()
	dc.response.pingV6 = v6.Statistics()

	return nil
}

func (dc *DropCheck) Dns() error {
	v4Ips, err := net.LookupIP(dc.v4target)
	if err != nil {
		return err
	}
	dc.response.dnsA = v4Ips[0]
	v6Ips, err := net.LookupIP(dc.v6target)
	if err != nil {
		return err
	}
	dc.response.dnsAAAA = v6Ips[0]

	return nil
}

func (dc *DropCheck) TraceRoute() error {
	return nil
}

func (dc *DropCheck) AllCheck() error {
	if err := dc.Ip(); err != nil {
		return err
	}
	if err := dc.Ping(); err != nil {
		return err
	}
	if err := dc.Dns(); err != nil {
		return err
	}

	return nil
}

func (dc *DropCheck) Out() error {
	table := [][]string{}
	num := 1
	if dc.exhibitorOut {
		exh := [][]string{
			{"Exhibitor", "VLAN", strconv.Itoa(dc.exhibitor.vlan)},
			{"Exhibitor", "出展社名", dc.exhibitor.name},
			{"Exhibitor", "メディア", dc.exhibitor.media},
			{"Exhibitor", "ケーブルタグ", dc.exhibitor.tag},
			{"Exhibitor", "パッチパネル", dc.exhibitor.bat},
			{"Exhibitor", "アドレスタイプ", dc.exhibitor.addressType},
			{"Exhibitor", "IPv4アドレス", dc.exhibitor.ipV4Address},
			{"Exhibitor", "IPv6アドレス", dc.exhibitor.ipV6Address},
			{"Exhibitor", "DHCP", strconv.FormatBool(dc.exhibitor.dhcp)},
		}
		table = append(table, exh...)
	}
	for _, i := range dc.response.addresses {
		iface := [][]string{
			{"Interface", "Address#" + strconv.Itoa(num), i.network.String()},
			{"Interface", "Address#" + strconv.Itoa(num), i.address.String()},
			//{"Interface", "Address#" + strconv.Itoa(num), i.gateway},
		}
		table = append(table, iface...)
		num++
	}
	table2 := [][]string{
		[]string{"IPv4 Ping", "PacketsSent", strconv.Itoa(dc.response.pingV4.PacketsSent)},
		[]string{"IPv4 Ping", "PacketLoss", strconv.FormatFloat(dc.response.pingV4.PacketLoss, 'f', 4, 64)},
		[]string{"IPv4 Ping", "IPAddr", dc.response.pingV4.IPAddr.String()},
		[]string{"IPv4 Ping", "Addr", dc.response.pingV4.Addr},
		[]string{"IPv4 Ping", "MinRtt", dc.response.pingV4.MinRtt.String()},
		[]string{"IPv4 Ping", "MaxRtt", dc.response.pingV4.MaxRtt.String()},
		[]string{"IPv4 Ping", "AvgRtt", dc.response.pingV4.AvgRtt.String()},
		[]string{"IPv6 Ping", "PacketsSent", strconv.Itoa(dc.response.pingV6.PacketsSent)},
		[]string{"IPv6 Ping", "PacketLoss", strconv.FormatFloat(dc.response.pingV6.PacketLoss, 'f', 4, 64)},
		[]string{"IPv6 Ping", "IPAddr", dc.response.pingV6.IPAddr.String()},
		[]string{"IPv6 Ping", "Addr", dc.response.pingV6.Addr},
		[]string{"IPv6 Ping", "MinRtt", dc.response.pingV6.MinRtt.String()},
		[]string{"IPv6 Ping", "MaxRtt", dc.response.pingV6.MaxRtt.String()},
		[]string{"IPv6 Ping", "AvgRtt", dc.response.pingV6.AvgRtt.String()},
		[]string{"DNS A Record", "RecordName", dc.v4target},
		[]string{"DNS A Record", "Addr", dc.response.dnsA.String()},
		[]string{"DNS AAAA Record", "RecordName", dc.v6target},
		[]string{"DNS AAAA Record", "Addr", dc.response.dnsAAAA.String()},
	}
	table = append(table, table2...)
	stdout := tablewriter.NewWriter(os.Stdout)
	stdout.SetAutoMergeCells(true)
	stdout.SetRowLine(true)
	stdout.SetCaption(true, "* Complete!")
	for _, i := range table {
		stdout.Append(i)
	}
	stdout.Render()

	return nil
}

func (exh *Exhibitor) Search(vlanId int) {
	exh.vlan = vlanId
	exh.name, _ = ExhibitorGet(vlanId, "出展社名")
	exh.space, _ = ExhibitorGet(vlanId, "小間番号")
	exh.media, _ = ExhibitorGet(vlanId, "メディア")
	exh.tag, _ = ExhibitorGet(vlanId, "ケーブルタグ")
	exh.bat, _ = ExhibitorGet(vlanId, "パッチパネル")
	exh.addressType, _ = ExhibitorGet(vlanId, "アドレスタイプ")
	exh.ipV4Address, _ = ExhibitorGet(vlanId, "IPv4アドレス")
	exh.ipV6Address, _ = ExhibitorGet(vlanId, "IPv6アドレス")
	dhcp, _ := ExhibitorGet(vlanId, "DHCP")
	exh.dhcp, _ = strconv.ParseBool(dhcp)
}

func ExhibitorGet(vlanId int, key string) (string, error) {
	out, err := exec.Command("python3", "pyMapper/map.py", strconv.Itoa(vlanId), key).Output()
	if err != nil {
		return "", err
	}
	return string(out), nil
}

func loadConfig() (string, error) {
	viper.SetConfigName("config")
	viper.AddConfigPath(".")
	if err := viper.ReadInConfig(); err != nil {
		return "", err
	}
	return viper.GetString("interface.name"), nil
}

func main() {
	nic, err := loadConfig()
	if err != nil {
		panic(err)
	}
	showNet := figure.NewFigure("ShowNet", "3-d", true)
	dropCheck := figure.NewFigure("DropCheck", "3-d", true)
	showNet.Print()
	dropCheck.Print()

	exh := Exhibitor{}
	exhibitorOut := false

	if len(os.Args) >= 2 {
		arg := os.Args[1]
		vlanId, err := strconv.Atoi(arg)
		if err != nil {
			panic(err)
		}
		exh.Search(vlanId)
		exhibitorOut = true
	}

	drop := DropCheck{
		interfaceName: nic,
		v4target:      "ipv4.google.com",
		v6target:      "ipv6.google.com",
		pingCount:     1,
		exhibitor:     &exh,
		exhibitorOut:  exhibitorOut,
	}
	if err := drop.AllCheck(); err != nil {
		panic(err)
	}
	drop.Out()
}
