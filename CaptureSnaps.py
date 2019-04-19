# -*- coding: utf-8 -*-
"""
Created on Thu Mar  11 21:40:21 2019

@author: Sayed Inamdar
"""

import cv2
import math
import os
import fnmatch
import random
import shutil

import logging

logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_name = str(__file__)
sep=''
if '/' in file_name:
    sep='/'
else:
    sep='\\'
file_name=file_name.split(sep)[-1].replace('.py','.log')

print("snaps file ",file_name)
formatter=logging.Formatter('%(asctime)s:%(filename)s:%(message)s')
file_handler = logging.FileHandler(f'./logs/{file_name}')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class Capture_Snapshots:
    
    def __init__(self,input_path,output_path,per_sec_frame_flag=True):
        self.input_path=input_path
        self.generate_output_path(output_path)
        self.output_path=output_path
        completed_video_path=input_path.replace('videos','completed_videos')
        self.generate_output_path(completed_video_path)
        self.completed_video_path=completed_video_path
        
        self.common_video_snap_name='video'
        self.output_shape1=640   #output dimensions first size
        self.output_shape2=480  #output dimensions second size
        self.no_of_frames_per_sec=3
        '''If it desired to capture atleast one frame sec then this flag is true else if desired to capture a frame for 5sec set False'''
        self.capture_frames_every_sec=per_sec_frame_flag
        self._video_dict = {}
        self.sec_to_drop=2

    def generate_output_path(self,path):
        try:
            if not os.path.exists(path):
                os.makedirs(path) 
        except Exception as e:
            logger.info(e)
        return path
     
        
    '''captures consecutive frames from the mili seconds 1,2,3 & 31 32 33'''
    def capture_consecutive_frames_in_a_sec(self,url,video_name):
        video = cv2.VideoCapture(self.input_path+url) 
        frame_rate=video.get(5) #captures the frame rate
        
        while (video.isOpened()):
            frame_id=video.get(1) # captures the current frame id
            return_value, current_frame = video.read()
            
            #if video is over exit
            if(return_value != True):
                break
            
            if (frame_id % math.floor(frame_rate) < self.no_of_frames_per_sec):
                file_name=f'{self.output_path}{video_name}_{int(frame_id)}.jpg'
                resized_image = cv2.resize(current_frame, (self.output_shape1, self.output_shape2))
                cv2.imwrite(file_name,resized_image)
        video.release()
        
    def capture_all_frames(self,video_name,inp_path,out_path):
        video = cv2.VideoCapture(inp_path+video_name) 
        frame_rate=video.get(5) #captures the frame rate
        video = cv2.VideoCapture(inp_path+video_name) 
        video_name=video_name.split('.')[0]
        
        while (video.isOpened()):
            frame_id=video.get(1) # captures the current frame id
            return_value, current_frame = video.read()
            
            #if video is over exit
            if(return_value != True):
                break
            file_name=f'{out_path}{video_name}_{int(frame_id)}.jpg'
            resized_image = cv2.resize(current_frame, (self.output_shape1, self.output_shape2))
            cv2.imwrite(file_name,resized_image)
        
        video.release()
    
    def get_vid_length(self,url):
        video = cv2.VideoCapture(self.input_path+url) 
        
        '''Setting video length feature on'''
        video.set(cv2.CAP_PROP_POS_AVI_RATIO,1)
        '''extract vido length in seconds'''
        video_length=video.get(cv2.CAP_PROP_POS_MSEC)/1000
        return video_length
    
    '''Returns the list fo frames numbers to be captured ************** RESTRICTED TO THREE FRAMES PER SECOND CURRENTLY '''
    def frame_numbers_to_be_captured(self,vid_length,frame_rate):
        frames_to_be_captured=[]
        low_frame_range=0
        high_frame_range=0
        counter=0
        
        for i in range(int(vid_length)):
            if counter<self.sec_to_drop:
                low_frame_range=high_frame_range+1
                high_frame_range=high_frame_range+int(frame_rate)
                counter+=1
                continue
            else:
                counter+=1
                low_frame_range=high_frame_range+1
                high_frame_range=high_frame_range+int(frame_rate)
                counter+=1
                no1, no2, no3 = random.sample(range(low_frame_range, high_frame_range), self.no_of_frames_per_sec)
                frames_to_be_captured.append(no1)
                frames_to_be_captured.append(no2)
                frames_to_be_captured.append(no3)
        return frames_to_be_captured
    
    def frame_numbers_to_be_captured_one_frame_five_sec(self,vid_length,frame_rate,no_of_frames_per_sec):
        frames_to_be_captured=[]
        low_frame_range=0
        high_frame_range=0
        
        for i in range(int(vid_length/no_of_frames_per_sec)):
            low_frame_range=high_frame_range+1
            high_frame_range=high_frame_range+ (int(frame_rate)*no_of_frames_per_sec)
            no1= random.sample(range(low_frame_range, high_frame_range), 1)
            frames_to_be_captured.append(no1[0])
            
        return frames_to_be_captured
    
    def capture_snaps_of_video(self, url, video_number):
        self._video_dict[video_number] = url
        video = cv2.VideoCapture(self.input_path+url) 
        frame_rate=video.get(5) #captures the frame rate
        '''Setting video length feature on'''
        video.set(cv2.CAP_PROP_POS_AVI_RATIO,1)
        '''extract vido length in seconds'''
        video_length=video.get(cv2.CAP_PROP_POS_MSEC)/1000
        
        
        
        if self.capture_frames_every_sec:
            '''captures any number of frames per second --- Original'''
            frames_to_be_captured=self.frame_numbers_to_be_captured(video_length,frame_rate)
        else:
            '''captures 1 frame per 3 seconds'''
            frames_to_be_captured=self.frame_numbers_to_be_captured_one_frame_five_sec(video_length,frame_rate,3)
            
        
        ### Following logic is generate the random number to prepend
        random_number=[]
        for i in range(0,len(frames_to_be_captured)):
            random_number.append(i)
        
        random.shuffle(random_number)
        ran_count=0
        ############################################################
        #Have to reopen the video since it is already been parsed for the preprocessing above
        video = cv2.VideoCapture(self.input_path+url) 
        new_url=url[:-4]
        new_output_path=f'{self.output_path}{new_url}/'
        self.generate_output_path(new_output_path)
        
        while (video.isOpened()):
            frame_id=int(video.get(1)) # captures the current frame id
            return_value, current_frame = video.read()
            #if video is over exit
            if(return_value != True):
                break
            
            if (frame_id in frames_to_be_captured):
                file_name= f'{new_output_path}{video_number:04}_{int(frame_id)}.jpg'
                resized_image = cv2.resize(current_frame, (self.output_shape1, self.output_shape2))
                cv2.imwrite(file_name,resized_image)
                ran_count+=1
        video.release()
    
    
    def capture_snaps_all_videos(self):
        all_videos=[]
        list_of_all_files = os.listdir(self.input_path)  
        pattern = "*.mp4"
        for file in list_of_all_files:  
            if fnmatch.fnmatch(file, pattern):
                all_videos.append(file)
        
        ### Following logic is generate the random number to prepend
        random_number=[]
        for i in range(0,len(list_of_all_files)):
            random_number.append(i)
        
        random.shuffle(random_number)
        ran_count=0
        ############################################################
        
        for counter,video_url in enumerate(all_videos,start=1):
            logger.info("Processing video number : {} \n video name : {}".format(counter,video_url))
            self.capture_snaps_of_video(video_url, counter)
            
            ##Move video to completed folder after capturing all the frames
            shutil.move(self.input_path+video_url,self.completed_video_path+video_url)
            ran_count+=1

        with open('resources/video_dict.json', 'w') as f:
            import json
            d = json.dumps(self._video_dict)
            f.write(d)
    
    @staticmethod
    def main():
        ##Capture_Snapshots classes takes as input input path and output path and per_sec_frame_flag       
        '''per_sec_frame_flag : If it desired to capture atleast one frame sec then this flag is true else if desired to capture a frame for 5sec set False'''
        base_url=os.path.dirname(os.path.realpath(__file__)).replace("\\","/")
        base_data_url = f'{base_url}/data'
        
        _capture_snapshots=Capture_Snapshots(input_path=base_data_url + '/videos/',output_path=base_data_url + '/snapshots/',per_sec_frame_flag=True)
        _capture_snapshots.capture_snaps_all_videos()       



if __name__ == '__main__':
    Capture_Snapshots.main()