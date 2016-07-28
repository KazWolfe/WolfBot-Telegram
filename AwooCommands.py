# coding=UTF-8

import os
import random
import AwooUtils
import telepot
import time
import urllib
import json

from telepot.exception import TelegramError

bot = None
__VERSION__ = None
prefs = None

def __adminCommand(f):
    # The Decorator for administrative commands.
    def wrapper(args):
        # Extract required variables from the args that were passed.
        user_id = args['user_id']
        chat_id = args['chat_id']
        chat_type = args['chat_type']

        # If this is a private chat, give the user admin powers.
        if chat_type == "private":
            return f(args)

        # Check if the user is listed in the Admins for the chat.
        if AwooUtils.isTelegramAdmin(user_id, chat_id):
            # Return the unwrapped function
            return f(args)
        else:
            # Kick the user back and tell them they're not a bloody admin.
            bot.sendMessage(chat_id, "You are not an admin, and are not allowed to run this command.")

    # Allow the Developer bypass. Considered safe because this method can't be called from chat without the use of /fexec
    wrapper._bypass = f

    # Return the unwrapped function or None, depending on the result of the Admin check.
    return wrapper


def __groupCommand(f):
    # The Decorator for group-only commands.
    def wrapper(args):
        # Extract required variables from the args that were passed.
        chat_type = args['chat_type']
        chat_id = args['chat_id']

        # Check that the chat ISN'T private
        if chat_type != "private":
            # The chat isn't private. We can safely assume that it is a group, so return the unwrapped function.
            return f(args)
        else:
            # Kick the user back and tell them to try to run this command in the right place.
            bot.sendMessage(chat_id,
                            "This command does not work in a Private Message. Try again in a group or channel.")

    # Allow the Developer bypass. THIS MAY BREAK THINGS IF CALLED ON SOME GROUP FUNCTIONS. That's why it's a DEVELOPER bypass.
    wrapper._bypass = f

    # Return the unwrapped function or None, depending on the result of the group check.
    return wrapper


def __restrictedCommand(f):
    # The Decorator for commands restricted to certain chats
    def wrapper(args):
        # Extract required variables from the args that were passed.
        chat_type = args['chat_type']
        chat_id = args['chat_id']

        # Get the allowed commands object for the chat at hand
        if chat_type != "private":
            allowed = prefs.get(chat_id, "allowedCommands", [])
        else:
            allowed = prefs.get("__private", "allowedCommands", [])

        cmd = f.__name__

        if cmd in allowed:
            # The chat isn't private. We can safely assume that it is a group, so return the unwrapped function.
            return f(args)
        else:
            # Kick the user back and tell them to try to run this command in the right place.
            bot.sendMessage(chat_id, "/" + cmd + " is not a valid command. See /help for more information.")

    # Allow the Developer bypass.
    wrapper._bypass = f

    # Return the unwrapped function or None, depending on the result of the group check.
    return wrapper


def __privateCommand(f):
    # The Decorator for PM-only commands.
    def wrapper(args):
        # Extract required variables from the args that were passed.
        chat_type = args['chat_type']
        chat_id = args['chat_id']

        # Check that the chat IS private
        if chat_type == "private":
            # The chat is private. Return the unwrapped function.
            return f(args)
        else:
            # Kick the user back and tell them to try to run this command in the right place.
            bot.sendMessage(chat_id, "This command does not work in a Group. Try again in a private message.")

    # Allow the Developer bypass. THIS MAY BREAK THINGS IF CALLED ON SOME PM FUNCTIONS. That's why it's a DEVELOPER bypass.
    wrapper._bypass = f

    # Return the unwrapped function or None, depending on the result of the group check.
    return wrapper


