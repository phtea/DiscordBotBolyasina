from typing import Any, Dict, List
import disnake
from disnake.ext import commands
import yt_dlp

import constants.emojis as Emojis

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients: Dict[int, disnake.VoiceClient] = {}
        self.queues: Dict[int, List[str]] = {}
        self.now_playing: Dict[int, str] = {}
        self.yt_dl_opts = {'format': 'bestaudio/best', 'noplaylist': 'True', 'default_search': 'auto', 'quiet': 'True', 'playlist_items': '1'}
        self.ytdl = yt_dlp.YoutubeDL(self.yt_dl_opts)
        self.ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    async def get_song_info(self, prompt):
        """
        Fetches information about a song from YouTube given a prompt.\n
        Parameters:
            prompt (str): The search query or URL of the song.
        Returns:
            Tuple[str, str]: A tuple of the URL and title of the song.
        """
        data = await self.bot.loop.run_in_executor(None, lambda: self.ytdl.extract_info(prompt, download=False))
        if not 'url' in data.keys():
            data = data['entries'][0]
        return (data['original_url'], data['title'])

    async def play_song(self, ctx, url, video_title):
        try:
            data = await self.bot.loop.run_in_executor(None, lambda: self.ytdl.extract_info(url, download=False))
            song_url = self.get_song_url_from_data(data)
            player = disnake.FFmpegPCMAudio(song_url, **self.ffmpeg_options)
            self.voice_clients[ctx.guild.id].play(player, after=lambda e: self.play_next(ctx, ctx.guild.id))
            print(f'{ctx.guild}: {video_title}')
            self.now_playing[ctx.guild.id] = video_title
            title = '🎵 Сейчас играет:'
            description = f'{video_title}\n{url}'
            colour = disnake.Color.green()
            embed = disnake.Embed(title=title,
                                description=description,
                                colour=colour)
            await ctx.send(embed=embed)
        except Exception as err:
            print("Error:", err)
            await ctx.send(f"Error: {err}")

    def get_song_url_from_data(self, data):
        if not 'url' in data.keys():
            data = data['entries'][0]
        song_url = data['url']
        return song_url

    async def voice_client_connect(self, ctx):
        try:
            voice_client = await ctx.author.voice.channel.connect()
            self.voice_clients[ctx.guild.id] = voice_client
        except Exception as e:
            print("Error:", e)

    def play_next(self, ctx, guild_id: int):
        
        async def play_next_async():
            if guild_id not in self.queues:
                return
            vc = self.voice_clients[guild_id]
            if len(self.queues[guild_id]) <= 0:
                vc.stop()
                if vc.is_playing():
                    vc.stop()
                await vc.disconnect()
                del self.voice_clients[guild_id]
                del self.queues[guild_id]
                if guild_id in self.now_playing:
                    del self.now_playing[guild_id]
                return
            next_song = self.queues[guild_id].pop(0)
            await self.play_song(ctx, next_song[0], next_song[1])
        self.bot.loop.create_task(play_next_async())

    @commands.command(name='play', aliases=['играть', 'p'], help='сыграть музыку с ютуба')
    async def play(self, ctx, *, prompt):
        msg = await ctx.send(Emojis.LOADING)
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await self.send_not_in_vc(msg)
        guild_id = ctx.guild.id
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        song = await self.get_song_info(prompt)
        title = '✅ Добавлено в очередь.'
        description = f'{song[1]} \n<{song[0]}>'
        colour = disnake.Color.green()
        embed = disnake.Embed(title=title,
                              description=description,
                              colour=colour)
        await msg.edit(embed=embed, content='')
        self.queues[guild_id].append(song)
        if not self.voice_clients.get(guild_id):
            await self.voice_client_connect(ctx)
        if not self.voice_clients[guild_id].is_playing():
            song = self.queues[guild_id].pop(0)
            await self.play_song(ctx, song[0], song[1])

    async def send_not_in_vc(self, msg) -> None:
        title = '❌ Ошибка'
        description = 'Зайдите сначала в голосовой канал 🙄'
        colour = disnake.Color.red()
        embed = disnake.Embed(title=title,
                                description=description,
                                colour=colour)
        await msg.edit(embed=embed, content='')
        return

    @commands.command(name='pause', help='пауза/продолжить')
    async def pause(self, ctx):
        msg = await ctx.send(Emojis.LOADING)
        guild_id = ctx.guild.id
        if guild_id not in self.voice_clients:
            return await self.send_not_in_vc(msg)
        vc = self.voice_clients[guild_id]
        if vc.is_playing():
            vc.pause()

        title = '✅ Музыка поставлена на паузу.'
        description = ''
        colour = disnake.Color.green()
        embed = disnake.Embed(title=title,
                              description=description,
                              colour=colour)
        await msg.edit(embed=embed, content='')

    @commands.command(name='resume', help='продолжить проигрывание')
    async def resume(self, ctx):
        msg = await ctx.send(Emojis.LOADING)
        guild_id = ctx.guild.id
        if guild_id not in self.voice_clients:
            return await self.send_not_in_vc(msg)
        vc = self.voice_clients[guild_id]
        if vc.is_paused():
            vc.resume()
        
        title = '✅ Музыка продолжена.'
        description = ''
        colour = disnake.Color.green()
        embed = disnake.Embed(title=title,
                              description=description,
                              colour=colour)
        await msg.edit(embed=embed, content='')

    @commands.command(name='stop', help='остановить проигрывание и покинуть голосовой канал')
    async def stop(self, ctx):
        msg = await ctx.send(Emojis.LOADING)
        guild_id = ctx.guild.id
        if guild_id not in self.queues:
            return await self.send_not_in_vc(msg)
        if guild_id not in self.voice_clients:
            return await self.send_not_in_vc(msg)
        vc = self.voice_clients[guild_id]
        if vc.is_playing():
            vc.stop()
        await vc.disconnect()
        if self.voice_clients[guild_id]:
            del self.voice_clients[guild_id]
        del self.queues[guild_id]
        if self.now_playing[guild_id]:
            del self.now_playing[guild_id]

        title = '✅ Музыка остановлена.'
        description = ''
        colour = disnake.Color.green()
        embed = disnake.Embed(title=title,
                              description=description,
                              colour=colour)
        await msg.edit(embed=embed, content='')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        is_bot = member == self.bot.user
        if not is_bot or after.channel or before.channel is None:
            return
        guild_id = before.channel.guild.id
        if guild_id not in self.voice_clients:
            return
        vc = self.voice_clients[guild_id]
        if vc.is_playing():
            vc.stop()
        await vc.disconnect()

        del self.voice_clients[guild_id]
        if guild_id in self.queues:
            del self.queues[guild_id]
        if guild_id in self.now_playing:
            del self.now_playing[guild_id]
        print("Я был кикнут с войса ;-;")

    @commands.command(name='queue', aliases=['q', 'оч'], help='показать очередь проигрывания')
    async def queue(self, ctx):
        msg = await ctx.send(Emojis.LOADING)
        guild_id = ctx.guild.id
        if guild_id not in self.queues or len(self.queues[guild_id])<=0:
            title = '👻 Очередь пуста.'
            description = ""
            colour = disnake.Color.yellow()
            embed = disnake.Embed(title=title,
                                description=description,
                                colour=colour)
            await msg.edit(embed=embed, content='')
            return
        queue = "\n".join(f"{i+1}. {song[1]}" for i, song in enumerate(self.queues[guild_id]))
        title = '💫 Очередь:'
        description = queue
        colour = disnake.Color.green()
        embed = disnake.Embed(title=title,
                            description=description,
                            colour=colour)
        await msg.edit(embed=embed, content='')
            

    @commands.command(name='nowplaying', aliases=['np'], help='показать текущую песню')
    async def now_playing_command(self, ctx):
        msg = await ctx.send(Emojis.LOADING)
        guild_id = ctx.guild.id
        if guild_id not in self.now_playing:
            title = '👻 Ничего не играет.'
            description = ""
            colour = disnake.Color.yellow()
            embed = disnake.Embed(title=title,
                                description=description,
                                colour=colour)
            await msg.edit(embed=embed, content='')
            return
        title = '🎵 Сейчас играет:'
        description = f"{self.now_playing[guild_id]}"
        colour = disnake.Color.green()
        embed = disnake.Embed(title=title,
                            description=description,
                            colour=colour)
        await msg.edit(embed=embed, content='')

    @commands.command(name='skip', aliases=['s'], help='Пропустить музыку')
    async def skip(self, ctx):
        msg = await ctx.send(Emojis.LOADING)
        guild_id = ctx.guild.id
        if guild_id not in self.voice_clients:
            return await self.send_not_in_vc(msg)
        self.voice_clients[guild_id].stop()
        title = '✅ Музыка пропущена.'
        description = ""
        colour = disnake.Color.green()
        embed = disnake.Embed(title=title,
                            description=description,
                            colour=colour)
        await msg.edit(embed=embed, content='')

def setup(bot):
    bot.add_cog(MusicCog(bot))