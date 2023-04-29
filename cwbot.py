import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

key = ""

with open('.key.txt', 'r') as id_file:
    key = id_file.readline()

bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary to store the last message sent by each user
last_messages = {}

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
    
    #proc = f"Below is a script from Wesnoth campaign After the Storm.\nWrite a response that completes {current_character}'s last line in the conversation. \n\n{user_name}: {message.content}\n{current_character}: "
    
    proc = f"Below is a script from Wesnoth campaign After the Storm.\n"
    
    sentence = []
    chat_memory.append(f'{user_name}: {message.content}')
    chat_log = '\n'.join([proc] + chat_memory)
    chat_log += f'\n{current_character}:'
    print(chat_log)
    
    while len(chat_log.split()) > 180:
        chat_memory = chat_memory[1:]
        chat_log = '\n'.join([proc] + chat_memory)
        print(chat_log)
    
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
        first_msg = f"Simulating {current_character}..."
        await message.channel.send(first_msg)
        await message.channel.send("Using the proc")
        await message.channel.send(proc)
    else:
        response = "error"
        await message.channel.send(response, reference=message)
        
        print(response)
        
        #response = response[len(chat_log):]
        
        response = str(f'\n{current_character}: {response}').replace('\n', '')
        
        # send response
        
        chat_memory.append(response)
    
    # Process commands if any
    await bot.process_commands(message)

bot.run(key)
