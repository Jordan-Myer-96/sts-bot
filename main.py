import discord
import aiohttp
import openai
import os
import random
import giphy_client
import requests
from titlecase import titlecase
from dotenv import load_dotenv
from discord.ext import commands
from giphy_client.rest import ApiException
from bs4 import BeautifulSoup
import re
from sympy import limit
#Change

load_dotenv()

hype_phrases = ["LET'S GO","WOOOOOO!!!!","I'M SO HYPED","I CAN'T WAIT",
                "IT'S HAPPENING—EVERYONE STAY CALM","YESSSSSS","FINALLY, I'VE BEEN WAITING ALL DAY",
                "WHEN IT'S FINALLY QUIZ TIME","THIS IS GOING TO BE SO LIT","I'M PUMPED","YOU ALREADY KNOW WHAT TIME IT IS"]

# Retrieve the Discord bot token from the environment
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


# Retrieve the OpenAI API key from the environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def generate_openai_response(question):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=question,
        max_tokens=150  # Adjust the maximum response length as needed
    )
    return response.choices[0].text


GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")


# Check if either token is missing
if not DISCORD_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Discord bot token or OpenAI API key not found in .env file")

# Define your desired intents. For example, to receive message events, use:
intents = discord.Intents.default()
intents.message_content = True


# Create an instance of the Bot class with intents
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')


@bot.command()
async def hello(ctx):
    await ctx.send("Hello, I'm your bot!")


# Define a custom command
@bot.command()
async def sts(ctx, *, query):
    # Convert the query to title case and replace spaces with underscores
    command = re.sub(r'\s+', '_', titlecase(query))
    
    # Create an HTTP session using aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://slay-the-spire.fandom.com/wiki/{command}") as response:
            if response.status == 200:
                # Parse the HTML content using BeautifulSoup
                soup = BeautifulSoup(await response.text(), 'html.parser')


                # Extract data from the HTML using BeautifulSoup
                img = soup.find(class_='pi-image-thumbnail')['src']
                title = soup.find(class_='page-header__title').text


                # Create an embed for the response
                embed = discord.Embed(
                    title=title,
                    color=0xf2ca4e,
                    url=f"https://slay-the-spire.fandom.com/wiki/{command}"
                )
                embed.set_image(url=img)


                # Extract and add fields from .pi-data elements
                pi_data_elements = soup.find_all(class_='pi-data')
                for pi_data in pi_data_elements:
                    label = pi_data.find(class_='pi-data-label').text
                    value = pi_data.find(class_='pi-data-value').text
                    embed.add_field(name=label, value=value, inline=True)


                # Send the embed in the Discord channel
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"The wiki search was https://slay-the-spire.fandom.com/wiki/{command}")
                await ctx.send(f"I'm afraid I didn't find what you were looking for. Failed with error code {response.status}")

@bot.command()
async def ask(ctx, *, question):
    try:
        response = generate_openai_response(question)
        await ctx.send(response)
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# You'll need to set up your Discord.py bot and command handling separately
# Assuming `bot` is your Discord.py bot instance, you can add your command like this:
@bot.command()
async def your_discord_command(ctx):
    await sts(ctx)


async def quiztime(ctx,title, *,q="super excited"):

    api_key = GIPHY_API_KEY
    api_instance = giphy_client.DefaultApi()
    
    try:

        api_response = api_instance.gifs_search_get(api_key,q,limit = 10, rating = "g")
        lst = list(api_response.data)
        giff = random.choice(lst)

        embed = discord.Embed(title=title)
        embed.set_image(url = f"https://media.giphy.com/media/{giff.id}/giphy.gif")

        await ctx.channel.send(embed=embed)

    except ApiException as r:
        print("Exception for the api")

@bot.event
async def on_message(message):
    # Check if the message is not sent by the bot itself
    if not message.author.bot:
        if "quiz time" in message.content.lower() or "quiztime" in message.content.lower():
            if message.content.startswith('!'):
                title = random.choice(hype_phrases)
            else: 
                title = "DID SOMEONE SAY QUIZ TIME?!?!?!"
            ctx = await bot.get_context(message)
            await quiztime(ctx, title = title)
            # Respond to the message
            #await ctx.invoke(bot.get_command('quiztime'), title=title,q = "super excited")


bot.run(DISCORD_TOKEN)

