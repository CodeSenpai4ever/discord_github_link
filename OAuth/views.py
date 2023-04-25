from django.http import HttpResponse
from django.shortcuts import render, redirect
import uuid

from modules import github_api
from modules.discord import discord
from modules.storage import storage

state = str(uuid.uuid4())


# Create your views here.
def linked_roles(request):
    url = discord.get_oauth_url()
    response = redirect(url)
    response.set_cookie('clientState', state)
    return response


def discord_oauth_callback(request):
    # 1. Uses the code to acquire Discord OAuth2 tokens
    code = request.GET['code']

    tokens = discord.get_oauth_tokens(code)

    # 2. Uses the Discord Access Token to fetch the user profile
    me_data = discord.get_user_data(tokens['access_token'])
    con_data = discord.get_connections_data(tokens['access_token'])
    user_id = me_data['user']['id']
    connections = con_data
    github_username = None
    for connection in connections:
        if connection['type'] == 'github':
            github_username = connection['name']
            break
    storage.store_discord_tokens(user_id, tokens)

    if not github_username:
        return 'You must connect your GitHub account to Discord to get access.  Please try again.\nIf you have already connected your GitHub account, please check if the Username shown on the Discord connection is up to date. If not disconnect the GitHub connection from your Discord account and connect it again.'
    else:
        # 3. Update the users metadata
        update_metadata(user_id, github_username)

        return HttpResponse('You did it!  Now go back to Discord.')


# Given a Discord UserId, push data to the Discord
# metadata endpoint.
def update_metadata(user_id, github_username):
    # Fetch the Discord tokens from storage
    tokens = storage.get_discord_tokens(user_id)
    metadata = {}
    try:
        metadata = {
                'collaborator': True if github_username in github_api.GithubAPI_UserRoles.get_collaborators() else False,
                'contributor': True if github_username in github_api.GithubAPI_UserRoles.get_contributors() else False,
                'stargazer': True if github_username in github_api.GithubAPI_UserRoles.get_stargazers() else False,
                'watcher': True if github_username in github_api.GithubAPI_UserRoles.get_subscribers() else False,
                'owner': True if github_username == github_api.GithubAPI_UserRoles.get_owner() else False,
        }
    except Exception as e:
        print('Error fetching external data:' + e)
        # If fetching the profile data for the external service fails for any reason,
        # ensure metadata on the Discord side is nulled out. This prevents cases
        # where the user revokes an external app permissions, and is left with
        # stale linked role data.

    # Push the data to Discord.
    discord.push_metadata(user_id, tokens, metadata)