def __developerCommand(f):
    # The Developer Command Wrapper.
    def wrapper(args):
        # Extract the required params from the args passed
        user_id = args['user_id']
        chat_id = args['chat_id']

        # Check if the user is a Developer or not.
        if AwooUtils.isDeveloper(user_id):
            # The user is a dev, so allow the comamnd to be run.
            return f(args)
        else:
            # KICK THE USER. THEY ARE NOT A DEVELOPER
            bot.sendMessage(chat_id, "You need to be a Developer of this bot to use this command.")

    # No Developer bypass on the Developer wrapper.

    # Return the unwrapped function or None, depending on the result of the group check.
    return wrapper


###################################### HELP COMMAND ##################################################

def help(args):
    # We need to add help manually, until I find a *real* way to register commands.

    # Get the list of required parameters.
    chat_id = args['chat_id']
    chat_type = args['chat_type']
    user_id = args['user_id']

    message = ""

    if chat_type != "private":
        message += "*/catfact*: Get a random cat fact, because there are no dogfacts APIs.\n"
        message += "*/getinfo*: Get some information about the current chat session.\n"
        message += "*/help*: Get some help on AwooBot and its functionality.\n"
        message += "*/howl*: Awoo!\n"
        message += "*/links*: Get a list of important links.\n"
        message += "*/pets*: Pet the bot.\n"
        message += "*/pogostatus*: Get status of Pokemon GO Server\n"
        message += "*/rules*: Get the rules for the current Chat.\n"
        message += "*/start*: Builtin command. Ensures the Bot is working.\n"
        message += "*/telladmins* _message_: Send the Admins a message.\n"

        if AwooUtils.isTelegramAdmin(user_id, chat_id):
            message += "\n\n* === ADMIN COMMANDS === *\n"
            message += "*/addlink* _title url [description]_: Add a new Link to the Links list.\n"
            message += "*/dellink* _title_: Remove a Link from the Links list.\n"
            message += "*/echo* _text_: Make the bot spit back text.\n"
            message += "*/ping*: Check if the bot is still alive.\n"
            message += "*/setrules* _rules_: Set the Rules for the current chat.\n"
            message += "*/setup*: Check if the chat is set up properly.\n"
            message += "*/setwelcome* _welcome_: Set the Welcome Message for the current chat.\n"
    else:
        message += "*/catfact*: Get a random cat fact!\n"
        message += "*/echo* _text_: Make the bot spit back text.\n"
        message += "*/getinfo*: Get some information about the current chat session.\n"
        message += "*/help*: Get some help on AwooBot and its functionality.\n"
        message += "*/howl*: Awoo!\n"
        message += "*/pets*: Pet the bot.\n"
        message += "*/ping*: Check if the bot is still alive.\n"
        message += "*/pogostatus*: Get status of Pokemon GO Server\n"
        message += "*/start*: Builtin command. Ensures the Bot is working.\n"
        message += "*/watchpkmn*: Watch Pokemon spawns (where permitted).\n"
        message += "\nNote: Commands for groups have been removed from this list."

    bot.sendMessage(chat_id, message, "Markdown", True)


##################################### GLOBAL COMMANDS ################################################

def me(args):
    return None
    ## We just ignore this command


def howl(args):
    chat_id = args['chat_id']

    bot.sendMessage(chat_id, "Awoo!")


def fetch(args):
    chat_id = args['chat_id']
    params = args['params']

    if len(params) == 0:
        bot.sendMessage(chat_id, "You need to tell me what to fetch.")
        return None

    bot.sendMessage(chat_id, "Do I look like a fucking housepet to you? Go get your own " + " ".join(params) + "!")


def pets(args):
    chat_id = args['chat_id']
    msg = args['message']

    name = AwooUtils.getFirstName(msg)

    things = ["pets", "steak", "treat", "coffee", "belly rub"]

    bot.sendMessage(chat_id, "Thanks for the " + random.choice(things) + ", " + name + "! I appreciate it!")


def infect(args):
    chat_id = args['chat_id']
    user_id = args['user_id']
    params = args['params']

    if len(params) != 0:
        bot.sendMessage(chat_id, "/infect expects zero arguments. Given " + str(len(params)) + ".")
        return None

    default = "If lycanthropy were possible, there would already be a werewolf or two in this chat. Sorry. I can't help, even though I really want to."

    msg = prefs.get(user_id, "infectMessage", default)

    bot.sendMessage(chat_id, msg)


