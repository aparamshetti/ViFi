# ViFi - All you need is 10, doesn’t matter where and when!


The project structure is as follows:
ViFi/
|--- CaptureSnaps.py
|--- ClientService.py
|--- Flask_VIFI.py
|--- IndexBuilder.py
|--- Main.py
|--- README.md
|--- SearchService.py
|--- StartSearchService.py
|--- TestClass.py
|--- VectorTransformation.py
|--- YoutubeDownloader.py
|--- model.h5
|--- logs
|--- master
|--- data
|   |--- completed_videos
|   |--- sliced_video_snapshots
|   |--- sliced_videos_testing
|   |--- snapshots
|   |--- test_answers
|   |--- videos
|--- resources
   |--- dictionaries
   |--- PlaylistList.py
   |--- image_videos.txt
   |--- matrix.pkl
   |--- test_results.csv
   |--- urls.json
   |--- vector.pkl
   |--- video_dict.json

The Main.py files generates the datasets by crawling Youtube for all the Playlists placed under resources/PlayList.py. The Main.py then builds the Index using the IndexBuilder which makes use of the resources/matrix.pkl and resources/vector.pkl files to generate the fingerprint.

The data/ contains all the downloaded videos under videos/ once all the snapshots are captures from the videos the videos videos for which the snapshots are captured are then moved to the completed_videos folder. Snapshot/ folder contains all the snapshots for all the videos.The sliced_video_testing is generated during testing the application which will then pick random videos(number configurable in code) from the completed_videos/ folder randomly slice any random 10 seconds(configurable in code) portion of the video and generate the testing snapshots under sliced_videos_testing/. All the predictions are then placed under test_answers/


The model.h5 is the trained model for the image to a vector conversion. The Indexer is placed under /resources/dictionaries/ after its built. the resources/urls.json contains all the youtube video urls's for all the indexed videos. 

The logs/ folder contains all the logs for the entire application.


