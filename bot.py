import discord
import interactions
import game
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

async def send_message(message, user_message, is_private):
    try:
        response = interactions.respond(user_message, message.author.id, message.author.name)
        if response is None or len(response) == 0:
            return
        embed = discord.Embed(title=user_message[1:].capitalize(),
                              description=response,
                              color=discord.Color.blue())
        await message.author.send(embed=embed) if is_private else await message.channel.send(embed=embed)
    except Exception as e:
        await initiate_message(client.get_user(717943669801353300), "Error", e)

async def initiate_message(user: discord.User, title, message):
    try:
        embed = discord.Embed(title=title,
                              description=message,
                              color=discord.Color.blue())
        if user is not None:
            await user.send(embed=embed)
    except Exception as e:
        await initiate_message(client.get_user(717943669801353300), "Error", e)

def run_discord_bot():
    @client.event
    async def on_ready():
        print(f'{client.user} is now running.')
        await(game.start_game())

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        user_message = str(message.content)

        if len(user_message) > 0 and user_message[0] == "?":
            user_message = user_message[1:]
            await send_message(message, user_message, is_private=True)
        else:
            await send_message(message, user_message, is_private=False)
    client.run(TOKEN)
