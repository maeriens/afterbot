import os
from slackclient import SlackClient


def getToken(SLACK_BOT_TOKEN, BOT_NAME):
    """ Handles the session of the slack bot and the Bot's ID """
    slack_client = SlackClient(SLACK_BOT_TOKEN)

    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot!
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print("Bot ID for " + user['name'] + " found")
                return user.get('id'), slack_client
    else:
        raise BotNameNotFound('Bot not found in users.list')
