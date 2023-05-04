import discord
from discord.ext import commands
import requests
import typing
import asyncio
import functools
import json

# For local streaming, the websockets are hosted without ssl - http://
HOST = 'localhost:5000'
URI = f'http://{HOST}/api/v1/generate'

config = None

with open('config.json', 'r') as cfg_file:
    config = json.loads(cfg_file.read())

assert config is not None

HOST = config.pop('host')

def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper

@to_thread
def run(prompt):
    global config
    request = config
    request['prompt'] = prompt

    print(request)

    result = ''

    try:
        response = requests.post(URI, json=request)

        if response.status_code == 200:
            result = response.json()['results'][0]['text']
            print(result)
        else:
            result =  f'*The Aragwaithi were a mistake...*\n\n(`this bot has broken down with the status code of {response.status_code}`)'
    except Exception as e:
            print(e)
            result =  f'*The Aragwaithi were a mistake...*\n\n(`this bot has broken down due to an internal error`)'
    return result

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

key = ""

with open('.key.txt', 'r') as id_file:
    key = id_file.readline()

bot = commands.Bot(command_prefix='/', intents=intents)

first_inter = False

current_character = "Mal Keshar"

chat_memory = []

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    global first_inter
    global chat_memory
    global current_character

    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    if not ('dark-hive' in message.channel.name):
        return
    
    user_name = message.author.name if message.author.nick is None else message.author.nick

    if message.content.startswith('!clearivy'):
        first_inter = False
        chat_memory.clear()
        await message.channel.send(f"`Message history reset` :face_in_clouds:")

    if not first_inter:
        first_inter = True
        await message.channel.send(f"{message.author.mention}, hi, I'm Ivyel, the Infiltrator designed by the Chaos Empire to impersonate various Iftu/AtS characters and I'm activated!")
        await message.channel.send("`Note that I may be slow to respond as I'm running locally at kabachuha's PC`")
        await message.channel.send(f"`Simulating {current_character}...` 🤖")
        await message.channel.send("`Rename your server nicknames to the characters whose role you want to play when interacting with me using Server Profile (Профиль сервера) settings`")
        await message.channel.send("`To change my role to another character print !impersonate charactername, to reset the chat use !clearivy`")
        await bot.process_commands(message)
        return

    if message.content.startswith('!impersonate'):
        ct = message.content[len('!impersonate')+1:]
        assert len(ct) > 0
        current_character = ct
        await message.channel.send(f"`Assuming the role of {current_character}.` 🕵")
        await bot.process_commands(message)
        return
    
    #proc = f"Below is a script from Wesnoth campaign After the Storm.\nWrite a response that completes {current_character}'s last line in the conversation. \n\n{user_name}: {message.content}\n{current_character}: "
    
    proc = f"Below is a script from Wesnoth campaign After the Storm.\n"

    if message.content.startswith('!proc'):
        await message.channel.send("Using the proc:")
        proctext = proc.split('\n')[0]
        await message.channel.send(f"*{proctext}*")
        await bot.process_commands(message)
        return
    
    sentence = []

    think_for_user = False #message.content.startswith('!thinkforme')

    if not think_for_user:
        chat_memory.append(f'{user_name}: {message.content}')

    chat_log = '\n'.join([proc] + chat_memory)
    chat_log += f'\n{user_name if think_for_user else current_character}:'
    print(chat_log)
    
    while len(chat_log.split()) > 180:
        chat_memory = chat_memory[1:]
        chat_log = '\n'.join([proc] + chat_memory)
        chat_log += f'\n{current_character}:'
        print(chat_log)

    if message.content.startswith('!combine'):
        chat_memory = chat_memory[:-1]
        chat_log = '\n'.join([proc] + chat_memory)
        await message.channel.send(f"Here is the chatlog I'm storing currently:\n```\n{chat_log}\n```")
        await bot.process_commands(message)
        return
    
    user_id = message.author.id
    print(message)
    print('message detected')
    
    # Check if the message contains attachments
    if len(message.attachments) > 0:
        await message.channel.send("`... Please... don’t... send pics to me...`", reference=message)
        return

    think_msg = await message.channel.send('`Thinking...`')
    response = await run(chat_log)
    print('response:')
    print(response)
    has_bug = response.startswith('*')
    if not has_bug:
        if response.startswith(' '):
            response = response[1:]
        if '\n' in response:
            response = response.split('\n')[0]

    if not has_bug:
        response = str(f'{user_name if think_for_user else current_character}: {response}').replace('\n', '')
        chat_memory.append(response)
    else:
        response = str(f'{response}').replace('\n', '')
    # send response
    await think_msg.delete()
    await message.channel.send(response, reference=message)

    # Process commands if any
    await bot.process_commands(message)

    #if think_for_user:
    #    await message.delete()

bot.run(key)
