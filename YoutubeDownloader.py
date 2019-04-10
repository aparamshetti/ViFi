# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 20:38:59 2019

@author: Sayed Inamdar
"""

from pytube import YouTube,Playlist

class YoutubeDownloader:
    
    def __init__(self,output_path='D:/youtube',threshold=400):
        self.output_path=output_path
        self.threshold=threshold
        self.max_vid_length=1200 #in seconds ; 20 mins 
        
    def download_single_video(self,url):
        try:
            video = YouTube(url)
            if 'lyric' in video.title.lower() or 'mashup' in video.title.lower():
                print("Ignored because its a lyrical video")
                return
            if int(video.length) > self.max_vid_length:
                print(f'Ignored because video is too long, name: {video.title}')
                return
            stream = video.streams.filter(file_extension = "mp4",adaptive=True)
            stream.first().download(self.output_path)
        except Exception as e:
            print(f'Could not downlaod {e}')
            
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
            print(f"Downloading song no {counter}")
            self.download_single_video(url+song)
    
    def download_audio(self,url):
        song = YouTube(url)
        song.streams.filter(only_audio=True).first().download(self.output_path)
    
    def download_audio_playlist(self,url):
        pl=Playlist(url).parse_links()
        for song in pl:
            self.download_audio(url+song)

if __name__=='__main__':
    #playlist_url='https://www.youtube.com/playlist?list=PLaFIwKHa3kMNGfT4thny073B9OrbD1evG'
    #playlist_url_bolly='https://www.youtube.com/playlist?list=PLvczmdAAtKHtY2Cz_Gd8n4Ry9dO7DtgTv' #2000-2005 bollywood   
    #playlist_url_taylor='https://www.youtube.com/playlist?list=PL1CbxROoA2JiVzg9zu_AkVHZR9S8mHhzh' #taylor swift
    #playlist_url='https://www.youtube.com/playlist?list=PLNaDy1xRJz8U6FCnP5LZpSgrSGA5lxbJu' #enrique
    #playlist_url='https://www.youtube.com/playlist?list=PLMRKdK25AuPVXH-65dQHkajrQIL_UMJxr'  #Ranbir 
    #playlist_url_bruno='https://www.youtube.com/playlist?list=PLDIoUOhQQPlUAdKrN4Z3FpWujWpuKk-sh'  #bruno mars
    #playlist_url_atif='https://www.youtube.com/playlist?list=PLotMWWn7H-dnMLAU3kQesxzzSL8iVzqYT' #atif aslam
    #playlist_url_ed='https://www.youtube.com/playlist?list=PLaq655wqcKDnUvTOizhqwNCiiF_grL1vh' #ed sheeran
    playlist_url_one_direction='https://www.youtube.com/playlist?list=PLxdmSpdkY-5LG9ZYDrX3qQq_iqsjfJhx9'
    
    _youtube_downloader=YoutubeDownloader()
    _youtube_downloader.download_playlist_videos_best_quality(playlist_url_one_direction)
        