def start(args):
    chat_id = args['chat_id']

    bot.sendMessage(chat_id, "Hello there! How are you?\nYou can get started with me by reading my /help!")


def getinfo(args):
    chat_id = args['chat_id']
    user_id = args['user_id']
    chat_type = args['chat_type']

    user = bot.getChatMember(chat_id, user_id)['user']

    userId = user['id']
    userName = user.get('username', "No Username Set")
    firstName = user.get('first_name')
    lastName = user.get('last_name')

    if firstName != None:
        if lastName != None:
            name = "(" + firstName + " " + lastName + ") "
        else:
            name = "(" + firstName + ") "
    else:
        name = " "

    result = "I am WolfBot, version " + __VERSION__ + \
             "\n--------------------" + \
             "\nI appear to be in a " + chat_type + " chat, with ID " + str(chat_id) + "." + \
             "\nYou appear to be " + userName + " " + name + ", with ID " + str(userId) + "."

    if AwooUtils.isDeveloper(user_id):
        result += " [DEV]"

    if chat_type != "private":
        if AwooUtils.isTelegramAdmin(user_id, chat_id):
            result = result + "\nYou are an Admin."
        if AwooUtils.isBotAdmin(chat_id):
            result += "\nI appear to be an Admin. Wheee!"

    bot.sendMessage(chat_id, result)


def pogostatus(args):
    chat_id = args['chat_id']

    startTime = time.time()
    reader = urllib.urlopen('https://pgorelease.nianticlabs.com/plfe/')
    page = reader.read()
    end = time.time()
    duration = end - startTime

    if (reader.getcode() == 200):
        if (duration < 0.8):
            bot.sendMessage(chat_id, "Pokemon GO servers appear to be online.")
        elif (duration > 0.8 and duration < 5):
            bot.sendMessage(chat_id, "Pokemon GO servers appear to be unstable.")
        else:
            bot.sendMessage(chat_id, "Pokemon GO servers appear to be down.")
    else:
        bot.sendMessage(chat_id, "Pokemon GO servers appear to be down.")
        
def donate(args):
    chat_id = args['chat_id']
    
    message = "Thanks for offering to donate to support the WolfBot cause! I've included some info " + \
              "below about how to help get my creator some money.\n\n" + \
              "[DigitalOcean Referral](https://m.do.co/c/77962b668c59) ***(Preferred)***: Get a DigitalOcean account and some servers! " + \
              "Once you've spent $25, the creator will also get $25. Plus, you get $10 free!\n" + \
              "[PayPal](https://paypal.me/KazWolfe): Send some money thru PayPal. It will only be used for servers, I promise."
              
    bot.sendMessage(chat_id, message, "Markdown", True)
    
def catfact(args):
    chat_id = args['chat_id']
    
    url = "http://catfacts-api.appspot.com/api/facts"
    
    fact = json.load(urllib.urlopen(url))
    
    bot.sendMessage(chat_id, fact['facts'][0])


###################################### PM COMMANDS ###################################################

@__privateCommand
def setinfectmessage(args):
    chat_id = args['chat_id']
    user_id = args['user_id']
    params = args['params']

    if len(params) == 0:
        prefs.set(user_id, "infectMessage", "")
        bot.sendMessage(chat_id, "Infect message removed.")
        return None

    infectMessage = " ".join(params)

    prefs.set(user_id, "infectMessage", "")

    bot.sendMessage(chat_id, "/infect message set to:\n\n" + infectMessage)


