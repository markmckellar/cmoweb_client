#!/usr/bin/python3
import cv2
import numpy as np
import glob
import os 
import sys
import json
import time
import shutil
import subprocess


class MakeVideo :

    def __init__(self):
        self.xxxx = 0


    def make_video_from_image_dir_ffmpeg(self,image_folder,image_input_pattern,video_name,video_json) :
            command = f"ffmpeg -y -framerate 24 -i {image_folder}/{image_input_pattern} -vf \"pad=ceil(iw/2)*2:ceil(ih/2)*2\" {video_name}"
            print(f"running:{command}")
            os.system(command)

            command = f"ffprobe {video_name} -show_format 2>&1 | sed -n 's/duration=//p'"
            print(f"running:{command}")
            #video_json["me_time"] = os.system(command)
            run_time =  subprocess.check_output(command, shell=True)
            print(f"got run_time of {run_time}")
            try :
            	video_json["me_time"] = float(run_time.strip().decode())
            except :
            	print(f"got error converting run_time of {run_time}")
            #video_json["me_time"] = os.popen(command).read()
            #tiiiiiiiiiiime = os.popen(command).read()

            all_json_files = [jsonFile for jsonFile in os.listdir(image_folder) if jsonFile.endswith("json")]
            all_json_files.sort()

            for json_file in all_json_files :
                    motion_event_json = {}
                    with open(image_folder+"/"+json_file, 'r') as f:
                        motion_event_json = json.load(f)   
                        video_json["me_array"].append(motion_event_json)

            with open(config["output_dir"]+"/" + video_json["me_tag"]+".json", 'w') as outfile:
                                outfile.write( json.dumps(video_json,indent=4) )


    def make_video_from_image_dir(self,image_folder,video_name,image_ends_with) :
        images = [img for img in os.listdir(image_folder) if img.endswith(image_ends_with)]
        images.sort()
        frame = cv2.imread(os.path.join(image_folder, images[0]))
        height, width, layers = frame.shape

        video = cv2.VideoWriter(video_name, 0, 1, (width,height))

        for image in images:
            video.write(cv2.imread(os.path.join(image_folder, image)))

        cv2.destroyAllWindows()
        video.release()



# get the config file 
	# "motion_event_processor":{
	# 	"active":true,
	# 	"watch_dir":"./images",
	# 	"output_dir":"./uploads",
	# 	"movie_type":"mp4",
	# 	"make_combined_move":true,
	# 	"make_event_movies":true,
	# 	"out_images":true,
	# 	"delete_when_done":true
	# },

if(len(sys.argv)!=2) :
    print("Invalid arguments : your_config_file.json : the \"output_image_dir\" is the dir which will be processed")
    print("You gave %i arguments" % (len(sys.argv)))
    quit()
config_file = sys.argv[1]

      
while(True) :

    config_json = {}
    with open(config_file, 'r') as f:
            config_json = json.load(f)   
    config = config_json["motion_event_processor"]
    if(config["active"])  :

        folder = config["watch_dir"]
        print(f"starting processing:folder={folder}")

        subfolders = [ f.path for f in os.scandir(folder) if f.is_dir() ]
        subfolders.sort()  

        make_video = MakeVideo()
        for image_dir in subfolders: 
            size = None
            img_array_for_a_dir = []

            # then the files...
            image_dir_base = os.path.basename(image_dir)

            if "not_ready" not in image_dir_base :
                video_name = config["output_dir"]+"/"+image_dir_base+".mp4"
                image_input_pattern = config["image_input_pattern"]
                print(f"processing:image_dir={image_dir} image_input_pattern={image_input_pattern} write to={video_name} image_dir_base={image_dir_base}")
                make_video.make_video_from_image_dir_ffmpeg(image_dir,
                    image_input_pattern,
                    video_name,
                    {
                        "me_tag":image_dir_base,
                        "me_array":[],
                        "me_time":-1,
                    })
            

            try :
            	if(config["delete_when_done"]) : shutil.rmtree(image_dir)
            except :
            	print(f"had an error removing {image_dir}")

        sleep_time = config["sleep_time"]
        print(f"sleeping for {sleep_time}...")
        time.sleep(sleep_time)
        
