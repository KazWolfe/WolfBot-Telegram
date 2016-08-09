# coding=UTF-8

from __CoreCommand__ import register
from __CoreCommand__ import PREFS as prefs
from __CoreCommand__ import COMMANDS as commands

from telepot.exception import TelegramError

import AwooUtils
import random
import json
import urllib

@register("start", "Get started with WolfBot!", "", {"groupExec": True, "privateExec": True, "adminNeeded": False, "restricted": False})
def start(bot, args):
    chat_id = args['chat_id']
    bot.sendMessage(chat_id, "Hi there! Welcome to WolfBot, a \"simple\" telegram Bot. Type /help to get started!")

@register("me", "", "", {"groupExec": True, "privateExec": True, "adminNeeded": False, "restricted": False})
def me(bot, args):
    return None
    ## We just ignore this command

@register("howl", "This bot *is* a wolf.", "", {"groupExec": True, "privateExec": True, "adminNeeded": False, "restricted": False})
def howl(bot, args):
    chat_id = args['chat_id']

    bot.sendMessage(chat_id, "Awoo!")

@register("fetch", "Make WolfBot fetch things!", "<thing>", {"groupExec": True, "privateExec": True, "adminNeeded": False, "restricted": False})
def fetch(bot, args):
    chat_id = args['chat_id']
    params = args['params']

    if len(params) == 0:
        bot.sendMessage(chat_id, "You need to tell me what to fetch.")
        return None

    bot.sendMessage(chat_id, "Do I look like a housepet to you? Go get your own " + " ".join(params) + "!")

@register("pets", "Give the bot a pet", "", {"groupExec": True, "privateExec": True, "adminNeeded": False, "restricted": False})
def pets(bot, args):
    chat_id = args['chat_id']
    msg = args['message']

    name = AwooUtils.getFirstName(msg)

    things = ["pets", "steak", "treat", "coffee", "belly rub"]

    bot.sendMessage(chat_id, "Thanks for the " + random.choice(things) + ", " + name + "! I appreciate it!")

@register("getinfo", "Print some diagnostic info about the current chat", "", {"groupExec": True, "privateExec": True, "adminNeeded": False, "restricted": False})
def getinfo(bot, args):
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

    result = "I am WolfBot, version " + AwooUtils.getVersion() + \
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

@register("catfacts", "Get a catfact, because there's no DogFact api.", "", {"groupExec": True, "privateExec": True, "adminNeeded": False, "restricted": False})
def catfact(bot, args):
    chat_id = args['chat_id']

    url = "http://catfacts-api.appspot.com/api/facts"

    fact = json.load(urllib.urlopen(url))

    bot.sendMessage(chat_id, fact['facts'][0])

@register("accuse", "Accuse someone of HAX!!!11!", "", {"groupExec": True, "privateExec": False, "adminNeeded": False, "restricted": False})
def accuse(bot, args):
    chat_id = args['chat_id']

    bot.sendMessage(chat_id, "HACKS!!!!!!!!1!!1!!")

@register("telladmins", "Send the Admins a message", "<message>", {"groupExec": True, "privateExec": False, "adminNeeded": False, "restricted": False})
def telladmins(bot, args):
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


@register("rules", "Read the Rules of the chat", "", {"groupExec": True, "privateExec": False, "adminNeeded": False, "restricted": False})
def rules(bot, args):
    chat_id = args['chat_id']

    rulelist = prefs.get(chat_id, "rules")

    if rulelist is None:
        rulelist = prefs.get("__default", "rules")

    bot.sendMessage(chat_id, rulelist, "Markdown", True)

@register("admintest", "Check for admin privileges", "", {"groupExec": False, "privateExec": False, "adminNeeded": True, "restricted": False})
def admintest(bot, args):
    chat_id = args['chat_id']

    bot.sendMessage(chat_id, "Admin Test Command. If you're running this, you're an admin!")


@register("echo", "Make the bot reply a message", "<message>", {"groupExec": False, "privateExec": False, "adminNeeded": True, "restricted": False})
def echo(bot, args):
    chat_id = args['chat_id']
    params = args['params']

    bot.sendMessage(chat_id, " ".join(params))


@register("ping", "Check if the bot is still alive", "", {"groupExec": False, "privateExec": False, "adminNeeded": True, "restricted": False})
def ping(bot, args):
    chat_id = args['chat_id']

    bot.sendMessage(chat_id, "Pong!")

@register("setup", "Run a test to see if the chat is set up right", "", {"groupExec": True, "privateExec": False, "adminNeeded": True, "restricted": False})
def setup(bot, args):
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

@register("fexec", "Force run a command, no matter what", "<command> [args]", {"superuserNeeded": True})
def fexec(bot, args):
    chat_id = args['chat_id']
    params = args['params']
    user_id = args['user_id']
    chat_type = args['chat_type']
    username = args['username']

    if len(params) == 0:
        bot.sendMessage(chat_id, "Usage: /fexec <command> [args]")
        return None

    command2 = params[0]
    params2 = params[1:]
    args2 = {'chat_id': chat_id, 'params': params2, 'user_id': user_id, 'chat_type': chat_type, 'username': username}

    print "   >>> [WARNING] Forcing execution of command " + command2 + "..."
    print "      >>> /" + command2 + " " + " ".join(params2)

    commands[command2]['function'](bot, args2)


@register("throwex", "Force throw an Exception", "[args]", {"superuserNeeded": True})
def throwex(bot, args):
    if len(args['params']) == 0:
        msg = "The exception you requested..."
    else:
        msg = " ".join(args['params'])

    raise RuntimeError(msg)


@register("reloadprefs", "Re-read preferences from the file", "", {"superuserNeeded": True})
def reloadprefs(bot, args):
    prefs.load()

@register("allowrestrictedcommand", "Allow a Restricted Command to be used in the current chat", "<command>", {"superuserNeeded": True})
def allowrestrictedcommand(bot, args):
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

@register("denyrestrictedcommand", "Disallow a Restricted Command from being used in the current chat", "<command>", {"superuserNeeded": True})
def denyrestrictedcommand(bot, args):
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
