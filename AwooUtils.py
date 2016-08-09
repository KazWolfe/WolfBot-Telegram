import json
import shlex
import sys

bot = None
prefs = None

class Prefs:
    """
    Object used for storing preferences.
    """

    def __init__(self):
        self._prefs = {}

    def __len__(self):
        return len(self._prefs)

    def __getitem__(self, chat):
        return self._prefs.get(str(chat), {})

    def get(self, chat, key, default = None):
        """
        Retrieve the value for the provided key in chat. Return None if the
        key or chat does not exist.
        """
        try:
            return self._prefs[str(chat)][key]
        except KeyError:
            return default

    def exists(self, chat, key):
        if (self.get(chat,key) is None):
            return False

        return True

    def set(self, chat, key, value):
        """
        Set the value for the provided key in chat, creating objects as needed.
        """
        c = self._prefs.get(str(chat), {})
        c[key] = value
        self._prefs[str(chat)] = c
        self.save()
        
    def delete(self, chat, key):
        c = self._prefs.get(str(chat), {})
        c.pop(key, None)
        self.save()
        
    def purgeChat(self, chat):
        self._prefs.pop(str(chat), None)
        self.save()

    def load(self):
        """
        Load preferences from the file.
        """
        with open('config/prefs.json', 'r') as f:
            try:
                self._prefs = json.loads(f.read())
            except ValueError:
                self._prefs = {}

    def save(self):
        """
        Save preferences from the file.
        """
        with open('config/prefs.json', 'w') as f:
            f.write(json.dumps(self._prefs, sort_keys=True))

    def all(self):
        return self._prefs

class CommandManager:
    def __init__(self):
        self._commands = {}

    def register(self, function, commandName, helptext, helpargs, permset):
        self._commands[commandName] = {"function": function, "helptext": helptext, "helpargs": helpargs, "permset": permset}

    def deregister(self, commandName):
        del self._commands[commandName]

    def gethelp(self):
        return None
        # ToDo: Real help!

    def execute(self, bot, commandName, args):
        chat_type = args['chat_type']
        chat_id = args['chat_id']
        user_id = args['user_id']

        try:
            command = self._commands[commandName]
        except KeyError:
            bot.sendMessage(chat_id, "The command /" + commandName + " does not exist.")
            return None

        # Make sure the user is a superuser for superuser commands
        if command["permset"].get("superuserNeeded", False):
            if not isDeveloper(user_id):
                bot.sendMessage(chat_id, "This command needs to be run by a Superuser.")

        # Make sure command can be run in a group
        if (not command["permset"].get("groupExec", False)) and (chat_type != "private"):
            bot.sendMessage(chat_id, "This command may not be run in groups. Try in a Private Message.");
            return None

        # Make sure command can be run in a private chat
        if (not command["permset"].get("privateExec", False)) and (chat_type == "private"):
            bot.sendMessage(chat_id, "This command may not be run in private chats. Try again in a Group.");
            return None

        # Make sure the user is privileged enough to run this command
        if command["permset"].get("adminNeeded", False):
            # Private chats don't have admins, so we can assume they are one.
            if chat_type != "private":
                if not isTelegramAdmin(user_id, chat_id):
                    bot.sendMessage(chat_id, "This command may only be run by a chat admin.")
                    return None

        command["function"](bot, args)

    def all(self):
        return self._commands



## STATIC UTILS FOR THIS PROJECT ##

def isCommand(msg):
    if 'text' in msg:
        if msg['text'].startswith('/'):
            if not msg['text'].startswith("/ "):
                if "@" in msg['text'].split()[0]:
                    if "@AwooBot" in msg['text'].split()[0]:
                        return True
                else:
                    return True
    return False

def parseCommand(cmd):
    def newSplit(value):
        lex = shlex.shlex(value)
        lex.quotes = '"'
        lex.whitespace_split = True
        lex.commenters = ''
        return list(lex)

    txt_split = cmd.split()
    return txt_split[0].split("@")[0].replace("/", "", 1), newSplit(" ".join(txt_split[1:]))

def getUserID(msg):
    if 'from' in msg:
        return str(msg['from']['id'])

def getBotID():
    return bot.getMe()[u'id']

