# dependencies: all imports + kaleido
from asyncio.tasks import sleep
import discord
from discord import member
from discord import emoji
from discord.channel import DMChannel
from discord.ext import commands
from discord.ext.commands.errors import CommandInvokeError, CommandNotFound, MissingAnyRole, MissingRequiredArgument, MissingRole, UnexpectedQuoteError
from requests.api import get
from discord_components import Button, DiscordComponents
import yfinance as yf
import plotly.express as px
import random
import datetime
from datetime import date
from discord.ext import tasks
import asyncio

# IMPORTANT: the server the bot runs on is 4 hours ahead of EST time and 5 hours ahead of CST time.

intents = discord.Intents.default()
intents.reactions = True

client = commands.Bot(command_prefix = '$', intents=intents)
client.remove_command('help')
DiscordComponents(client)

async def easter_egg():
    print('Easter egg sequence activated.')
    # better to use loop than recursion as new thread would be added with recursion
    while True:
        print('Checking if current hour is 11 AM EST.')
        current_time = datetime.datetime.now().time()
        current_time_array = str(current_time).split(':')
        # 11AM eastern time
        if int(current_time_array[0]) == 15:
            # chit-chat channel id
            channel = client.get_channel(751504980606713891)
            await channel.send('What is my purpose?')
            await asyncio.sleep(3600)
        else:
            # wait for an hour to check again
            await asyncio.sleep(3600)

@client.event
async def on_ready():
    print('Bot is ready!')
    # TODO: uncomment for addition of new timed tasks
    # loop = asyncio.get_event_loop()
    # TODO: uncomment for addition of new timed tasks
    # easter_egg_task = loop.create_task(easter_egg())
    # weekly_poll_task = loop.create_task(weekly_poll())
    # TODO: when adding weekly poll, add to the wait task below.
    # await asyncio.wait([])

# TODO: expand on this (send message to channel)
@client.event
async def on_member_remove(member):
    print(f'{member} is gone!')

@client.event
async def on_member_join(member):
    # welcome channel id
    channel = client.get_channel(738557213471408228)
    await channel.send(f'Welcome {member} to the RexFinance Discord! Please review the #rules and reach out to a Moderator if you have questions!')

# begin commands
@client.command()
async def hello(context):
    await context.send('Hello there!')

@client.command()
async def donate(context):
    await context.send('I am working on this bot in my own spare time unpaid. I am happy to work for free, ' 
    'however I would more than welcome a generous donation from you! Simply click the button below to donate using Venmo or PayPal.\n\n'
    'Thanks for being a part of RexNation - *Rex\'s Twin*', components=[[Button(label='Donate Using Venmo', style=5, url='https://venmo.com/u/samwbriggs'),\
    Button(label='Donate Using Paypal', style=5, url='https://paypal.me/samwbriggs?country.x=US&locale.x=en_US')]])

@client.command()
async def motivation(context):
    await context.message.delete()
    # give a list of random responses
    quotes = ['*\"An investment in knowledge pays the best interest.\"* - Benjamin Franklin',
              '*\"I will tell you how to become rich. Close the doors. Be fearful when others are greedy. Be greedy when others are fearful.\"* - Warren Buffett',
              '*\"Given a 10% chance of a 100 times payoff, you should take that bet every time.\"* - Jeff Bezos',
              '*\"I don\'t look to jump over seven-foot bars; I look around for one-foot bars that I can step over.\"* - Warren Buffett',
              '*\"In investing, what is comfortable is rarely profitable.\"* - Robert Arnott',
              '*\"The biggest risk of all is not taking one.\"* - Mellody Hobson',
              '*\"Know what you own, and know why you own it.\"* - Peter Lynch',
              '*\"Wide diversification is only required when investors do not understand what they are doing.\"* - Warren Buffett',
              '*\"Great companies are built on great products\"* - Elon Musk',
              '*\"I think it is possible for ordinary people to choose to be extraordinary.\"* - Elon Musk',
              '*\"I could either watch it happen or be a part of it.\"* - Elon Musk',
              '*\"Persistence is very important. You should not give up unless you are forced to give up.\"* - Elon Musk',
              '*\"Scared money don\'t make money\"* - RexFinance']
    await context.send(f'{context.author.mention}, ' + random.choice(quotes))

