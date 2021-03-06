import discord
from discord.ext import tasks
from discord.ext.commands import Bot

import random
import requests
import time
from requests.api import get

guild_subscriptions = True
fetch_offline_members = True

# =================================================

# Server-Bot Channel
serverBot = 854653166842150922

# 10-Man Channel
mainChannel = 843111309058899998

# CommonCrayon, Thisted, Cktos
admin = [277360174371438592, 114714586799800323, 335786316782501888]


serverip_file = open("serverip.txt")
serverip = serverip_file.read()

rconPassword_file = open("rconpassword.txt")
rconPassword = rconPassword_file.read()

# =================================================

# Rcon Process ====================================
from valve.rcon import RCON

SERVER_ADDRESS = (serverip, 27015)
PASSWORD = rconPassword

async def execCommand(command):
    with RCON(SERVER_ADDRESS, PASSWORD) as rcon:
        response = (rcon(command))[0:764]
        return response

async def changeMap(workshopid):
    with RCON(SERVER_ADDRESS, PASSWORD) as rcon:
        command = ("host_workshop_map " + str(workshopid))
        return (rcon(command))

# =================================================


async def getID():
    import uuid
    return (uuid.uuid1())



# Retriving Map Information.
def get_mapinfo(workshopid):
    try:
        payload = {"itemcount": 1, "publishedfileids[0]": [str(workshopid)]}
        r = requests.post("https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/", data=payload)
        data = r.json()

        name = data["response"]["publishedfiledetails"][0]["title"]
        
        filename = data["response"]["publishedfiledetails"][0]["filename"]
        filename = filename.split("/")[-1]
        

        preview_url = data["response"]["publishedfiledetails"][0]["preview_url"]
        thumbnail = preview_url + "/?ima=fit"

        workshop_link = "https://steamcommunity.com/sharedfiles/filedetails/?id=" + str(workshopid)

        return (name, workshop_link, thumbnail, filename)
    except:
        print("Failed to Get Map Data of " + str(workshopid))


def retry(retryAttempts):
    import time
    time.sleep(1)
    retryAttempts += 1
    return (retryAttempts)



async def demo_start(retryAttempts):
    try:

        # Demo Start
        demoid = await getID()
        print(demoid)
        response = await execCommand("tv_record " + str(demoid))
        DemoEmbed = discord.Embed(title="Demo Started as: " + str(demoid), description=response, color=0xFF6F00)
        channel = client.get_channel(serverBot)
        await channel.send(embed=DemoEmbed)


    except:
        retryAttempts = retry(retryAttempts)

        if retryAttempts != 5:

            channel = client.get_channel(serverBot)
            await channel.send("Failed to Start Demo. Retrying...")  

            time.sleep(1)
            await demo_start(retryAttempts)
        
        else:
            channel = client.get_channel(serverBot)
            await channel.send("Failed to Start Demo.")


async def get_stats(retryAttempts):
    try:
        # Get Stats
        channel = client.get_channel(843598844758982666)
        teamA = channel.members

        channel = client.get_channel(832598037598961684)
        teamB = channel.members  

        teamAList = []
        for playerA in teamA:
            teamAList.append(playerA.name)

        printTeamA = (', '.join(teamAList))

        teamBList = []
        for playerB in teamB:
            teamBList.append(playerB.name)

        printTeamB = (', '.join(teamBList))


        statEmbed = discord.Embed(title="10 Man", color=0xFF6F00)
        statEmbed.add_field(name="Team A", value=printTeamA, inline=True)
        statEmbed.add_field(name="Team B", value=printTeamB, inline=True)

        channel = client.get_channel(mainChannel)
        await channel.send(embed=statEmbed)

    except:

        retryAttempts = retry(retryAttempts)

        if retryAttempts != 5:

            channel = client.get_channel(serverBot)
            await channel.send("Match Start Embed Failed. Retrying...")  

            await get_stats(retryAttempts)
        
        else:
            channel = client.get_channel(serverBot)
            await channel.send("Match Start Embed Failed.")


client = discord.Client()



# Initiating the BotCrayon.
@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    game = discord.Game("10 Mans")
    await client.change_presence(status=discord.Status.online, activity=game)