@__privateCommand
def sendmessage(args):
    user_id = args['user_id']
    params = args['params']

    if len(params) < 2:
        bot.sendMessage(user_id, "/sendmessage expects two arguments: chat_id, message. Given " + str(len(params)))
    else:
        if (params[0] < 0):
            if not AwooUtils.isTelegramAdmin(user_id, params[0]):
                bot.sendMessage(user_id, "You need to be an Admin in the group you are sending a message to.")
            else:
                bot.sendMessage(params[0], ' '.join(params[1:]))
                bot.sendMessage(user_id, "Message sent")
        else:
            bot.sendMessage(params[0], ' '.join(params[1:]))
            bot.sendMessage(user_id, "Message sent")


###################################### GROUP COMMANDS ################################################

@__groupCommand
def accuse(args):
    chat_id = args['chat_id']

    bot.sendMessage(chat_id, "HACKS!!!!!!!!1!!1!!")

@__groupCommand
def links(args):
    chat_id = args['chat_id']

    linkList = prefs.get(chat_id, 'links')

    message = "*Useful Links*\n" + \
              "=====================\n"

    if (linkList is None) or (len(linkList) == 0):
        bot.sendMessage(chat_id, "No link data found. Admins may add links by using /addlink.")
        return None

    linkCount = len(linkList)
    for i, linkEntry in enumerate(linkList):
        name = linkEntry['title']
        url = linkEntry['url']
        desc = linkEntry['desc']

        message += "[" + name + "](" + url + "): " + desc
        if linkCount != i - 1:
            message += "\n"

    bot.sendMessage(chat_id, message, "Markdown", True)


@__groupCommand
def telladmins(args):
    chat_id = args['chat_id']
    user_id = args['user_id']
    username = args['username']
    params = args['params']

    blacklist = prefs.get(chat_id, 'telladminBlacklist', [])

    if user_id in blacklist:
        return None

    complaint = " ".join(params)

    admins = AwooUtils.getChatAdmins(chat_id)

    chatname = bot.getChat(chat_id)[u'title']

    sendSoftFail = False

    for i in admins:
        try:
            bot.sendMessage(i, "[ADM] User complaint from " + username + " in chat " + chatname + ": " + complaint)
        except TelegramError as e:
            sendSoftFail = True

    if sendSoftFail:
        bot.sendMessage(chat_id,
                        "Complaint could not be sent to all admins. It is highly recommended that all admins open a private convo with the Bot.")


@__groupCommand
def rules(args):
    chat_id = args['chat_id']

    rulelist = prefs.get(chat_id, "rules")

    if rulelist is None:
        rulelist = prefs.get("__default", "rules")

    bot.sendMessage(chat_id, rulelist, "Markdown", True)


########################## GLOBAL ADMIN COMMANDS BELOW THIS LINE ####################################

@__adminCommand
def admintest(args):
    chat_id = args['chat_id']

    bot.sendMessage(chat_id, "Admin Test Command. If you're running this, you're an admin!")


@__adminCommand
def echo(args):
    chat_id = args['chat_id']
    params = args['params']

    bot.sendMessage(chat_id, " ".join(params))


@__adminCommand
def ping(args):
    chat_id = args['chat_id']

    bot.sendMessage(chat_id, "Pong!")


