#!/usr/bin/env python
# -*- coding: utf-8 -*-

import AwooUtils
import urllib2
from datetime import datetime, time
from geopy.distance import distance
import json

bot = None
pokemonWatchdogSeen = []
prefs = None

def titleWatchdog(msg):
    groupId = msg[u'chat'][u'id']

    offendingUserId = msg[u'from'][u'id']
    offendingUsername = msg[u'from'][u'username']
    offendingFirstName = msg[u'from'][u'first_name']
    offendingLastName = msg[u'from'][u'last_name']

    offendingTitle = msg[u'new_chat_title']

    if offendingUsername == "":
        offendingUsername = offendingFirstName + " " + offendingLastName

    if AwooUtils.isTelegramAdmin(offendingUserId, groupId):
        return None
    else:
        for i in AwooUtils.getChatAdmins(groupId):
            bot.sendMessage(i, "[ADM] A Group Name has been changed by " + offendingUsername + ". New name: " + offendingTitle)

def pokemonWatchdog():
    global pokemonWatchdogSeen
    p = prefs

    now = int((datetime.now() - datetime(1970, 1, 1)).total_seconds() * 1000)
    message = ""

    parsedPokemon = {}

    for chat_id in p.all():
    
        source = prefs.get(chat_id, 'pokemonDataSource', None)
        if source is None:
            continue
            
        source = source + "/raw_data"

        s = json.load(urllib2.urlopen(source))
        pokemonList = s["pokemons"]

        location = prefs.get(chat_id, 'pokemonLocation', None)

        for i in pokemonList:
            id = i['pokemon_id']
            lat = i['latitude']
            lon = i['longitude']
            enc_id = i['encounter_id']
            despawn = datetime.fromtimestamp(i['disappear_time'] / 1000).strftime('%H:%M:%S')

            nearby = location is None or \
                    location['radius'] >= distance((lat, lon), location['pos']).miles

            if (nearby and enc_id not in pokemonWatchdogSeen):
                parsedPokemon[id] = parsedPokemon.get(id, [])
                parsedPokemon[id].append({'lat': lat, 'lon': lon, 'despawn': despawn})
                pokemonWatchdogSeen.append(enc_id)
                
                
        # Skip the program chats
        if chat_id == "__default" or chat_id == "__private" or chat_id == "__group":
            continue
            
        message = ""
        alertList = p.get(chat_id, 'alertPokemonList')

        if alertList is None:
            continue

        for i in parsedPokemon.keys():
            if i in alertList:
                for j in parsedPokemon[i]:
                    message += AwooUtils.getPokemonName(i) + " has been spotted! It despawns at " + str(j['despawn']) + \
                            ". [ᕕ( ᐛ )ᕗ](http://maps.google.com?q=" + str(j['lat']) + "," + str(j['lon']) + ")\n"

        if (chat_id < 0):
            # Group chat, so we need to handle this
            now_time = now.time()
            if now_time >= time(06, 00) and now_time <= time(23, 59):
                if len(message) != 0:
                    if (len(message) > 4095):
                        messages = message.split('\n')
                        currMsg = ""
                        for m in messages:
                            if len(currMsg) + len(m) + 1 > 4095:
                                bot.sendMessage(chat_id, currMsg, "Markdown", True)
                                currMsg = ""
                            else:
                                currMsg += m + "\n"
                    else:
                        bot.sendMessage(chat_id, message, "Markdown", True)
        else:
            if len(message) != 0:
                if (len(message) > 4095):
                    messages = message.split('\n')
                    currMsg = ""
                    for m in messages:
                        if len(currMsg) + len(m) + 1 > 4095:
                            bot.sendMessage(chat_id, currMsg, "Markdown", True)
                            currMsg = ""
                        else:
                            currMsg += m + "\n"
                else:
                    bot.sendMessage(chat_id, message, "Markdown", True)

def newUserWatchdog(msg, chat_id):
    if msg['new_chat_member']['id'] == AwooUtils.getBotID():
        return None

    # Get the First Name of the user.
    firstName = AwooUtils.getFirstName(msg, 'new_chat_member')

    # Try to read the custom file for the specified chat.
    welcomeMsg = prefs.get(chat_id, "welcomeMessage")
    if welcomeMsg is None:
        welcomeMsg = prefs.get("__default", "welcomeMessage")
        print "No welcome message for group " + str(chat_id) + ". Showing default."

    # Send the Welcome Message
    bot.sendMessage(chat_id, welcomeMsg.replace("{firstname}", firstName), "Markdown")
