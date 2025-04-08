import os
import sys
import random
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
import paho.mqtt.client as mqtt
from mqtt_init import *
from db_manager import DBManager
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt

db = DBManager("iot_data.csv")

global clientname, CONNECTED
CONNECTED = False
r = random.randrange(1, 10000000)
clientname = "IOT_client-Id234-" + str(r)
DHT_topic = 'pr/home/5976397/sts'
relay_topic = 'pr/home/1234567/sts'
update_rate = 5000
global DHT_ON
DHT_ON = False

class Mqtt_client():
    def __init__(self):
        self.broker = ''
        self.topic = ''
        self.port = ''
        self.clientname = ''
        self.username = ''
        self.password = ''
        self.subscribeTopic = ''
        self.publishTopic = ''
        self.publishMessage = ''
        self.on_connected_to_form = ''

    def set_on_connected_to_form(self, on_connected_to_form):
        self.on_connected_to_form = on_connected_to_form
    def get_broker(self): return self.broker
    def set_broker(self, value): self.broker = value
    def get_port(self): return self.port
    def set_port(self, value): self.port = value
    def get_clientName(self): return self.clientname
    def set_clientName(self, value): self.clientname = value
    def get_username(self): return self.username
    def set_username(self, value): self.username = value
    def get_password(self): return self.password
    def set_password(self, value): self.password = value
    def get_subscribeTopic(self): return self.subscribeTopic
    def set_subscribeTopic(self, value): self.subscribeTopic = value
    def get_publishTopic(self): return self.publishTopic
    def set_publishTopic(self, value): self.publishTopic = value
    def get_publishMessage(self): return self.publishMessage
    def set_publishMessage(self, value): self.publishMessage = value

    def on_log(self, client, userdata, level, buf):
        print("log: " + buf)

    def on_connect(self, client, userdata, flags, rc):
        global CONNECTED
        if rc == 0:
            print("connected OK")
            CONNECTED = True
            self.on_connected_to_form()
        else:
            print("Bad connection Returned code=", rc)

    def on_disconnect(self, client, userdata, flags, rc=0):
        global CONNECTED
        CONNECTED = False
        print("DisConnected result code " + str(rc))

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        print("message from:" + topic, m_decode)
        mainwin.connectionDock.update_btn_state(m_decode)

    def connect_to(self):
        self.client = mqtt.Client(self.clientname, clean_session=True)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.username, self.password)
        print("Connecting to broker ", self.broker)
        self.client.connect(self.broker, self.port)

    def disconnect_from(self):
        self.client.disconnect()

    def start_listening(self):
        self.client.loop_start()

    def stop_listening(self):
        self.client.loop_stop()

    def subscribe_to(self, topic):
        if CONNECTED:
            self.client.subscribe(topic)
        else:
            print("Can't subscribe. Connection should be established first")

    def publish_to(self, topic, message):
        if CONNECTED:
            self.client.publish(topic, message)
        else:
            print("Can't publish. Connection should be established first")

class ConnectionDock(QDockWidget):
    def __init__(self, mc):
        super().__init__()
        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)

        self.eHostInput = QLineEdit(broker_ip)
        self.eHostInput.setInputMask('999.999.999.999')
        self.ePort = QLineEdit(broker_port)
        self.ePort.setValidator(QIntValidator())
        self.eClientID = QLineEdit(clientname)
        self.eUserName = QLineEdit(username)
        self.ePassword = QLineEdit(password)
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePublisherTopic = QLineEdit(DHT_topic)
        self.eSubscribeTopic = QLineEdit(relay_topic)

        self.Temperature = QLineEdit()
        self.Humidity = QLineEdit()

        self.eConnectbtn = QPushButton("Enable/Connect")
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)


        formLayout = QFormLayout()
        formLayout.addRow("Connect", self.eConnectbtn)
        formLayout.addRow("Pub topic", self.ePublisherTopic)
        formLayout.addRow("Temperature", self.Temperature)
        formLayout.addRow("Humidity", self.Humidity)

        widget = QWidget()
        widget.setLayout(formLayout)
        self.setWidget(widget)

    def update_btn_state(self, text):
        global DHT_ON
        DHT_ON = not DHT_ON

    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: green")
        self.mc.subscribe_to(self.eSubscribeTopic.text())

    def on_button_connect_click(self):
        self.mc.set_broker(self.eHostInput.text())
        self.mc.set_port(int(self.ePort.text()))
        self.mc.set_clientName(self.eClientID.text())
        self.mc.set_username(self.eUserName.text())
        self.mc.set_password(self.ePassword.text())
        self.mc.connect_to()
        self.mc.start_listening()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.temp_value = 23
        self.mc = Mqtt_client()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(update_rate)

        self.setGeometry(30, 600, 300, 150)
        self.setWindowTitle('DHT Sensor')

        self.connectionDock = ConnectionDock(self.mc)
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)

    def update_data(self):
        global DHT_ON  # 🟢 חייב להיות השורה הראשונה בפונקציה
        
        if DHT_ON:
            print('Next update')
            self.temp_value += 2
            temp = self.temp_value
            hum = 74 + random.randrange(1, 25) / 10
            current_data = f'Temperature: {temp} Humidity: {hum}'
            self.connectionDock.Temperature.setText(str(temp))
            self.connectionDock.Humidity.setText(str(hum))
            self.mc.publish_to(DHT_topic, current_data)
            db.add_record(
                clientID=clientname,
                receiver="DHT Sensor",
                transmitter="SensorUnit",
                topic=DHT_topic,
                subscriber="GUI",
                message=current_data
            )
            if temp > 45:
                self.mc.publish_to(relay_topic, current_data)
                self.connectionDock.Temperature.setText('')
                self.connectionDock.Humidity.setText('')
                self.temp_value = 23
                DHT_ON = False

app = QApplication(sys.argv)
mainwin = MainWindow()
mainwin.show()
app.exec_()
