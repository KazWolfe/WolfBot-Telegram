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
import AwooCommands
import AwooChat

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
                    # Try executing a function in the AwooCommand modune, named
                    # the same as thsg variable cmd.
                    print AwooUtils.commandLogger(cmd, args)
                    func = getattr(AwooCommands, cmd)
                    func(args)

                except Exception:
                    # If it fails, something went sorta wrong. We need to check if it's a
                    # coding error or if it's a nonexistent command.
                    e = sys.exc_info()[0]

                    # Is this command nonexistent?
                    if "'module' object has no attribute '" + cmd + "'" in traceback.format_exc(e):
                        # Send a message back saying that this command doesn't exist.
                        bot.sendMessage(chat_id, "/" + cmd + " is not a valid command. See /help for more information.")
                    else:
                        # Report the fact that the command failed to run, and notify the Developers.
                        bot.sendMessage(chat_id,
                                        "[Error] Could not run command. The developers have been notified and are being beaten savagely for their mistake.")
                        for i in __DEVELOPERS__:
                            bot.sendMessage(i,
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
                bot.sendMessage(130977405, "WolfBot was kicked from chat " + str(msg['chat']['title']))
                prefs.purgeChat(msg['chat']['id'])

        # Check if the title exists.
        elif content_type == 'new_chat_title':
            AwooChat.titleWatchdog(msg)
        

##### END DEFINITIONS #####
### Below this is the actual program. Chatbots are teeny!

# Get Core Config
with open('config/core.json', 'r') as f:
    try:
        coreconfig = json.loads(f.read())
    except ValueError:
        print "config/core.json not found or incorrect! Please set it up and try again!"
        sys.exit()
        
__APIKEY__ = coreconfig['apikey']
__DEVELOPERS__ = coreconfig['superusers']
__VERSION__ = coreconfig['version']

# Create the Chatbot instance.
bot = telepot.Bot(__APIKEY__)

# Prepare a thread handler
def run_threaded(f):
    t = threading.Thread(target=f)
    t.start();
    
# Pass required variables over to the modules, and report on completion.
prefs = AwooUtils.Prefs()
prefs.load()
print 'Loaded Preferences for ' + str(len(prefs.all())) + ' chats.'
AwooUtils.prefs = prefs
AwooUtils.bot = bot
AwooUtils.__VERSION__ = __VERSION__
AwooUtils.__DEVELOPERS__ = __DEVELOPERS__
print 'Loaded core module AwooUtils'
AwooCommands.prefs = prefs
AwooCommands.bot = bot
AwooCommands.__VERSION__ = __VERSION__
AwooUtils.__DEVELOPERS__ = __DEVELOPERS__
print 'Loaded module AwooCommands'
AwooChat.prefs = prefs
AwooChat.bot = bot
AwooChat.__VERSION__ = __VERSION__
AwooUtils.__DEVELOPERS__ = __DEVELOPERS__
schedule.every(5).minutes.do(run_threaded, AwooChat.pokemonWatchdog)
print 'Loaded module AwooChat'

# Load and initialize all the commands

# Actually handle the message listener.
bot.message_loop(handle)
print 'Initialized WolfBot (@AwooBot) version ' + __VERSION__ + ', by @KazWolfe'

# Keep the program awake, and run scheduled tasks.
while True:
    schedule.run_pending()
    time.sleep(1)
