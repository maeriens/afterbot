# First attempt for a Slack Bot

 I created a virtual environment in my own machine (not sure
what to commit and what not) and added the corresponding 
files to deploy it to Heroku as a worker.

 This is based in the basic bot constructed in [FullStackPython](https://www.fullstackpython.com/blog/build-first-slack-bot-python.html)
 
## Usage

 - Create a virtual environment, I used Python 3.5.
 - Set up the bot in Slack, and grab it's token
 - You need to set up the Slack bot token as an environment variable
 - Alternatively, you can enter it in the variable in bot.py
 - Put the bot name so the file searches for it 
 - Set up the 'trigger words' needed to start/update/list/help
 - If you want to add some responses to certain users, you will need to create
   files inside the **txt** folder. **They should have the same name as the Slack users**
   Make it a plain text file, with one phrase per line, or a CSV.
