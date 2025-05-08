import os
import json
from collections import Counter
from zipfile import ZipFile, BadZipFile


def process_zip_and_save(file_stream, upload_path, user_id):

    try:
        with ZipFile(file_stream) as archive:
            with archive.open('your_instagram_activity/likes/liked_posts.json') as f:
                total_liked_posts = len(json.load(f)['likes_media_likes'])  # Total liked posts

            with archive.open('your_instagram_activity/likes/liked_comments.json') as f:
                total_liked_comments = len(json.load(f)['likes_comment_likes'])  # Total liked comments

            # Access the comments JSON file
            with archive.open('your_instagram_activity/comments/post_comments_1.json') as f:
                posts_comments_data = json.load(f) 
                
                 # Ensure the data is not empty
            if posts_comments_data:
                # Count the number of comments per account
                account_posts_comments_counts = Counter(
                    comment['string_map_data']['Media Owner']['value']
                    for comment in posts_comments_data
                    if 'string_map_data' in comment and 'Media Owner' in comment['string_map_data']
                )

                # Find the account with the most comments
                if account_posts_comments_counts:
                    most_commented_account_for_posts, most_commented_account_count_for_posts = account_posts_comments_counts.most_common(1)[0]
                else:
                    most_commented_account_for_posts = None
                    most_commented_account_count_for_posts = 0

                # Total number of comments
                total_posts_comments = len(posts_comments_data)
            else:
                # Handle case where the data is empty
                most_commented_account_for_posts = None
                most_commented_account_count_for_posts = 0
                total_posts_comments = 0
                        

            with archive.open('your_instagram_activity/comments/reels_comments.json') as f:
                reels_comments_data = json.load(f) # Load the reels comments JSON file
                total_reels_comments = len(reels_comments_data) #Calculate the total number of comments on reels

                # Ensure 'comments_reels_comments' exists in the JSON data
                if 'comments_reels_comments' in reels_comments_data:
                    account_reels_comments_counts = Counter(
                        comment['string_map_data']['Media Owner']['value']
                        for comment in reels_comments_data['comments_reels_comments']
                        if 'string_map_data' in comment and 'Media Owner' in comment['string_map_data'])

                    # Find the account with the most comments
                    if account_reels_comments_counts:
                        most_commented_account_for_reels, most_commented_account_count_for_reels = account_reels_comments_counts.most_common(1)[0]
                    else:
                        most_commented_account_for_reels = None
                        most_commented_account_count_for_reels = 0
                else:
                    # Handle case where 'comments_reels_comments' is missing
                    most_commented_account_for_reels = None
                    most_commented_account_count_for_reels = 0
                    total_reels_comments = 0
               

        # Ensure the upload directory exists, if not create it
        if not os.path.isdir(upload_path):
            os.mkdir(upload_path)

        # Save the analysis result to a JSON file
        path = os.path.join(upload_path, f'{user_id}.json')
        with open(path, 'w') as f:
            json.dump({
                'total_liked_posts': total_liked_posts,
                "total_liked_comments": total_liked_comments,
                'total_posts_comments': total_posts_comments,
                'most_commented_account_for_posts': most_commented_account_for_posts,
                'most_commented_account_count_for_posts': most_commented_account_count_for_posts,
                'total_reels_comments': total_reels_comments,
                'most_commented_account_for_reels': most_commented_account_for_reels,
                'most_commented_account_count_for_reels': most_commented_account_count_for_reels
            }, f)

        return path
    
    except (BadZipFile, OSError, KeyError, json.JSONDecodeError) as error:
        raise error


