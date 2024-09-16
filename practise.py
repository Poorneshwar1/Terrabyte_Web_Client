# this file is not realted to project 

# used to test some code

import os
import json

# Path to the folder containing both images and JSON files
folder_path = 'downloadedImages'

def mapImageToJson(folder_path):
    # Dictionary to store the mapping
    imageJsonDict = {}

    image_arr = []
    for path in os.listdir(folder_path):
        full_path = os.path.join(folder_path, path)
        if os.path.isfile(full_path) and path.lower().endswith('.jpg'):
            image_arr.append(path)

    def find_full_filename(image_list, search_string):
        for fname in image_list:
            if search_string in fname:
                return fname
            else:
                pass   
        return fname

    # Iterate over each file in the folder
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if file_name.endswith('.json'):
            with open(file_path, 'r') as f:
                data = json.load(f)
                image_file_name = data.get('bounding_boxes')
                subimage_file_names = [entry['subimage_file_name'] for entry in image_file_name]
                for x in subimage_file_names:
                    fullImageName = find_full_filename(image_arr,x)
                
                # Check if the corresponding image file exists
                if os.path.isfile(os.path.join(folder_path, fullImageName)):
                    imageJsonDict[fullImageName] = file_name
    return imageJsonDict

# Print the mapping
#print(mapImageToJson(folder_path))
#print(image_to_json_map[image_arr[0]])

retuDict = mapImageToJson(folder_path)

keyArr=list(retuDict.keys())
print(len(keyArr))
print(retuDict[keyArr[0]])