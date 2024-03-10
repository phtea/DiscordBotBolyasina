import disnake
from disnake.ext import commands

class PaginatorCog(disnake.ui.View):
    current_page : int = 1
    sep : int = 5
    last_page : int = 1

    def __init__(self, data, title):
        super().__init__()
        self.data = data
        self.title = title
        self.last_page = int(len(self.data) / self.sep) + 1


    async def send(self, ctx):
        self.message = await ctx.send(view=self)
        await self.update_message(self.data[:self.sep])

    def create_embed(self, data):
        embed = disnake.Embed(title=self.title, colour=disnake.Color.dark_teal())
        for item in data:
            embed.add_field(name=item, value=item, inline=False)
        return embed            

    def update_buttons(self):
        if self.current_page == 1:
            self.first_page_button.disabled = True
            self.previous_page_button.disabled = True
        else:
            self.first_page_button.disabled = False
            self.previous_page_button.disabled = False
        if self.current_page == self.last_page:
            self.last_page_button.disabled = True
            self.next_page_button.disabled = True
        else:
            self.last_page_button.disabled = False
            self.next_page_button.disabled = False


    async def update_message(self, data):
        self.update_buttons()
        await self.message.edit(embed=self.create_embed(data).set_footer(text=f'Page {self.current_page} of {int(len(self.data) / self.sep) + 1}'), view=self)

    @disnake.ui.button(label='|<',
                       style=disnake.ButtonStyle.primary)
    async def first_page_button(self, button:disnake.ui.Button, interaction:disnake.Interaction):
        await interaction.response.defer()
        self.current_page = 1
        until_item = self.current_page * self.sep
        await self.update_message(self.data[:until_item])

    @disnake.ui.button(label='<',
                       style=disnake.ButtonStyle.primary)
    async def previous_page_button(self, button:disnake.ui.Button, interaction:disnake.Interaction):
        await interaction.response.defer()
        self.current_page -= 1
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(self.data[from_item:until_item])

    @disnake.ui.button(label='>',
                       style=disnake.ButtonStyle.primary)
    async def next_page_button(self, button:disnake.ui.Button, interaction:disnake.Interaction):
        await interaction.response.defer()
        self.current_page += 1
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(self.data[from_item:until_item])

    @disnake.ui.button(label='>|',
                       style=disnake.ButtonStyle.primary)
    async def last_page_button(self, button:disnake.ui.Button, interaction:disnake.Interaction):
        await interaction.response.defer()
        self.current_page = self.last_page
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(self.data[from_item:])