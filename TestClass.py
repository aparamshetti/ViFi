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
import requests
from collections import Counter
from multiprocessing import Process
from IndexBuilder import IndexBuilder
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

formatter=logging.Formatter('%(asctime)s:%(filename)s:%(message)s')
file_handler = logging.FileHandler(f'./logs/{file_name}')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class TestClass:
    '''cropped_vid_len is length of sliced video default is 10'''
    def __init__(self,inp_path,out_path,snap_out_path,cropped_vid_len=10):
        #checking if the inp and output paths are present if not create them
        self.generate_output_path(inp_path)
        self.generate_output_path(out_path)
        self.generate_output_path(snap_out_path)
        
        ##Input and out paths
        self.input_path=inp_path
        self.output_path=out_path
        self.test_snap_out_path=snap_out_path
        self.file_name_appended="_sliced.mp4"
        self.cropped_vid_len=cropped_vid_len
    
    def generate_output_path(self,path):
        try:
            if not os.path.exists(path):
                os.makedirs(path) 
        except Exception as e:
            logger.info(e)
        return path
    
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
            logger.info("\nProcessing video : {}".format(video_url))
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
        
        while len(picked_videos_numbers) < test_size:
            num=random.randint(0,len(all_videos)-1)
            if num not in picked_videos_numbers:
                picked_videos_numbers.append(num)
            
        
        picked_videos=[ all_videos[vid_num] for vid_num in picked_videos_numbers ]
        return picked_videos

    # Processes all the frames and hits the URl to get the Response and returns a list indicating final prediction ranking
    def process_testing_snap_folders(self,inp_path):
        all_predictions=dict()
        #Get only the directories in the input path
        try:
            list_of_all_files = [ name for name in os.listdir(inp_path) if os.path.isdir(os.path.join(inp_path, name)) ]
        except Exception as e:
            logger.info(f'Coulnt find any folders in the path {inp_path}')
            return
        
        for folder in list_of_all_files:
            prediction=self.process_testing_snaps(inp_path+folder+'/')
            all_predictions[folder]=prediction

    # SINGLE PRERDICTION ----Processes all the frames and hits the URl to get the Response and returns a list indicating final prediction ranking
    def single_testing_snap_folder(self,inp_path):
        #Get only the directories in the input path
        try:
            list_of_all_files = [ name for name in os.listdir(inp_path) if os.path.isdir(os.path.join(inp_path, name)) ]
        except Exception as e:
            logger.info(f'Coulnt find any folders in the path {inp_path}')
            return
        
        for folder in list_of_all_files[0]:
            prediction=self.process_testing_snaps(inp_path+folder+'/')
        return prediction
    
    ## Takes inp path and captures the results for the all the frame in a dictionary and returns the Ranking of the videos
    def process_testing_snaps(self,input_path):
        list_of_all_images = os.listdir(input_path)
        fp_vector_dict=dict()
        final_frame_responses=dict()
        
        _index_builder=IndexBuilder()
        _index_builder._load_model()
        
        '''store all fingerprints and vectors as tuples in a list '''
        for image in list_of_all_images:
            ## Capture the frame number from the image, which will be used to create a dictionary of prection for that frame number
            frame_number=image.split('.')[0].split('_')[2]  ## image_name = 'vidname_slice_01.jpg'
            #Call the image vectorize method here passing the image'''
            image_finger_print=_index_builder._finger_print(input_path+image)
            vector=_index_builder._vectorize(input_path+image) 
            fp_vector_dict[frame_number]=(image_finger_print,vector)


        '''Make requests to the server and store the results in the dict'''
        for f_id,values in fp_vector_dict.keys():
            fp=values[0]
            vector=values[1]
            response=self.generate_url_to_hit(fp,vector)
            
            final_frame_responses[f_id]=response ## extract the result from the response based on the format


        '''#### MULTIPROCESSING BACKUP !!!Make requests to the server and store the results in the dict        
        processes=[]
        for f_id,values in fp_vector_dict.keys():
            
            fp=values[0]
            vector=values[1]
            process=Process(target=self.generate_url_to_hit_multiprcoess,args=(fp,vector,f_id,final_frame_responses))
            processes.append(process)
            process.start()
        
        for process in processes:
            process.join() '''
                
        
        '''Calculate the frequencies of the values of the dictionary and return the results'''
        final_prediction=Counter(final_frame_responses.values()).most_common()
        return final_prediction
    
    ### Multiprocessing !!!!!!!This method takes in fingerprint and vector and hits the get request to the server and returns the response        
    def generate_url_to_hit_multiprcoess(self,fingerprint,vector,fr_id,final_frame_responses):
        port_no=8000 #temp
        URL=f'http://localhost:{port_no}/search'
        response = requests.get(url = URL, params={'fp': fingerprint, 'vector': vector})
        final_frame_responses[fr_id]=response ## extract final answer field from response

    
    ### This method takes in fingerprint and vector and hits the get request to the server and returns the response        
    def generate_url_to_hit(self,fingerprint,vector):
        port_no=8000 #temp
        URL=f'http://localhost:{port_no}/search'
        response = requests.get(url = URL, params={'fp': fingerprint, 'vector': vector})
        return response.json()
    
    @staticmethod
    def main():
        #base_url=os.path.dirname(os.path.realpath(__file__)).replace("\\","/")
        base_url='D:/Workspaces/ViFI_IR_Project/ViFi'
        base_data_url = f'{base_url}/data'
        testing_set_size=10
        
        _testing_obj=TestClass(inp_path=base_data_url+'/completed_videos/',
                               out_path=base_data_url+'/sliced_videos_testing/',
                               snap_out_path=base_data_url+'/sliced_video_snapshots/')
        
        testing_vids=_testing_obj.random_videos_for_testing(testing_set_size)
        _testing_obj.slice_all_video(testing_vids)
        
        ##process each testing snaps folder and get the result
        _testing_obj.process_testing_snap_folders(inp_path=base_data_url+'/sliced_video_snapshots/')
        
if __name__ =="__main__":
    TestClass.main()

