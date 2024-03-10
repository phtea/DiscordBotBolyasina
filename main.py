import disnake
from disnake.ext import commands
from disnake import TextInputStyle
import asyncio
import time
import re
# Запросы
import requests
# Работа с байтами
from io import BytesIO

# Importing cogs
from cogs.aicog import AICog
from cogs.musiccog import MusicCog
from cogs.paginator import PaginatorCog
from cogs.vidtotextcog import VidToText

# Импорт модулей
import constants.config as cf
import constants.emojis as emoji

# Импорт встроенных библиотек
import random
import datetime
# dotenv

from dotenv import load_dotenv
load_dotenv()
import os
API_KEY = os.getenv("API_KEY")
BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID"))


game = disnake.Activity(name=cf.BOT_STATUS,
                        type=disnake.ActivityType.watching)

bot = commands.Bot(command_prefix=cf.PREFIX,
                   intents=disnake.Intents.all(), status=disnake.Status.dnd,
                   activity=game)

# Adding cog classes
bot.add_cog(MusicCog(bot))
bot.add_cog(AICog(bot))
bot.add_cog(VidToText(bot))

@bot.event
async def on_ready():
    print(f"Bot {bot.user} is online now!")
    print(f'Status: {game.type.name} {game.name}')
    user = bot.get_user(BOT_OWNER_ID)
    if user is None:
        return
    if user.avatar is None:
        return
    cf.BOT_OWNER_AVATAR = user.avatar.url

# удаление плохих сообщений
@bot.listen('on_message')
async def on_bad_message(message):
    for content in message.content.split():
        for censored_word in cf.CENSORED_WORDS:
            if content == censored_word:
                await message.delete()
                print(f'Было замечено плохое слово от {message.author}')

# ответ на рофл сообщение
@bot.listen('on_message')
async def on_funny_message(message):
    if 'псих' in message.content.lower():
        await message.reply('эй сам такой!!')

@bot.listen('on_message')  # наоборот
async def on_bad_word(message):
    if message.content.lower().endswith(' наоборот'):
        await message.reply(message.content[-10::-1])
        check_dm = message.channel.type == disnake.ChannelType.private
        if not check_dm:
            await message.delete()

@bot.event  # написать ошибку
async def on_command_error(ctx, error):
    print('\n', error)
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"> {ctx.author.mention}, у тебя нет прав на эту команду 🤡")
    elif isinstance(error, commands.UserInputError):
        await ctx.send(f'> Правильно будет так:\n> *{ctx.prefix}{ctx.command.name} {ctx.command.brief}*')

@bot.command(name="imposter", aliases=['sus'], help="📮")
@commands.is_owner()
async def sus(ctx, username=None):
    await ctx.message.delete()

    if username is not None:
        user = None
        for member in ctx.guild.members:
            if member.display_name == username:
                user = member
                break
        if user is None:
            await ctx.send('не нашёл :(')
            return
        user_name = user.display_name
        user_avatar = user.avatar
    else:
        user = random.choice(ctx.guild.members)
        user_name = user.display_name
        user_avatar = user.avatar
    try:
        await bot.user.edit(avatar=user_avatar, username=user_name)
        await ctx.send(f"sus")
    except:
        await ctx.send(f"не смог засаситься")

@bot.command(name="ping", aliases=['пинг'], help="проверка связи с ботом)")
async def ping(ctx):
    await ctx.send("понг")

@bot.command(name='кент', aliases=['кентяра'], brief="<@никнейм>", help="дать роль кента 🍷")
@commands.has_permissions(administrator=True)
async def giveadmin(ctx, member: disnake.Member):
    embed = disnake.Embed(
        title="опана",
        description=f"{member.mention} теперь кентяра 😎",
        color=0xff0000
    )
    embed.set_image(
        url='https://media.discordapp.net/attachments/782152878579515452/1115699035173572759/gigachad-chad_1.gif')
    embed.set_footer(text=cf.FOOTER_TEXT, icon_url=cf.BOT_OWNER_AVATAR)
    role = disnake.utils.get(member.guild.roles, id=cf.ADMIN_ROLE)
    if role is not None:
        await member.add_roles(role)
    await ctx.send(embed=embed)

@bot.command(name="answer", aliases=['ответ', 'ответить'], brief='<id_сообщения> <текст>', help='ответить челу от имени бота')
async def answer(ctx, message: disnake.Message, *, text):
    await message.reply(text)
    await ctx.message.delete()
    print('ответ был выполнен')

@bot.slash_command(name='ответить_по_айди', description='отвечу челу по айдишнику сообщения 🗿')
async def reply_by_id(ctx, message: disnake.Message, *, text):
    await message.reply(text)
    await ctx.send('x', ephemeral=True)
    print('ответ был выполнен')

@bot.command()
async def test(ctx):
    msg = await ctx.send(emoji.LOADING)
    embed = disnake.Embed(
        colour=disnake.Colour.dark_teal(),
        description='description',
        title='title')
    embed.set_author(name='phtea', url='https://www.youtube.com/@phtea_').set_footer(text='footer', icon_url='https://www.youtube.com/@phtea_')
    await msg.edit(content=None,embed=embed)

def main(bot):
    bot.run(API_KEY)
    print('Bot disconnected')

if __name__ == '__main__':
    main(bot)