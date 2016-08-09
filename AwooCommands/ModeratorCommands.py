from __CoreCommand__ import register
from __CoreCommand__ import PREFS as prefs

import AwooUtils

@register("sendmessage", "Send an announce message to a chat", "<chat_id> <message>", {"groupExec": False, "privateExec": True, "adminNeeded": False, "restricted": False})
def sendmessage(bot, args):
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

@register("setrules", "Set the chat Rules", "<rules>", {"groupExec": True, "privateExec": False, "adminNeeded": True, "restricted": False})
def setrules(bot, args):
    chat_id = args['chat_id']

    prefs.set(chat_id, "rules", " ".join(args['params']).replace("\\n", "\n"))

    bot.sendMessage(chat_id, "Rules have been updated.")

@register("setwelcome", "Set the chat welcome message", "<rules>", {"groupExec": True, "privateExec": False, "adminNeeded": True, "restricted": False})
def setwelcome(bot, args):
    chat_id = args['chat_id']

    prefs.set(chat_id, "welcomeMessage", " ".join(args['params']).replace("\\n", "\n"))

    bot.sendMessage(chat_id, "The Welcome Message has been updated.")