@tasks.loop(minutes=1.0)
async def timer(scheduleMsg, time):
    import datetime

    utcTime = datetime.datetime.utcnow()
    cestTime = ("{:d}:{:02d}".format(utcTime.hour+2, utcTime.minute))

    cest = list(cestTime.split(":"))
    schTime = list(time.split(":"))

    minCountdown = ((int(schTime[0])*60) + int(schTime[1])) - ((int(cest[0])*60) + int(cest[1]))

    hour = minCountdown // 60
    minute = minCountdown - hour*60

    UpdatedEmbed = discord.Embed(title="10 Man", description="Join a 10 Man!", color=0xFF6F00)
    UpdatedEmbed.set_thumbnail(url="https://imgur.com/vUG7MDU.png")
    UpdatedEmbed.add_field(name="Time:", value=time + " CEST", inline=False)
    UpdatedEmbed.add_field(name="Countdown:", value="Starting in " + str(hour) + "H " + str(minute) + "M", inline=False)
    UpdatedEmbed.set_footer(text="???? or  ???? to join or leave 10 man.            ")

    await scheduleMsg.edit(embed=UpdatedEmbed)

    if hour == 0 and minute == 0:
        UpdatedEmbed = discord.Embed(title="10 Man", description="Join a 10 Man!", color=0xFF6F00)
        UpdatedEmbed.set_thumbnail(url="https://imgur.com/vUG7MDU.png")
        UpdatedEmbed.add_field(name="Time:", value=time + " CEST", inline=False)
        UpdatedEmbed.add_field(name="Countdown:", value="**Started!**", inline=False)
        UpdatedEmbed.set_footer(text="???? or  ???? to join or leave 10 man.            ")

        await scheduleMsg.edit(embed=UpdatedEmbed)
        timer.stop()



