import paho.mqtt.client as mqtt
import json
import time
import threading

# 使用成研的公网MQTT配置
MQTT_BROKER = "183.220.194.193"  # 改为你的MQTT服务器地址
MQTT_PORT = 26686
MQTT_TOPIC = "iot-dispatcher/cmlc/edge/14218415137302460078284052000205"
MQTT_USERNAME = "cmlc"    # 认证用户名
MQTT_PASSWORD = "odD8#Cr628"    # 认证密码
INTERVAL_SEC = 1  # 发送间隔时间

# 使用国创软件的MQTT配置
# MQTT_BROKER = "114.117.182.61"  # 改为你的MQTT服务器地址
# MQTT_PORT = 1883
# MQTT_TOPIC = "iot-dispatcher/cmlc/edge/14218400000101570378916300000170"
# MQTT_USERNAME = "uav"    # 认证用户名
# MQTT_PASSWORD = "nuhduav"    # 认证密码
# INTERVAL_SEC = 10  # 发送间隔时间


# # 使用国创测试的MQTT配置
# MQTT_BROKER = "172.20.6.25"  # 改为你的MQTT服务器地址
# MQTT_PORT = 1883
# MQTT_TOPIC = "14218400000101570378916300000170"
# MQTT_USERNAME = "uav"    # 认证用户名
# MQTT_PASSWORD = "nuhduav"    # 认证密码
# INTERVAL_SEC = 5  # 发送间隔时间

# # 预定义的5个不同JSON数据包
# JSON_DATA = [
# {
#   "event": "BeginTracking",
#   "timestamp": 1,
#   "metadata": {
#     "latitude": 30.570551,
#     "longitude": 104.036633,
#     "altitude": 481,
#     "speed_x": -1.7686163,
#     "speed_y": 2.4319708,
#     "speed_z": 1.4638141,
#     "data_id": "d6bd8a2960cf67a800289f51cbe9941c",
#     "radar_id": "Sf855715844Task1",
#     "device_id": "51010000491327970978"
#   },
#   "extra": {}
# },
# {
#   "event": "BeginTracking",
#   "timestamp": 2,
#   "metadata": {
#     "latitude": 30.569946,
#     "longitude": 104.037644,
#     "altitude": 500,
#     "speed_x": -1.7686163,
#     "speed_y": 2.4319708,
#     "speed_z": 1.4638141,
#     "data_id": "d6bd8a2960cf67a800289f51cbe9941c",
#     "radar_id": "Sf855715844Task1",
#     "device_id": "51010000491327970978"
#   },
#   "extra": {}
# },
# {
#   "event": "BeginTracking",
#   "timestamp": 3,
#   "metadata": {
#     "latitude": 30.578645,
#     "longitude": 104.041434,
#     "altitude": 540,
#     "speed_x": -1.7686163,
#     "speed_y": 2.4319708,
#     "speed_z": 1.4638141,
#     "data_id": "d6bd8a2960cf67a800289f51cbe9941c",
#     "radar_id": "Sf855715844Task1",
#     "device_id": "51010000491327970978"
#   },
#   "extra": {}
# },
# {
#   "event": "BeginTracking",
#   "timestamp": 4,
#   "metadata": {
#     "latitude": 30.569428,
#     "longitude": 104.036692,
#     "altitude": 494,
#     "speed_x": -1.7686163,
#     "speed_y": 2.4319708,
#     "speed_z": 1.4638141,
#     "data_id": "d6bd8a2960cf67a800289f51cbe9941c",
#     "radar_id": "Sf855715844Task1",
#     "device_id": "51010000491327970978"
#   },
#   "extra": {}
# }, 
# {
#   "event": "BeginTracking",
#   "timestamp": 5,
#   "metadata": {
#     "latitude": 30.5690,
#     "longitude": 104.036041,
#     "altitude": 510,
#     "speed_x": -1.7686163,
#     "speed_y": 2.4319708,
#     "speed_z": 1.4638141,
#     "data_id": "d6bd8a2960cf67a800289f51cbe9941c",
#     "radar_id": "Sf855715844Task1",
#     "device_id": "51010000491327970978"
#   },
#   "extra": {}
# },   
# {
#   "event": "BeginTracking",
#   "timestamp": 6,
#   "metadata": {
#     "latitude": 30.569979,
#     "longitude": 104.036132,
#     "altitude": 470,
#     "speed_x": -1.7686163,
#     "speed_y": 2.4319708,
#     "speed_z": 1.4638141,
#     "data_id": "d6bd8a2960cf67a800289f51cbe9941c",
#     "radar_id": "Sf855715844Task1",
#     "device_id": "51010000491327970978"
#   },
#   "extra": {}
# }, 
# ]

