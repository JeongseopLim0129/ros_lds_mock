import roslibpy
import numpy as np
import time

# ==========================================
ROBOT_IP = 'localhost' 
ROBOT_PORT = 9090
# ==========================================

class TurtleController:
    def __init__(self, ip, port):
        # 1. 연결 설정
        print(f"Connecting to ROS 2 Bridge at {ip}:{port}...")
        self.client = roslibpy.Ros(host=ip, port=port)
        
        try:
            self.client.run()
            print("Connected! Waiting for /scan topic...")
        except Exception as e:
            print(f"연결 실패! 에러: {e}")
            self.client = None
            return

        # 2. 통신 설정
        self.talker = roslibpy.Topic(self.client, '/turtle1/cmd_vel', 'geometry_msgs/Twist')
        self.listener = roslibpy.Topic(self.client, '/scan', 'sensor_msgs/LaserScan')
        self.listener.subscribe(self.process_scan_data)

        # 3. [핵심] 현재 속도 상태 저장 (기본값: 전진)
        # 이 변수들을 계속 유지하다가, 센서가 "위험해!" 하면 값만 바꿉니다.
        self.current_linear = 0.2  # 기본 직진 속도
        self.current_angular = 0.0 # 기본 회전 속도 (0이면 직진)

    def process_scan_data(self, msg):
        """
        [두뇌 역할]
        여기서는 로봇을 직접 움직이지 않고, '어떻게 움직여야 할지' 방향만 정합니다.
        """
        ranges = np.array(msg['ranges'])
        if len(ranges) < 360: return

        # 거리 계산
        front = np.r_[ranges[350:360], ranges[0:10]]
        left  = ranges[80:100]
        right = ranges[260:280]

        front_dist = np.mean(front)
        left_dist  = np.mean(left)
        right_dist = np.mean(right)

        safe_dist = 0.6
        
        # [판단 로직] -> 변수 값만 업데이트!
        if front_dist < safe_dist:
            # 벽 발견!
            if left_dist > right_dist:
                # 왼쪽으로 가자 (전진하면서 좌회전)
                self.current_linear = 0.2
                self.current_angular = 1.0
                action = "turn_left ⬅️"
            else:
                # 오른쪽으로 가자 (전진하면서 우회전)
                self.current_linear = 0.2
                self.current_angular = -1.0
                action = "turn_right ➡️"
        else:
            # 안전함 -> 다시 직진 모드로 복귀
            self.current_linear = 0.2
            self.current_angular = 0.0
            action = "go_forward ⬆️"

        # (선택사항) 너무 시끄러우면 로그는 필요할 때만 출력
        print(f"Action Update: {action} (F:{front_dist:.2f})")

    def publish_command(self):
        """
        [엔진 역할]
        현재 설정된 속도값(self.current_...)을 실제로 전송합니다.
        """
        if not self.talker: return

        message_data = {
            'linear': {'x': float(self.current_linear), 'y': 0.0, 'z': 0.0},
            'angular': {'x': 0.0, 'y': 0.0, 'z': float(self.current_angular)}
        }
        self.talker.publish(roslibpy.Message(message_data))

    def run_forever(self):
        """
        [심장 역할]
        센서 데이터가 오든 말든, 0.1초마다 꾸준히 명령을 보냅니다.
        """
        if not self.client: return

        print(">>> 자율주행 시작 (Ctrl+C로 종료)")
        try:
            while self.client.is_connected:
                # 1. 현재 정해진 속도로 명령 전송 (무조건 실행)
                self.publish_command()
                
                # 2. 0.1초 대기 (1초에 10번 전송)
                # 이 간격이 짧을수록 움직임이 부드러워집니다.
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n종료합니다.")
        finally:
            self.listener.unsubscribe()
            self.talker.unadvertise()
            self.client.terminate()

if __name__ == '__main__':
    controller = TurtleController(ROBOT_IP, ROBOT_PORT)
    controller.run_forever()



# import roslibpy
# import numpy as np
# import time

# # ==========================================
# # 설정 (리눅스 IP 주소)
# # WSL2를 쓴다면 보통 'localhost'로 접속 가능합니다.
# # 안 되면 리눅스에서 'hostname -I'로 확인한 IP를 넣으세요.
# ROBOT_IP = 'localhost' 
# ROBOT_PORT = 9090
# # ==========================================