@__adminCommand
@__restrictedCommand
def watchpkmn(args):
    chat_id = args['chat_id']
    params = args['params']

    p = prefs

    currentWatch = p.get(chat_id, "alertPokemonList")

    if currentWatch is None:
        currentWatch = []

    if (len(params) == 0):
        bot.sendMessage(chat_id, "Command requires one or two arguments: [add|remove|list|source|location] <pokemon_id>.")
        return None
        
    if (params[0].lower() == "add"):
        remove = False
    elif (params[0].lower() == "remove"):
        remove = True
    elif (params[0].lower() == "source"):
        if len(params) == 1:
            prefs.set(chat_id, "pokemonDataSource", None)
            bot.sendMessage(chat_id, "Source removed. Chat will receive no more notifications.")
        elif len(params) == 2:
            prefs.set(chat_id, "pokemonDataSource", params[1])
            bot.sendMessage(chat_id, "Source set to " + params[1])
        else:
            bot.sendMessage(chat_id, "Command requires zero or one argument: /watchpkmn source [url]")
        return None
    elif (params[0].lower() == "location"):
        if len(params) == 1:
            prefs.set(chat_id, "pokemonLocation", None)
            bot.sendMessage(chat_id, "Location removed. Chat will receive notifications for all pokemon in source.")
        elif len(params) == 4:
            try:
                prefs.set(chat_id, "pokemonLocation", {
                    'pos': (float(params[1]), float(params[2])),
                    'radius': float(params[3])})
            except ValueError:
                bot.sendMessage(chat_id, "All arguments to `/watchpkmn location` must be numbers")
        else:
            bot.sendMessage(chat_id, "Command requires zero or three arguments: /watchpkmn location [latitude longitude radius]")
        return None
    elif (params[0].lower() == "list"):
        list = []

        message = "Pokemon being watched:\n"
        for i in currentWatch:
            list.append(AwooUtils.getPokemonName(i) + " (" + str(i) +")")

        if (len(list) == 0):
            list.append("None")

        message = message + ", ".join(list)

        bot.sendMessage(chat_id, message)
        return None
    else:
        bot.sendMessage(chat_id, "Invalid argument. Use one of `add`, `remove`, `list`, or `source`.", "Markdown", True)
        return None

    ids = []
    rejected = []

    for i in params[1:]:
        if i.isdigit() and (1 <= int(i) <= 151):
            ids.append(i)
        elif (1 <= AwooUtils.getPokemonId(i.lower()) <= 151):
            ids.append(AwooUtils.getPokemonId(i.lower()))
        else:
            rejected.append(i)

    skipped = []
    completed = []
    for i in ids:
        i = int(i)
        if remove:
            if (i not in currentWatch):
                skipped.append(AwooUtils.getPokemonName(i) + " (" + str(i) +")")
            else:
                currentWatch.remove(i)
                completed.append(AwooUtils.getPokemonName(i) + " (" + str(i) +")")
        else:
            if (i in currentWatch):
                skipped.append(AwooUtils.getPokemonName(i) + " (" + str(i) +")")
            else:
                currentWatch.append(i)
                completed.append(AwooUtils.getPokemonName(i) + " (" + str(i) +")")

    message = ""
    if (len(completed) > 0):
        if remove == True:
            message += "The following Pokemon were removed:\n"
        else:
            message += "The following Pokemon were added:\n"
        completed.sort()
        message = message + ", ".join(completed)
        if (len(skipped) > 0):
            message += "\n\n"

    if (len(skipped) > 0):
        message += "The following Pokemon were skipped:\n"
        skipped.sort()
        message = message + ", ".join(skipped)
        if (len(rejected) > 0):
            message += "\n\n"

    if (len(rejected) > 0):
        message += "The following parameters were invalid:\n"
        rejected.sort()
        message = message + ", ".join(rejected)

    bot.sendMessage(chat_id, message)

    currentWatch.sort()
    p.set(chat_id, "alertPokemonList", currentWatch)


########################## GROUP ADMIN COMMANDS BELOW THIS LINE #####################################

@__adminCommand
@__groupCommand
def addlink(args):
    chat_id = args['chat_id']
    params = args['params']

    currentLinks = prefs.get(chat_id, "links") # Returns a List of Dicts containing our links

    if len(params) < 2:
        bot.sendMessage(chat_id, "/addlink expects two or more arguments: /addlink <url> <title> [description]")
        return None

    url = params[0]
    title = params[1]
    desc = " ".join(params[2:])

    newEntry = {'url': url, 'title': title, 'desc': desc}
    msg = ""

    if currentLinks is not None:
        for entry in currentLinks:
            if entry['title'] == newEntry['title']:
                bot.sendMessage(chat_id, "Link titles must be unique. Not added.")
                return None
            if entry['url'] == newEntry['url']:
                msg = "Warning: This link is already in the database. Adding anyways...\n"
    else:
        currentLinks = []

    currentLinks.append(newEntry)

    prefs.set(chat_id, "links", currentLinks)
    bot.sendMessage(chat_id, msg + "Link \"" + title + "\" added to this chat's database.")

