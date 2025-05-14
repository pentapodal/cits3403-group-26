import os
import json
from collections import Counter
from zipfile import ZipFile, BadZipFile


def process_zip_and_save(file_stream, upload_path, username):

    try:
        with ZipFile(file_stream) as archive:
            # Your liked posts
            with archive.open('your_instagram_activity/likes/liked_posts.json') as f:
                # Load the liked posts JSON file
                liked_posts_data = json.load(f)
                # Ensure data is not empty
                if liked_posts_data:
                    # Count the number of likes per account
                    liked_posts_count = Counter(
                        post['title']
                        for post in liked_posts_data['likes_media_likes']
                        if 'title' in post
                    )
                    # Find the account with the most likes
                    if liked_posts_count:
                        most_liked_account_for_posts, most_liked_account_count_for_posts = liked_posts_count.most_common(1)[0]
                    else:
                        # Handle case where no likes are found
                        most_liked_account_for_posts = None
                        most_liked_account_count_for_posts = 0

                    # Total number of liked posts
                    total_liked_posts = len(liked_posts_data['likes_media_likes'])
                else:
                    # Handle case where the data is empty
                    most_liked_account_for_posts = None
                    most_liked_account_count_for_posts = 0
                    total_liked_posts = 0


            # Your liked comments 
            with archive.open('your_instagram_activity/likes/liked_comments.json') as f:
                liked_comments_data = json.load(f)

                if liked_comments_data:
                    liked_comments_count = Counter(
                        comment['title']
                        for comment in liked_comments_data['likes_comment_likes']
                        if 'title' in comment
                        )
                    if liked_comments_count:
                        most_liked_account_for_comments, most_liked_account_count_for_comments = liked_comments_count.most_common(1)[0]
                    else:
                        most_liked_account_for_comments = None
                        most_liked_account_count_for_comments = 0

                    total_liked_comments = len(liked_comments_data['likes_comment_likes'])

                else:
                    most_liked_account_for_comments = None
                    most_liked_account_count_for_comments = 0
                    total_liked_comments = 0


            # Your liked stories
            with archive.open('your_instagram_activity/story_interactions/story_likes.json') as f:
                liked_stories_data = json.load(f)

                if liked_stories_data:
                    liked_stories_count = Counter(
                        story['title']
                        for story in liked_stories_data['story_activities_story_likes']
                        if 'title' in story
                        )
                    if liked_stories_count:
                        most_liked_account_for_stories, most_liked_account_count_for_stories = liked_stories_count.most_common(1)[0]
                    else:
                        most_liked_account_for_stories = None
                        most_liked_account_count_for_stories = 0

                    total_liked_stories = len(liked_stories_data['story_activities_story_likes'])
                else:
                    most_liked_account_for_stories = None
                    most_liked_account_count_for_stories = 0
                    total_liked_stories = 0   


            # Your comments on posts
            with archive.open('your_instagram_activity/comments/post_comments_1.json') as f:
                posts_comments_data = json.load(f) 

                if posts_comments_data:
                    account_posts_comments_counts = Counter(
                        comment['string_map_data']['Media Owner']['value']
                        for comment in posts_comments_data
                        if 'string_map_data' in comment and 'Media Owner' in comment['string_map_data']
                        )
                    if account_posts_comments_counts:
                        most_commented_account_for_posts, most_commented_account_count_for_posts = account_posts_comments_counts.most_common(1)[0]
                    else:
                        most_commented_account_for_posts = None
                        most_commented_account_count_for_posts = 0

                    total_posts_comments = len(posts_comments_data)
                else:
                    most_commented_account_for_posts = None
                    most_commented_account_count_for_posts = 0
                    total_posts_comments = 0
                        

            # Your comments on reels
            with archive.open('your_instagram_activity/comments/reels_comments.json') as f:
                reels_comments_data = json.load(f)

                if 'comments_reels_comments' in reels_comments_data:
                    account_reels_comments_counts = Counter(
                        comment['string_map_data']['Media Owner']['value']
                        for comment in reels_comments_data['comments_reels_comments']
                        if 'string_map_data' in comment and 'Media Owner' in comment['string_map_data']
                        )
                    if account_reels_comments_counts:
                        most_commented_account_for_reels, most_commented_account_count_for_reels = account_reels_comments_counts.most_common(1)[0]
                    else:
                        most_commented_account_for_reels = None
                        most_commented_account_count_for_reels = 0

                    total_reels_comments = len(reels_comments_data)

                else:
                    most_commented_account_for_reels = None
                    most_commented_account_count_for_reels = 0
                    total_reels_comments = 0
            

            # Your stories posted
            with archive.open('your_instagram_activity/media/stories.json') as f:
                stories_data = json.load(f)
                total_stories_posted = len(stories_data['ig_stories'])


            # Your messages (I have to take a different approach here)
            # because there are heaps of messages JSON file for each different chat
            # that are in a different folder with different folder names
            inbox_path = 'your_instagram_activity/messages/inbox'
            message_counts = Counter()
            total_users_messaged = 0

            for folder_name in archive.namelist():
                if folder_name.startswith(inbox_path) and folder_name.endswith('message_1.json'):
                    with archive.open(folder_name) as f:
                        messages_data = json.load(f)
                        if 'participants' in messages_data and 'messages' in messages_data:
                            participants = [p['name'] for p in messages_data['participants']]
                            # The second participant is the user, so we dont count it
                            yourself = participants[1]
                            # The rest are the people messaged
                            other_participants = [p for p in participants if p != yourself]

                            if other_participants:
                                for participant in other_participants:
                                    # Count the number of messages sent by the user to this participant
                                    user_messages_to_participant = [
                                        msg for msg in messages_data['messages']
                                        if msg.get('sender_name') == yourself
                                    ]
                                    message_counts[participant] += len(user_messages_to_participant)
                                total_users_messaged += len(other_participants)

            if message_counts:
                # Remove the user's own name (yourself) from the message counts
                if yourself in message_counts:
                    del message_counts[yourself]

                # Get the top 3 most messaged people
                top_3_most_messaged = message_counts.most_common(3)
                #most_messaged_person, most_messages_count = top_3_most_messaged[0] if top_3_most_messaged else (None, 0)
                top_3_most_messaged_people = [
                    {'name': person, 'message_count': count}
                    for person, count in top_3_most_messaged
                ]
            else:
                #most_messaged_person = None
                #most_messages_count = 0
                top_3_most_messaged_people = []


        # Ensure the upload directory exists, if not create it
        if not os.path.isdir(upload_path):
            os.mkdir(upload_path)

        # Save the analysis result to a JSON file
        path = os.path.join(upload_path, f'{username}.json')
        with open(path, 'w') as f:
            json.dump({
                'total_liked_posts': total_liked_posts,
                'most_liked_account_for_posts': most_liked_account_for_posts,
                'most_liked_account_count_for_posts': most_liked_account_count_for_posts,

                "total_liked_comments": total_liked_comments,
                'most_liked_account_for_comments': most_liked_account_for_comments,
                'most_liked_account_count_for_comments': most_liked_account_count_for_comments,

                'total_liked_stories': total_liked_stories,
                'most_liked_account_for_stories': most_liked_account_for_stories,
                'most_liked_account_count_for_stories': most_liked_account_count_for_stories,

                'total_posts_comments': total_posts_comments,
                'most_commented_account_for_posts': most_commented_account_for_posts,
                'most_commented_account_count_for_posts': most_commented_account_count_for_posts,

                'total_reels_comments': total_reels_comments,
                'most_commented_account_for_reels': most_commented_account_for_reels,
                'most_commented_account_count_for_reels': most_commented_account_count_for_reels,

                'total_people_messaged': total_users_messaged,
                'top_3_most_messaged_people': top_3_most_messaged_people,

                'total_stories_posted': total_stories_posted
            }, f)

        return path
    
    except (BadZipFile, OSError, KeyError, json.JSONDecodeError) as error:
        raise error


