import threading
from flask import Flask ,render_template, request, redirect, send_from_directory, url_for, jsonify
from clientSimple1 import download_cmd, req_data, send_req, USER_URL
# from flask_socketio import SocketIO, emit
import os,json
import asyncio

app = Flask(__name__)
app.config['DOWNLOAD_FOLDER'] = 'downloadedImages'

with open('metadata.json', 'r') as file:
    metadata = json.load(file)

data = send_req(
            method="POST",
            endpoint=USER_URL,
            url="login",
            req_data={
                "username": "", #enter your username here
                "password": "" #enter your password here
            },
            parameters=None
        )

def has_files(directory):
    # Check if the directory exists
    if not os.path.isdir(directory):
        print(f"The directory '{directory}' does not exist.")
        return False

    # Iterate over the contents of the directory
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        # Check if the item is a file
        if os.path.isfile(item_path):
            return True

    return False

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
                    if(find_full_filename(image_arr,x)):
                        fullImageName = find_full_filename(image_arr,x)
                    else:
                        fullImageName = "not_there" #some random name
                
                # Check if the corresponding image file exists
                if os.path.isfile(os.path.join(folder_path, fullImageName)):
                    imageJsonDict[fullImageName] = file_name
    return imageJsonDict



@app.route("/")
def home():
    return render_template("home.html",plants=metadata["eagli_plants"])

@app.route("/image")
def image():
    ImageJsonMap = mapImageToJson(app.config['DOWNLOAD_FOLDER'])
    ImageNameArr = list(ImageJsonMap.keys())
    return render_template('images.html', files=ImageNameArr, plants=metadata["eagli_plants"], PlantName=req_data['eagli_parameters.plants'],dict = ImageJsonMap)

@app.route("/get_images")
def get_images():
    ImageJsonMap = mapImageToJson(app.config['DOWNLOAD_FOLDER'])
    ImageNameArr = list(ImageJsonMap.keys())
    return jsonify(ImageNameArr)


@app.route('/downloadImgs', methods=['POST'])
def downloadImgs():

    for path in os.listdir(app.config['DOWNLOAD_FOLDER']):
        if os.path.exists(os.path.join(app.config['DOWNLOAD_FOLDER'], path)):
            os.remove(os.path.join(app.config['DOWNLOAD_FOLDER'], path))
 
    if request.method == 'POST':
        # Start the download process in a separate thread
        #query_data = req_data
        #threading.Thread(target=download_cmd, args=(query_data, app.config['DOWNLOAD_FOLDER'])).start()
        plant_type=request.form.get("plant_type")
        req_data['eagli_parameters.plants']=plant_type
        print(req_data['eagli_parameters.plants'])
        res_data = download_cmd(query_data=req_data,download_dir=app.config['DOWNLOAD_FOLDER'])
        if(res_data[0]['ack_received']):
            return redirect(url_for("image"))
        elif(res_data[0]['error']):
            return render_template("error.html")
        else:
            return render_template("error.html")
    
    return redirect(url_for("home"))


@app.route('/show_img/<filename>')
def show_img(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'] , filename)

@app.route("/get_jsons")
def get_jsons():
    ImageJsonMap = mapImageToJson(app.config['DOWNLOAD_FOLDER'])
    ImageJsonContentMap = {}

    for image_filename, json_filename in ImageJsonMap.items():
        json_filepath = os.path.join(app.config['DOWNLOAD_FOLDER'], json_filename)

        # Read the JSON file
        with open(json_filepath, 'r') as json_file:
            json_content = json.load(json_file)
        
        # Build a new dictionary with image and corresponding JSON content
        ImageJsonContentMap[image_filename] = json_content

    return jsonify(ImageJsonContentMap)



if __name__=="__main__":
    app.run(debug=True) 