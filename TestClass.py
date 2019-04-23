# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 20:07:09 2019

@author: Sayed Inamdar
"""
import os
import re
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import fnmatch
from CaptureSnaps import CaptureSnapshots
import random
import pandas as pd
import json
from IndexBuilder import IndexBuilder
from ClientService import ClientService
import logging
import numpy as np
import math
import webbrowser

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
    def __init__(self,inp_path,out_path,snap_out_path,use_server = False,cropped_vid_len=10):
        # checking if the inp and output paths are present if not create them
        self.generate_output_path(inp_path)
        self.generate_output_path(out_path)
        self.generate_output_path(snap_out_path)
        
        ##Input and out paths
        self.input_path=inp_path
        self.output_path=out_path
        self.test_snap_out_path=snap_out_path
        self.file_name_appended="_sliced.mp4"
        self.cropped_vid_len=cropped_vid_len
        self.index_path = 'resources/dictionaries/'
        self.video_dict_path = 'resources'
        self.chrome_path='C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'

        if not use_server:
            self._master, self._video_dict = self.load_master_dict()
    
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
        ffmpeg_extract_subclip (self.input_path+video_name, start_time, end_time,
                                targetname=self.output_path + ''.join(output_file_name[:-1]) + self.file_name_appended)
    
    def get_random_start_time(self,vid_length):
        start_time=0
        if vid_length<self.cropped_vid_len:
            start_time=0
            
        else:
            start_time=random.randint(0,int(vid_length-self.cropped_vid_len))
        return start_time
            
    
    def slice_all_video(self,video_list):
        # Instatiating CaptureSnaps
        _capture_snapshots=CaptureSnapshots(per_sec_frame_flag=False, input_path=self.input_path, output_path=self.output_path)
        
        for video_url in video_list:
            logger.info("\nProcessing video : {}".format(video_url))
            vid_len=_capture_snapshots.get_vid_length(video_url)
            start_time=self.get_random_start_time(vid_len)
            self.slice_video(video_url,vid_len,start_time)
            
            ##create a new folder for the video snaps and put all snaps inside that
            vid_name=video_url.split('.')
            new_snap_out_path=self.test_snap_out_path + ''.join(vid_name[:-1]) + '/'
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
    def process_testing_snaps(self, input_path, url, num_servers):
        dirs = [os.path.join(input_path, f) for f in os.listdir(input_path)
                if os.path.isdir(os.path.join(input_path, f))]

        index_builder = IndexBuilder('model.h5', input_path, 'resources')

        data_frame = pd.DataFrame(columns=['actual', 'precision', 'recall', 'is_first'])

        '''store all fingerprints and vectors as tuples in a list '''
        for dir in dirs:
            actual = os.path.split(dir)[-1]
            print(actual)
            df = self._run(index_builder, dir, url, num_servers)

            if df is not None:
                df['actual'] = actual

                precision = 1 if df[df['predicted'] == actual]['predicted'].count() > 0 else 0
                recall = precision
                top = df.loc[df['score'].idxmax()]
                is_first = 1 if top['predicted'] == actual else 0

                data_frame = data_frame.append(pd.DataFrame(data=[[actual, precision, recall, is_first]],
                                                            columns=['actual', 'precision', 'recall', 'is_first']))

        return data_frame

    def test_run(self, input_path, url, num_servers, ):
        index_builder = IndexBuilder('model.h5', input_path, 'resources')

        actual = input_path.split()[-1]
        df = self._run(index_builder, input_path, url, num_servers)
        df['actual'] = actual

        return df

    def _run(self, index_builder, filepath, url, num_servers):
        client = ClientService(index_builder, filepath, url, num_servers)
        results = client.run()

        matching_frame_results = []
        for result in list(results):
            if len(result) != 0:
                matching_frame_results.extend(result)

        df = None
        if len(matching_frame_results) > 0:
            df = self.convert_to_df(matching_frame_results)

        return df

    def convert_to_df(self, matching_frame_results):
        df = pd.DataFrame.from_records(matching_frame_results, columns=['video_id', 'similarity'])
        df = df.groupby('video_id').similarity.agg(['sum', 'count']).reset_index()
        df['number_frames'] = len(matching_frame_results)
        df['score'] = df['sum'] / df['number_frames']
        df.sort_values(by='score', ascending=False, inplace=True)

        df['predicted'] = self._video_dict[df['video_id'][0]]

        print(df[['video_id', 'score']].head())
        
        return df

    @staticmethod
    def _cosine_similarity(query, vector):
        return np.dot(query, vector) / (np.sqrt(np.dot(query, query)) * np.sqrt(np.dot(vector, vector)))

    def load_master_dict(self):
        with open(os.path.join(self.index_path, "inverted_index_master.json"), 'r') as f:
            master = json.load(f)
         
        with open(os.path.join(self.video_dict_path, "video_dict.json"), 'r') as f:
            video_dict = json.load(f)
        
        return master, video_dict
    
    def run_local(self):
        test_files = os.listdir(self.test_snap_out_path)
    
        all_results = []
        actuals = []
        
        base_url = 'data'
        index = IndexBuilder('model.h5', base_url + '\snapshots', 'resources')

        pattern = re.compile('.*\.jpg')
        for t in test_files:
            print(t)
            actuals.append(t)
            filepath = os.path.join(self.test_snap_out_path, t)
            images = [os.path.join(filepath, f) for f in os.listdir(filepath)
                      if os.path.isfile(os.path.join(filepath, f)) and pattern.findall(f)]

            results = []
            for img in images:
                fp, query_vec = index.finger_print(img)
                if str(fp) in self._master:
                    vec_list = self._master[str(fp)]
                    for ans_vec in vec_list:
                        c = self._cosine_similarity(query_vec, ans_vec[1])
                        results.append([ans_vec[0].split('_')[0], c])
                
            all_results.append(results)

        for ind, test in enumerate(test_files):
            if len(all_results[ind]) > 0:
                df = pd.DataFrame(all_results[ind], columns=["video_id", "cosine"]).fillna(0)
                df_new = df.groupby("video_id")["cosine"].agg(['mean', 'count']).reset_index()
#<<<<<<< HEAD
                #for i in range(df_new.shape[0]):
                #    df_new.ix[i, "prediction"] = self._video_dict[df_new.ix[i, "video_id"]]
                 #   df_new.ix[i, "score"] = df_new.ix[i, "mean"] * (df_new.ix[i, "count"])
#=======
                
                for i in range(df_new.shape[0]):
                    df_new.ix[i,"prediction"] = self._video_dict[df_new.ix[i,"video_id"]]
                    df_new.ix[i,"score"] = df_new.ix[i,"mean"]*(df_new.ix[i,"count"])
                df_new["Actual"] = test
                df_new.sort_values(by="score",inplace=True,ascending=False)
                df_new.to_csv(os.path.join("data/test_answers",test+".csv"),index=False)

        with open('./resources/urls.json','r') as f:
            url_dict=json.load(f)
        
        final_df = pd.DataFrame(columns=['actual','predicted','precision','recall','accuracy','ndcg','urls'])
        for file in os.listdir("data/test_answers/"):
            if fnmatch.fnmatch(os.path.join('data/test_answers',file), '*.csv'):
                df = pd.read_csv(os.path.join('data/test_answers',file))
                for i in range(min(10,df.shape[0])):
                    if df.ix[i,"prediction"] == df.ix[i,"Actual"]:
                        precision = 1
                        recall = 1
                        try:
                            ndcg = 1/math.log(i+1,2)
                        except:
                            ndcg=-1
                    else:
                        precision = 0
                        recall = 0
                        ndcg = 0
                
                if df.ix[0,"prediction"] == df.ix[0,"Actual"]:
                    accuracy = 1
                else:
                    accuracy = 0                   

            predicted=df.ix[0,"prediction"]
            url=url_dict.get(predicted,None)
            final_df = final_df.append(pd.DataFrame(data=[[df.ix[0,"Actual"],df.ix[0,"prediction"], precision, recall, accuracy,ndcg,url]],
                                                    columns=['actual','predicted', 'precision', 'recall', 'accuracy','ndcg','urls']))
        final_df.to_csv(os.path.join('data/test_answers',"final.csv"),index=False)

        return final_df

#>>>>>>> a20c3f9795444e600ce4d06624c038bd232484dd

                
        # data_frames = []
        #
        # for i, res in enumerate(all_results):
        #     if len(res) > 0:
        #         print(actuals[i])
        #         data_frames.append(self.convert_to_df(res))
        #
        # final_df = pd.DataFrame(columns=['actual', 'precision', 'recall', 'is_first'])
        #
        # '''store all fingerprints and vectors as tuples in a list '''
        # for i, df in enumerate(data_frames):
        #     actual = actuals[i]
        #     df['actual'] = actual
        #     precision = 1 if df[df['predicted'] == actual]['predicted'].count() > 0 else 0
        #     recall = precision
        #     top = df.loc[df['score'].idxmax()]
        #     is_first = 1 if top['predicted'] == actual else 0
        #
        #     final_df = final_df.append(pd.DataFrame(data=[[actual, precision, recall, is_first]],
        #                                             columns=['actual', 'precision', 'recall', 'is_first']))

        # return final_df
    
    def build_test_set(self):
        # print(_testing_obj.test_snap_out_path)
        testing_vids=_testing_obj.random_videos_for_testing(testing_set_size)
        testing_vids=_testing_obj.random_videos_for_testing(testing_set_size)
        self.slice_all_video(testing_vids)
        
    
    def test_videos(self,flag='local'):
        url = 'http://localhost:{0}/search'
        num_servers = 2
        
        if flag.lower()=='server':
            pass
            ##process each testing snaps folder and get the result
            # _testing_obj.process_testing_snap_folders(inp_path=base_data_url+'/sliced_video_snapshots/')
            # df = _testing_obj.test_run(base_data_url + '/sliced_video_snapshots/Labrinth - Jealous/', url, num_servers)
            # df = _testing_obj.test_run(base_data_url + '/sliced_video_snapshots/Luis Fonsi - Despacito ft/', url, num_servers)
    
            # df = _testing_obj.process_testing_snaps(base_data_url + '/sliced_video_snapshots/', url, num_servers)
        else:
            df = _testing_obj.run_local()
            print(df.head())
            df.to_csv('resources/test_results.csv', index=False)
           #df = _testing_obj.process_testing_snaps(base_data_url + '/sliced_video_snapshots/', url, num_servers) 
        return df
    
    def launch_video(self,df,chrome_path=''):
        #url='https://www.youtube.com/watch?v=E817KHhU42Y'
        try:
            url=df.iloc[0]['urls']
            if chrome_path is '':
                chrome_path=self.chrome_path
            webbrowser.get(chrome_path).open(url)
        except:
            print(f'Could Not Launch the vide {Exception}')
            logger.error(f'Exception caugth '+str(Exception))

if __name__ == "__main__":
    #base_url=os.path.dirname(os.path.realpath(__file__)).replace("\\","/")
    base_url='.'
    base_data_url = f'{base_url}/data'
    testing_set_size=100
    
    _testing_obj=TestClass(inp_path=base_data_url+'/completed_videos/',
                           out_path=base_data_url+'/sliced_videos_testing/',
                           snap_out_path=base_data_url+'/sliced_video_snapshots/')
    
    #_testing_obj.build_test_set()
    df=_testing_obj.test_videos()
    _testing_obj.launch_video(df)
