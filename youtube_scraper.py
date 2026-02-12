from googleapiclient.discovery import build
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime
import time
from html import unescape

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv('YOUTUBE_API_KEY')

# Build YouTube client - FIXED
youtube = build('youtube', 'v3', developerKey='AIzaSyAiJcxcfPpv7eZjsNlGS_57hlLe_vbtoCE')

def extract_video_id(url):
    """
    Extract video ID from YouTube URL
    """
    if 'youtube.com/watch?v=' in url:
        return url.split('watch?v=')[1].split('&')[0]
    elif 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0]
    else:
        return url

def get_video_info(video_id):
    """Get video title, channel, stats"""
    try:
        request = youtube.videos().list(
            part='snippet,statistics',
            id=video_id
        )
        response = request.execute()
        
        if response['items']:
            video = response['items'][0]
            snippet = video['snippet']
            stats = video['statistics']
            
            return {
                'video_id': video_id,
                'title': snippet['title'],
                'channel': snippet['channelTitle'],
                'published_at': snippet['publishedAt'],
                'view_count': stats.get('viewCount', 0),
                'like_count': stats.get('likeCount', 0),
                'comment_count': stats.get('commentCount', 0)
            }
    except Exception as e:
        print(f"Error getting video info: {e}")
        return None

def get_video_comments(video_id, max_comments=500):
    """
    Collect comments from a YouTube video
    """
    print(f"\n🎬 Fetching comments from video ID: {video_id}")
    
    comments_data = []
    
    try:
        request = youtube.commentThreads().list(
            part='snippet,replies',
            videoId=video_id,
            maxResults=100,
            order='relevance',
            textFormat='plainText'
        )
        
        response = request.execute()
        page_count = 1
        
        while response and len(comments_data) < max_comments:
            print(f"  📄 Processing page {page_count}... ({len(comments_data)} comments so far)")
            
            for item in response['items']:
                # Top-level comment
                comment = item['snippet']['topLevelComment']['snippet']
                text = unescape(comment['textDisplay'])
                
                comments_data.append({
                    'comment_id': item['id'],
                    'video_id': video_id,
                    'author': comment['authorDisplayName'],
                    'text': text,
                    'like_count': comment['likeCount'],
                    'published_at': comment['publishedAt'],
                    'reply_count': item['snippet']['totalReplyCount'],
                    'is_reply': False
                })
                
                # Get replies
                if 'replies' in item:
                    for reply in item['replies']['comments']:
                        reply_snippet = reply['snippet']
                        reply_text = unescape(reply_snippet['textDisplay'])
                        
                        comments_data.append({
                            'comment_id': reply['id'],
                            'video_id': video_id,
                            'author': reply_snippet['authorDisplayName'],
                            'text': reply_text,
                            'like_count': reply_snippet['likeCount'],
                            'published_at': reply_snippet['publishedAt'],
                            'reply_count': 0,
                            'is_reply': True
                        })
            
            # Get next page
            if 'nextPageToken' in response and len(comments_data) < max_comments:
                request = youtube.commentThreads().list(
                    part='snippet,replies',
                    videoId=video_id,
                    pageToken=response['nextPageToken'],
                    maxResults=100,
                    order='relevance',
                    textFormat='plainText'
                )
                response = request.execute()
                page_count += 1
                time.sleep(0.5)
            else:
                break
        
        print(f"  ✅ Successfully collected {len(comments_data)} comments!")
        return comments_data
        
    except Exception as e:
        if 'commentsDisabled' in str(e):
            print("  ❌ Comments are disabled for this video")
        elif 'quotaExceeded' in str(e):
            print("  ❌ API quota exceeded. Try again tomorrow.")
        else:
            print(f"  ❌ Error: {e}")
        return []

def save_data(comments_data, video_info):
    """Save collected data to CSV files"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save comments
    if comments_data:
        df_comments = pd.DataFrame(comments_data)
        comments_file = f'youtube_comments_{timestamp}.csv'
        df_comments.to_csv(comments_file, index=False, encoding='utf-8')
        print(f"\n💾 Comments saved to: {comments_file}")
        
        print(f"\n📊 Preview of collected data:")
        print(df_comments[['author', 'text', 'like_count']].head(10))
        print(f"\n📈 Statistics:")
        print(f"   Total comments: {len(df_comments)}")
        print(f"   Top-level comments: {len(df_comments[df_comments['is_reply'] == False])}")
        print(f"   Replies: {len(df_comments[df_comments['is_reply'] == True])}")
        print(f"   Average likes per comment: {df_comments['like_count'].mean():.2f}")
    
    # Save video info
    if video_info:
        df_video = pd.DataFrame([video_info])
        video_file = f'video_info_{timestamp}.csv'
        df_video.to_csv(video_file, index=False, encoding='utf-8')
        print(f"\n💾 Video info saved to: {video_file}")
        
        print(f"\n🎥 Video Details:")
        print(f"   Title: {video_info['title']}")
        print(f"   Channel: {video_info['channel']}")
        print(f"   Views: {int (video_info['view_count']):,}")
        print(f"   Likes: {int (video_info[ 'like_count']):,}")
        print(f"   Total comments: {int (video_info['comment_count']):,}")

def main():
    """Main function"""
    print("=" * 60)
    print("🎯 YouTube Comment Scraper for Sentiment Analysis")
    print("=" * 60)
    
    print("\nEnter the YouTube video URL or video ID:")
    print("Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    video_input = input("\n👉 Video URL/ID: ").strip()
    
    if not video_input:
        print("❌ No URL provided. Exiting.")
        return
    
    video_id = extract_video_id(video_input)
    print(f"\n✅ Video ID: {video_id}")
    
    print("\n📺 Fetching video information...")
    video_info = get_video_info(video_id)
    
    if not video_info:
        print("❌ Could not fetch video info. Check your video ID.")
        return
    
    print(f"\nHow many comments do you want to collect?")
    print(f"(Video has {video_info['comment_count']} total comments)")
    
    max_comments_input = input("👉 Number of comments (default 500): ").strip()
    max_comments = int(max_comments_input) if max_comments_input else 500
    
    comments = get_video_comments(video_id, max_comments=max_comments)
    
    if not comments:
        print("\n❌ No comments collected. Exiting.")
        return
    
    save_data(comments, video_info)
    
    print("\n" + "=" * 60)
    print("✅ Data collection complete!")
    print("=" * 60)
    print("\n📌 Next steps:")
    print("   1. Open the CSV file to see your data")
    print("   2. Start cleaning and preprocessing")
    print("   3. Run sentiment analysis")

if __name__ == "__main__":
    main()