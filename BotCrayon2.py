
import discord
from discord.ext import tasks
from discord.ext.commands import Bot

import random
import requests

guild_subscriptions = True
fetch_offline_members = True

# =================================================

from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
scheduler = BackgroundScheduler(jobstores=jobstores)
scheduler.start()

job_time = datetime.now() + timedelta(hours=1)


# =================================================

mainChannel = 854653166842150922
perms = []
admin = [277360174371438592, 114714586799800323]

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

async def reserve(userid):
    perms.append(userid)

async def unReserve(userid):
    perms.remove(userid)

def timeout(userid):
    perms.remove(userid)
    embed = discord.Embed(title="Server Reservation",description="Reservation of 1 hour has ended.", color=0xFF6F00)

    channel = client.get_channel(mainChannel)
    #await channel.send(embed=embed)  
    print("STOPPED")


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

    # User asking for help.
    if message.content.startswith(">rcon "):

        userid = message.author.id
        username = message.author

        access = (userid in perms) or (userid in admin)

        if (message.channel.id == mainChannel) and access == True:

            command = message.content[6:]

            try:
                response = await execCommand(command)
                print(response)

                successEmbed = discord.Embed(title="Successfully sent command: " + command ,description=response, color=0xFF6F00)

                channel = client.get_channel(mainChannel)
                await channel.send(embed=successEmbed)
            
            except Exception:
                channel = client.get_channel(mainChannel)
                await channel.send("Failed Command: " + command)
        
        else:
            channel = client.get_channel(mainChannel)
            await channel.send("Permission Denied.")



    if message.content.startswith(">map "):

        userid = message.author.id
        username = message.author

        access = (userid in perms) or (userid in admin)

        if (message.channel.id == mainChannel) and access == True:  

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

                channel = client.get_channel(mainChannel)
                await channel.send(embed=embed)
            
            except Exception:
                channel = client.get_channel(mainChannel)
                await channel.send("Failed Change Map to: " + workshopid)

        else:
            channel = client.get_channel(mainChannel)
            await channel.send("Permission Denied.")


    if message.content.startswith(">reserve"):

        userid = message.author.id
        username = message.author


        reservable_file = open("reservable.txt")
        reservable = reservable_file.read()

        if (len(perms) == 0):

            if reservable == "True":
                try:
                    await reserve(userid)

                    scheduler.add_job(timeout, 'date', run_date=job_time, args=[userid])

                    embed = discord.Embed(title="Server Reservation",description=str(username) + " reserved the server.", color=0xFF6F00)

                    channel = client.get_channel(mainChannel)
                    await channel.send(embed=embed)

                except Exception:
                    embed = discord.Embed(title="Server Reservation",description="Failed to reserve server.", color=0xFF6F00)

                    channel = client.get_channel(mainChannel)
                    await channel.send(embed=embed)                    

            else:
                embed = discord.Embed(title="Server Reservation", description="Disabled by Admin.", color=0xFF6F00)

                channel = client.get_channel(mainChannel)
                await channel.send(embed=embed)                

        else:
            embed = discord.Embed(title="Server Reservation", description="Server is already reserved.", color=0xFF6F00)

            channel = client.get_channel(mainChannel)
            await channel.send(embed=embed)  



    if message.content.startswith(">unreserve"):

        userid = message.author.id
        username = message.author

        access = userid in perms
        
        if access == True:

            try: 
                embed = discord.Embed(title="Server Reservation",description=str(username) + " unreserved server.", color=0xFF6F00)

                await unReserve(userid)

                channel = client.get_channel(mainChannel)
                await channel.send(embed=embed)

            except Exception:
                embed = discord.Embed(title="Server Reservation",description=str(username) + " failed to unreserve server.", color=0xFF6F00)
                channel = client.get_channel(mainChannel)
                await channel.send(embed=embed)                

        else:
            channel = client.get_channel(mainChannel)
            await channel.send("Server not reserved by: " + str(username))    


    if message.content.startswith(">captains"):

        try:
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
            embed = discord.Embed(title="Failed", description="Common Bug: If the Bot has been run after people have joined voice, the bot will not see those members.", color=0xFF6F00)

        channel = client.get_channel(mainChannel)
        await channel.send(embed=embed)        





    if message.content.startswith(">start"):

        userid = message.author.id

        access = userid in admin
        
        if access == True:
            
            f = open('reservable.txt', 'w')
            f.write("True")

            channel = client.get_channel(mainChannel)
            await channel.send("Server is Reservable.")
        else:
            channel = client.get_channel(mainChannel)
            await channel.send("Access Denied.")



    if message.content.startswith(">stop"):

        userid = message.author.id

        access = userid in admin
        
        if access == True:

            perms.clear()
            
            f = open('reservable.txt', 'w')
            f.write("False")

            channel = client.get_channel(mainChannel)
            await channel.send("Server is Not Reservable.")
        else:
            channel = client.get_channel(mainChannel)
            await channel.send("Access Denied.")



    if message.content.startswith(">help"):

        embed = discord.Embed(title="BotCrayon", description="I am used to reserve the server to the community.", color=0xFF6F00)
        embed.set_thumbnail(url="https://i.imgur.com/laJnwhg.png")

        embed.add_field(name=">help", value="Displays this embed.", inline=False)
        
        embed.add_field(name=">reserve", value="Reserves the server for 1 hour." + "\n(Bug: Currently does not notify you when the hour is finished.)", inline=False)
        embed.add_field(name=">unreserve", value="Unreserves the server.", inline=False)
        embed.add_field(name=">commands", value="Displays a list of commands sendable through rcon.", inline=False)
        embed.add_field(name=">captains", value="Picks Random Captains.", inline=False)

        embed.add_field(name="__Admin:__", value="Admin Commands.", inline=False)

        embed.add_field(name=">start", value="Enables Server Reservation.", inline=False)
        embed.add_field(name=">stop", value="Disables Server Reservation and Unreserves the Server.", inline=False)
        
        embed.set_footer(text="BotCrayon made by CommonCrayon")


        channel = client.get_channel(mainChannel)
        await channel.send(embed=embed) 



    if message.content.startswith(">commands"):

        embed = discord.Embed(title="BotCrayon", description="List of Commands used by Rcon", color=0xFF6F00)
        embed.set_thumbnail(url="https://i.imgur.com/laJnwhg.png")
        embed.add_field(name=">map  [WorkshopID]", value="Changes Map using WorkshopID", inline=False)
        
        embed.add_field(name=">rcon mp_warmup_start", value="Starts Warmup", inline=False)
        embed.add_field(name=">rcon mp_warmuptime [Seconds]", value="Sets the length of warmup.", inline=False)
        embed.add_field(name=">rcon mp_warmup_end", value="Ends Warmup", inline=False)

        embed.add_field(name=">rcon exec [Script]", value="Executes script. Eg >rcon exec gamemode_competitive", inline=False)

        embed.add_field(name=">rcon tv_record [DemoName]", value="Starts to Record Demo.", inline=False)
        embed.add_field(name=">rcon tv_stoprecord", value="Stops Recording Demo.", inline=False)
        
        embed.set_footer(text="BotCrayon made by CommonCrayon")


        channel = client.get_channel(mainChannel)
        await channel.send(embed=embed) 

        

# Bot Token
token_file = open("bot_token.txt")
token = token_file.read()
client.run(token)