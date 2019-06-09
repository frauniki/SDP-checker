package main

import (
	"net"
	"os"
	"strconv"

	"github.com/common-nighthawk/go-figure"
	"github.com/olekukonko/tablewriter"
	"github.com/sparrc/go-ping"
)

type Ip struct {
	network net.IP
	address net.IP
	gateway net.IP
}

type Response struct {
	addresses []net.Addr
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
}

func (dc *DropCheck) Ip() error {
	iface, err := net.InterfaceByName(dc.interfaceName)
	if err != nil {
		return err
	}
	dc.response.addresses, err = iface.Addrs()
	if err != nil {
		return nil
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
	for _, i := range dc.response.addresses {
		row := []string{"Interface", "Address#" + strconv.Itoa(num), i.String()}
		table = append(table, row)
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

func main() {
	showNet := figure.NewFigure("ShowNet", "3-d", true)
	dropCheck := figure.NewFigure("DropCheck", "3-d", true)
	showNet.Print()
	dropCheck.Print()
	drop := DropCheck{
		interfaceName: "en0",
		v4target:      "ipv4.google.com",
		v6target:      "ipv6.google.com",
		pingCount:     3,
	}
	if err := drop.AllCheck(); err != nil {
		panic(err)
	}
	drop.Out()
}
