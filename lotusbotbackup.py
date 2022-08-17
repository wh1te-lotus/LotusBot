import discord
import os
import time
import shelve
import datetime
import discord.ext
import threading
from discord.utils import get
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, CheckFailure, check
#^ basic imports for other features of discord.py and python ^

client = discord.Client()

client = commands.Bot(command_prefix = '!') #put your own prefix here

global mutedrole
mutedrole = None
global casedirectory
casedirectory = "./lotusbot_cases"

def checkmutedrole(ctx):
    global casedirectory
    openshelf = shelve.open(casedirectory)
    global mutedrole
    if mutedrole != None and "mutedrole" in openshelf:
        #NOTE: check which guild instead of assuming there's only one
        guild = client.guilds[0]
        mutedroleid = openshelf["mutedrole"]
        mutedrole = guild.get_role(int(mutedroleid))
    openshelf.close()

@client.event
async def on_ready():
    print("bot online") #will print "bot online" in the console when the bot is online

@client.event
async def on_message_edit(before, after):
    print("Message by " + before.author.name + " was edited.")
    print("\t Before: " + before.content)
    print("\t After: " + after.content)

@client.event
async def on_message_delete(message):
    print("Message by  + ctx.something was deleted.")

@client.command()
async def ping(ctx):
    '''Returns the bot latency from the server, in milliseconds.'''
    if ctx.author.permissions_in(ctx.channel).manage_messages == False:
        await ctx.send("Insufficient permissions.")
        return
    import datetime
    elapsedtime = datetime.datetime.now() - ctx.message.created_at
    await ctx.send(":ping_pong: Pong! " + str(elapsedtime.microseconds/1000) + " ms") #simple command so that when you type "!ping" the bot will respond with "pong!"

@client.command()
async def kick(ctx, member : discord.Member, *, reason):
    '''Kicks a member from the server; however, they can still rejoin.
    Requires the KICK_MEMBERS permission.'''
    if ctx.author.permissions_in(ctx.channel).kick_members == False or member.permissions_in(ctx.channel).kick_members == True:
        await ctx.send("Insufficient permissions.")
        return
    #message = ctx.message.content
    #splitmessage = message.split(" ")
    #reason = " ".join(splitmessage[2:])
    casetype = "Kick"
    await send_dm(ctx, member, "You were kicked in " + ctx.guild.name + " for `" + reason + "`")
    await member.kick(reason=reason)
    await ctx.send(member.name + " was kicked.")
    createcase(ctx, member, reason, casetype)

#@client.command()
#async def ban(ctx, member : discord.Member, reason):
#  try:
#    await member.ban()(reason=None)
#    await ctx.send(member.name + " was banned.")

@client.command()
async def ban(ctx, member : discord.Member, *, reason):
    '''Permanently bans a member from the server.
     Requires the BAN_MEMBERS permission.'''
    if ctx.author.permissions_in(ctx.channel).ban_members == False or member.permissions_in(ctx.channel).ban_members == True:
        await ctx.send("Insufficient permissions.")
        return
    #message = ctx.message.content
    #splitmessage = message.split(" ")
    #reason = " ".join(splitmessage[2:])
    casetype = "Permanent Ban"
    await send_dm(ctx, member, "You were banned in " + ctx.guild.name + " for `" + reason + "`")
    await member.ban(reason=reason)
    await ctx.send(member.name + " was banned.")
    createcase(ctx, member, reason, casetype)

@client.command()
#async def unban(ctx, member : discord.Member):
async def unban(ctx):
    '''Removes a ban from a member, allowing them to rejoin the server.
    Requires the BAN_MEMBERS permission.'''
    if ctx.author.permissions_in(ctx.channel).ban_members == False:
        await ctx.send("Insufficient permissions.")
        return
    message = ctx.message.content
    splitmessage = message.split(" ")
    userid = int(splitmessage[1])
    usermention = "<@" + splitmessage[1] + ">"
    bannedusers = await ctx.guild.bans()
    for i in bannedusers:
        if userid == i.user.id:
            await ctx.guild.unban(i.user)
            await ctx.send(i.user.name + " was unbanned.")