def getUsername(msg, chat_action='from'):
    if 'username' in msg[chat_action]:
        return str(msg[chat_action]['username'])
    return ""

def getFirstName(msg, chat_action='from'):
    if 'first_name' in msg[chat_action]:
        return str(msg[chat_action]['first_name'])
    return getUsername(msg)

def getChatAdminsIncludingBot(chat_id):
    rawadms = bot.getChatAdministrators(chat_id)

    admins = []

    for i in rawadms:
        admins.append(i[u'user'][u'id'])

    return admins

def getChatAdmins(chat_id):
    admins = getChatAdminsIncludingBot(chat_id)

    botId = getBotID()

    if botId in admins:
        admins.remove(botId)

    return admins

def isBotAdmin(chat_id):
    admins = getChatAdminsIncludingBot(chat_id)

    return getBotID() in admins

def isTelegramAdmin(user_id, chat_id):

    return int(user_id) in getChatAdmins(chat_id)

def checkIfBanned(user_id, chat_id):
    banString = str(user_id) + ":" + str(chat_id)

    with open('config/bannedusers.txt', 'r+') as inFile:
        for line in inFile:
            if banString in line:
                return True

    return False

def banUser(user_id, chat_id):
    # 0: Success
    # 1: Not In Chat
    # 2: Already Banned

    banString = str(user_id) + ":" + str(chat_id)

    if checkIfBanned(user_id, chat_id):
        return 2
    else:
        if str("u'left'") in bot.getChatMember(chat_id, user_id):
            return 1
        else:
            bot.kickChatMember(chat_id, user_id)

            with open('config/bannedusers.txt', 'a+') as f:
                f.write(banString)

            return 0

def unbanUser(user_id, chat_id):
    # 0: Success
    # 1: In chat
    # 2: Not Banned

    banString = str(user_id) + ":" + str(chat_id)

    if not checkIfBanned(user_id, chat_id):
        return 2
    else:
        if str("u'left'") not in bot.getChatMember(chat_id, user_id):
            return 1
        else:
            bot.unbanChatMember(chat_id, user_id)

            f = open("config/bannedusers.txt", "r+")
            lines = f.readlines()
            f.close()
            f = open("config/bannedusers.txt", "w+")

            for line in lines:
                if line != banString + "\n":
                    f.write(line)

            f.close()

            return 0

def commandLogger(cmd, args):
    chat_id = args['chat_id']
    user_id = args['user_id']
    username = args['username']
    chat_type = args['chat_type']
    params = " ".join(args['params'])

    if chat_type == "private":
        return "Got command " + cmd + " from " + username + "@PrivateMessage (" + user_id + "@PrivateMessage)\n   >>> /" + cmd + " " + params
    else:
        return "Got command " + cmd + " from " + username + "@" + bot.getChat(chat_id)[u'title'] + " (" + user_id + "@" + str(chat_id) + ")\n   >>> /" + cmd + " " + params

def isDeveloper(user_id):
    if str(user_id) in SUPERUSERS:
        return True

    return False

