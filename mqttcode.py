# Complete project details at https://RandomNerdTutorials.com/raspberry-pi-pico-w-mqtt-micropython/
# Min egen anpassning

from machine import Pin #, I2C (när det väl behövs)
from time import sleep
import network #modul för att koppla till wifi
from umqtt.simple import MQTTClient
import config
import random

# Constants for MQTT Topics
MQTT_TOPIC_HIT = 'boat/hit'
MQTT_TOPIC_AMMO = 'boat/ammo'

# MQTT Parameters
MQTT_SERVER = config.mqtt_server
MQTT_PORT = 0
#MQTT_USER = config.mqtt_username
#MQTT_PASSWORD = config.mqtt_password
MQTT_CLIENT_ID = b"RP2040"
MQTT_KEEPALIVE = 300 # ändra till lämligt tidsintervall
MQTT_SSL = False   # set to False if using local Mosquitto MQTT broker, dvs ej via cloud/över nätverk
MQTT_SSL_PARAMS = {'server_hostname': MQTT_SERVER}

# Initialize I2C communication
#i2c = I2C(id=0, scl=Pin(5), sda=Pin(4), freq=10000)


def initialize_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Connect to the network
    wlan.connect(ssid, password)

    # Wait for Wi-Fi connection
    connection_timeout = 10
    while connection_timeout > 0:
        if wlan.status() >= 3:
            break
        connection_timeout -= 1
        print('Waiting for Wi-Fi connection...')
        sleep(1)

    # Check if connection is successful
    if wlan.status() != 3:
        return False
    else:
        print('Connection successful!')
        network_info = wlan.ifconfig()
        print('IP address:', network_info[0])
        return True

def connect_mqtt():
    try:
        client = MQTTClient(client_id=MQTT_CLIENT_ID,
                            server=MQTT_SERVER,
                            port=MQTT_PORT,
                            #user=MQTT_USER,
                            #password=MQTT_PASSWORD,
                            keepalive=MQTT_KEEPALIVE,
                            ssl=MQTT_SSL,
                            ssl_params=MQTT_SSL_PARAMS)
        client.connect()
        return client
    except Exception as e:
        print('Error connecting to MQTT:', e)
        raise  # Re-raise the exception to see the full traceback

def publish_mqtt(topic, value):
    client.publish(topic, value, qos=1)
    print(topic + ": " + value)
    print("End of publish\n")

button = Pin(13, Pin.IN)

try:
    if not initialize_wifi(config.wifi_ssid, config.wifi_password):
        print('Error connecting to the network... exiting program')
    else:
        # Connect to MQTT broker, start MQTT client
        client = connect_mqtt()        
        while True:
            if button.value():
                damage = random.randint(1, 100)
                # Här skickas datan
                publish_mqtt(MQTT_TOPIC_HIT, "hit detected;" + str(damage))
                
                # ger utrymme för debounce av knappen
                sleep(0.3) 
            else:
                pass
                
            # En kort paus i loopen så att Picon inte går på 100% högvarv i onödan
            sleep(0.05)

except Exception as e:
    print('Error:', e)