# 成研通信协议
JSON_DATA = [
{
  "event": "BeginTracking",
  "timestamp": 1731731306000,
  "edgeId": "1421841513730246",
  "metadata": {
    "deviceId": "14218415137302460078284052000205",
    "taskId": "ccd89e0b-0219-41ae-b403-6cddb2dc7782",
    "objectData": {
      "latitude": 30.56913479,
      "longitude": 104.03592903,
      "altitude": 450,
      "dataId": "123",
      "speedX": 0,
      "speedY": 0,
      "speedZ": 0.4,
      "length": 0,
      "width": 0,
      "height": 0,
      "objectType": 40,
      "probability": 0.567
    },
    "aiData": {
      "className": "drone",
      "isDetect": 1,
      "isTrack": 1
    },
    "extention": {
      "mode": "full-auto"
    }
  }
}
# {
#   "event": "BeginTracking",
#   "edgeId": "1337472012288",
#   "timestamp": 2,
#   "metadata": {
#     "deviceId": "422037861126",
#     "taskId": "d0652e40-aa9c-4629-9bab-559e961c9031",
#     "objectData": {
#       "latitude": 30.571551,
#       "longitude": 104.035633,
#       "altitude": 481,
#       "speedX": 10.4,
#       "speedY": 14.4,
#       "speedZ": 0.9,
#       "dataId": "583",
#       "length": 10,
#       "width": 164,
#       "height": 0.9,
#       "objectType": 40,
#       "probability": 0.567,
#     },
#     "aiData": {
#       "className": "drone",
#       "detectConfidence": 1,
#       "trackConfidence": 1
#     },
#     "extention": {
#       "mode": "full-auto",
#       "id": "168168168"
#     }
#   }
# },
# {
#   "event": "BeginTracking",
#   "edgeId": "1337472012288",
#   "timestamp": 3,
#   "metadata": {
#     "deviceId": "422037861126",
#     "taskId": "d0652e40-aa9c-4629-9bab-559e961c9031",
#     "objectData": {
#       "latitude": 30.570551,
#       "longitude": 104.038633,
#       "altitude": 421,
#       "speedX": -10.4,
#       "speedY": 164.4,
#       "speedZ": 0.9,
#       "dataId": "583",
#       "length": 10,
#       "width": 164,
#       "height": 0.9,
#       "objectType": 40,
#       "probability": 0.567,
#     },
#     "aiData": {
#       "className": "drone",
#       "detectConfidence": 0.5,
#       "trackConfidence": 0.5
#     },
#     "extention": {
#       "mode": "full-auto"
#     }
#   }
# },
# {
#   "event": "BeginTracking",
#   "edgeId": "1337472012288",
#   "timestamp": 4,
#   "metadata": {
#     "deviceId": "422037861126",
#     "taskId": "d0652e40-aa9c-4629-9bab-559e961c9031",
#     "objectData": {
#       "latitude": 30.578551,
#       "longitude": 104.052633,
#       "altitude": 560,
#       "speedX": -10.4,
#       "speedY": 164.4,
#       "speedZ": 0.9,
#       "dataId": "583",
#       "length": 10,
#       "width": 164,
#       "height": 0.9,
#       "objectType": 40,
#       "probability": 0.567,
#     },
#     "aiData": {
#       "className": "drone",
#       "detectConfidence": 0.5,
#       "trackConfidence": 0.5
#     },
#     "extention": {
#       "mode": "full-auto"
#     }
#   }
# }, 
# {
#   "event": "BeginTracking",
#   "edgeId": "1337472012288",
#   "timestamp": 5,
#   "metadata": {
#     "deviceId": "422037861126",
#     "taskId": "d0652e40-aa9c-4629-9bab-559e961c9031",
#     "objectData": {
#       "latitude": 30.575551,
#       "longitude": 104.039633,
#       "altitude": 600,
#       "speedX": -10.4,
#       "speedY": 164.4,
#       "speedZ": 0.9,
#       "dataId": "583",
#       "length": 10,
#       "width": 164,
#       "height": 0.9,
#       "objectType": 40,
#       "probability": 0.567,
#     },
#     "aiData": {
#       "className": "drone",
#       "detectConfidence": 0.5,
#       "trackConfidence": 0.5
#     },
#     "extention": {
#       "mode": "full-auto"
#     }
#   }
# }
# ,
# {
#   "event": "EndTracking",
#   "edgeId": "1421840000010157",
#   "timestamp": 6,
#   "metadata": {
#     "deviceId": "14218400000101570378916300000170",
#     "taskId": "d0652e40-aa9c-4629-9bab-559e961c9031"
#   }
# }
]


current_index = 0  # 当前发送的数据索引

def on_connect(client, userdata, flags, rc):
    """ MQTT连接回调 """
    connect_status = {
        0: "连接成功",
        1: "协议版本错误",
        2: "客户端标识无效",
        3: "服务不可用",
        4: "用户名或密码错误",  # 新增密码错误状态
        5: "未授权"
    }
    status_msg = connect_status.get(rc, f"未知错误：{rc}")
    
    if rc == 0:
        print(f"{status_msg}")
        start_publishing(client)
    else:
        print(f"连接失败：{status_msg}")
        if rc == 4:  # 单独处理认证错误
            print("请检查用户名和密码配置")

def publish_next(client):
    """ 发送下一个数据包 """
    global current_index
    payload = json.dumps(JSON_DATA[current_index])
    result = client.publish(MQTT_TOPIC, payload)
    
    if result[0] == mqtt.MQTT_ERR_SUCCESS:
        print(f"发送成功：{JSON_DATA[current_index]['timestamp']}")
    else:
        print(f"发送失败，错误码：{result[0]}")

    # 更新索引并设置下一个定时任务
    current_index = (current_index + 1) % len(JSON_DATA)
    threading.Timer(INTERVAL_SEC, publish_next, args=(client,)).start()

def start_publishing(client):
    """ 开始定时发送任务 """
    print(f"开始每{INTERVAL_SEC}秒发送一次数据")
    threading.Thread(target=publish_next, args=(client,)).start()

if __name__ == "__main__":
    client = mqtt.Client()
    
    # 设置认证信息（生产环境建议从环境变量获取）
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)  # 新增认证设置
    
    client.on_connect = on_connect

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n程序终止")
        client.disconnect()
        client.loop_stop()

