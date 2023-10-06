# dependencies: all imports + kaleido
import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandInvokeError, CommandNotFound, MissingAnyRole, MissingRequiredArgument, MissingRole, UnexpectedQuoteError
from requests.api import get
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import random
import datetime
import asyncio
from html2image import Html2Image

# IMPORTANT: the server the bot runs on is 5 hours ahead of EST time and 6 hours ahead of CST time.

intents = discord.Intents.all()
intents.reactions = True

client = commands.Bot(command_prefix = '$', intents=intents)
client.remove_command('help')

# TODO: this module spits out annoying error messages?
hti = Html2Image()

async def check_bell_ring():
    while True:
        weekday = datetime.date.today().weekday()
        current_time = datetime.datetime.now().time()
        current_time_array = str(current_time).split(':')
        # 16PM eastern time
        if int(current_time_array[0]) == 21 and int(current_time_array[1]) == 0o1 and weekday < 5:
            # cleanspark channel id
            cleanspark_channel = client.get_channel(738569186430812165)
            await get_end_of_day_msg('CLSK', cleanspark_channel)
            # flux channel id
            flux_channel = client.get_channel(890594561150287922)
            await get_end_of_day_msg('FLUX', flux_channel)
            # tesla channel id
            tesla_channel = client.get_channel(752946856593457273)
            await get_end_of_day_msg('TSLA', tesla_channel)
            # shift channel id
            shift_channel = client.get_channel(814347091455377438)
            await get_end_of_day_msg('SFT', shift_channel)
            # palantir channel id
            palantir_channel = client.get_channel(834546191043002399)
            await get_end_of_day_msg('PLTR', palantir_channel)
            # sgblocks channel id
            sgblocks_channel = client.get_channel(788482090941415424)
            await get_end_of_day_msg('SGBX', sgblocks_channel)
            # curiositystream channel id
            curiositystream_channel = client.get_channel(794716236142870579)
            await get_end_of_day_msg('CURI', curiositystream_channel)
            # humbl channel id
            humbl_channel = client.get_channel(788222389438644234)
            await get_end_of_day_msg('HMBL', humbl_channel)
            # li-cycle channel id
            li_cycle_channel = client.get_channel(862409656429183068)
            await get_end_of_day_msg('LICY', li_cycle_channel)
            # one-stop channel id
            one_stop_channel = client.get_channel(908141514562097243)
            await get_end_of_day_msg('OSS', one_stop_channel)
            # wait for an hour to check again
            await asyncio.sleep(3600)
        else:
            # wait for a minute to check again
            await asyncio.sleep(60)

async def get_end_of_day_msg(ticker, channel):
    current_price = get_price(ticker)
    current_price = round(current_price, 4)
    daily_percentage = get_daily_percent(ticker) * 100
    # if the percentage is positive, add a plus before the percent to show it
    if(daily_percentage > 0):
        daily_percentage_str = '+' + str(round(daily_percentage, 2))
    else:
        daily_percentage_str = str(round(daily_percentage, 2))
    get_graph(ticker, daily_percentage, '1d', False)

    hour_notif = check_hours(True, ticker, daily_percentage)
    # tell user if after-hours and generate html
    html_template = generate_html(ticker, current_price, daily_percentage_str, hour_notif)

    size = (1320, 1270)
    # SO MUCH BETTER :)
    hti.screenshot(html_str=html_template, save_as='img2.png', size=size)

    # the < and > disables embed preview
    live_chart_link = '<https://finance.yahoo.com/chart/{ticker}>'.format(ticker=ticker.upper())

    await channel.send(file=discord.File('img2.png'))
    await channel.send('Interactive Chart: ' + live_chart_link)
    
async def easter_egg():
    print('Easter egg sequence activated.')
    # better to use loop than recursion as new thread would be added with recursion
    while True:
        print('Checking if current hour is 11 AM EST.')
        current_time = datetime.datetime.now().time()
        current_time_array = str(current_time).split(':')
        # 11AM eastern time
        if int(current_time_array[0]) == 16:
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
    # check_bell_ring_task = loop.create_task(check_bell_ring())
    # easter_egg_task = loop.create_task(easter_egg())
    # weekly_poll_task = loop.create_task(weekly_poll())
    # await asyncio.wait([check_bell_ring_task])

# begin commands
@client.command()
async def hello(context):
    await context.send('Hello there!')

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
async def search(context, ticker, time_frame = '1D'):
    current_price = get_price(ticker)
    current_price = round(current_price, 4)
    daily_percentage = get_daily_percent(ticker) * 100
    # if the percentage is positive, add a plus before the percent to show it
    if(daily_percentage > 0):
        daily_percentage_str = '+' + str(round(daily_percentage, 2))
    else:
        daily_percentage_str = str(round(daily_percentage, 2))
    get_graph(ticker, daily_percentage, time_frame.upper(), False)

    if time_frame.upper() == '3M' or time_frame.upper() == '1Y' or time_frame.upper() == '5Y':
        # the price (and percentage) change will still be displayed as the daily change.
        hour_notif = 'You are currently viewing the <strong>' + time_frame.upper() + '</strong> chart. <strong>The price above still reflects the daily change.</strong>'
    else:
        hour_notif = check_hours(False, ticker, daily_percentage)
    
    # tell user if after-hours and generate html
    html_template = generate_html(ticker, current_price, daily_percentage_str, hour_notif)

    # if the hour notification is blank, shrink the screenshot size.
    if not hour_notif:
        size = (1320, 1170)
    else:
        size = (1320, 1320)
    # SO MUCH BETTER :)
    hti.screenshot(html_str=html_template, save_as='img2.png', size=size)

    # the < and > disables embed preview
    live_chart_link = '<https://finance.yahoo.com/chart/{ticker}>'.format(ticker=ticker.upper())

    await context.send(file=discord.File('img2.png'))
    await context.send('Interactive Chart: ' + live_chart_link)

