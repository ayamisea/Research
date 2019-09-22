import argparse
import pandas as pd
import os
import numpy as np

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

DEVELOPER_KEY = 'AIzaSyATcidzxnjLni8Pg00iOBAfoRkREqxo91o'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
developerKey=DEVELOPER_KEY)

def youtube_search(options):    
    search_response = youtube.search().list(
    q=options.q,
    part='id,snippet',
    maxResults=options.max_results,
    type=options.type
    ).execute()

    return search_response

def video_comment(vID,commentNum):
    comment_response = youtube.commentThreads().list(
    part="snippet",
    maxResults=commentNum,
    order="relevance", #relevance or time
    videoId=vID
    ).execute()
    
    vid_comments = pd.DataFrame()
    for comment_result in comment_response.get('items', []):
        data = {'id':vID,
                'text':comment_result['snippet']['topLevelComment']['snippet']['textOriginal'],
                'likeCount':comment_result['snippet']['topLevelComment']['snippet'].get('likeCount',np.nan)
                }

        vid_comments = vid_comments.append(data,ignore_index = True)
    
    return vid_comments
    
def video_statistics(vID):
    stat_response = youtube.videos().list(
        part="statistics",
        id=vID
    ).execute()
    
    return stat_response.get('items', ['statistics'])[0]['statistics']   

def search_info(args):
    videos = pd.DataFrame()
    comments = pd.DataFrame()

    search_response = youtube_search(args)
    
    # Video
    for search_result in search_response.get('items', []):
        vID = search_result['id']['videoId']
        
        # Get video comments
        cmt_num = args.comment_count
        comment = video_comment(vID,cmt_num)
        comments = comments.append([comment])
        
        comments = comments.reset_index(drop=True)
        
        # Get Video Statistics
        stat_response = video_statistics(vID)
        
        data = {'id': vID,
                'title': search_result['snippet']['title'],
                'published_date':search_result['snippet']['publishedAt'],
                'viewCount':stat_response.get('viewCount',np.nan),
                'likeCount':stat_response.get('likeCount',np.nan),
                'dislikeCount':stat_response.get('dislikeCount',np.nan),
                'commentCount':stat_response.get('commentCount',np.nan)
                }
        
        videos = videos.append(data,ignore_index=True)
            
    return videos ,comments

def getMostPopularVideo(args):
    popular_response = youtube.videos().list(
        part="snippet,statistics",
        chart="mostPopular",
        maxResults=args.max_results,
        regionCode=args.region_code
    ).execute()

    popularVideo = pd.DataFrame()
    for item in popular_response.get('items', []):
        data = {
                'id':item['id'],
                'title':item['snippet'].get('title',np.nan),
                'publishedAt':item['snippet'].get('publishedAt',np.nan),
                'categoryId':item['snippet'].get('categoryId',np.nan),
                'tags':item['snippet'].get('tags',np.nan),
                'viewCount':item['statistics'].get('viewCount',np.nan),
                'likeCount': item['statistics'].get('likeCount',np.nan),
                'dislikeCount': item['statistics'].get('dislikeCount',np.nan),
                'commentCount': item['statistics'].get('commentCount',np.nan)
                }
        
        popularVideo = popularVideo.append(data,ignore_index = True)
    return popularVideo

if __name__ == '__main__':
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    
    parserS = argparse.ArgumentParser()
    parserS.add_argument('--q', default='說好不哭')
    parserS.add_argument('--type', default='video')
    parserS.add_argument('--max_results', default=25)
    parserS.add_argument('--comment_count', default=5)
    Sargs = parserS.parse_args()
    
    parserP = argparse.ArgumentParser()
    parserP.add_argument('--region_code', default='TW')
    parserP.add_argument('--max_results', default=50)
    Pargs = parserP.parse_args()
    
    try:        
        #videos ,comments = search_info(Sargs)
        popularVideo = getMostPopularVideo(Pargs)
        
    except HttpError as e:
        print ('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
    