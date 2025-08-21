import json
import time
import math
import random
from typing import List
import paho.mqtt.client as mqtt

class GPSSimulator:
    def __init__(self, noise_level: str = 'low'):
        # WGS84椭球参数
        self.a = 6378137.0  # 长半轴 (m)
        self.f = 1/298.257223563  # 扁率
        self.b = self.a * (1 - self.f)  # 短半轴 (m)
        
        # 设置扰动强度等级
        self.noise_levels = {
            'low': 0.000001,     # 低扰动 (约0.1米级别)
            'medium': 0.00001,   # 中扰动 (约1米级别)
            'high': 0.00005       # 高扰动 (约10米级别)
        }
        self.noise = self.noise_levels[noise_level]
        self.mqtt_client = None

    def calculate_displacement(self, lat: float, lon: float, direction: float, distance: float) -> tuple:
        """计算基于方向和距离的经纬度位移（使用椭球模型修正）"""
        rad = math.radians(direction)
        
        # 地理坐标系下的分量位移
        delta_x = distance * math.sin(rad)
        delta_y = distance * math.cos(rad)
        
        # 转换为经度纬度变化量（考虑椭球曲率）
        delta_lon = (delta_x / (self.a * math.cos(math.radians(lat))) + 
                     (delta_x**3 * math.sin(math.radians(lat))**2) / (6 * self.a**3))
        delta_lat = (delta_y / self.b - 
                     (delta_y**3) / (6 * self.b**3))
        
        return delta_lat, delta_lon

    def add_noise(self, value: float) -> float:
        """添加高斯噪声扰动"""
        return value + random.gauss(0, self.noise)

    def generate_trajectory(self, 
                          start_lat: float, 
                          start_lon: float, 
                          start_alt: float, 
                          direction: float,  # 0-360度 (正北为0，顺时针增加)
                          speed: float,      # 米/秒
                          total_distance: float) -> List[dict]:
        
        total_time = int(total_distance / speed)
        data_points = []
        current_lat = start_lat
        current_lon = start_lon
        current_alt = start_alt
        
        base_timestamp = int(time.time() * 1000)
        
        for t in range(total_time + 1):
            distance_covered = speed * t
            delta_lat, delta_lon = self.calculate_displacement(
                current_lat, current_lon, direction, distance_covered)
            if t % 10==0:
                apply_noise = 1
            else:
                apply_noise = 0

            actual_lat = start_lat + delta_lat
            actual_lon = start_lon + delta_lon

            if apply_noise:
                noisy_lat = self.add_noise(actual_lat)
                noisy_lon = self.add_noise(actual_lon)
                noisy_alt = start_alt
            else:
                # 添加带扰动的位置数据
                noisy_lat = actual_lat
                noisy_lon = actual_lon
                noisy_alt = start_alt

            data = {
                "event": "BeginTracking",
                "timestamp": base_timestamp + t * 1000,
                "metadata": {
                    "latitude": round(noisy_lat, 7),
                    "longitude": round(noisy_lon, 7),
                    "altitude": round(noisy_alt, 2),
                    "speed_x": round(math.sin(math.radians(direction)) * speed, 7),
                    "speed_y": round(math.cos(math.radians(direction)) * speed, 7),
                    "speed_z": -0.1 if t < total_time/2 else 0.1,  # 模拟垂直速率
                    "data_id": "e32a1c2098e9fc0a006a342e0d5290d0",
                    "radar_id": "Sf855715844Task1",
                    "device_id": "51010000491327775901"
                },
                "extra": {}
            }
            data_points.append(data)
            
        return data_points
    
    def generate_and_stream(self, 
                        start_lat: float,
                        start_lon: float,
                        start_alt: float,
                        direction: float,
                        speed: float,
                        total_distance: float,
                        interval: int = 1):
        """实时生成并流式传输数据"""
        total_time = int(total_distance / speed)
        data_points = []
        current_lat = start_lat
        current_lon = start_lon
        current_alt = start_alt

        base_timestamp = int(time.time() * 1000)
        
        for t in range(total_time + 1):
            distance_covered = speed * t
            delta_lat, delta_lon = self.calculate_displacement(
                current_lat, current_lon, direction, distance_covered)
            
            actual_lat = start_lat + delta_lat
            actual_lon = start_lon + delta_lon

            # 增加每隔xx秒一次扰动
            if t % 10==0:
                apply_noise = 1
            else:
                apply_noise = 0

            if apply_noise:
                noisy_lat = self.add_noise(actual_lat)
                noisy_lon = self.add_noise(actual_lon)
                noisy_alt = start_alt
            else:
                # 添加带扰动的位置数据
                noisy_lat = actual_lat
                noisy_lon = actual_lon
                noisy_alt = start_alt
            
            # ==== 修改部分结束 ====
            
            # 构建数据点
            data_point = {
                "event": "BeginTracking",
                "timestamp": int(base_timestamp  + t*1000),
                "metadata": {
                    "latitude": round(noisy_lat, 7),
                    "longitude": round(noisy_lon, 7),  
                    "altitude": round(self.add_noise(start_alt), 2),
                    "speed_x": round(math.sin(math.radians(direction)) * speed, 7),
                    "speed_y": round(math.cos(math.radians(direction)) * speed, 7),
                    "speed_z": -0.1 if t < total_time/2 else 0.1,  # 模拟垂直速率
                    "data_id": "e32a1c2098e9fc0a006a342e0d5290d0",
                    "radar_id": "Sf855715844Task1",
                    "device_id": "51010000491327775901"
                },
                "extra": {}
            }
            # 在发送前添加以下打印语句
            print(f"Time {t}s | 理论坐标: ({actual_lat:.6f}, {actual_lon:.6f}) | GPS上报: ({noisy_lat:.6f}, {noisy_lon:.6f})")
        
            # 发送到MQTT
            if self.mqtt_client:
                self.send_to_mqtt(data_point)
            else:
                print("未启用MQTT传输")
            
            # 控制发送间隔
            time.sleep(interval)

    def init_mqtt(self, 
                    mqtt_host: str,
                    mqtt_port: int = 1883,
                    mqtt_topic: str = "flight/telemetry",
                    client_id: str = None,
                    username: str = None,
                    password: str = None):
            """初始化MQTT连接配置"""
            self.mqtt_host = mqtt_host
            self.mqtt_port = mqtt_port
            self.mqtt_topic = mqtt_topic
            self.mqtt_client = mqtt.Client(client_id=client_id or f'flight-sim-{random.randint(1000,9999)}')
            
            if username and password:
                self.mqtt_client.username_pw_set(username, password)
            
            # 设置TLS（如果需要）
            # self.mqtt_client.tls_set()
            
            try:
                self.mqtt_client.connect(mqtt_host, mqtt_port, 60)
                self.mqtt_client.loop_start()
            except Exception as e:
                print(f"MQTT连接失败: {str(e)}")
                self.mqtt_client = None
    
    def send_to_mqtt(self, data: dict):
        """通过MQTT发送数据"""
        if not self.mqtt_client:
            print("MQTT未初始化")
            return
        
        try:
            payload = json.dumps(data)
            result = self.mqtt_client.publish(
                self.mqtt_topic, 
                payload,
                qos=1  # 确保至少送达一次
            )
            
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                print(f"消息发送失败，错误码：{result.rc}")
        except Exception as e:
            print(f"发送时发生异常：{str(e)}")
    

    def plot_static_trajectory(self, 
                             trajectory: List[dict],
                             title: str = "无人机飞行轨迹模拟",
                             save_path: str = None):
        """静态轨迹可视化（生成完整轨迹图）"""
        import matplotlib.pyplot as plt
        
        # 提取坐标数据
        lats = [p['metadata']['latitude'] for p in trajectory]
        lons = [p['metadata']['longitude'] for p in trajectory]
        
        # 创建带时间序颜色映射的轨迹图
        plt.figure(figsize=(12, 8))
        sc = plt.scatter(lons, lats, 
                        c=range(len(lats)), 
                        cmap='viridis',
                        s=50,
                        alpha=0.7)
        
        # 标注起点终点
        plt.scatter(lons[0], lats[0], 
                   c='green', s=150, label='Start Point', 
                   marker='^', edgecolors='black')
        plt.scatter(lons[-1], lats[-1], 
                   c='red', s=150, label='End Point',
                   marker='s', edgecolors='black')
        
        # 图表装饰
        plt.colorbar(sc, label='Time Index')
        plt.xlabel('Longitude (deg)')
        plt.ylabel('Latitude (deg)')
        plt.title(title)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend()
        
        # 调节显示范围
        plt.xlim(min(lons)-0.0003, max(lons)+0.0003)
        plt.ylim(min(lats)-0.0003, max(lats)+0.0003)
        
        # 保存或显示
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"轨迹图已保存至：{save_path}")
        else:
            plt.show()
    
    def realtime_visualize(self, 
                         trajectory: List[dict],
                         refresh_interval: float = 0.5):
        """实时动态轨迹模拟"""
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(10, 6))
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title('Real-time Flight Tracking')
        
        # 初始化空数据
        lons, lats = [], []
        line, = plt.plot([], [], 'b-', alpha=0.5)
        point = plt.scatter([], [], c='red', s=50, alpha=0.8)
        
        # 设置坐标范围
        all_lons = [p['metadata']['longitude'] for p in trajectory]
        all_lats = [p['metadata']['latitude'] for p in trajectory]
        plt.xlim(min(all_lons)-0.0002, max(all_lons)+0.0002)
        plt.ylim(min(all_lats)-0.0002, max(all_lats)+0.0002)
        
        # 动态绘制
        for idx, p in enumerate(trajectory):
            lons.append(p['metadata']['longitude'])
            lats.append(p['metadata']['latitude'])
            
            # 更新图形
            line.set_xdata(lons)
            line.set_ydata(lats)
            point.set_offsets([lons[-1], lats[-1]])
            
            # 绘制当前速度信息
            plt.annotate(f"Speed: {p['metadata']['speed_x']:.1f},{p['metadata']['speed_y']:.1f} m/s\n"
                        f"Alt: {p['metadata']['altitude']} m\n"
                        f"Time: {idx} s",
                        xy=(0.05, 0.85), 
                        xycoords='axes fraction',
                        ha='left')
            
            plt.pause(refresh_interval)
            
        plt.show()

