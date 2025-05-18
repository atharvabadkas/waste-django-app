from datetime import datetime

from .filename import parse_filename

# Function to segregate and process images
def process_images(image_data):
    # Sort images by timestamp
    image_data.sort(key=lambda x: x['name'])

    sets = []  # To store image sets
    temp_set = []  # Temporary set for grouping images

    for image in image_data:
        parsed_data = parse_filename(image['name'])         #image['name'] is filename
        if parsed_data:
            image.update(parsed_data)

            # Grouping logic: if current set is empty or random_num matches the last in temp_set, add to the set
            if not temp_set or temp_set[-1]['random_num'] == image['random_num']:
                temp_set.append(image)
            else:
                # Process the completed set
                sets.append(assign_set_flags(temp_set))
                temp_set = [image]  # Start a new set with the current image
    
    # Process the last set
    if temp_set:
        sets.append(assign_set_flags(temp_set))

    return sets


def assign_set_flags(image_set):
    # Count proxy and weight images
    proxy_count = sum(1 for img in image_set if img['weight'] == '65100001')
    weight_count = sum(1 for img in image_set if img['weight'] != '65100001')

    # print(f"Processing set with {len(image_set)} images: {proxy_count} proxy, {weight_count} weight")

    # Condition 1: 1 proxy + 1 weight
    if len(image_set) == 2 and proxy_count == 1 and weight_count == 1:
        for image in image_set:
            image['set_flag'] = 'RN1'
        
        # Check time difference for RN1
        proxy_image = next(img for img in image_set if img['weight'] == '65100001')
        weight_image = next(img for img in image_set if img['weight'] != '65100001')

        #weight image
        if (-10000 <= int(weight_image['weight']) <= 200000):
            weight_image['weight_flag'] = 'WT1'
        else:
            weight_image['weight_flag'] = 'WT2'
        #proxy image
        if(int(proxy_image['weight']) == 65100001):
            proxy_image['weight_flag'] = 'WT1'
        else:
            proxy_image['weight_flag'] = 'WT2'

        # Convert timestamps to datetime objects for comparison
        proxy_timestamp = datetime.strptime(proxy_image['time_date'], "%Y-%m-%d %H:%M:%S")
        weight_timestamp = datetime.strptime(weight_image['time_date'], "%Y-%m-%d %H:%M:%S")

        time_diff = abs((proxy_timestamp - weight_timestamp).total_seconds())
        if time_diff > 30:
            proxy_image['time_flag'] = 'TM2'
            weight_image['time_flag'] = 'TM2'
        else:
            proxy_image['time_flag'] = 'TM1'
            weight_image['time_flag'] = 'TM1'


    # Condition 2: Multiple proxies + 1 weight
    elif proxy_count > 1 and weight_count == 1:
        # Duplicate the weight image to pair with each proxy
        weight_image = next(img for img in image_set if img['weight'] != '65100001')
        proxy_images = [img for img in image_set if img['weight'] == '65100001']
        
        #weight image
        if (-10000 <= int(weight_image['weight']) <= 200000):
            weight_image['weight_flag'] = 'WT1'
        else:
            weight_image['weight_flag'] = 'WT2'
        #proxy image
        for img in proxy_images:
            if(int(img['weight']) == 65100001):
                img['weight_flag'] = 'WT1'
            else:
                img['weight_flag'] = 'WT2'    


        # Create pairs of proxy and weight images
        paired_images = []
        for idx, proxy_image in enumerate(proxy_images):
            # Clone the weight image and assign a pair ID
            paired_weight = weight_image.copy()
            pair_id = f"RN2_{idx + 1}"  # Assign unique pair ID
            proxy_image['pair_id'] = pair_id
            paired_weight['pair_id'] = pair_id

            # Set flags for both images
            proxy_image['set_flag'] = 'RN2'
            paired_weight['set_flag'] = 'RN2'

            # Check time difference for RN2
            proxy_timestamp = datetime.strptime(proxy_image['time_date'], "%Y-%m-%d %H:%M:%S")
            weight_timestamp = datetime.strptime(paired_weight['time_date'], "%Y-%m-%d %H:%M:%S")

            time_diff = abs((proxy_timestamp - weight_timestamp).total_seconds())
            if time_diff > 30:
                proxy_image['time_flag'] = 'TM2'
                paired_weight['time_flag'] = 'TM2'
            else:
                proxy_image['time_flag'] = 'TM1'
                paired_weight['time_flag'] = 'TM1'

            # # Add to paired images
            paired_images.append(proxy_image)
            paired_images.append(paired_weight)

        return paired_images
    

    # Condition 3: Only 1 weight image
    elif len(image_set) == 1 and weight_count == 1:
        for image in image_set:
            image['set_flag'] = 'RN3'
            image['time_flag'] = 'Na'
            weight = image['weight']
            if (weight.lstrip('-').isdigit() and -10000 <= int(weight) <= 200000):
                image['weight_flag'] = 'WT1'
            else:
                image['weight_flag'] = 'WT2'
            

    # Condition 4: Mark as invalid if no conditions are met
    else:
        for image in image_set:
            image['set_flag'] = 'Invalid'
            image['time_flag'] = 'Invalid'
            image['weight_flag'] = 'Invalid'

    return image_set