# def process_scan_data(msg):
#     """
#     ROS 2 LaserScan 메시지를 받아서 주행 판단을 내리는 콜백 함수
#     """
#     # 1. 데이터 파싱 (리스트 -> 넘파이 배열)
#     # mock_publisher에서 보낸 ranges 데이터
#     ranges = np.array(msg['ranges'])
    
#     # 데이터 개수 확인 (LDS-02 모의 데이터는 360개)
#     if len(ranges) < 360:
#         return

#     # 2. 방향별 거리 계산 (제공해주신 로직 적용)
#     # 정면: 350~360도 + 0~10도
#     front = np.r_[ranges[350:360], ranges[0:10]]
#     # 왼쪽: 80~100도 (90도 부근)
#     left  = ranges[80:100]
#     # 오른쪽: 260~280도 (270도 부근)
#     right = ranges[260:280]

#     # 평균 거리 계산
#     # (실제 센서는 inf 값이 있을 수 있어 np.nanmean 등을 쓰기도 하지만, 모의 데이터라 mean 사용)
#     front_dist = np.mean(front)
#     left_dist  = np.mean(left)
#     right_dist = np.mean(right)

#     # 3. 행동 결정 로직
#     safe_dist = 0.6  # 안전거리 기준 (살짝 여유 있게 잡음)
#     action = ""

#     if front_dist < safe_dist:
#         # 앞에 벽이 있으면 더 넓은 쪽으로 회전
#         if left_dist > right_dist:
#             action = "turn_left ⬅️"
#             go_left()
#         else:
#             action = "turn_right ➡️"
#             go_right()
#     else:
#         # 앞이 뚫려있으면 전진
#         action = "go_forward ⬆️"
#         go_front()

#     # 4. 결과 출력
#     print("-" * 30)
#     print(f"패턴 감지: {msg['header']['frame_id']} (timestamp: {msg['header']['stamp']['sec']})")
#     print(f"Front: {front_dist:.2f} m")
#     print(f"Left : {left_dist:.2f} m")
#     print(f"Right: {right_dist:.2f} m")
#     print(f"결정된 행동: [ {action} ]")

# def go_front():
#     global talker
#     linear_speed = 2.0
#     angular_speed = 0.0
#     message_data = {
#     'linear': {'x': linear_speed, 'y': 0.0, 'z': 0.0},
#     'angular': {'x': 0.0, 'y': 0.0, 'z': angular_speed}
#     }
#     talker.publish(roslibpy.Message(message_data))

# def go_left():
#     global talker
#     linear_speed = 2.0
#     angular_speed = 2.0
#     message_data = {
#     'linear': {'x': linear_speed, 'y': 0.0, 'z': 0.0},
#     'angular': {'x': 0.0, 'y': 0.0, 'z': angular_speed}
#     }
#     talker.publish(roslibpy.Message(message_data))

# def go_right():
#     global talker
#     linear_speed = 2.0
#     angular_speed = -2.0
#     message_data = {
#     'linear': {'x': linear_speed, 'y': 0.0, 'z': 0.0},
#     'angular': {'x': 0.0, 'y': 0.0, 'z': angular_speed}
#     }
#     talker.publish(roslibpy.Message(message_data))

# def main():
#     print(f"Connecting to ROS 2 Bridge at {ROBOT_IP}:{ROBOT_PORT}...")
    
#     global talker
#     # 1. ROS Bridge 연결
#     client = roslibpy.Ros(host=ROBOT_IP, port=ROBOT_PORT)
    
#     try:
#         client.run()
#         print("Connected! Waiting for /scan topic...")
#     except Exception as e:
#         print(f"연결 실패! 리눅스에서 rosbridge가 켜져있는지 확인하세요.\n에러: {e}")
#         return
    
#     talker = roslibpy.Topic(client, '/turtle1/cmd_vel', 'geometry_msgs/Twist')

#     # 2. Subscriber 설정
#     listener = roslibpy.Topic(client, '/scan', 'sensor_msgs/LaserScan')
    
#     # 메시지가 오면 process_scan_data 함수 실행
#     listener.subscribe(process_scan_data)

#     # 3. 프로그램 유지
#     try:
#         while client.is_connected:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print("\n종료합니다.")
#     finally:
#         listener.unsubscribe()
#         client.terminate()

# if __name__ == '__main__':
#     main()