@__adminCommand
@__groupCommand
def dellink(args):
    chat_id = args['chat_id']
    params = args['params']

    currentLinks = prefs.get(chat_id, "links") # Returns a List of Dicts containing our links

    if 0 == len(params) > 1:
        bot.sendMessage(chat_id, "/dellink expects one argument: /dellink <title>")
        return None

    title = " ".join(params[0:])

    success = False

    for entry in currentLinks:
        if title == entry['title']:
            currentLinks.remove(entry)
            success = True

    if success:
        prefs.set(chat_id, "links", currentLinks)
        bot.sendMessage(chat_id, "Link " + title + " removed from this chat's database.")
    else:
        bot.sendMessage(chat_id, "Link isn't present in the chat's database. Not removed.")

@__adminCommand
@__groupCommand
def setrules(args):
    chat_id = args['chat_id']

    prefs.set(chat_id, "rules", " ".join(args['params']).replace("\\n", "\n"))

    bot.sendMessage(chat_id, "Rules have been updated.")

@__adminCommand
@__groupCommand
def setwelcome(args):
    chat_id = args['chat_id']

    prefs.set(chat_id, "welcomeMessage", " ".join(args['params']).replace("\\n", "\n"))

    bot.sendMessage(chat_id, "The Welcome Message has been updated.")

@__adminCommand
@__groupCommand
def kick(args):
    chat_id = args['chat_id']
    # params = args['params']

    if not AwooUtils.isBotAdmin(chat_id):
        bot.sendMessage(chat_id, "Bot is not an Admin in this chat.")
        return None

    bot.sendMessage(chat_id, "COMMAND_NOT_IMPLEMENTED")
    return None

    # if len(params) == 1:
    #    for user in params:
    #        result = AwooUtils.banUser(user, chat_id)
    #        if result == 1:
    #            bot.sendMessage(chat_id, "User " + username + " is not in this chat.")
    #        elif result == 2:
    #            bot.sendMessage(chat_id, "User " + username + " is currently banned.")
    #        else:
    #            AwooUtils.unbanUser(user, chat_id)
    #            bot.sendMessage(chat_id, "User " + username + " has been kicked from the chat.")
    # else:
    #    bot.sendMessage(chat_id, "/kick expects one argument (user id). Given " + len(params) + ".")


@__adminCommand
@__groupCommand
def ban(args):
    chat_id = args['chat_id']
    # params = args['params']

    if not AwooUtils.isBotAdmin(chat_id):
        bot.sendMessage(chat_id, "Bot is not an Admin in this chat.")
        return None

    bot.sendMessage(chat_id, "COMMAND_NOT_IMPLEMENTED")
    return None

    # if len(params) == 1:
    #    for user in params:
    #        result = AwooUtils.banUser(user, chat_id)
    #        if result == 1:
    #            bot.sendMessage(chat_id, "User " + username + " is not in this chat.")
    #        elif result == 2:
    #            bot.sendMessage(chat_id, "User " + username + " is currently banned.")
    #        else:
    #            bot.sendMessage(chat_id, "User " + username + " has been banned from the chat.")
    # else:
    #    bot.sendMessage(chat_id, "/ban expects one argument (user id). Given " + len(params) + ".")