@client.command()
async def search(context, ticker):
    current_price = get_price(ticker)
    daily_percentage = get_daily_percent(ticker) * 100
    # if the percentage is positive, add a plus before the percent to show it
    if(daily_percentage > 0):
        daily_percentage_str = '+' + str(round(daily_percentage, 2))
    else:
        daily_percentage_str = str(round(daily_percentage, 2))
    get_graph(ticker, daily_percentage)

    # tell user if after-hours
    weekday = datetime.date.today().weekday()
    current_time = datetime.datetime.now().time()
    current_time_array = str(current_time).split(':')
    if weekday < 5:
        if((int(current_time_array[0]) >= 21 and int(current_time_array[0]) <= 23)) or int(current_time_array[0] == 1) or int(current_time_array[0] == 0):
            await context.send('The current price of **' + ticker.upper() + '** is: **{}'.format(round(current_price, 4)) + ' (' + daily_percentage_str + ')**\n It is currently after-hours. *Prices may move slightly during this time.*', file = discord.File("Images/img1.png"))
        elif(int(current_time_array[0]) > 9 and (int(current_time_array[0]) < 14 and int(current_time_array[1]) < 30)):
            await context.send('The current price of **' + ticker.upper() + '** is: **{}'.format(round(current_price, 4)) + ' (' + daily_percentage_str + ')**\n It is currently pre-market trading hours. *Prices may move slightly during this time.*', file = discord.File("Images/img1.png"))
        else:
            await context.send('The current price of **' + ticker.upper() + '** is: **{}'.format(round(current_price, 4)) + ' (' + daily_percentage_str + ')**\n', file = discord.File("Images/img1.png"))
    else:
        # it's the weekend!
        await context.send('The current price of **' + ticker.upper() + '** is: **{}'.format(round(current_price, 4)) + ' (' + daily_percentage_str + ')**\n It is currently the weekend!🥳 *Most prices will not move until market open on Monday morning.*', file = discord.File("Images/img1.png"))

@client.command()
@commands.has_any_role('Administrator', 'Moderator')
async def clear(context, n = 2):
    await context.channel.purge(limit = n)

