from DrivingInterface.drive_controller import DrivingController
import math

class DrivingClient(DrivingController):
    def __init__(self):
        # =========================================================== #
        #  Area for member variables =============================== #
        # =========================================================== #
        # Editing area starts from here
        #

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

        refnum = 24 - max(0, sensing_info.speed-70) / 100
        way_points = []
        y = math.sqrt(math.pow(sensing_info.distance_to_way_points[0], 2)-math.pow(sensing_info.to_middle, 2))
        way_points.append({'x': 0, 'y': y})
        for i in range(9):
            x = way_points[i]['x'] + (10 * math.sin(math.radians(sensing_info.track_forward_angles[i])))
            y = way_points[i]['y'] + (10 * math.cos(math.radians(sensing_info.track_forward_angles[i])))
            way_points.append({'x': x, 'y': y})
        if sensing_info.speed < 120:
            ref_idx = 7
        else:
            ref_idx = max(5, int(sensing_info.speed/refnum))
        target_x = way_points[ref_idx]['x']
        target_y = way_points[ref_idx]['y']
        brk = max(0, abs(sensing_info.track_forward_angles[ref_idx] - sensing_info.moving_angle)-25) / 840 + max(0, sensing_info.speed - 180) / 100
        spdnum = abs(sensing_info.to_middle-12)/40 + max(0, abs(sensing_info.track_forward_angles[ref_idx]) - abs(sensing_info.moving_angle/2)-4) / 600 + max(0, sensing_info.speed-100) / 105
        steering = (math.atan((target_x - sensing_info.to_middle)/target_y) -
                    math.radians(sensing_info.moving_angle)) * spdnum
        if sensing_info.speed < 200:
            car_controls.brake = 0 + brk
        elif 200 <= sensing_info.speed:
            car_controls.brake = 0.5 + brk
        car_controls.steering = steering
        car_controls.throttle = 1

        
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