if __name__ == "__main__":
    # 1. 创建模拟器实例
    simulator = GPSSimulator(noise_level='medium')
    
    # 2. 配置MQTT连接（参数根据实际情况修改）
    # simulator.init_mqtt(
    #     mqtt_host="nee1f8f9.ala.dedicated.aliyun.emqxcloud.cn",  # 测试用公共MQTT服务器
    #     mqtt_port=1883,
    #     mqtt_topic="drones/flight123/telemetry",
    #     username="admin",    # 如有认证需要
    #     password="123456"
    # )
    simulator.init_mqtt(
        mqtt_host="demo.uavcmlc.com",  # 测试用公共MQTT服务器
        mqtt_port=26686,
        mqtt_topic="iot-dispatcher/test-guochuang",
        username="cmlc",    # 如有认证需要
        password="odD8#Cr628"
    )
    
    # 3. 启动数据生成和传输
    simulator.generate_and_stream(
        start_lat=30.5726681,
        start_lon=104.0369716,
        start_alt=470,
        direction=90,    # 东方向
        speed=100.0,      # 30米/秒
        total_distance=10000,  # 1公里距离
        interval=1       # 每秒发送一次
    )
    
    # 4. 关闭连接
    if simulator.mqtt_client:
        simulator.mqtt_client.loop_stop()
        simulator.mqtt_client.disconnect()

# if __name__ == "__main__":
#     # 创建模拟器实例
#     simulator = GPSSimulator(noise_level='high')
    
#     # 生成飞行轨迹数据（先不要连接MQTT）
#     trajectory = simulator.generate_trajectory(
#         start_lat=30.5778583,
#         start_lon=104.0424741,
#         start_alt=510,
#         direction=90,
#         speed=100.0,
#         total_distance=5000
#     )
    
#     # # 方式一：静态轨迹验证（建议首次验证时使用）
#     # simulator.plot_static_trajectory(
#     #     trajectory,
#     #     title="成都无人机测试航线",
#     #     save_path="flight_path.png"
#     # )
    
#     # 方式二：实时动态模拟（用于观察时间序列特征）
#     simulator.realtime_visualize(
#         trajectory,
#         refresh_interval=0.3  # 调节刷新速度
#     )x25__1.4.0_20250424beta1__10h29m
