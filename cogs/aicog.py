import disnake
from disnake.ext import commands
from freeGPT import AsyncClient
from io import BytesIO
from PIL import Image
from modules.utils import chunked_send

class AICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ask', aliases=['аск', 'фыл'], help='Спросите искуственный интеллект')
    async def chat(self, ctx, *, prompt):
        try:
            resp = await AsyncClient.create_completion("gpt3", prompt)
        except Exception as e:
            resp = f'error: {e}'
        await chunked_send(ctx, resp)
        
    @commands.command(name='aipic', aliases=['аипик', 'фшзшс'], help='Спросите картинку у искусственного интеллекта')
    async def give_picture(self, ctx, *, prompt):
        try:
            
            resp = await AsyncClient.create_generation("prodia", prompt)
            image = Image.open(BytesIO(resp))
            # Save the image to a BytesIO buffer
            image_bytes = BytesIO()
            image.save(image_bytes, format='PNG')
            # Seek to the beginning of the buffer
            image_bytes.seek(0)
            # Send the image along with the response
            await ctx.send(file=disnake.File(image_bytes, filename='image.png'))
        except Exception as e:
            print(f"aipic: {e}")
            await ctx.send(f"An error occurred: {e}")
        finally:
            # Close the BytesIO buffer
            image_bytes.close()




def setup(bot):
    bot.add_cog(AICog(bot))
