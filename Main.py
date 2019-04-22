# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 20:30:25 2019

@author: Sayed Inamdar
"""
import os
import logging
from YoutubeDownloader import YoutubeDownloader
from CaptureSnaps import CaptureSnapshots
from IndexBuilder import IndexBuilder

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


class Main:
    def __init__(self):
        self.list_of_required_folders=['data','logs','master','resources']
        self.base_path=os.path.dirname(os.path.realpath(__file__)).replace("\\","/")
        
    
    def build_folder_structure(self):
        for folder in self.list_of_required_folders:
            if not os.path.exists(f'{self.base_path}/{folder}') :
                os.mkdir(f'{self.base_path}/{folder}')
                logger.info(f"Creating folder : {folder}")
    
    def generate_dataset(self):
        logger.info('Downloading videos')
        YoutubeDownloader.main()
        logger.info('Capturing Snapshots')
        CaptureSnapshots.main()
    
    
if __name__=='__main__':
    _main=Main()
    _main.build_folder_structure()
    #_main.generate_dataset()
    IndexBuilder.main()
    
