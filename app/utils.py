import os
import json
from collections import Counter
from zipfile import ZipFile, BadZipFile
from flask import current_app


def process_zip_and_save(file_stream, username):
    upload_path = current_app.config['UPLOAD_PATH']
    try:
        with ZipFile(file_stream) as archive:
            # Your liked posts
            try:
                with archive.open('your_instagram_activity/likes/liked_posts.json') as f:
                    liked_posts_data = json.load(f)

                    if 'likes_media_likes' in liked_posts_data and liked_posts_data['likes_media_likes']:
                        account_likes_counter = Counter(
                            post['title']
                            for post in liked_posts_data['likes_media_likes']
                            if 'title' in post
                        )

                        top_3_most_liked_account_for_posts = [
                            {'name': person, 'liked_posts_count': count}
                            for person, count in account_likes_counter.most_common(3)
                        ]

                        total_liked_posts = len(liked_posts_data['likes_media_likes'])
                    else:
                        top_3_most_liked_account_for_posts = []
                        total_liked_posts = 0
            except KeyError:
                top_3_most_liked_account_for_posts = []
                total_liked_posts = 0
            except FileNotFoundError:
                top_3_most_liked_account_for_posts = []
                total_liked_posts = 0

            # Your liked comments
            try:
                with archive.open('your_instagram_activity/likes/liked_comments.json') as f:
                    liked_comments_data = json.load(f)

                    if 'likes_comment_likes' in liked_comments_data and liked_comments_data['likes_comment_likes']:
                        liked_comments_count = Counter(
                            comment['title']
                            for comment in liked_comments_data['likes_comment_likes']
                            if 'title' in comment
                        )

                        top_3_most_liked_account_for_comments = [
                            {'name': person, 'liked_comments_count': count}
                            for person, count in liked_comments_count.most_common(3)
                        ]

                        total_liked_comments = len(liked_comments_data['likes_comment_likes'])
                    else:
                        top_3_most_liked_account_for_comments = []
                        total_liked_comments = 0
            except KeyError:
                top_3_most_liked_account_for_comments = []
                total_liked_comments = 0
            except FileNotFoundError:
                top_3_most_liked_account_for_comments = []
                total_liked_comments = 0

            # Your liked stories
            try:
                with archive.open('your_instagram_activity/story_interactions/story_likes.json') as f:
                    liked_stories_data = json.load(f)

                    if 'story_activities_story_likes' in liked_stories_data and liked_stories_data['story_activities_story_likes']:
                        liked_stories_count = Counter(
                            story['title']
                            for story in liked_stories_data['story_activities_story_likes']
                            if 'title' in story
                        )

                        top_3_most_liked_account_for_stories = [
                            {'name': person, 'story_activities_story_likes': count}
                            for person, count in liked_stories_count.most_common(3)
                        ]

                        total_liked_stories = len(liked_stories_data['story_activities_story_likes'])
                    else:
                        top_3_most_liked_account_for_stories = []
                        total_liked_stories = 0
            except KeyError:
                top_3_most_liked_account_for_stories = []
                total_liked_stories = 0
            except FileNotFoundError:
                top_3_most_liked_account_for_stories = []
                total_liked_stories = 0

            # Your comments on posts
            try:
                with archive.open('your_instagram_activity/comments/post_comments_1.json') as f:
                    posts_comments_data = json.load(f)

                    if posts_comments_data:
                        account_posts_comments_counts = Counter(
                            comment['string_map_data']['Media Owner']['value']
                            for comment in posts_comments_data
                            if 'string_map_data' in comment and 'Media Owner' in comment['string_map_data']
                        )

                        top_3_most_commented_accounts_for_posts = [
                            {'name': account, 'comment_count': count}
                            for account, count in account_posts_comments_counts.most_common(3)
                        ]

                        total_posts_comments = len(posts_comments_data)
                    else:
                        top_3_most_commented_accounts_for_posts = []
                        total_posts_comments = 0
            except KeyError:
                top_3_most_commented_accounts_for_posts = []
                total_posts_comments = 0
            except FileNotFoundError:
                top_3_most_commented_accounts_for_posts = []
                total_posts_comments = 0

            # Your comments on reels
            try:
                with archive.open('your_instagram_activity/comments/reels_comments.json') as f:
                    reels_comments_data = json.load(f)

                    if 'comments_reels_comments' in reels_comments_data and reels_comments_data['comments_reels_comments']:
                        account_reels_comments_counts = Counter(
                            comment['string_map_data']['Media Owner']['value']
                            for comment in reels_comments_data['comments_reels_comments']
                            if 'string_map_data' in comment and 'Media Owner' in comment['string_map_data']
                        )
                        top_3_most_commented_accounts_for_reels = [
                            {'name': account, 'comment_count': count}
                            for account, count in account_reels_comments_counts.most_common(3)
                        ]

                        total_reels_comments = len(reels_comments_data['comments_reels_comments'])
                    else:
                        top_3_most_commented_accounts_for_reels = []
                        total_reels_comments = 0
            except KeyError:
                top_3_most_commented_accounts_for_reels = []
                total_reels_comments = 0
            except FileNotFoundError:
                top_3_most_commented_accounts_for_reels = []
                total_reels_comments = 0

            # Your stories posted
            try:
                with archive.open('your_instagram_activity/media/stories.json') as f:
                    stories_data = json.load(f)
                    total_stories_posted = len(stories_data['ig_stories'])
            except KeyError:
                total_stories_posted = 0
            except FileNotFoundError:
                total_stories_posted = 0

            # Your messages (I have to take a different approach here)
            # because there are heaps of messages JSON file for each different chat
            # that are in a different folder with different folder names
            inbox_path = 'your_instagram_activity/messages/inbox'
            message_counts = Counter()
            total_users_messaged = 0

            for folder_name in archive.namelist():
                if folder_name.startswith(inbox_path) and folder_name.endswith('message_1.json'):
                    try:
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
                    except KeyError:
                        continue
                    except FileNotFoundError:
                        continue

            if message_counts:
                # Remove the user's own name (yourself) from the message counts
                if yourself in message_counts:
                    del message_counts[yourself]

                # Get the top 3 most messaged people
                top_3_most_messaged = message_counts.most_common(3)
                top_3_most_messaged_people = [
                    {'name': person, 'message_count': count}
                    for person, count in top_3_most_messaged
                ]
            else:
                top_3_most_messaged_people = []


        # Ensure the upload directory exists, if not create it
        if not os.path.isdir(upload_path):
            os.mkdir(upload_path)

        # Save the analysis result to a JSON file
        path = os.path.join(upload_path, f'{username}.json')
        with open(path, 'w') as f:
            json.dump({
                'total_liked_posts': total_liked_posts,
                'top_3_most_liked_account_for_posts': top_3_most_liked_account_for_posts,

                "total_liked_comments": total_liked_comments,
                'top_3_most_liked_account_for_comments': top_3_most_liked_account_for_comments,

                'total_liked_stories': total_liked_stories,
                'top_3_most_liked_account_for_stories': top_3_most_liked_account_for_stories,

                'total_posts_comments': total_posts_comments,
                'top_3_most_commented_accounts_for_posts': top_3_most_commented_accounts_for_posts,

                'total_reels_comments': total_reels_comments,
                'top_3_most_commented_accounts_for_reels': top_3_most_commented_accounts_for_reels,

                'total_people_messaged': total_users_messaged,
                'top_3_most_messaged_people': top_3_most_messaged_people,

                'total_stories_posted': total_stories_posted
            }, f)

        return path

    except (BadZipFile, OSError, KeyError, json.JSONDecodeError) as error:
        raise error


