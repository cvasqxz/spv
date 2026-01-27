import network
import time
import requests

def rssi_to_stars(rssi):
	if rssi >= -40:
		return "★★★★★"
	elif rssi >= -50:
		return "★★★★☆"
	elif rssi >= -60:
		return "★★★☆☆"
	elif rssi >= -70:
		return "★★☆☆☆"
	elif rssi >= -80:
		return "★☆☆☆☆"
	else:
		return "☆☆☆☆☆"


def connect_to_wifi():
	wlan = network.WLAN(network.STA_IF)

	if wlan.active() and wlan.isconnected() and network_info[0] != '0.0.0.0':
		print(f"Already connected to WiFi, IP = {network_info[0]}")
		return

	wlan.active(True)

	networks = wlan.scan()
	networks = sorted(networks, key=lambda x: x[3], reverse=True)
	max_length = max(16, max(len(item[0]) for item in networks))

	print("Available WiFi Networks:\n")
	print(f"#   {'SSID':<{max_length+1}} strength")
	print("-"*(max_length + 14))

	for index, net in enumerate(networks):
		ssid, bssid, channel, rssi, _, _ = net
		ssid   = ssid.decode("utf-8")
		signal = rssi_to_stars(rssi)
		
		print(f"{index:<3} {ssid:<{max_length+1}} {signal}")

	print("-"*(max_length+ 14))
	network_selected = input("> Select network: ")
	password = input("> Password: ")

	ssid = networks[int(network_selected)][0]
	wlan.connect(ssid, password)

	connection_timeout = 10
	while connection_timeout > 0:
		if wlan.status() >= 3:
			break
		connection_timeout -= 1
		time.sleep(1)

	if wlan.status() != 3:
		print("Failed to establish a network connection")
	else:
		network_info = wlan.ifconfig()
		print(f"Connection successful!, IP = {network_info[0]}")


if __name__ == "__main__":
	connect_to_wifi()