import discord
from discord import app_commands
from discord.ui import Button, View
from dotenv import load_dotenv
import random
import os
import aiohttp  # Import aiohttp for async HTTP requests

# Constants
EMBED_COLOR = 0xE67389
MY_GUILD = discord.Object(id=935395948727779328)  # Replace with your guild ID

class MyBot(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

intents = discord.Intents.default()
client = MyBot(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')
    await client.setup_hook()

def random_picture_embed():
    seed = random.random()
    embed = discord.Embed(title="Random Picture From The Web", color=EMBED_COLOR)
    embed.set_image(url=f"https://picsum.photos/seed/{seed}/300/300")
    return embed

class RandPic(View):
    def __init__(self):
        super().__init__()
        self.message = None
        self.add_item(Button(label="Donate👉💰", url="https://www.paypal.me/tipmebig", style=discord.ButtonStyle.link))

    def set_message(self, message):
        self.message = message

    async def on_timeout(self):
        if self.message:
            for item in self.children:
                item.disabled = True
            await self.message.edit(view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == interaction.message.interaction.user.id

    @discord.ui.button(label="🔄", style=discord.ButtonStyle.blurple, custom_id="rand-pic")
    async def new_picture(self, interaction: discord.Interaction, button: Button):
        embed = random_picture_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Cannabis🌿", style=discord.ButtonStyle.green, custom_id="cannabis-pic")
    async def cannabis_pic(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        embed = await get_cannabis_picture_embed()
        await interaction.edit_original_response(embed=embed, view=self)
        
@client.tree.command(name="random-pic", description="Random Pics from The Web")
async def random_pic(interaction: discord.Interaction):
    embed = random_picture_embed()
    view = RandPic()
    message = await interaction.response.send_message(embed=embed, view=view)
    view.set_message(message)

async def get_cannabis_picture_embed():
    async with aiohttp.ClientSession() as session:
        unsplash_endpoint = 'https://api.unsplash.com/photos/random'
        access_key = os.getenv('ACCESS_KEY')

        if not access_key:
            return discord.Embed(title="Error", description="Unsplash ACCESS_KEY not found. Please check your .env file.", color=0xFF0000)

        params = {'query': 'cannabis', 'client_id': access_key}
        try:
            async with session.get(unsplash_endpoint, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    image_url = data['urls']['regular']
                    return discord.Embed(title='Random Cannabis Photo', color=EMBED_COLOR).set_image(url=image_url)
                else:
                    return discord.Embed(title="Error", description="Error fetching photo. Please try again later.", color=0xFF0000)
        except Exception as e:
            return discord.Embed(title="Error", description=f"An error occurred: {e}", color=0xC80027)

# Run the bot
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
if token:
    client.run(token)
else:
    print("No token found. Please check your .env file.")
