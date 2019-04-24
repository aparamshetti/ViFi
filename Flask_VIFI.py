# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 17:27:16 2019

@author: Sayed Inamdar
"""

from flask import Flask
from flask import render_template
from flask import request
import os
from shutil import copyfile
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api
import pandas as pd

from TestClass import TestClass

base_path='D:/Workspaces/New_vifi/ViFi/'
input_path=base_path+'data/videos'
output_path=base_path+'data/completed_videos'


base_url='.'
base_data_url = f'{base_url}/data'
testing_set_size=1

_testing_obj=TestClass(inp_path=base_data_url+'/completed_videos/',
                       out_path=base_data_url+'/sliced_videos_testing/',
                       snap_out_path=base_data_url+'/sliced_video_snapshots/')

app= Flask(__name__)
api = Api(app)
CORS(app)

@app.route('/')
def get():
    return 'Vifi Flask Home Page'

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        #f = request.files['the_file']
        dc=request.files.to_dict(flat=False)
        dci=dc.get('image')
        dci=dci[0]
        a=str(dci).strip()
        file_name=a.replace("<FileStorage:","").replace("('video/mp4')>","").replace("'","").strip()
        print("file_name is : ",file_name)
        move_files(file_name,input_path,output_path)
        
        print ('Received file')
        return '<h1> POST Method <h1>'
    else:
        print("Get method")
        return '<h1> Get Method <h1>'


def move_files(file_name,input_path,output_path):
    list_dir=os.listdir(input_path)
    print("File_name in move files is ", file_name)
    
    if file_name in list_dir:
        try:
            copyfile(input_path+'/'+file_name,output_path+'/'+file_name)
            print("Copied file")
        except:
            print(f"Couldn't find the file {input_path+'/'+file_name} and \n out : {output_path+'/'+file_name}")
    run_test(file_name)
    
    
def run_test(file_name):
    _testing_obj.build_test_set()
    #This method is called to fix the naming convention between the url dict and the names in snapshots
    #TestClass.update_url_dict()
    print("running the test ....")
    df=_testing_obj.test_videos(1)
    #_testing_obj.launch_video(df)
    file_path=base_data_url+'/'+'test_answers/'+file_name.replace('.mp4','.csv')
    print("Opening the new frame ", file_path)
    with open(file_path,'r') as f:
        out_frame=pd.read_csv(f)
    print("Output frame is ",out_frame)
          
def post_results(file_name):
    print("Posting the Results ")
    file_path=base_data_url+'/'+'test_answers/'+file_name.replace('.mp4','.csv')
    with open(file_path,'r') as f:
        out_frame=pd.read_csv(f)    

if __name__ == '__main__':
    
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(port=5000)
    
    