@client.command()
async def candle(context, ticker, time_frame = '1D'):
    # check to see if crypto.. candles don't play nice with them in yFinance at this time!
    if '-' in ticker.upper():
        await context.send('Cryptocurrency has not yet been optimized for candle charts! Try using **$search** instead.')
        return

    current_price = get_price(ticker)
    current_price = round(current_price, 4)
    daily_percentage = get_daily_percent(ticker) * 100
    # if the percentage is positive, add a plus before the percent to show it
    if(daily_percentage > 0):
        daily_percentage_str = '+' + str(round(daily_percentage, 2))
    else:
        daily_percentage_str = str(round(daily_percentage, 2))
    get_graph(ticker, daily_percentage, time_frame.upper(), True)

    # currently the only two options for daily charts
    if time_frame.upper() == '1D' or time_frame.upper() == '1H' or time_frame.upper() == '3M' or time_frame.upper() == '1Y' or time_frame.upper() == '5Y':
        hour_notif = check_hours(False, ticker, daily_percentage)
    else:
        await context.send('Invalid time frame specified.')
        return

    # as of this time the price (and percentage) change will still be displayed as the daily change regardless of time frame.
    if not time_frame.upper() == '1D':
        hour_notif += '\n\nYou are currently viewing the <strong>' + time_frame.upper() + '</strong> chart. <strong>The price above still reflects the daily change.</strong>'

    # tell user if after-hours and generate html
    html_template = generate_html(ticker, current_price, daily_percentage_str, hour_notif)

    # if the hour notification is blank, shrink the screenshot size.
    if not hour_notif:
        size = (1320, 1170)
    else:
        size = (1320, 1320)
    # SO MUCH BETTER :)
    hti.screenshot(html_str=html_template, save_as='img2.png', size=size)

    # the < and > disables embed preview
    live_chart_link = '<https://finance.yahoo.com/chart/{ticker}>'.format(ticker=ticker.upper())

    await context.send(file=discord.File('img2.png'))
    await context.send('Interactive Chart: ' + live_chart_link)

@client.command()
@commands.has_any_role('Administrator', 'Moderator')
async def clear(context, n = 2):
    await context.channel.purge(limit = n)

# TODO: only one poll can exist IN ANY server at a time. Should this be changed?
@client.command()
@commands.max_concurrency(1, per = commands.BucketType.default, wait = False)
async def poll(context, question, option_list, time = '1'):
    # delete message to create poll
    await context.message.delete()

    #option_list is taken in as a string, but tokenized by a ','
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
    sleep_task_completed = await sleep_task

    if sleep_task_completed == False:
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

    em.add_field(name = 'Commands:', value = '$hello\n $search\n $candle\n $clear\n $poll\n $pollcancel\n')
    em.add_field(name = 'Temporary:', value = 'No current temporary commands!\nThese usually appear with holiday updates.')
    await context.send(embed = em)

@help.command()
async def hello(context):
    em = discord.Embed(title = 'Hello', description = 'The bot gives a friendly greeting to you!')

    em.add_field(name = 'Syntax: ', value = '$hello')
    await context.send(embed = em)

@help.command()
async def search(context):
    em = discord.Embed(title = 'Search', description = 'Give the bot a ticker symbol, and it will output a graph of the current price as well as a link to an interactive stock chart.')

    em.add_field(name = 'Syntax: ', value = '$search [ticker] [timeframe]')
    await context.send(embed = em)

@help.command()
async def candle(context):
    em = discord.Embed(title = 'Candle', description = 'Give the bot a ticker symbol, and it will output a candle chart of the current price as well as a link to an interactive stock chart.')

    em.add_field(name = 'Syntax: ', value = '$candle [ticker] [timeframe]')
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
    previous_close = ticker.history(period='2d')['Close'][0]
    current_close = get_price(symbol)
    return ((current_close/previous_close) - 1)

