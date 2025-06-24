import time
from machine import Pin, SoftI2C
import machine
import network
from umqtt.simple import MQTTClient
import ujson

from AHT10 import AHT10

from ota import OTAUpdater
from WIFI_CONFIG import SSID, PASSWORD

firmware_url = "https://raw.githubusercontent.com/<username>/<repo_name>/<branch_name>"

# I2C und Sensor initialisieren
i2c = SoftI2C(scl=Pin(1), sda=Pin(2))
sensor = AHT10(i2c)

# WLAN und MQTT-Daten
SSID = "BZTG-IoT"
PASSWORD = "WerderBremen24"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(txpower=8)
    wlan.connect(SSID, PASSWORD)

    print("Verbinde mit dem WLAN...")
    
    while not wlan.isconnected():
        time.sleep(1)

    if wlan.isconnected():
        print("Verbunden! IP:", wlan.ifconfig()[0])
        return wlan

def send_data():
    temperatur = round(sensor.temperature())
    feuchtigkeit = round(sensor.humidity())

    werte = {
        "Temperatur": temperatur,
        "Feuchtigkeit": feuchtigkeit
    }

    wlan = connect_wifi()
    if wlan:
        try:
            client = MQTTClient("Umgebungstemperaturen", "185.216.176.124", 1883)
            client.connect()
            print("MQTT verbunden")
            client.publish("sensor/temperature", ujson.dumps(werte))
            print("Gesendet:", werte)
            client.disconnect()
            
        finally:
            wlan.disconnect()
            wlan.active(False)
            print("WLAN getrennt")

while True:
    send_data()
    machine.deepsleep(60000)