# User Commands.
@client.event
async def on_message(message):

    if message.author == client.user:
        return


    if message.content.startswith(">rcon "):

        userid = message.author.id
        access = (userid in admin)

        if (message.channel.id == serverBot) and access == True:

            command = message.content[6:]

            try:
                response = await execCommand(command)

                successEmbed = discord.Embed(title="Successfully sent command: " + command ,description=response, color=0xFF6F00)

                channel = client.get_channel(serverBot)
                await channel.send(embed=successEmbed)
            
            except Exception:
                channel = client.get_channel(serverBot)
                await channel.send("Failed Command: " + command)
        
        else:
            channel = client.get_channel(serverBot)
            await channel.send("Permission Denied.")


    if message.content.startswith(">start"):

        userid = message.author.id

        if (message.channel.id == serverBot) and (userid in admin):

            retryAttempts = 0
            await demo_start(retryAttempts)

            try:
                # Warmup End
                response = await execCommand("mp_warmup_end")
                warmupEndEmbed = discord.Embed(title="Warmup Ended", description=response, color=0xFF6F00)
                channel = client.get_channel(serverBot)
                await channel.send(embed=warmupEndEmbed) 
            except:
                channel = client.get_channel(serverBot)
                await channel.send("Failed Warmup End.")

            retryAttempts = 0
            await get_stats(retryAttempts)


    if message.content.startswith(">end"):

        userid = message.author.id

        if (message.channel.id == serverBot) and (userid in admin):

            response = await execCommand("tv_stoprecord")

            DemoEndEmbed = discord.Embed(title="Demo Stopped", description=response, color=0xFF6F00)

            channel = client.get_channel(serverBot)
            await channel.send(embed=DemoEndEmbed)

            GameFinished = discord.Embed(title="Game Finished", color=0xFF6F00)

            channel = client.get_channel(mainChannel)
            await channel.send(embed=GameFinished)


    if message.content.startswith(">map "):

        userid = message.author.id
        access = (userid in admin)

        if (message.channel.id == serverBot) and access == True:  

            workshopid = message.content[5:]

            try:
                await changeMap(workshopid)

                try:

                    (name, workshop_link, thumbnail, filename) = get_mapinfo(workshopid)

                    # Creating Embed.
                    embed = discord.Embed(title="Successfully Changed Map to: " + str(name), color=0xFF6F00)
                    embed.url = workshop_link
                    embed.set_image(url=thumbnail)
                    embed.set_footer(text="Map ID: " + workshopid + "     " + "File Name: " + filename)

                except Exception:
                    embed = discord.Embed(title="Successfully Changed Map to: " + str(workshopid), color=0xFF6F00)

                channel = client.get_channel(serverBot)
                await channel.send(embed=embed)

                
            
            except Exception:
                channel = client.get_channel(serverBot)
                await channel.send("Failed Change Map to: " + workshopid)

        else:
            channel = client.get_channel(serverBot)
            await channel.send("Permission Denied.")


    if message.content.startswith(">captains"):

        try:
            msgSent = message.channel.id
            channel = client.get_channel(843598844758982666)

            members = channel.members 

            memNames = []
            for member in members:
                memNames.append(member.name)

            printMembers = (', '.join(memNames))

            embed = discord.Embed(title="Captain Picker", description="A random captain picker.", color=0xFF6F00)
            embed.add_field(name="Voice Members", value=printMembers, inline=False)

            cap1 = (random.choice(memNames))


            if len(memNames) > 1:

                memNames.remove(cap1)
                cap2 = (random.choice(memNames))

            else:
                cap2 = "Not Enough Members."

            
            embed.add_field(name="Captain 1", value=cap1, inline=False)
            embed.add_field(name="Captain 2", value=cap2, inline=False)
            

        except Exception:
            embed = discord.Embed(title="Failed", color=0xFF6F00)

        channel = client.get_channel(msgSent)
        await channel.send(embed=embed)


    if message.content.startswith(">schedule "):

        userid = message.author.id
        time = message.content[10:]
        access = userid in admin
        
        if access == True:
            
            ScheduleEmbed = discord.Embed(title="10 Man", description="Join a 10 Man!", color=0xFF6F00)
            ScheduleEmbed.set_thumbnail(url="https://imgur.com/vUG7MDU.png")
            ScheduleEmbed.add_field(name="Time:", value=time + " CEST", inline=False)
            ScheduleEmbed.add_field(name="Countdown:", value="Starting in", inline=False)
            ScheduleEmbed.set_footer(text="???? or  ???? to join or leave 10 man.            ")

            channel = client.get_channel(843111309058899998)
            scheduleMsg = await channel.send("<@&843565546004021297>", embed=ScheduleEmbed)

            await scheduleMsg.add_reaction('????')
            await scheduleMsg.add_reaction('????')

            timer.start(scheduleMsg, time)

        else:
            channel = client.get_channel(843111309058899998)
            await channel.send("Access Denied.")


    if message.content.startswith(">help"):

        embed = discord.Embed(title="BotCrayon", description="I am used to reserve the server to the community.", color=0xFF6F00)
        embed.set_thumbnail(url="https://i.imgur.com/laJnwhg.png")

        embed.add_field(name=">help", value="Displays this embed.", inline=False)
        
        embed.add_field(name=">commands", value="Displays a list of commands sendable through rcon.", inline=False)
        embed.add_field(name=">captains", value="Picks Random Captains.", inline=False)

        embed.add_field(name="__Admin:__", value="Admin Commands.", inline=False)

        embed.add_field(name=">map [WorkshopID]", value="Changes map to Workshop ID", inline=False)
        embed.add_field(name=">warmup", value="Extends Warrmup Time and Starts Warmup", inline=False)
        embed.add_field(name=">start", value="Starts Game and Records Demo", inline=False)
        embed.add_field(name=">stop", value="Stops Demo", inline=False)
        
        embed.set_footer(text="BotCrayon made by CommonCrayon")


        channel = client.get_channel(serverBot)
        await channel.send(embed=embed) 


    if message.content.startswith(">commands"):

        embed = discord.Embed(title="BotCrayon", description="List of Commands used by Rcon", color=0xFF6F00)
        embed.set_thumbnail(url="https://i.imgur.com/laJnwhg.png")
        embed.add_field(name=">map  [WorkshopID]", value="Changes Map using WorkshopID", inline=False)
        
        embed.add_field(name=">rcon mp_warmup_start", value="Starts Warmup", inline=False)
        embed.add_field(name=">rcon mp_warmuptime [Seconds]", value="Sets the length of warmup.", inline=False)
        embed.add_field(name=">rcon mp_warmup_end", value="Ends Warmup", inline=False)

        embed.add_field(name=">rcon exec [Script]", value="Executes script. Eg >rcon exec gamemode_competitive", inline=False)
        embed.add_field(name=">rcon exec prac", value="Practice Config", inline=False)
        embed.add_field(name=">rcon exec surf, kz, bhop", value="For Said Settins", inline=False)

        embed.add_field(name=">rcon tv_record [DemoName]", value="Starts to Record Demo.", inline=False)
        embed.add_field(name=">rcon tv_stoprecord", value="Stops Recording Demo.", inline=False)
        
        embed.set_footer(text="BotCrayon made by CommonCrayon")


        channel = client.get_channel(serverBot)
        await channel.send(embed=embed) 

        

# Bot Token
token_file = open("bot_token.txt")
token = token_file.read()
client.run(token)