@__adminCommand
@__groupCommand
def setup(args):
    chat_id = args['chat_id']

    message = ""

    hasRules = prefs.exists(chat_id, "rules")
    hasLinks = prefs.exists(chat_id, "links")
    hasWelcome = prefs.exists(chat_id, "welcomeMessage")

    if (hasRules and hasLinks and hasWelcome):
        bot.sendMessage(chat_id, "Congratulations! This room is completely set up and ready to go!")
        return None

    if not hasRules:
        message += "❌ *Problem:* This Chat has no rules set!\n      *Resolution*: Use `/setrules` to make some!\n\n"
    else:
        message += "✅ The chat has a rule set.\n\n"

    if not hasLinks:
        message += "❌ *Problem:* This Chat has no links!\n      *Resolution*: Add links using the `/addlink` command!\n\n"
    else:
        message += "✅ The chat has links defined.\n\n"

    if not hasWelcome:
        message += "❌ *Problem:* This Chat has no welcome message!\n      *Resolution*: Use `/setwelcome` to add one!\n\n"
    else:
        message += "✅ The chat has a welcome text.\n\n"

    if not AwooUtils.isBotAdmin(chat_id):
        message += "❌ *Problem:* The Bot is not listed as an Admin.\n      *Resolution*: Add the Bot as a chat admin.\n\n"
    else:
        message += "✅ The Bot is a chat admin."

    bot.sendMessage(chat_id, message, "Markdown")


######################################### DEVELOPER COMMANDS ######################################################

@__developerCommand
def fexec(args):
    chat_id = args['chat_id']
    params = args['params']
    user_id = args['user_id']
    chat_type = args['chat_type']
    username = args['username']

    if len(params) == 0:
        bot.sendMessage(chat_id, "Usage: /fexec <command> [args]")

    command2 = params[0]
    params2 = params[1:]
    args2 = {'chat_id': chat_id, 'params': params2, 'user_id': user_id, 'chat_type': chat_type, 'username': username}

    print "   >>> [WARNING] Forcing execution of command " + command2 + "..."
    print "      >>> /" + command2 + " " + " ".join(params2)

    globals()[command2]._bypass(args2)


@__developerCommand
def throwex(args):
    if len(args['params']) == 0:
        msg = "The exception you requested..."
    else:
        msg = " ".join(args['params'])

    raise RuntimeError(msg)


@__developerCommand
def reloadprefs(args):
    prefs.load()

@__developerCommand
def dumpprefs(args):
    chat_id = args['chat_id']

    pl = prefs[chat_id]

    bot.sendMessage(chat_id, str(pl))

@__developerCommand
def allowrestrictedcommand(args):
    chat_id = args['chat_id']
    params = args['params']

    if len(params) == 1:
        cmd = params[0]

        ca = prefs.get(chat_id, "allowedCommands", [])

        if cmd in ca:
            bot.sendMessage(chat_id, "Command " + cmd + " already allowed for chat ID " + str(chat_id))
        else:
            ca.append(cmd)
            prefs.set(chat_id, "allowedCommands", ca)
            bot.sendMessage(chat_id, "Command " + cmd + " allowed for chat ID " + str(chat_id))
    elif len(params) == 2:
        cmd = params[0]
        cid = params[1]

        ca = prefs.get(cid, "allowedCommands", [])

        if cmd in ca:
            bot.sendMessage(cid, "Command " + cmd + " already allowed for chat ID " + str(cid))
        else:
            ca.append(cmd)
            prefs.set(cid, "allowedCommands", ca)
            bot.sendMessage(chat_id, "Command " + cmd + " allowed for chat ID " + str(cid))

@__developerCommand
def denyrestrictedcommand(args):
    chat_id = args['chat_id']
    params = args['params']

    if len(params) == 1:
        cmd = params[0]

        ca = prefs.get(chat_id, "allowedCommands", [])

        if cmd not in ca:
            bot.sendMessage(chat_id, "Command " + cmd + " already disallowed for chat ID " + str(chat_id))
        else:
            ca.remove(cmd)
            prefs.set(chat_id, "allowedCommands", ca)
            bot.sendMessage(chat_id, "Command " + cmd + " disallowed for chat ID " + str(chat_id))
    elif len(params) == 2:
        cmd = params[0]
        cid = params[1]

        ca = prefs.get(cid, "allowedCommands", [])

        if cmd not in ca:
            bot.sendMessage(cid, "Command " + cmd + " already disallowed for chat ID " + str(cid))
        else:
            ca.remove(cmd)
            prefs.set(cid, "allowedCommands", ca)
            bot.sendMessage(chat_id, "Command " + cmd + " disallowed for chat ID " + str(cid))
