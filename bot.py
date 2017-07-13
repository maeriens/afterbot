# Based on the www.fullstackpython.com tutorial

import os
import time
from re import search, escape, sub
from datetime import datetime
from slackclient import SlackClient
from random import choice
from get_slack_token import getToken
from bad_guys import THE_BAD_GUYS as imported_guys

# starterbot's ID as an environment variable. Slack bot token
# can be defined as an ENVIRONMENT variable called SLACK_BOT_TOKEN
# 'SLACK TOKEN FOR BOT GOES HERE'
SLACK_BOT_TOKEN = ''
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

valid_start = ['sale after', 'pinta after', 'afterrrrrr',
               'after el viernes', 'after?']
yeah_action = ['+1', 'me sumo', 'me copa']
boo_action = ['-1', 'me bajo', 'no me la banco']
valid_action = yeah_action + boo_action
list_action = ['lista', 'ebrios', 'quienes van']
help_action = ['help', 'ayuda', 'aiuda']
all_actions = valid_start + valid_action + list_action + help_action

ebrios = {'Office1': [], 'Office2': []}

# Reject user for not completing
if not (valid_start and valid_action and list_action and help_action):
    raise Exception('Pero definime las variables querido')

# Import the users which will prompt extra responses
THE_BAD_GUYS = imported_guys


def escuchamelo(command, channel, user, ebrios):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification. Not known, but if
        a channel starts with D, it's a private channel.
    """
    if channel[0] == 'D':
        return postea(channel, choice(THE_BAD_GUYS['direct']))
    if command in help_action:
        return aiuda(channel)

    action, where = analiza(command)

    if action:
        if where:
            if where.isnumeric():
                return postea(channel, 'Los dos lugares no querido...')
            elif action in valid_start:
                ebrios = sale_after(channel, where, ebrios, user)
            elif action in valid_action:
                ebrios = update_after(channel, action, where, ebrios, user)
            elif action in list_action:
                listar(channel, where, ebrios)
        else:
            if ebrios['Office1'] or ebrios['Office2'] or action in valid_start:
                response = 'No me dijiste dónde...'
            else:
                response = 'No hay after armado, podrías ' \
                    'armar uno <@' + user + '>'
            return postea(channel, response)
    else:
        pass


def analiza(command):
    """
        Regex to get what to do. I hate this function. It's personal.
        I escape the simbols that would break the regex with 'scape'.
        Checks what action and where. Returns a string 1 if both locations.
    """
    action, where = None, None

    for option in all_actions:
        action_found = search(escape(option), command)
        if action_found:
            action = action_found.group(0)
            break

    if 'office1' in command and 'office2' in command:
        where = '1'
    else:
        for place in ['office1', 'office2']:
            where_found = search(place, command)
            if where_found:
                where = (where_found.group(0)).capitalize()
    return action, where


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


def sale_after(channel, where, ebrios, user):
    """
        Start an after office. YOLO BILINGUAL.
    """
    trampa = ['Office1', 'Office2']
    trampa.remove(where)
    if not ebrios[where]:
        if user in ebrios[trampa[0]]:
            return postea(channel, 'Pero si estás en el otro...')
        ebrios[where].append(user)
    else:
        return postea(channel, 'Ya hay un after ahí...')
    response = 'SALE AFTER en ' + where + ' :beer:\n' \
        '*La tiró* <@' + user + '> *!*'
    postea(channel, response)


def update_after(channel, action, where, ebrios, user):
    """
        This docblock makes no sense, the name of the function
        was really clear, do you get the iron-y?
        Someone with anemia wouldn't either.
    """
    if where:
        trampa = ['Office1', 'Office2']
        trampa.remove(where)
    response = ''
    if not ebrios[where]:
        if user in ebrios[trampa[0]]:
            response = "Pero si estás en el otro..."
        else:
            response = 'No hay after armado, podrías armar uno <@' + user + '>'
        return postea(channel, response)
    elif action in yeah_action:
        if user in ebrios[trampa[0]]:
            response = "Ya estás en el otro after, vas a meter viajecito?"
        elif user not in ebrios[where]:
            ebrios[where].append(user)
            if(not bardear(channel, user)):
                response = '<@' + user + '> se suma! :beer:'
        else:
            response = 'Ya estabas en la lista...'
    elif action in boo_action:
        if user in ebrios['Office1']:
            where = 'Office1'
            ebrios[where].remove(user)
            response = '<@' + user + '> se baja... :snowflake:'
        elif user in ebrios['Office2']:
            where = 'Office2'
            ebrios[where].remove(user)
            response = '<@' + user + '> se baja... :snowflake:'
        else:
            response = 'Ni estás en la lista, <@' + user + '>'
        if not ebrios[where]:
            response += '\nBueh, re ortibas, no queda nadie! Se cancela!'
    else:
        return postea(channel, 'No entendí')
    postea(channel, response)
    return ebrios[where]


def aiuda(channel):
    """ Shows the help commands """
    response = '*Arrancar un after:* _{0}_ + *dónde*\n*Coparse/Ortibarse:* ' \
        '_{1}_ + *dónde*\n*Listar:* _{2}_ + *dónde*\n*Ayuda:* _{3}_'.format(
            ', '.join(valid_start),
            ', '.join(valid_action),
            ', '.join(list_action),
            ', '.join(help_action))
    postea(channel, response)


def listar(channel, where, ebrios):
    """ Lists the cool guys who added themselves """
    if ebrios[where]:
        response = 'Los que se coparon en ' + where + ':'
        for ebrio in ebrios[where]:
            response += '\n' + vos_quien_sos(ebrio) + ''
    else:
        response = 'No hay after armado en ' + where + \
            ', podrías armar uno <@' + user + '>'
    postea(channel, response)


def bardear(channel, user):
    """
        This command returns silly answers predefined in the corresponding
        txt files in the txt folder (Because I wanted to work with files)
        to users listed in the THE_BAD_GUYS dictionary. If not found, it
        simply returns False so a default answer is given.
    """
    name = vos_quien_sos(user)
    if name in THE_BAD_GUYS.keys():
        if ebrios['Office1'] or ebrios['Office2']:
            msg = 'Ah no, mirá quién se suma! '
        else:
            msg = 'PERO MIRÁ QUIEN ORGANIZA! '
        msg += '<@' + name + '>! ' + choice(THE_BAD_GUYS[name])
        postea(channel, msg)
        return True
    return False


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
        step = 0.25
        while True:
            command, channel, user = traducitelo(slack_client.rtm_read())
            if command and channel:
                command = sub(r'\\u\w{4}', '',
                              command.encode('latin-1', 'backslashreplace')
                              .decode('latin-1'))
                print(command)
                escuchamelo(command, channel, user, ebrios)
            time.sleep(step)
            sleeper += step
            # On Sundays, we clear the after list. Don't wear pink.
            if (sleeper % 86400 == 0) and \
                    datetime.now().strftime('%A') == 'Sun':
                sleeper = 0
                for key in ebrios.keys():
                    ebrios[key] = []
                postea(channel, 'R E S T A R T I N G, D U D E')
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
