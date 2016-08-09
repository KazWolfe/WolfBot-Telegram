# Telegram API Wishlist
#  - Send messages to one person only (in chat)
#  - Get User ID from Username
#  - Get list of users from Chat
#  - Invite Users to Chat
#  - Delete messages from Chat Record

import json
import threading
import time
import traceback
import schedule
import sys
import telepot
import AwooUtils
import AwooChat
import AwooCommands

from AwooUtils import SUPERUSERS
from AwooUtils import VERSION
from AwooCommands.__CoreCommand__ import COMMANDS

def handle(msg):

    print("Got message: " + str(msg))
    flavor = telepot.flavor(msg)

    # The message is chat. Easy enough.
    if flavor == "chat":
        # Get the Message Content Information from the Message.
        content_type, chat_type, chat_id = telepot.glance(msg)

        # This message is a chat event (sent by a user).
        if content_type == 'text':
            # Is this a command?
            if AwooUtils.isCommand(msg):
                # Parse some information from the message, and get it ready.
                cmd, params = AwooUtils.parseCommand(msg['text'])
                user_id = AwooUtils.getUserID(msg)
                username = AwooUtils.getUsername(msg)

                # Create the Arguments packet. Commands may pick and choose what parameters
                # they want to use from this.
                args = {'chat_id': chat_id,
                        'params': params,
                        'user_id': user_id,
                        'chat_type': chat_type,
                        'username': username,
                        'message': msg}
                try:
                    # Run a command from the CommandManager, if it exists
                    COMMANDS.execute(BOT, cmd, args)

                except Exception:
                    # Report the fact that the command failed to run, and notify the Developers.
                    BOT.sendMessage(chat_id,
                                    "[Error] Could not run command. The developers have been notified and are being beaten savagely for their mistake.")
                    for i in SUPERUSERS:
                        BOT.sendMessage(i,
                                        r"\[DEV] Internal Error. Trace:\n\n```" + traceback.format_exc(e) + "```",
                                        "Markdown")
                    # Print the stack trace.
                    traceback.print_exc()

        # A new Chat Member has been added!
        elif content_type == 'new_chat_member':
            AwooChat.newUserWatchdog(msg, chat_id)
            
        elif content_type == 'left_chat_member':
            if msg['left_chat_participant']['id'] == AwooUtils.getBotID():
                # Debug
                for i in SUPERUSERS:
                    BOT.sendMessage(i, "WolfBot was kicked from chat " + str(msg['chat']['title']))
                PREFS.purgeChat(msg['chat']['id'])

        # Check if the title exists.
        elif content_type == 'new_chat_title':
            AwooChat.titleWatchdog(msg)
        

##### END DEFINITIONS #####
### Below this is the actual program. Chatbots are teeny!

# Create the Chatbot instance.
BOT = telepot.Bot(AwooUtils.getApiKey())
AwooUtils.bot = BOT

# Prepare a thread handler
def run_threaded(f):
    t = threading.Thread(target=f)
    t.start();

# Pass required variables over to the modules, and report on completion.
PREFS = AwooUtils.Prefs()
AwooUtils.prefs = PREFS
PREFS.load()
print 'Loaded Preferences for ' + str(len(PREFS.all())) + ' chats.'
schedule.every(5).minutes.do(run_threaded, AwooChat.pokemonWatchdog)
print 'Loaded module AwooChat'


# Actually handle the message listener.
BOT.message_loop(handle)
print 'Initialized WolfBot (@AwooBot) version ' + VERSION + ', by @KazWolfe'

# Keep the program awake, and run scheduled tasks.
while True:
    schedule.run_pending()
    time.sleep(1)
