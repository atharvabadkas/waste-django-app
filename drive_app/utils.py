#remove duplicates, assign flags(temp)

#Remove duplicate images based on unique identifiers like name, timestamp, and weight.
def remove_duplicates(images):
    seen = set()
    unique_images = []
    for image in images:
        # Use a tuple of unique attributes as the identifier
        identifier = (image['time_date'], image['item_weight'])
        if identifier not in seen:
            seen.add(identifier)
            unique_images.append(image)
    return unique_images


# Function to assign flags based on temperature ranges
def assign_flags(camera_temp, mcu_temp):
    camera_flag = "N/A"
    mcu_flag = "N/A"

    # Camera temperature conditions
    if 5 <= int(camera_temp) <= 45:
        camera_flag = "TC1"
    elif 45 < int(camera_temp) <= 55:
        camera_flag = "TC2"
    elif 55 < int(camera_temp) <= 100:
        camera_flag = "TC3"
    else:
        camera_flag = "TC4"

    # MCU temperature conditions
    if 5 <= int(mcu_temp) <= 60:
        mcu_flag = "TX1"
    elif 60 < int(mcu_temp) <= 80:
        mcu_flag = "TX2"
    elif 80 < int(mcu_temp) <= 100:
        mcu_flag = "TX3"
    else:
        mcu_flag = "TX4"

    return camera_flag, mcu_flag