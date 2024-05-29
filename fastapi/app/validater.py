from haversine import haversine
from .config import Config
from .fcm_notification import send_push_notification


class validateInSafeArea:
    def __init__(self):
        pass
    
    def isinsafearea(self, current_loc, safe_area_list):
        distance_list = []
        for safe_area in safe_area_list:
            safe_area_location = (safe_area.latitude, safe_area.longitude)
            distance = haversine(current_loc, safe_area_location, unit='m')
            distance_list.append(distance)
            
        min_distance = min(distance_list)
        min_distance_index = distance_list.index(min_distance)
        nearest_safe_area = safe_area_list[min_distance_index]

        if min_distance > nearest_safe_area.radius:
            print(f"[INFO] Current location is not in safe area({nearest_safe_area.area_name})")
            return nearest_safe_area, False
        else:
            return nearest_safe_area, True
    
    async def pushNotification(self, fcm_token, latest_location, before_location, safeArea):
        if latest_location.isInSafeArea == 0 and before_location.isInSafeArea == 1:
            data = {
                "safeAreaName" : safeArea.area_name,
                "time" : latest_location.time
            }
            send_push_notification(Config.temp_fcm_token, "어디U", "안심 구역 이탈", data)
        elif latest_location.isInSafeArea == 1 and before_location.isInSafeArea == 0:
            data = {
                "safeAreaName" : safeArea.area_name,
                "time" : latest_location.time
            }
            send_push_notification(fcm_token, "어디U", "안심 구역 진입", data)
    

