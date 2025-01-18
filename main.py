import network
import time
from machine import Pin

from hcsr04 import HCSR04
from umqtt.simple import MQTTClient
    
# ESP32 Pin assignment 
# i2c = I2C(scl=Pin(22), sda=Pin(21))
sensor = HCSR04(trigger_pin=22, echo_pin=23, echo_timeout_us=10000)

# Wi-Fi Configuration
WIFI_SSID = ""  #  Wi-Fi SSID
WIFI_PASSWORD = ""  # Wi-Fi password

# Local MQTT Configuration
# MQTT_BROKER = "broker.hivemq.com"
MQTT_BROKER = "test.mosquitto.org"

# MQTT_PORT = 1883  # Default MQTT port
MQTT_PORT = 8883 # MQTT over TLS
MQTT_TOPIC = "parking/distance"  # Topic to publish distance data

# with open('mosquitto.org.crt') as f:
#     cert_data = f.read()
# #     print(cert_data)
with open('ca.crt') as f:
    cert_data = f.read()
#     print(cert_data)

# Connect to Wi-Fi
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Connecting to Wi-Fi...")
    while not wlan.isconnected():
        time.sleep(1)
    print("Connected to Wi-Fi:", wlan.ifconfig())

# Publish data to MQTT broker
def publish_to_mqtt(client, distance):
    try:
        payload = f"{distance}"  # Sending distance as plain text
        client.publish(MQTT_TOPIC, payload, qos=1)
        print("Published to MQTT:", payload)
    except Exception as e:
        print("Failed to publish to MQTT:", e)
        

# Main loop
def main():
    connect_to_wifi()

    # Initialize MQTT client
    client = MQTTClient(
        client_id="esp32_client",  # Unique client ID
        server=MQTT_BROKER,
        port=MQTT_PORT,
        keepalive=60,
        ssl=True,
        ssl_params={
            'cert': cert_data
        } 
    )

    # Connect to the MQTT broker
    try:
        client.connect()
        print("Connected to MQTT broker")
    except Exception as e:
        print("Failed to connect to MQTT broker:", e)
        return

    while True:
        distance = sensor.distance_cm()
        print("Distance:", distance, "cm")

        # Publish the distance to MQTT broker
        publish_to_mqtt(client, distance)

        time.sleep(3) 



# Run the main function
if __name__ == "__main__":
    main()