@client.command()
async def mutedrole(ctx):
    '''Sets the role used for the !mute command.
    Requires the MANAGE_ROLES permission.'''
    if ctx.author.permissions_in(ctx.channel).manage_roles == False:
        await ctx.send("Insufficient permissions.")
        return
    message = ctx.message.content
    splitmessage = message.split(" ")
    global mutedrole
    rolemention = splitmessage[1]
    mutedroleid = splitmessage[1].strip("<@&>")
    mutedrole = ctx.guild.get_role(int(mutedroleid))
    await ctx.send("Muted role set to " + rolemention)
    global casedirectory
    casehistory = shelve.open(casedirectory)
    casehistory["mutedrole"] = mutedroleid
    casehistory.close()

def convert_to_seconds(s):
    seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    return int(s[:-1]) * seconds_per_unit[s[-1]]

@client.command()
async def mute(ctx, member : discord.Member, duration, *, reason):
    '''Temporarily adds the role defined by !mutedrole.
    Automatically removes it after the given period of time. Requires the MANAGE_ROLES permission.'''
    if ctx.author.permissions_in(ctx.channel).manage_roles == False or member.permissions_in(ctx.channel).manage_roles == True:
        await ctx.send("Insufficient permissions.")
        return
    checkmutedrole(ctx)
    #message = ctx.message.content
    #splitmessage = message.split(" ")
    #reason = " ".join(splitmessage[3:])
    #duration = splitmessage[2]
    casetype = "Mute"
    timeunits = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days", "w": "weeks"}
    dmduration = duration[:-1] + " " + timeunits[duration[-1]]
    await send_dm(ctx, member, "You were muted in " + ctx.guild.name + " for `" + dmduration +  "` for `" + reason + "`")
    global mutedrole
    await member.add_roles(mutedrole)
    await ctx.send(member.name + " was muted.")
    #global unmutetimer
    #unmutetimer = await threading.Timer(convert_to_seconds(mutetime), unmute, [member])
    #unmutetimer.start()
    createcase(ctx, member, reason, casetype, duration = dmduration)
    await autounmute(member, convert_to_seconds(duration))

async def autounmute(member, mutetime):
    time.sleep(mutetime)
    global mutedrole
    await member.remove_roles(mutedrole)

@client.command()
async def unmute(ctx, member : discord.Member):
    '''Manually removes the role set with !mutedrole.
     Requires the MANAGE_ROLES permission.'''
    if ctx.author.permissions_in(ctx.channel).manage_roles == False or member.permissions_in(ctx.channel).manage_roles == True:
        await ctx.send("Insufficient permissions.")
        return
    global mutedrole
    await member.remove_roles(mutedrole)

@client.command()
async def warn(ctx, member : discord.Member, *, reason):
    '''Adds an official warning to the !case logs and DMs the user.
    Requires the MANAGE_ROLES permission.'''
    if ctx.author.permissions_in(ctx.channel).manage_roles == False or member.permissions_in(ctx.channel).manage_roles == True:
        await ctx.send("Insufficient permissions.")
        return
    #message = ctx.message.content
    #splitmessage = message.split(" ")
    #reason = " ".join(splitmessage[2:])
    casetype = "Warning"
    await send_dm(ctx, member, "You were warned in " + ctx.guild.name + " for `" + reason + "`")
    await ctx.send(member.name + " was warned.")
    createcase(ctx, member, reason, casetype)

async def send_dm(ctx, member, message):
    try:
        await member.send(message)
    except:
        await ctx.send("Couldn't send a direct message to the member. Command carried out anyway.")



