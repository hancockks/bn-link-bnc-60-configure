This script will automatically configure a BN-LINK BNC-60 power-monitoring smart Wifi plug
that has been flashed with Tasmota firmware.

The script configures the system in three phases:
1. location, mqtt, and hardware configuration template
2. power monitoring calibration
3. Wifi credentials

After configuring wifi crendentials, the smart plug will remove itself from its self-created ad-hoc SSID and join the network.

The rough steps to use this script:

1. use tuya-convert to flash the firmware<br>
See https://github.com/ct-Open-Source/tuya-convert
2. once flashed, the wifi plug will create a new SSID with a SSID of tasmota-XXXX. You must connect to this.
3. copy the sample.ini script and fill in all the pertinent information with your own local configuration
4. run  ```python configure.py myconfiguration.ini```


After configuring the local time zone information, mqtt, and hardware template, the script will prompt for calibrating your power monitoring hardware.  More information can be found at https://tasmota.github.io/docs/Power-Monitoring-Calibration/