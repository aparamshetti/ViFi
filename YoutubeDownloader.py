# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 20:38:59 2019

@author: Sayed Inamdar
"""

from pytube import YouTube,Playlist
import os
from resources.PlaylistList import PlaylistList
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


class YoutubeDownloader:
    
    def __init__(self,output_path,threshold=400):
        self.threshold=threshold
        self.max_vid_length=1200 #in seconds ; 20 mins 
        self.generate_video_output_path(output_path)
        output_path_name=output_path
        self.output_path=self.generate_video_output_path(output_path_name)
        print(self.output_path)
        
    def generate_video_output_path(self,path):
        try:
            if not os.path.exists(path):
                os.makedirs(path) 
        except Exception as e:
            logger.error(e)
        return path
        
    def download_single_video(self,url):
        try:
            video = YouTube(url)
            if 'lyric' in video.title.lower() or 'mashup' in video.title.lower() or 'audio' in video.title.lower():
                logger.warning(f"Ignored because its a lyrical video : {video.title}")
                return
            if int(video.length) > self.max_vid_length:
                logger.warning(f'Ignored because video is too long, name: {video.title}')
                return
            stream = video.streams.filter(file_extension = "mp4",adaptive=True)
            stream.first().download(self.output_path)
        except Exception as e:
            logger.error(f'Could not downlaod video failed with exception : {e}')
            
    def download_playlist_video(self,url):
        pl=Playlist(url)
        pl.download_all(self.output_path)
        
    def download_playlist_videos_best_quality(self,url):
        pl=Playlist(url).parse_links()
        counter=0
        for song in pl:
            if counter>self.threshold:
                break
            counter+=1
            self.download_single_video(url+song)
    
    def download_audio(self,url):
        song = YouTube(url)
        song.streams.filter(only_audio=True).first().download(self.output_path)
    
    def download_audio_playlist(self,url):
        pl=Playlist(url).parse_links()
        for song in pl:
            self.download_audio(url+song)

    @staticmethod
    def main():
        base_url=os.path.dirname(os.path.realpath(__file__)).replace("\\","/")
        base_data_url = f'{base_url}/data'
        
        #Get list of playlists
        list_of_playlists=PlaylistList.get_playslists()
        logger.info(f"Downloading the folowing playlists {list_of_playlists}")
        for key,value in list_of_playlists.items():
            logger.info(f"Downloading Playlist : {key}")
            _youtube_downloader=YoutubeDownloader(output_path=base_data_url + '/videos/')
            _youtube_downloader.download_playlist_videos_best_quality(value)
        


if __name__=='__main__':
    YoutubeDownloader.main()
    

        
    
            