# return a line chart of a stock of a given period!
def get_graph(ticker, daily_percentage, time_frame, is_candle):
    # introduce time-frames
    if time_frame == '1H':
        data = yf.download(tickers = ticker, period = '1d', interval = '1m')
        data = data[-61:]
    elif time_frame == '3M':
        data = yf.download(tickers = ticker, period = '3mo', interval = '1d')
    elif time_frame == '1Y':
        data = yf.download(tickers = ticker, period = '1y', interval = '1d')
    elif time_frame == '5Y':
        data = yf.download(tickers = ticker, period = '5y', interval = '1d')
    else:
        data = yf.download(tickers = ticker, period = '1d', interval = '1m')

    # check if candle chart was requested
    if(is_candle == False):
        figure = px.line(x = data.index, y = data.Close, labels = {'x':'', 'y':''})
        
        # Decide what color the line should be based off of negative or positive
        if(daily_percentage > 0):
            # normal green
            figure.update_traces(line_color = '#1CE912')
            figure.update_layout({
                    'title_font_color': '#FF8700',
                    'margin': {
                            'l': 0,
                            'r': 30,
                            'b': 0,
                            't': 30
                    },
                })
        else:
            # normal red
            figure.update_traces(line_color = '#E91212')
            figure.update_layout({
                    'title_font_color': '#7C00FF',
                    'margin': {
                        'l': 0,
                        'r': 30,
                        'b': 0,
                        't': 30
                    },
                })
    else:
        figure = go.Figure(data=[go.Candlestick(x=data.index,
                open=data["Open"],
                high=data["High"],
                low=data["Low"],
                close=data["Close"])])
        
        figure.update_layout({
                'xaxis_rangeslider_visible': False,
                'margin': {
                    'l': 50,
                    'r': 30,
                    'b': 40,
                    't': 30
                },
            })

    figure.update_layout({
        'plot_bgcolor': 'rgba(25, 25, 25, 0)',
        'paper_bgcolor': 'rgba(25, 25, 25, 1)',
        'xaxis_color': 'rgba(220, 221, 222, 1)',
        'yaxis_color': 'rgba(220, 221, 222, 1)',
        'yaxis_gridcolor': 'rgba(220, 221, 222, 0.3)',
        'xaxis_gridcolor': 'rgba(220, 221, 222, 0.3)',
    })
    
    figure.write_image("img1.png", scale = 2)
    
    # MacOS: /Users/sambriggs/Documents/DiscordBot/Images/img1.png
    # PC: C:\DiscordBot\Images\img1.png
    # PebbleHost: Images/img1.png
    return

def check_hours(is_end_of_day_msg, ticker, daily_percentage):
    if is_end_of_day_msg:
        if (daily_percentage > 0):
            hour_notif = 'Finished <strong>green</strong> today.'
            return hour_notif
        else:
            hour_notif = 'Finished <strong>red</strong> today.'
            return hour_notif

    weekday = datetime.date.today().weekday()
    current_time = datetime.datetime.now().time()
    current_time_array = str(current_time).split(':')
    hour_notif = ''
    if weekday < 5:
        if((int(current_time_array[0]) >= 22 and int(current_time_array[0]) <= 24)) or int(current_time_array[0] == 2) or int(current_time_array[0] == 1):
            hour_notif = 'It is currently after-hours. <strong>Prices may move slightly during this time.</strong>'
        elif(int(current_time_array[0]) > 10 and (int(current_time_array[0]) < 15 and int(current_time_array[1]) < 30)):
            hour_notif = 'It is currently pre-market trading hours. <strong>Prices may move slightly during this time.</strong>'
    else:
        # it's the weekend!
        hour_notif = 'It is currently the weekend! <strong>Most prices will not move until market open on Monday morning.</strong>'

    return hour_notif

def generate_html(ticker, current_price, daily_percentage_str, hour_notif):
    discord_role_colors = ['#00C09A','#00D166', '#0099E1', '#A652BB', '#FD0061', '#F8C300', '#F93A2F', '#91A6A6', '#597E8D']
    rand_discord_role_color = random.choice(discord_role_colors)

    # get html to img representation
    html_template = """<!DOCTYPE html>
        <html>
        <head>
            <link rel="preconnect" href="https://fonts.googleapis.com"> 
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin> 
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@700&display=swap" rel="stylesheet">

            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
        </head>
        <body>
            <h1>{ticker}</h1>
            <p><strong>${current_price} ({daily_percentage_str})</strong></p>
            <p>{hour_notif}</p>
            <img id="graph-image" src="C:/Users/Sam/Documents/GitHub/RexFinance-Discord-Bot/img1.png" alt="Stock Graph">
        </body>
        </html>

        <style>
            body {{
                zoom: 3;
                background-color: {rand_discord_role_color};
                margin: 20px;
            }}

            h1 {{
                font-family: 'Roboto', sans-serif;
                color: white;
                margin: 0;
                padding: 0;
            }}

            p {{
                font-family: 'Montserrat', sans-serif;
                color: white;
                margin: 0;
                margin-bottom: 10px;
                padding: 0;
            }}

            #graph-image {{
                width: 400px;
                border-radius: 16px;
                box-shadow: rgba(0, 0, 0, 0.35) 0px 5px 15px;
            }}
        </style>""".format(ticker=ticker.upper(), current_price=current_price, daily_percentage_str=daily_percentage_str, rand_discord_role_color=rand_discord_role_color, hour_notif=hour_notif)

    return html_template

client.run('<SuperSecretKey>')
# Main: <SuperSecretKey>
# Beta: <SuperSecretKey>