from __CoreCommand__ import register

#  The command (without slash) that this function corresponds to
name = "start"

# The Helptext String for this command
helptext = "Get started with WolfBot!"

# A formatted list of arguments for this command
# Ex:   <add|remove> [name]
helpargs = ""

permset = {
            "groupExec": True,
            "privateExec": True,
            "adminNeeded": False,
            "restricted": False
          }

@register(name, helptext, helpargs, permset)
def start(bot, args):
    chat_id = args['chat_id']
    bot.sendMessage(chat_id, "Hi there! Welcome to WolfBot, a \"simple\" telegram Bot. Type /help to get started!")