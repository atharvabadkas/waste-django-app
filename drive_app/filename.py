import re
from datetime import datetime

from .utils import assign_flags

def parse_filename(filename):
    # filename = "DT20241120_TM155547_MC64E8337E7884_WT-685_TC38_TX37_RN520.jpg"
    pattern = r"DT(?P<date>\d{8})_TM(?P<time>\d{6})_.*_WT(?P<weight>-?\d+)_TC(?P<cam_temp>\d+)_TX(?P<mcu_temp>\d+)_RN(?P<random_num>\d+)"
    match = re.match(pattern, filename)
    
    if match:
        # Extract details
        date = match.group("date")  # Format: YYYYMMDD
        time = match.group("time")  # Format: HHMMSS
        weight = match.group("weight")
        cam_temp = match.group("cam_temp")
        mcu_temp = match.group("mcu_temp")
        random_num = match.group("random_num")
        
        # Convert to timestamp format: "YYYY-MM-DD HH:MM:SS"
        timestamp = datetime.strptime(f"{date}{time}", "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")

        # Get the flags based on temperature ranges
        camera_flag, mcu_flag = assign_flags(cam_temp, mcu_temp)
        
        return {
            "timestamp": timestamp,
            "weight": weight,
            "cam_temp": cam_temp,
            "mcu_temp": mcu_temp,
            "random_num": random_num,
            "camera_flag": camera_flag,
            "mcu_flag": mcu_flag,
        }
    else:
        return {
            "timestamp": "Invalid filename",
            "weight": "N/A",
            "cam_temp": "N/A",
            "mcu_temp": "N/A",
            "random_num": "N/A",
            "camera_flag": "N/A",
            "mcu_flag": "N/A",
        }