def createcase(ctx, member, reason, casetype, duration = None):
    global casedirectory
    casehistory = shelve.open(casedirectory)
    if "casenumber" not in casehistory:
        casehistory["casenumber"] = 0
    casenumber = casehistory["casenumber"] + 1
    if str(member.id) not in casehistory:
        casehistory[str(member.id)] = []
    caseDetails = {"tag": member.name + "#" + member.discriminator, "reason": reason, "moderator": ctx.author.name + "#" + ctx.author.discriminator, "time": str(datetime.datetime.now()), "casenumber": casenumber, "type": casetype, "duration": duration, "deleted": False}
    currentcases = casehistory[str(member.id)]
    currentcases.append(caseDetails)
    casehistory[str(member.id)] = currentcases
    casehistory["casenumber"] = casenumber
    casehistory.close()
    return casenumber

def printcases(case):
    return """**Case #%d at %s**
**Type:** %s %s
**Member:** %s
**Reason:** %s
**Moderator:** %s \n\n""" % (case["casenumber"], case["time"], case["type"], "\n**Duration:** " + case["duration"] if case["duration"] else "", case["tag"], case["reason"], case["moderator"])

@client.command()
async def cases(ctx, member : discord.Member):
    '''Brings up the member's list of official infractions.
    Requires the MANAGE_ROLES permission.'''
    if ctx.author.permissions_in(ctx.channel).manage_roles == False:
        await ctx.send("Insufficient permissions.")
        return
    global casedirectory
    casehistory = shelve.open(casedirectory)
    rawcases = casehistory[str(member.id)]
    casestring = ""
    for i in rawcases:
        if i["deleted"] == False:
            casestring += printcases(i)
    await ctx.send(casestring)
    casehistory.close()

@client.command()
async def deletecase(ctx, casenumber):
    '''Removes an active case from a member.
    Requires the MANAGE_ROLES permission.'''
    if ctx.author.permissions_in(ctx.channel).manage_roles == False:
        await ctx.send("Insufficient permissions.")
        return
    global casedirectory
    casehistory = shelve.open(casedirectory)
    stop = False
    for x in casehistory:
        if stop == True:
            break
        if x == "casenumber":
            continue
        currentcases = casehistory[str(x)]
        for i in range(len(currentcases)):
            #print("current number: " + str(currentcases[i]["casenumber"]) + " / looking for " + str(casenumber))
            if int(currentcases[i]["casenumber"]) == int(casenumber):
                #print("FOUND IT")
                currentcases[i]["deleted"] = True
                casehistory[str(x)] = currentcases
                stop = True
                break
    casedeletedtext = "**Successfully deleted case.**\n\n" + printcases(currentcases[i])
    casehistory.close()
    await ctx.send(casedeletedtext)

@cases.error
@mute.error
@warn.error
@kick.error
@ban.error
async def command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send(str(error))
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You need to provide a " + str(error).split(" ")[0] + ". Type !help <command> for the proper syntax.")


@client.command()
async def tempban(ctx, member : discord.Member, duration, *, reason):
    '''Temporarily bans a member from the server.
     Automatically removes it after the given period of time. Requires the BAN_MEMBERS permission.'''
    if ctx.author.permissions_in(ctx.channel).ban_members == False or member.permissions_in(ctx.channel).ban_members == True:
        await ctx.send("Insufficient permissions.")
        return
    #message = ctx.message.content
    #splitmessage = message.split(" ")
    #reason = " ".join(splitmessage[2:])
    casetype = "Temporary Ban"
    timeunits = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days", "w": "weeks"}
    dmduration = duration[:-1] + " " + timeunits[duration[-1]]
    await send_dm(ctx, member, "You were banned in " + ctx.guild.name + " for `" + dmduration +  "` for `" + reason + "`")
    memberid = member.id
    await member.ban(reason=reason)
    await ctx.send(member.name + " was banned.")
    createcase(ctx, member, reason, casetype, duration = dmduration)
    await autounban(ctx, memberid, convert_to_seconds(duration))


async def autounban(ctx, memberid, duration):
    time.sleep(duration)
    bannedusers = await ctx.guild.bans()
    for i in bannedusers:
        if memberid == i.user.id:
            await ctx.guild.unban(i.user)
            await ctx.send(i.user.name + " was unbanned.")