# TODO (Improvement?): private message the caller instead of having them type everything on one line.
# TODO: only one poll can exist IN ANY server at a time. Should this be changed?
@client.command()
@commands.max_concurrency(1, per = commands.BucketType.default, wait = False)
async def poll(context, question, option_list, time = '1'):
    # delete message to create poll
    await context.message.delete()

    # option_list is taken in as a string, but tokenized by a ','
    if not option_list:
        await context.send('Options required.')
        return

    for char in time:
        if char.isdigit():
            is_number = True
        else:
            is_number = False
            break
    
    if is_number == False:
        await context.send('You cannot use alpha-numeric characters when specifying time-frame.')
        return
    if int(time) > 4:
        await context.send('As of right now, polls are limited to 4 hours. Please try again with a smaller time-frame.')
        return
    if int(time) <= 0:
        await context.send('You cannot host a poll for less than 1 hour!')
        return
    current_time = datetime.datetime.now().time()
    current_time_array = str(current_time).split(':')
    if (int(current_time_array[0]) + int(time) >= 29 or (int(current_time_array[0]) + int(time) >= 5 and int(current_time_array[0]) < 5)):
        await context.send('Due to the bot restarting at midnight, your poll cannot be created. Either wait until then, or lower your time-frame.')
        return
    options = option_list.split(',')
    if len(options) < 2:
        await context.send('Too few options were given.')
        return
    if len(options) > 4:
        await context.send('Too many poll options were given. (Polls are currently limited to 4 options!)')
        return
    
    formatted_options = ''
    i = 1
    for option in options:
        formatted_options += str(i) + '. ' + option + '\n'
        i += 1
    
    em = discord.Embed(title = 'Poll: ' + question, description = formatted_options + f'\n*Asked by* {context.author.mention}', colour = 0xFF8700)
    poll_title = em.title
    # ping everyone automatically
    poll = await context.send('@everyone', embed = em)
    poll_id = poll.id
    
    if len(options) == 4:
        await poll.add_reaction('1️⃣')
        await poll.add_reaction('2️⃣')
        await poll.add_reaction('3️⃣')
        await poll.add_reaction('4️⃣')
    elif len(options) == 3:
        await poll.add_reaction('1️⃣')
        await poll.add_reaction('2️⃣')
        await poll.add_reaction('3️⃣')
    elif len(options) == 2:
        await poll.add_reaction('1️⃣')
        await poll.add_reaction('2️⃣')

    time_in_seconds = int(time) * 3600

    # create a task that can be cancelled by a different command
    sleep_task = asyncio.ensure_future(poll_sleep(time_in_seconds))
    sleep_task.set_name('sleep_task')
    # boolean to see if task was cancelled
    sleep_task_cancelled = await sleep_task

    if sleep_task_cancelled == False:
        await poll.delete()
        await context.send('The existing poll was cancelled!')
        return

    update_message_cache = discord.utils.get(client.cached_messages, id=poll_id)
    reactions = update_message_cache.reactions
    total_reaction_count = 0
    reaction_percentages = []
    reaction_counts = []
    for reaction in reactions:
        if reaction.emoji != '1️⃣' and reaction.emoji != '2️⃣' and reaction.emoji != '3️⃣' and reaction.emoji != '4️⃣':
            # remove any reaction that isn't one for options
            reactions.remove(reaction)
            continue
        else:
            # subtract one for bot reaction
            total_reaction_count += reaction.count - 1

    if total_reaction_count == 0:
        await poll.delete()
        await context.send('No one voted on **' + poll_title + '**!')
        return
    else:
        # convert reactions to percentages
        for reaction in reactions:
            percentage = round((reaction.count - 1)/total_reaction_count * 100)
            reaction_percentages.append(percentage)
            reaction_counts.append(reaction.count - 1)
        await poll.delete()

        # print results
        message_results = ''
        index = 0
        for option in options:
            message_results += '**' + str(reactions[index]) + ' ' + options[index] + '**' + ': ' + str(int(reaction_percentages[index])) + '%. ' +\
            '(' + str(int(reaction_counts[index])) + ' Votes)'
            # if winner, add trophy
            if reaction_percentages[index] == max(reaction_percentages):
                message_results += '🏆\n'
            else:
                message_results += '\n'
            index += 1
    
        await context.send('Results for **' + poll_title + f'**\n*Asked by* {context.author.mention}\n\n' + message_results)

async def poll_sleep(time_in_seconds):
    try:
        await asyncio.sleep(time_in_seconds)
        return True
    except asyncio.CancelledError:
        print('Cancelled the existing poll!')
        return False

# loop through existing tasks, and if sleep_task is found cancel it
@client.command()
@commands.has_any_role('Administrator', 'Moderator')
async def pollcancel(context):
    for task in asyncio.all_tasks():
        if task.get_name() == 'sleep_task':
            task.cancel()
# end commands

# begin help commands
@client.group(invoke_without_command = True)
async def help(context):
    em = discord.Embed(title = 'Help', description = 'To get more details about a command, type **$help [command]**.')

    em.add_field(name = 'Commands:', value = '$help\n $donate\n $hello\n $search\n $clear\n $poll\n $pollcancel\n')
    em.add_field(name = 'Temporary:', value = 'No current temporary commands!\nThese usually appear with holiday updates.')
    await context.send(embed = em)

@help.command()
async def hello(context):
    em = discord.Embed(title = 'Hello', description = 'The bot gives a friendly greeting to you!')

    em.add_field(name = 'Syntax: ', value = '$hello')
    await context.send(embed = em)

@help.command()
async def donate(context):
    em = discord.Embed(title = 'Donate', description = 'An easy way to support my work is by giving a generous donation! Currently accepting Venmo.')

    em.add_field(name = 'Syntax: ', value = '$donate')
    await context.send(embed = em)

