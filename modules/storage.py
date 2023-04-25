import modules.models


# A class for storing data, it is better not to change if you do not know what you are doing.

class storage():
    # Creating Data to Write to a Dictionary
    def store_discord_tokens(user_id, tokens):
        try:
            user = modules.models.DiscordUser.objects.get(user_id=user_id)
        except modules.models.DiscordUser.DoesNotExist:
            modules.models.DiscordUser.objects.create(user_id=user_id, access_token=tokens['access_token'],
                                                      refresh_token=tokens['refresh_token'],
                                                      expires_in=tokens['expires_in'])
        if modules.models.DiscordUser.objects.get(user_id=user_id):
            modules.models.DiscordUser.objects.filter(user_id=user_id).update(access_token=tokens['access_token'],
                                                                              refresh_token=tokens['refresh_token'],
                                                                              expires_in=tokens['expires_in'])
        else:
            modules.models.DiscordUser.objects.create(user_id=user_id, access_token=tokens['access_token'],
                                                      refresh_token=tokens['refresh_token'],
                                                      expires_in=tokens['expires_in'])

    # Getting data from a dictionary
    def get_discord_tokens(user_id):
        try:
            user = modules.models.DiscordUser.objects.get(user_id=user_id)
            return {'access_token': user.access_token, 'refresh_token': user.refresh_token,
                    'expires_in': user.expires_in}
        except:
            return None
