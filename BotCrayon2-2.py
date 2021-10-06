import discord
from discord.ext import tasks
from discord.ext.commands import Bot

import random
import requests

guild_subscriptions = True
fetch_offline_members = True

# =================================================

# Server-Bot Channel
serverBot = 854653166842150922

# 10-Man Channel
mainChannel = 843111309058899998

# CommonCrayon, Thisted, Cktos, Karl
admin = [277360174371438592, 114714586799800323, 335786316782501888, 342426491675738115]


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
        return (rcon(command))

async def changeMap(workshopid):
    with RCON(SERVER_ADDRESS, PASSWORD) as rcon:
        command = ("host_workshop_map " + str(workshopid))
        return (rcon(command))

# =================================================


async def getMap():
    try:
        response = await execCommand("status")

        for item in response.split("\n"):
            if "map" in item:
                lineMap = item.strip()
            
        mapDetails = (lineMap.split("/"))
        workshopid = mapDetails[1]
        mapname = mapDetails[2]

        return(workshopid, mapname)
    
    except:
        import uuid
        return ("Failed!",uuid.uuid1())



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



#====== >START ====================================================================================================
async def demo_start():
    try:
        (workshopid, mapname) = await getMap()
        await execCommand("tv_record " + mapname)

        DemoEmbed = discord.Embed(title="Demo Started", description="Demo Name: " + mapname, color=0xFF6F00)
        channel = client.get_channel(serverBot)

        await channel.send(embed=DemoEmbed)

    except:
        channel = client.get_channel(serverBot)
        await channel.send("Failed to Start Demo.")



async def end_warmup():
    try:
        await execCommand("mp_warmup_end")
        warmupEndEmbed = discord.Embed(title="Warmup Ended", color=0xFF6F00)
        channel = client.get_channel(serverBot)
        await channel.send(embed=warmupEndEmbed) 
    except:
        channel = client.get_channel(serverBot)
        await channel.send("Failed Warmup End.")



async def get_stats():
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

        (workshopid, mapname) = await getMap()
        (name, workshop_link, thumbnail, filename) = get_mapinfo(workshopid)

        statEmbed = discord.Embed(title="10 Man", description=name, color=0xFF6F00)
        statEmbed.set_image(url=thumbnail)
        statEmbed.add_field(name="Team A", value=printTeamA, inline=True)
        statEmbed.add_field(name="Team B", value=printTeamB, inline=True)

        channel = client.get_channel(mainChannel)
        await channel.send(embed=statEmbed)

    except:
        channel = client.get_channel(serverBot)
        await channel.send("Match Start Embed Failed.")

#====================================================================================================================



client = discord.Client()



# Initiating the BotCrayon.
@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    game = discord.Game("10 Mans")
    await client.change_presence(status=discord.Status.online, activity=game)



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

            await demo_start()

            await end_warmup()

            await get_stats()


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