def getPokemonName(id):
    pokemon = ["bulbasaur", "ivysaur", "venusaur", "charmander", "charmeleon", "charizard", "squirtle", "wartortle",
               "blastoise", "caterpie", "metapod", "butterfree", "weedle", "kakuna", "beedrill", "pidgey", "pidgeotto",
               "pidgeot", "rattata", "raticate", "spearow", "fearow", "ekans", "arbok", "pikachu", "raichu",
               "sandshrew", "sandslash", "nidoran(f)", "nidorina", "nidoqueen", "nidoran(f)", "nidorino", "nidoking",
               "clefairy", "clefable", "vulpix", "ninetales", "jigglypuff", "wigglytuff", "zubat", "golbat", "oddish",
               "gloom", "vileplume", "paras", "parasect", "venonat", "venomoth", "diglett", "dugtrio", "meowth",
               "persian", "psyduck", "golduck", "mankey", "primeape", "growlithe", "arcanine", "poliwag", "poliwhirl",
               "poliwrath", "abra", "kadabra", "alakazam", "machop", "machoke", "machamp", "bellsprout", "weepinbell",
               "victreebel", "tentacool", "tentacruel", "geodude", "graveler", "golem", "ponyta", "rapidash",
               "slowpoke", "slowbro", "magnemite", "magneton", "farfetch'd", "doduo", "dodrio", "seel", "dewgong",
               "grimer", "muk", "shellder", "cloyster", "gastly", "haunter", "gengar", "onix", "drowzee", "hypno",
               "krabby", "kingler", "voltorb", "electrode", "exeggcute", "exeggutor", "cubone", "marowak", "hitmonlee",
               "hitmonchan", "lickitung", "koffing", "weezing", "rhyhorn", "rhydon", "chansey", "tangela", "kangaskhan",
               "horsea", "seadra", "goldeen", "seaking", "staryu", "starmie", "mr. mime", "scyther", "jynx",
               "electabuzz", "magmar", "pinsir", "tauros", "magikarp", "gyarados", "lapras", "ditto", "eevee",
               "vaporeon", "jolteon", "flareon", "porygon", "omanyte", "omastar", "kabuto", "kabutops", "aerodactyl",
               "snorlax", "articuno", "zapdos", "moltres", "dratini", "dragonair", "dragonite", "mewtwo", "mew"]

    return pokemon[id-1].capitalize()

def getPokemonId(name):
    pokemon = ["bulbasaur", "ivysaur", "venusaur", "charmander", "charmeleon", "charizard", "squirtle", "wartortle",
               "blastoise", "caterpie", "metapod", "butterfree", "weedle", "kakuna", "beedrill", "pidgey", "pidgeotto",
               "pidgeot", "rattata", "raticate", "spearow", "fearow", "ekans", "arbok", "pikachu", "raichu",
               "sandshrew", "sandslash", "nidoran(f)", "nidorina", "nidoqueen", "nidoran(m)", "nidorino", "nidoking",
               "clefairy", "clefable", "vulpix", "ninetales", "jigglypuff", "wigglytuff", "zubat", "golbat", "oddish",
               "gloom", "vileplume", "paras", "parasect", "venonat", "venomoth", "diglett", "dugtrio", "meowth",
               "persian", "psyduck", "golduck", "mankey", "primeape", "growlithe", "arcanine", "poliwag", "poliwhirl",
               "poliwrath", "abra", "kadabra", "alakazam", "machop", "machoke", "machamp", "bellsprout", "weepinbell",
               "victreebel", "tentacool", "tentacruel", "geodude", "graveler", "golem", "ponyta", "rapidash",
               "slowpoke", "slowbro", "magnemite", "magneton", "farfetch'd", "doduo", "dodrio", "seel", "dewgong",
               "grimer", "muk", "shellder", "cloyster", "gastly", "haunter", "gengar", "onix", "drowzee", "hypno",
               "krabby", "kingler", "voltorb", "electrode", "exeggcute", "exeggutor", "cubone", "marowak", "hitmonlee",
               "hitmonchan", "lickitung", "koffing", "weezing", "rhyhorn", "rhydon", "chansey", "tangela", "kangaskhan",
               "horsea", "seadra", "goldeen", "seaking", "staryu", "starmie", "mr. mime", "scyther", "jynx",
               "electabuzz", "magmar", "pinsir", "tauros", "magikarp", "gyarados", "lapras", "ditto", "eevee",
               "vaporeon", "jolteon", "flareon", "porygon", "omanyte", "omastar", "kabuto", "kabutops", "aerodactyl",
               "snorlax", "articuno", "zapdos", "moltres", "dratini", "dragonair", "dragonite", "mewtwo", "mew"]

    try:
        return pokemon.index(name) + 1
    except ValueError:
        return 0

def getCoreConfig():
    with open('config/core.json', 'r') as f:
        try:
            coreconfig = json.loads(f.read())
        except ValueError:
            print "config/core.json not found or incorrect! Please set it up and try again!"
            sys.exit()

    return coreconfig

def getVersion():
    return getCoreConfig()['version']

def getSuperusers():
    return getCoreConfig()['superusers']

def getApiKey():
    return getCoreConfig()['apikey']

def getPrefs():
    return prefs

VERSION = getVersion()
SUPERUSERS = getSuperusers()