import discord
import interactions
import game
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
print(TOKEN)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)
async def send_message(message, user_message, is_private):
    try:
        response = interactions.respond(user_message, message.author.id, message.author.name)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

async def initiate_message(user: discord.User, message):
    if user != None:
        await user.send(message)

def run_discord_bot():
    @client.event
    async def on_ready():
        print(f'{client.user} is now running.')
        await(game.start_game())

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        if len(user_message) > 0 and user_message[0] == "?":
            user_message = user_message[1:]
            await send_message(message, user_message, is_private=True)
        else:
            await send_message(message, user_message, is_private=False)
    client.run(TOKEN)
