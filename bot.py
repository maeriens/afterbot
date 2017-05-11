# Based on the www.fullstackpython.com tutorial

import os
import time
from datetime import datetime
from slackclient import SlackClient
from random import choice
from get_slack_token import getToken
from bad_guys import THE_BAD_GUYS as imported_guys

# starterbot's ID as an environment variable. Slack bot token
# can be defined as an ENVIRONMENT variable called SLACK_BOT_TOKEN
SLACK_BOT_TOKEN = ''  # 'SLACK TOKEN FOR BOT GOES HERE'
BOT_NAME = ''  # 'BOT NAME HERE'

if os.environ.get('SLACK_BOT_TOKEN'):
    BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
else:
    BOT_TOKEN = SLACK_BOT_TOKEN

# Variables should be set to get Bot's ID and the client going.
if not BOT_TOKEN:
    raise Exception('Variable SLACK_BOT_TOKEN no debería estar vacía')
if not BOT_NAME:
    raise Exception('Variabl BOT_NAME no debería estar vacía')


BOT_ID, slack_client = getToken(BOT_TOKEN, BOT_NAME)

AT_BOT = '<@' + BOT_ID + '>'

valid_start = ['sale after?', 'pinta after?', 'afterrrrrr', 'after el viernes?'
               'after?']
valid_action = ['+1', 'me sumo', 'me copa', '-1', 'me bajo', 'no me la banco']
list_action = ['lista', 'ebrios', 'quienes van?']
help_action = ['help', 'ayuda', 'aiuda']
ebrios = []

# Reject user for not completing
if not (valid_start and valid_action and list_action and help_action):
    raise Exception('Pero definime las variables querido')
flags = {'after': 0}

# Import the users which will prompt extra responses
THE_BAD_GUYS = imported_guys


def escuchamelo(command, channel, user):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification. Not known, but if
        a channel starts with D, it's a private channel.
    """
    if channel[0] == 'D':
        return postea(channel, 'Solo funciono en canales baby ;)')
    global ebrios
    if command in help_action:
        aiuda(channel)
    elif command in valid_start:
        ebrios = sale_after(channel, ebrios, user)
    elif command in valid_action:
        ebrios = update_after(channel, command, ebrios, user)
    elif command in list_action:
        listar(channel, ebrios)
    else:
        pass


def traducitelo(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID. I Stole this entire
        description. Nobody cares. Hail Satan.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and output['user'] != BOT_ID:
                if AT_BOT in output['text']:
                    output['text'] = output['text']\
                        .split(AT_BOT)[1].strip().lower()
                return output['text'], output['channel'], output['user']

    return None, None, None


def vos_quien_sos(user):
    """
        Grab the username, as the slack api grabs it's ID only
    """
    user_info = slack_client.api_call('users.info', user=user)
    return user_info['user']['name']


def sale_after(channel, ebrios, user):
    """
        Start an after office. YOLO BILINGUAL.
    """
    if flags['after']:
        response = 'Ya hay un after!'
        postea(channel, response)
        listar(channel, ebrios)
        return ebrios
    flags['after'] = 1
    response = 'SALE AFTER! :beer:\n*La tiró!*\n <@' + user + '>'
    bardear(channel, user)
    postea(channel, response)
    ebrios.append(user)
    return ebrios


def update_after(channel, command, ebrios, user):
    """
        This docblock makes no sense, the name of the function
        was really clear, do you get the iron-y?
        Someone with anemia wouldn't either.
    """
    if not flags['after']:
        response = 'No hay after armado, podrías armar uno <@' + user + '>'
        postea(channel, response)
        return ebrios
    if command.startswith('+'):
        if user not in ebrios:
            ebrios.append(user)
            response = '<@' + user + '> se suma! :beer:'
            bardear(channel, user)
        else:
            response = 'Ni estabas en la lista...'
    elif command.startswith('-'):
        if user not in ebrios:
            response = 'What? You were not even in the list, <@' + user + '>'
        else:
            response = '<@' + user + '> se baja... :snowflake:'
            ebrios.remove(user)
            if not ebrios:
                flags['after'] = 0
                response += '\nBueh, re ortibas, no queda nadie! Se cancela!'
                postea(channel, response)
                return ebrios
    postea(channel, response)
    listar(channel, ebrios)
    return ebrios


def aiuda(channel):
    """ Shows the help commands """
    response = '*Arrancar un after:* _{0}_\n*Coparse/Ortibarse:* ' \
        '_{1}_\n*Listar:* _{2}_\n*Ayuda:* _{3}_'.format(
            ', '.join(valid_start),
            ', '.join(valid_action),
            ', '.join(list_action),
            ', '.join(help_action))
    postea(channel, response)


def listar(channel, ebrios):
    """ Lists the cool guys who added themselves """
    if flags['after']:
        response = 'Los que se coparon:'
        for ebrio in ebrios:
            response += '\n <@' + user + '>'
    else:
        response = 'No hay after armado, podrías armar uno <@' + user + '>'
    postea(channel, response)


def bardear(channel, user):
    """
        This command returns silly answers predefined in the corresponding
        txt files in the txt folder (Because I wanted to work with files)
        to users listed in the THE_BAD_GUYS dictionary.
    """
    name = vos_quien_sos(user)
    if name in THE_BAD_GUYS.keys():
        if not flags['after']:
            msg = 'Ah no, mirá quién se suma! '
        else:
            msg = 'PERO MIRÁ QUIEN ORGANIZA! '
        msg += name + '! ' + choice(THE_BAD_GUYS[name])
        postea(channel, msg)


def postea(channel, response):
    """
        Handles posting to the channel. I left the channel variable
        so I can extend it to be an all purpose bot in the future
        if needed.
    """
    slack_client.api_call('chat.postMessage', channel=channel,
                          text=response, as_user=True)


if __name__ == '__main__':
    if slack_client.rtm_connect():
        print('Bot connected and running!')
        sleeper = 0
        while True:
            command, channel, user = traducitelo(
                slack_client.rtm_read())
            if command and channel:
                escuchamelo(command, channel, user)
            time.sleep(1)
            sleeper += 1
            # On Sundays, we clear the after list. Don't wear pink.
            if (sleeper % 86400 == 0) and \
                    datetime.now().strftime('%A') == 'Sun':
                sleeper = 0
                flags['after'] = 0
                ebrios = []
                print('R E S T A R T I N G, D U D E')

    else:
        print("Connection failed. Invalid Slack token or bot ID?")
