import cv2
import math
import os
import fnmatch
import random

class Capture_Snapshots:
    
    def __init__(self,per_sec_frame_flag=True,input_path='D:/youtube/',output_path='D:/youtube/Snapshot_1_3sec/'):
        self.input_path=input_path
        self.output_path=output_path
        self.common_video_snap_name='video'
        self.output_shape1=640   #output dimensions first size
        self.output_shape2=480  #output dimensions second size
        self.no_of_frames_per_sec=3
        '''If it desired to capture atleast one frame sec then this flag is true else if desired to capture a frame for 5sec set False'''
        self.capture_frames_every_sec=per_sec_frame_flag 
     
        
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
    
    '''Returns the list fo frames numbers to be captured ************** RESTRICTED TO THREE FRAMES PER SECOND CURRENTLY '''
    def frame_numbers_to_be_captured(self,vid_length,frame_rate):
        frames_to_be_captured=[]
        low_frame_range=0
        high_frame_range=0
        
        for i in range(int(vid_length)):
            low_frame_range=high_frame_range+1
            high_frame_range=high_frame_range+int(frame_rate)
            no1, no2, no3 = random.sample(range(low_frame_range, high_frame_range), self.no_of_frames_per_sec)
            frames_to_be_captured.append(no1[0])
            frames_to_be_captured.append(no2[0])
            frames_to_be_captured.append(no3[0])
        
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
    
    def capture_snaps_of_video(self,url,video_name):
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
            
        
        ### Following logic is generate the ranbdom number to prepend
        random_number=[]
        for i in range(1,len(frames_to_be_captured)):
            random_number.append(i)
        
        random.shuffle(random_number)
        ran_count=0
        ############################################################
            
        
        #Have to reopen the video since it is already been parsed for the preprocessing above
        video = cv2.VideoCapture(self.input_path+url) 
        while (video.isOpened()):
            frame_id=int(video.get(1)) # captures the current frame id
            return_value, current_frame = video.read()
            #if video is over exit
            if(return_value != True):
                break
            
            if (frame_id in frames_to_be_captured):
                file_name=f'{self.output_path}{random_number[ran_count]}{video_name}_{int(frame_id)}.jpg'
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
        
        ### Following logic is generate the ranbdom number to prepend
        random_number=[]
        for i in range(1,len(list_of_all_files)):
            random_number.append(i)
        
        random.shuffle(random_number)
        ran_count=0
        ############################################################
        
        for counter,video_url in enumerate(all_videos,start=1):
            print("Processing video number : {} \n video name : {}".format(counter,video_url))
            self.capture_snaps_of_video(video_url, f'{random_number[ran_count]}_{self.common_video_snap_name}_{counter}')
            ran_count+=1

if __name__ == '__main__':
    ##Capture_Snapshots classes takes as input input path and output path and per_sec_frame_flag       
    '''per_sec_frame_flag : If it desired to capture atleast one frame sec then this flag is true else if desired to capture a frame for 5sec set False'''
    _capture_snapshots=Capture_Snapshots(per_sec_frame_flag=False)
    _capture_snapshots.capture_snaps_all_videos()       
            