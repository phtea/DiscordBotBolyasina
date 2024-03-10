import disnake
from disnake.ext import commands
import cv2
import os
import yt_dlp
import asyncio
import modules.vid2text as vid2text
import constants.emojis as Emojis

class VidToText(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.yt_dl_opts = {
            'format': 'worst',
            'noplaylist': True,
            'default_search': 'auto',
            'quiet': True,
            'playlist_items': '1',
            'outtmpl': 'temp_video.mp4'  # Save the video as .mp4 format
        }

    @commands.command(name="v2t", help="Downloads a video from YouTube and converts frames to text")
    async def vid_to_text_command(self, ctx, video_url: str):
        try:
            msg = await ctx.send(Emojis.LOADING)
            
            video_file = "temp_video.mp4"

            if os.path.exists(video_file):
                os.remove(video_file)

            with yt_dlp.YoutubeDL(self.yt_dl_opts) as ydl:
                ydl.download([video_url])

            fps, frame_count = self.get_video_info(video_file)

            print("frame_count", frame_count)

            delay: float = 0.5
            step: float = fps * delay
            width: int = 80

            frames = vid2text.video_to_frames(video_file, width, step)

            print('Done. look! :D')
            for frame in frames:
                await msg.edit(f'`{frame}`')
                await asyncio.sleep(delay)
        except Exception as e:
            await ctx.send(f"Error: {e}")

    def get_video_info(self, video_file: str):
        cap = cv2.VideoCapture(video_file)  # Open the .mp4 file
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        return fps, frame_count

def setup(bot):
    bot.add_cog(VidToText(bot))