# -*- coding: euc-kr -*-
'''
discord bot


APPLICATION ID
940969912720052374

PUBLIC KEY
ac83fcedfc7e3cc92ef996eaa814062505e526e02da386509dc07c7ef50a62db

TOKEN
OTQwOTY5OTEyNzIwMDUyMzc0.YgPIhQ.8P-6mKBGk1E0h1nKM179K0FSLSY

https://discord.com/oauth2/authorize?client_id=940969912720052374
'''

#���ڵ� ���̺귯��
import discord, asyncio, os
from discord.ext import commands

#����� ���̺귯��
import random
import time
import pandas as pd
Token = 'OTQwOTY5OTEyNzIwMDUyMzc0.YgPIhQ.8P-6mKBGk1E0h1nKM179K0FSLSY'

#�� ���� ����
#discord.Activity discord.Game discord.Streaming
bot_activity_s = discord.Streaming(name="�ߵ�", url='https://www.youtube.com/watch?v=pBEAzM2TRmE')
bot_activity_g = discord.Game("��¶�� ����")
bot = commands.Bot(command_prefix='��', status=discord.Status.do_not_disturb, activity=bot_activity_g, help_command=None)


#Ŀ�ǵ� ����Ʈ
@bot.command(aliases=['�ȳ�', '����', 'Hi'])
async def Hello(ctx):
    await ctx.send("{} �ȳ�!".format(ctx.author.mention))

@bot.command(aliases=['���̽�', '�ֻ���', 'roll'])
async def Dice(ctx, number:int):
    await ctx.send("�ֻ��� ��������...")
    await ctx.send("{name}��(��) �ֻ����� ���� {dice}��(��) ����".format(name=ctx.author.mention, dice=random.randint(1, int(number))))

@bot.command(aliases=['inf', '?', '����', '��������'])
async def Information(ctx):
    members = [member.name for member in ctx.guild.members]
    await ctx.send(
        "{} ������ {} �����̸� �������� {} �̰� �� {} ���Դϴ�.".format(
            ctx.guild.name, 
            ctx.guild.region, 
            members, 
            ctx.guild.member_count
        )
    )

@bot.command(aliases=['�̸�����'])
async def emoivb(ctx, channel: discord.VoiceChannel, *, new_name):
    await channel.edit(name=new_name)

@bot.command(aliases=['����', '����', 'h'])
async def help(ctx):
    embed = discord.Embed(title="��溿", description="��! �� �δ���", color=0x4432a8)
    embed.add_field(name="1. �λ�", value="!Hello/!�ȳ�/!����/!Hi",inline=False)
    embed.add_field(name="2. ����", value="!Information/!inf/!����/!��������",inline=False)
    embed.add_field(name="3. �ֻ���", value="!Dice/!���̽�/!�ֻ���/!roll",inline=False)
    embed.add_field(name="4. ű", value="!ű",inline=False)
    embed.add_field(name="5. ��Ʈ", value="!��Ʈ",inline=False)
    embed.add_field(name="6. ��Ʈ����", value="!��Ʈ����",inline=False)
    await ctx.send(embed=embed)

@bot.command(aliases=['ű', '��', '����'])
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'User {ctx.member} has kicked.')

@bot.command(aliases=['��Ʈ'])
async def mute(ctx, member: discord.Member, *, reason=None):
    await member.edit(mute=True)
    await ctx.delte()

@bot.command(aliases=['��Ʈ����'])
async def unmute(ctx, member: discord.Member, *, reason=None):
    await member.edit(mute=False)

@bot.command(aliases=['�к���'])
async def chnick(ctx, member: discord.Member, nick):
    await member.edit(nick=nick)
    await ctx.channel.purge(limit=2) 

@bot.command(pass_context = True)
async def clean(ctx, number):
    number = int(number) #Converting the amount of messages to delete to an integer
    async for x in ctx.channel.history(limit = number+1):
        await x.delete()

@bot.command(pass_context=True)
async def checkrole(ctx, member: discord.Member):
    memberrole = member.roles
    print(memberrole)


@bot.command()
async def clear(ctx, amount=100000000):
	await ctx.channel.purge(limit=amount)       

@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()
@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()

@bot.command(aliases=['�������'])
async def printrole(ctx):
    valid_roles = [y.name.lower() for y in ctx.message.guild.roles]
    print(valid_roles)
    for i in range(len(valid_roles)):
        print(valid_roles[i])

@bot.command(aliases=['����','��'])
async def leavevc(ctx, id):
    member = await ctx.message.guild.fetch_member(id)
    await member.move_to(None)

@bot.command()
async def chlog(ctx):
    data = pd.DataFrame(columns=['content', 'time', 'author'])

    async for msg in ctx.channel.history(limit=100): # As an example, I've set the limit to 10000
        if msg.author != bot.user:                        # meaning it'll read 10000 messages instead of           
            data = data.append({'content': msg.content,
                                'time': msg.created_at,
                                'author': msg.author.name}, ignore_index=True)
    
    file_location = "MB.csv" # Set the string to where you want the file to be saved to
    data.to_csv(file_location)

@bot.command(pass_context=True)
@commands.has_role("Admin") # This must be exactly the name of the appropriate role
async def members(ctx):
    #������ 795914762004856842
    #���ۼ� 938280795506892850
    server = bot.guilds.cache.get(938280795506892850)
    memberList = server.members
    print(memberList)

@bot.command(pass_context=True, aliases=['��'])
async def addrole(ctx, member: discord.Member, role):
    rol = discord.utils.get(ctx.message.guild.roles,name=role)
    await member.add_roles(rol)
    await ctx.channel.purge(limit=1)

@bot.command(aliases=['����'])
async def createrole(ctx, role):
    await ctx.message.guild.create_role(name=role)
    valid_roles = [y.name.lower() for y in ctx.message.guild.roles]
    print(valid_roles)

@bot.command(aliases=['��������'])
async def deleterole(ctx, role):
    #find role object
    role_object = discord.utils.get(ctx.message.guild.roles, name=role)
    #delete role
    await role_object.delete()

@bot.command()
async def setrolecl(ctx, role):
    role_object = discord.utils.get(ctx.message.guild.roles, name=role)
    await role_object.edit(colour=discord.Colour(0x734721))

@bot.event
async def on_ready(): # �� ����� ����
    print('Login -', bot.user.name, bot.user.id)

@bot.event
async def on_message(ctx):
    await bot.process_commands(ctx)
    


bot.run(Token)