@help.command()
async def search(context):
    em = discord.Embed(title = 'Search', description = 'Give the bot a ticker symbol, and it will find the latest up-to-date price in the stock-market!')

    em.add_field(name = 'Syntax: ', value = '$search [ticker]')
    await context.send(embed = em)

@help.command()
async def clear(context):
    em = discord.Embed(title = 'Clear', description = 'The bot clears a specified amount of messages in the channel. If no number is given, it will delete one message.')

    em.add_field(name = 'Syntax: ', value = '$clear **or** $clear [number of messages]')
    await context.send(embed = em)

@help.command()
async def poll(context):
    em = discord.Embed(title = 'Poll', description = 'The bot creates a poll that users can react to for a given time-frame. If no number for the time-frame is given, it will default to 1 hour. Only one poll can exist at a time.\n\n To participate in a poll, simply react to which number corresponds to your answer on the message below the poll. The number reactions should automatically be added for you to click or tap on.')

    em.add_field(name = 'Syntax: ', value = '$poll ["poll question"] ["comma-delimited list of options" (max of 4, min of 2)] **or** $poll ["poll question"] ["comma-delimited list of options" (max of 4, min of 2)] [number in hours how long poll should last (max of 4)]')
    await context.send(embed = em)

@help.command()
async def pollcancel(context):
    em = discord.Embed(title = 'PollCancel', description = 'The bot cancels an active poll.')

    em.add_field(name = 'Syntax: ', value = '$pollcancel')
    await context.send(embed = em)
#end help commands

@client.event
async def on_command_error(context, error):
    # if a user types a command that isn't defined the bot reports it
    if isinstance(error, CommandNotFound):
        print(error)
        return
    # this may not be correct for handling incorrect ticker symbol
    if isinstance(error, CommandInvokeError):
        await context.send('Something went wrong! Please use **$help** for more information.')
        print(error)
        return
    if isinstance(error, UnexpectedQuoteError):
        await context.send('You gave me an unexpected quote. What\'s wrong with you?')
        return
    if isinstance(error, MissingRole) or isinstance(error, MissingAnyRole):
        await context.send('You don\'t have the required role to use this command.')
        return
    if isinstance(error, MissingRequiredArgument):
        await context.send('Required arguments are missing for this command! Please type \'$help\' for more information.')
        return
    if isinstance(error, commands.MaxConcurrencyReached):
        # error only applies to the 'poll' command
        await context.send('There can only be one poll outstanding at a time! If you wish to cancel the existing poll, let a moderator know and have them use the $pollcancel command.')
        return
    raise error

def get_price(symbol):
    ticker = yf.Ticker(symbol)
    data_today = ticker.history(period='1d')
    return data_today['Close'][0]

def get_daily_percent(symbol):
    ticker = yf.Ticker(symbol)
    previous_close = ticker.history(period='2d')
    current_close = get_price(symbol)
    return ((current_close/previous_close) - 1)['Close'][0]

# return a line chart of a stock of a period of one day!
def get_graph(ticker, daily_percentage):
    data = yf.download(tickers = ticker, period = '1d', interval = '1m')
    figure = px.line(x = data.index, y = data.Close, labels = {'x':'', 'y':''})
    # Decide what color the line should be based off of negative or positive
    if(daily_percentage > 0):
        # normal green
        figure.update_traces(line_color = '#1CE912')
        figure.update_layout({'title_font_color': '#FF8700'})
    else:
        # normal red
        figure.update_traces(line_color = '#E91212')
        figure.update_layout({'title_font_color': '#7C00FF'})

    figure.update_layout({
        'plot_bgcolor': 'rgba(25, 25, 25, 0)',
        'paper_bgcolor': 'rgba(25, 25, 25, 1)',
        'xaxis_color': 'rgba(220, 221, 222, 1)',
        'yaxis_color': 'rgba(220, 221, 222, 1)',
    })
    
    figure.write_image("Images/img1.png", scale = 2)
    
    # MacOS: /Users/sambriggs/Documents/DiscordBot/Images/img1.png
    # PC: C:\DiscordBot\Images\img1.png
    # PebbleHost: Images/img1.png
    return

client.run('<SuperSecretKey>')
# Main: <SuperSecretKey>
# Beta: <SuperSecretKey>
