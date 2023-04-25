#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import datetime
import os
import sys
import threading
import time


def update_data():
    from modules import github_api
    from modules.discord import discord
    from modules.models import DiscordUser
    from modules.storage import storage
    start_time = time.time()
    while True:
        collaborators = github_api.GithubAPI_UserRoles.get_collaborators()
        contributors = github_api.GithubAPI_UserRoles.get_contributors()
        stargazers = github_api.GithubAPI_UserRoles.get_stargazers()
        subscribers = github_api.GithubAPI_UserRoles.get_subscribers()
        owner = github_api.GithubAPI_UserRoles.get_owner()
        for user in DiscordUser.objects.all():
            access_token = None
            if user.expires_in < time.time():
                access_token = discord.get_access_token(user.user_id, storage.get_discord_tokens(user.user_id))
            con_data = discord.get_connections_data(
                access_token or storage.get_discord_tokens(user.user_id)['access_token'])
            for con in con_data:
                if con['type'] == 'github':
                    github_username = con['name']
            metadata = {
                    'collaborator': True if github_username in collaborators else False,
                    'contributor': True if github_username in contributors else False,
                    'stargazer': True if github_username in stargazers else False,
                    'watcher': True if github_username in subscribers else False,
                    'owner': True if github_username == owner else False,
            }
            old_metadata = discord.get_metadata(user.user_id, storage.get_discord_tokens(user.user_id))
            if old_metadata != metadata:
                discord.push_metadata(user.user_id, storage.get_discord_tokens(user.user_id), metadata)
        print(datetime.datetime.now().strftime('%H:%M:%S'))
        time.sleep(60.0 - ((time.time() - start_time) % 60.0))


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'discord_github_link.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    tmain = threading.Thread(target=main)
    t = threading.Thread(target=update_data)
    tmain.start()
    t.start()
    tmain.join()
