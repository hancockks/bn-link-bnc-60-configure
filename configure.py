import sys
import configparser
import requests
import urllib
import time

from six.moves import configparser
from six.moves import input as raw_input

MAX_RETRIES = 10
locationTemplate='latitude {}; longitude {}; timezone {}; timedst {}; timestd {}'
mqttTemplate='MqttHost {}; MqttUser {}; MqttPassword {}'
hardwareTemplate='template {}; module 0'
powerTemplate='PowerSet {:.4f}; VoltageSet {:.4f}; CurrentSet {:.4f}'
networkTemplate='SSID1 {}; Password1 {}; SSID2 {}; Password2 {}'

def getSendCommand(payload):
	print("{}, {}".format(getUrl(), payload))
	r = requests.get(getUrl(), params=payload)
	r.raise_for_status()
	return r

def merge_dicts(a,b):
	z = a.copy()
	z.update(b)
	return z

def wait_connection(ip):
	exception =  None
	for _ in range(MAX_RETRIES):
		try:
			url = 'http://{}'.format(config.get("tasmota","ip"))
			r = requests.get(url, timeout=0.200)
			r.raise_for_status()
		except requests.exceptions.RequestException as e:
			exception = e
			continue
		else:
			break
	else:
		raise exception
		

def getUrl():
	return 'http://{}/cm'.format(config.get("tasmota","ip"))

def getLocationCommands():
	return locationTemplate.format(
		config.get("location","latitude"),
		config.get("location","longitude"),
		config.get("location", "timezone"),
		config.get("location", "timedst"),
		config.get("location", "timestd"))

def getMqttCommands():
	return mqttTemplate.format(
		config.get("mqtt", "host"),
		config.get("mqtt", "user"),
		config.get("mqtt", "password"))

def getHardwareCommands():
	return hardwareTemplate.format(
		config.get("hardware","template")
	)

def getAuth():
	return {
		"user" : config.get("tasmota","username"), 
		"password": config.get("tasmota","password")
	}

def configure_base(ip):
	print("Configuring location, MQTT, and hardware template...")
	command = {"cmnd" : "BACKLOG {}".format(
		";".join([getLocationCommands(),getMqttCommands(),getHardwareCommands()]))}
	payload = merge_dicts(getAuth(), command)
	return getSendCommand(payload)

def getNetworkCommands():
	return networkTemplate.format(
		config.get("wlan","ssid1"),
		config.get("wlan","password1"),
		config.get("wlan","ssid2"),
		config.get("wlan","password2")
	)

def configure_wlan(ip):
	print("Configuring wlan...")
	command = {"cmnd" : "BACKLOG {}".format(getNetworkCommands())}
	payload = merge_dicts(getAuth(), command)
	return getSendCommand(payload)


def power_on(ip):
	command = {"cmnd" : "Power1"}
	payload = merge_dicts(getAuth(), command)
	r = getSendCommand(payload)
	if r.json()["POWER"] == "ON":
		time.sleep(0.5)
	else:
		command = {"cmnd" : "Power on"}
		payload = merge_dicts(getAuth(), command)
		r = getSendCommand(payload)
		time.sleep(0.5)

def power_prompt(ip):
	p = raw_input("Calibrate power monitoring [Y/N]") or "Y"
	if p.lower() != "y":
		return None,None,None
	print("Make sure you have a known power source before proceeding.")
	power_on(ip)
	watts = float(raw_input("Test device wattage [60W]: ") or "60.0")
	volts = float(raw_input("Voltage [120V]: ") or "120.0")
	current = 1000 * watts / volts
	return watts, volts, current


def configure_power(ip,watts,volts,current):
	print("Configuring power settings...")
	powerBacklog = powerTemplate.format(watts,volts,current)
	command = {"cmnd" : "BACKLOG {}".format(powerBacklog)}
	payload = merge_dicts(getAuth(), command)
	return getSendCommand(payload)


usageText = '''
python configure.py configuration.ini

configuration.ini is a configuration file containing all the configuration information
for the local network.
'''

def usage():
	print(usageText)
	exit(1)

if len(sys.argv) != 2:
	usage()

config = configparser.ConfigParser()
config.read(sys.argv[1])

ip = config.get("tasmota", "ip")

wait_connection(ip)
configure_base(ip)
wait_connection(ip)
watts, volts, current = power_prompt(ip)
if watts is not None:
	configure_power(ip,watts,volts,current)

wait_connection(ip)
configure_wlan(ip)