def extract_and_save_profile_pic_from_json(file_stream, username):
    """
    Extracts the profile picture using the uri in your_instagram_activity/media/profile_photos.json,
    saves it to uploads, and returns the photo bytes (or None if not found).
    """
    import json
    from zipfile import ZipFile
    import os

    profile_pics_path = current_app.config['PROFILE_PICS_PATH']
    try:
        with ZipFile(file_stream) as archive:
            try:
                with archive.open('your_instagram_activity/media/profile_photos.json') as f:
                    profile_json = json.load(f)
                uri = profile_json["ig_profile_picture"][0]["uri"]
            except Exception as e:
                return None

            # Now extract the photo using the URI
            if uri in archive.namelist():
                if not os.path.isdir(profile_pics_path):
                    os.makedirs(profile_pics_path, exist_ok=True)
                save_path = os.path.join(profile_pics_path, f'{username}.jpg')
                with archive.open(uri) as pic_file:
                    photo_bytes = pic_file.read()
                    with open(save_path, 'wb') as out_pic:
                        out_pic.write(photo_bytes)
                return photo_bytes
            else:
                return None
    except (BadZipFile, OSError) as error:
        print("Error extracting profile pic:", error)
        raise error


def process_and_save_all(file_stream, username):
    process_zip_and_save(file_stream, username)
    file_stream.seek(0)
    extract_and_save_profile_pic_from_json(file_stream, username)