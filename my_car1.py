from DrivingInterface.drive_controller import DrivingController
import math

col = False

class DrivingClient(DrivingController):
    def __init__(self):
        # =========================================================== #
        #  Area for member variables =============================== #
        # =========================================================== #
        # Editing area starts from here
        self.col = col
        self.is_debug = True

        # api or keyboard
        self.enable_api_control = True # True(Controlled by code) /False(Controlled by keyboard)
        super().set_enable_api_control(self.enable_api_control)

        #
        # Editing area ends
        # ==========================================================#
        super().__init__()

    
    def control_driving(self, car_controls, sensing_info):

        # =========================================================== #
        # Area for writing code about driving rule ================= #
        # =========================================================== #
        # Editing area starts from here
        #

        if self.is_debug:
            print("=========================================================")
            print("[MyCar] to middle: {}".format(sensing_info.to_middle))

            print("[MyCar] collided: {}".format(sensing_info.collided))
            print("[MyCar] car speed: {} km/h".format(sensing_info.speed))

            print("[MyCar] is moving forward: {}".format(sensing_info.moving_forward))
            print("[MyCar] moving angle: {}".format(sensing_info.moving_angle))
            print("[MyCar] lap_progress: {}".format(sensing_info.lap_progress))

            print("[MyCar] track_forward_angles: {}".format(sensing_info.track_forward_angles))
            print("[MyCar] track_forward_obstacles: {}".format(sensing_info.track_forward_obstacles))
            print("[MyCar] opponent_cars_info: {}".format(sensing_info.opponent_cars_info))
            print("[MyCar] distance_to_way_points: {}".format(sensing_info.distance_to_way_points))
            print("=========================================================")

        ###########################################################################

        # Moving straight forward
        car_controls.throttle = 1
        if sensing_info.collided:
            self.col = True
            # print('충돌')
            # print('바꾼뒤', self.col)
        if self.col:
            # if sensing_info.moving_forward > 0 and # 벽에 부딧칠때의 상황
            print(sensing_info.to_middle)
            if -10 < sensing_info.moving_angle < 10:  # 장애물에 똑바로 부딪칠시 -> 그대로 후진
                car_controls.throttle = - 1
                if sensing_info.track_forward_obstacles[0]:
                    if sensing_info.track_forward_obstacles[0]['dist'] > 10:
                        self.col = False
                else:
                    self.col = False
            else:  # 잔디에 쳐박힐시 / 비스듬하세 부딪칠 시
                if -90 < sensing_info.moving_angle < 90:  # 똑바로 처박힘 not (- 10 < sensing_info.to_middle < 10)
                    if sensing_info.to_middle < 0 and -90 < sensing_info.moving_angle < 0:  # 왼쪽, 오른쪽 위에
                        car_controls.throttle = - 1
                        car_controls.steering = 1
                        print(1 - 1)
                    elif sensing_info.to_middle > 0 and 0 < sensing_info.moving_angle < 90:
                        car_controls.throttle = - 1
                        car_controls.steering = -1
                        print(1 - 2)
                    else:
                        car_controls.throttle = 1
                        print(2)
                    if sensing_info.to_middle == 0 or -20 < sensing_info.moving_angle < 20:
                        self.col = False
                else:  # 거꾸로 처박힘
                    if sensing_info.to_middle < 0:  # 왼쪽 위치
                        car_controls.steering = 1
                        if sensing_info.moving_angle < 0:
                            car_controls.throttle = - 1
                            print(3)
                        else:
                            car_controls.throttle = + 1
                            print(4)
                    else:  # 오른 위치
                        car_controls.steering = -1
                        if sensing_info.moving_angle < 0:
                            car_controls.throttle = + 1
                            print(5)
                        else:
                            car_controls.throttle = - 1
                            print(6)
                    if -20 < sensing_info.moving_angle < 20:
                        self.col = False

        else:
            self.col = False
            # 유라 코드 보고 베낀 거라 확실하진 않지만
            # 앞으로 가야될 길의 x, y 좌표를 구하는 코드
            way_points = []
            y = math.sqrt(math.pow(sensing_info.distance_to_way_points[0], 2)-math.pow(sensing_info.to_middle, 2))
            way_points.append({'x': 0, 'y': y})
            for i in range(19):  # 19개의 지점에 대한 angle에 따른 x, y 좌표
                x = way_points[i]['x'] + (10 * math.sin(math.radians(sensing_info.track_forward_angles[i])))
                y = way_points[i]['y'] + (10 * math.cos(math.radians(sensing_info.track_forward_angles[i])))
                way_points.append({'x': x, 'y': y})

            # print(way_points)
            # refnum = 얼마나 멀리 있는 지점을 보고 달릴 건지 정하는 변수. 밑의 ref_idx를 정할 때 사용. 속도가 빨라질 수록 refnum은 줄어들게.
            refnum = 40
            if sensing_info.speed < 120:    # ref_idx = 열 개의 지점 중 몇 번째 지점을 기준으로 핸들을 돌릴 건지 정하는 변수.
                ref_idx = 7                 # 처음에 속도가 너무 느릴 때는 너무 짧게 보길래 강제로 멀리 보게 변수 조정.
            else:
                ref_idx = max(5, int(sensing_info.speed/refnum))    # 속도 120km 이상일 때는 속도에 맞춰서 보도록.
            # target_x, target_y = 현재 보고 있는 지점
            target_x = way_points[ref_idx]['x']
            target_y = way_points[ref_idx]['y']
            mid = 0
            # idx = 10
            if sensing_info.track_forward_obstacles:
                # for i in range(19):
                #     if sensing_info.distance_to_way_points[i] > sensing_info.track_forward_obstacles[0]['dist']:
                #         idx = i - 2
                #         if idx < 0:
                #             idx = 0
                #         break
                if sensing_info.track_forward_angles[ref_idx] > 10 and sensing_info.track_forward_obstacles[0]['to_middle'] > 0:
                    mid += min(10, max(0, sensing_info.speed/max(1, sensing_info.track_forward_obstacles[0]['dist'])))
                    target_y -= 5
                elif sensing_info.track_forward_angles[ref_idx] < 10 and sensing_info.track_forward_obstacles[0]['to_middle'] < 0:
                    mid -= min(10, max(0, sensing_info.speed/max(1, sensing_info.track_forward_obstacles[0]['dist'])))
                    target_y -= 5
                if -2 < sensing_info.track_forward_obstacles[0]['to_middle'] < 2:
                    if sensing_info.track_forward_angles[ref_idx] < 0:
                        mid *= 3
                        target_y -= 5
                    else:
                        mid *= 3
                        target_y -= 5
                print(mid)
            target_x += mid
            # spdnum = 핸들을 꺾는 정도. 중심에서 벗어날수록, 현재 나의 각도와 앞으로 볼 각도의 크기 차이가 클수록, 속도가 높을수록 핸들을 확 돌리도록.
            spdnum = abs(sensing_info.to_middle - 12)/40 + max(0, abs(sensing_info.track_forward_angles[ref_idx] - sensing_info.moving_angle)) / 480 + max(1, sensing_info.speed-90) /100
            # steering = 핸들 꺾는 정도.
            steering = (math.atan((target_x - sensing_info.to_middle)/target_y) -
                        math.radians(sensing_info.moving_angle)) * spdnum
            # brk = 브레이크 잡는 정도. 현재 나의 각도와 앞으로 볼 각도의 크기 차이가 클수록 세게. && 속도가 180이 넘으면 브레이크 잡도록.
            brk = max(0, abs(sensing_info.track_forward_angles[ref_idx] - sensing_info.moving_angle)-30) / 840 + max(0, sensing_info.speed - 180) / 150
            # 속도가 200이 넘으면 brk에 0.3을 더해 더 세게 브레이크 잡기.
            if sensing_info.speed < 100:
                car_controls.brake = 0 + brk
            elif 100 <= sensing_info.speed:
                car_controls.brake = 0.3 + brk
            if steering > 1:
                steering = 1
            elif steering < -1:
                steering = -1
            car_controls.steering = steering
            # 언제나 풀악셀...
            car_controls.throttle = 1

            if sensing_info.collided:
                car_controls.throttle = 0

        
        if self.is_debug:
            print("[MyCar] steering:{}, throttle:{}, brake:{}"\
                  .format(car_controls.steering, car_controls.throttle, car_controls.brake))

        #
        # Editing area ends
        # ==========================================================#
        return car_controls


    # ============================
    # If you have NOT changed the <settings.json> file
    # ===> player_name = ""
    #
    # If you changed the <settings.json> file
    # ===> player_name = "My car name" (specified in the json file)  ex) Car1
    # ============================
    def set_player_name(self):
        player_name = "broad==accel"
        return player_name


if __name__ == '__main__':
    print("[MyCar] Start Bot! (PYTHON)")

    client = DrivingClient()
    return_code = client.run()

    print("[MyCar] End Bot! (PYTHON)")

    exit(return_code)
