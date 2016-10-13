from __CoreCommand__ import register
from __CoreCommand__ import PREFS as prefs

@register("links", "Show the Links in this chat, set by staff", "", {"groupExec": True, "privateExec": False, "adminNeeded": False, "restricted": False})
def links(bot, args):
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

@register("addlink", "Add a link to the chat", "<url> <title> [description]", {"groupExec": True, "privateExec": False, "adminNeeded": True, "restricted": False})
def addlink(bot, args):
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

@register("dellink", "Remove a link from the chat", "<title>", {"groupExec": True, "privateExec": False, "adminNeeded": True, "restricted": False})
def dellink(bot, args):
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