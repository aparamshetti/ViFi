# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 20:07:09 2019

@author: Sayed Inamdar
"""
import os
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import fnmatch
from CaptureSnaps import Capture_Snapshots
import random

class TestClass:
    
    def __init__(self,cropped_vid_len,inp_path,out_path,snap_out_path):
        self.cropped_vid_len=cropped_vid_len
        self.input_path=inp_path
        self.output_path=out_path
        self.file_name_appended="_sliced.mp4"
        self.test_snap_out_path=snap_out_path
    
    def slice_video(self,video_name,vid_length,start_time):
        end_time=vid_length

        if vid_length <= self.cropped_vid_len:
            end_time=vid_length
        else:
            end_time=start_time+self.cropped_vid_len

        print(f'Start time {start_time}')
        print(f'End time {end_time}')
        #check if video length is 
        output_file_name=video_name.split('.')
        ffmpeg_extract_subclip (self.input_path+video_name, start_time, end_time, targetname=self.output_path+output_file_name[0]+self.file_name_appended)
    
    def get_random_start_time(self,vid_length):
        start_time=0
        if vid_length<self.cropped_vid_len:
            start_time=0
            
        else:
            start_time=random.randint(0,int(vid_length-self.cropped_vid_len))
        return start_time
            
    
    def slice_all_video(self,video_list):
        # Instatiating CaptureSnaps
        _capture_snapshots=Capture_Snapshots(per_sec_frame_flag=False,input_path=self.input_path,output_path=self.output_path)
        
        for video_url in video_list:
            print("\nProcessing video : {}".format(video_url))
            vid_len=_capture_snapshots.get_vid_length(video_url)
            start_time=self.get_random_start_time(vid_len)
            self.slice_video(video_url,vid_len,start_time)
            
            ##create a new folder for the video snaps and put all snaps inside that
            vid_name=video_url.split('.')
            new_snap_out_path=self.test_snap_out_path+vid_name[0]+'/'
            if not os.path.exists(new_snap_out_path):
                os.makedirs(new_snap_out_path)
            
            _capture_snapshots.capture_all_frames(vid_name[0]+self.file_name_appended,inp_path=self.output_path, out_path=new_snap_out_path)
    
    ##This method generates a list of videos to be tested for 
    def random_videos_for_testing(self,test_size):
        list_of_all_files = os.listdir(self.input_path)
        all_videos=[]
        pattern = "*.mp4"
        
        for file in list_of_all_files:  
            if fnmatch.fnmatch(file, pattern):
                all_videos.append(file)
                
        picked_videos_numbers=[]
        
        if test_size > len(all_videos):
            test_size=len(all_videos)
        
        while len(picked_videos_numbers) <= test_size:
            num=random.randint(0,len(all_videos))
            if num not in picked_videos_numbers:
                picked_videos_numbers.append(num)
        
        picked_videos=[ all_videos[vid_num] for vid_num in picked_videos_numbers ]
        return picked_videos

if __name__ =="__name__":
    _testing_obj=TestClass(cropped_vid_len=10,inp_path='D:/youtube/already snapped_videos/',out_path='D:/youtube/sliced/',snap_out_path='D:/youtube/test_snaps/')
    testing_vids=_testing_obj.random_videos_for_testing(10)
    _testing_obj.slice_all_video(testing_vids)
