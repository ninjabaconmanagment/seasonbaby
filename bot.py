import discord
import requests
import math

client = discord.Client()

# Constant
DISCORD_TOKEN = "NDUzNTU0MjE2OTI1OTIxMjgw.Dfgv6Q.tRtRm184XhX3o1w0iqQOeEApHYk"

FORTNITE_API_KEY = 'ddff1624-beae-4000-948e-8a9f051a2dbf'

rank_range_dict = {
    'Wood': [0.00, 1.00], 
    'Carton': [1.00, 2.99], 
    'Bronze': [3.00, 4.00], 
    'Silver': [4.00, 5.00], 
    'Gold': [5.00, 5.99], 
    'Platinum': [5.99, 6.99], 
    'Diamond': [6.99, 7.99], 
    'Ruby': [7.99, 8.99], 
    'Royality': [8.99, 9.99], 
    'Illuminati': [9.99, 10.99], 
    'Hackeur': [10.99, 20.00]
}

# Return the overall K/D of the fortnite player pass in parameter
def get_ratio(username):
    print(username)
    link = 'https://api.fortnitetracker.com/v1/profile/pc/' + username
    response = requests.get(link, headers={'TRN-Api-Key': FORTNITE_API_KEY})
    if response.status_code == 200:
        collection = response.json()
        if 'error' in collection:
            return "-1"
        else:
            return '%.2f'%(getSeasonKD(collection['stats']))
        print("Invalid username")
        return "-1"
    else:
        print("Error recovering fortnite data")
        return "-2"

def getSeasonKD(res):
    game_type_list = ['curr_p2', 'curr_p9', 'curr_p10']
    kd_avg = 0.0
    game_types_count = 0

    for game_type in game_type_list:
        if game_type in res:
            kd_avg += res[game_type]['kd']['valueDec']
            game_types_count += 1

    if game_types_count < 1:
        return 0.0
    else:
        return kd_avg / game_types_count

def print_nextLvl(begin, end, ratio):
    progress_string = "["
    numerator = ratio - begin
    denominator = end - begin
    completion_percent = numerator / denominator

    square_count = 41
    filled_squares = math.floor(completion_percent * square_count)
    for _ in range(0, filled_squares):
        progress_string += '■'
    for _ in range(filled_squares, square_count):
        progress_string += '□'
    progress_string += ']'

    return progress_string


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    # The command /patch return a link withvthe lastest patch note
    if message.content.startswith('/patch'):
        await client.send_message(message.channel, 'Last patchnotes: https://www.epicgames.com/fortnite/en/news')
    # The command /rank return attribute a rank according to the K/D of the user
    if message.content.startswith("/rank"):
        username = '{0.author.display_name}'.format(message)
        ratio = float(get_ratio(username))
        if ratio > -1:
            member_roles = message.author.roles
            for role in member_roles:
                if role.name in rank_range_dict:
                    await client.remove_roles(message.author, discord.utils.get(message.server.roles, name=role.name))
            for rank in rank_range_dict:
                if ratio > rank_range_dict[rank][1]:
                    continue
                else:
                    role = discord.utils.get(message.server.roles, name=rank)
                    msg = ("{0.author.mention} You have been ranked " + role.name).format(message)
                    await client.send_message(message.channel, msg)
                    msgRatio = "Next level: " + str(ratio) + "k/d  **→**  " + str(rank_range_dict[rank][1]) + "k/d"
                    await client.send_message(message.channel, msgRatio)
                    await client.send_message(message.channel, print_nextLvl(rank_range_dict[rank][0], rank_range_dict[rank][1], ratio))
                    await client.add_roles(message.author, role)
                    break
        elif ratio == -1:
            msg = "Your discord name is not a fortnite username! Use the command ```/nick YOUR_FORTNITE_USERNAME``` first!".format(message)
            await client.send_message(message.channel, msg)
        elif ratio == -2:
            msg = "The fortnite servers are offline. Try again later!".format(message)
            await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(DISCORD_TOKEN)
