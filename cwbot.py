import discord
from discord.ext import commands
import requests

# For local streaming, the websockets are hosted without ssl - http://
HOST = 'localhost:5000'
URI = f'http://{HOST}/api/v1/generate'

def run(prompt):
    request = {
        'prompt': prompt,
        'max_new_tokens': 200,
        'do_sample': True,
        'temperature': 0.72,
        'top_p': 0.73,
        'typical_p': 1,
        'repetition_penalty': 1.1,
        'encoder_repetition_penalty': 1,
        'top_k': 0,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 2048,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

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
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    if not ('dark-hive' in message.channel.name):
        return
    
    user_name = message.author.name if message.author.nick is None else message.author.nick

    if message.content.startswith('!impersonate'):
        ct = message.content[len('!impersonate')+1:]
        assert len(ct) > 0
        message.channel.send(f"`Assuming the role of {current_character}.` 🕵")
        await message.channel.send(first_msg)
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
    chat_memory.append(f'{user_name}: {message.content}')
    chat_log = '\n'.join([proc] + chat_memory)
    chat_log += f'\n{current_character}:'
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
    
    if not first_inter:
        first_inter = True
        first_msg = f"{message.author.mention}, hi, I'm Ivyel and I'm activated!"
        await message.channel.send(first_msg)
        await message.channel.send(f"`Simulating {current_character}...` 🤖")
    else:
        response = run(message.content)
        print(response)
        has_bug = response.startswith('*')
        if not has_bug:
            response = response[len(proc):]
            if '\n' in response:
                response = response.split('\n')[0]
        
        if chat_log in response:
            response = response[len(chat_log):]
        
        if not has_bug:
            response = str(f'{current_character}: {response}').replace('\n', '')
        else:
            response = str(f'{response}').replace('\n', '')
        # send response
        chat_memory.append(response)
        await message.channel.send(response, reference=message)
    
    # Process commands if any
    await bot.process_commands(message)

bot.run(key)
