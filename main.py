import asyncio
import os
import discord
from discord import app_commands
from discord.ext import tasks
import requests, time
import random, json
import dotenv, traceback

def get_api_key():
    lines = open("api_key.txt").read().splitlines()
    return random.choice(lines).strip()

app = discord.Client(intents=discord.Intents.all())
dotenv.load_dotenv()
tree = app_commands.CommandTree(app)

DBTOCLEAR = {
    "QUAKECRAFT": "Quake",
    "WALLS": "Walls",
    "PAINTBALL": "Paintball",
    "SURVIVAL_GAMES": "Blitz Survival Games",
    "TNTGAMES": "TNT Games",
    "VAMPIREZ": "VampireZ",
    "WALLS3": "Mega Walls",
    "ARCADE": "Arcade",
    "ARENA": "Arena",
    "UHC": "UHC Champions",
    "MCGO": "Cops and Crims",
    "BATTLEGROUND": "Warlords",
    "SUPER_SMASH": "Smash Heroes",
    "GINGERBREAD": "Turbo Kart Racers",
    "HOUSING": "Housing",
    "SKYWARS": "Skywars",
    "TRUE_COMBAT": "Crazy Walls",
    "SPEED_UHC": "Speed UHC",
    "SKYCLASH": "SkyClash",
    "LEGACY": "Classic Games",
    "PROTOTYPE": "Prototype",
    "BEDWARS": "Bedwars",
    "MURDER_MYSTERY": "Murder Mystery",
    "BUILD_BATTLE": "Build Battle",
    "DUELS": "Duels",
    "SKYBLOCK": "SkyBlock",
    "PIT": "Pit",
    "REPLAY": "Replay",
    "SMP": "SMP",
    "WOOL_GAMES": "Wool Wars",
    "TOURNAMENT": "Tournament",
    "MAIN": "Main"
}

@app.event
async def on_ready():
    print('Sycn les ptn de command')
    update_stats.start()
    # await tree.sync(guild=discord.Object(id=1145009611481559110))

def format_points(points):
    return f"{points:,}"

@tasks.loop(
    seconds=50
)
async def update_stats():
    try:
        await asyncio.sleep(10)
        guild = app.get_guild(1145009611481559110)
        channel = app.get_channel(1145179961771184209)
        embed = await generate_stats_embed(guild)
        async for msg in channel.history(limit=1):
            if msg.author.id == app.user.id:
                await msg.edit(
                    content=f"Updated <t:{int(time.time())}:R> (<t:{int(time.time())}:f>)",
                    embed=embed
                )
                return
            await channel.send(
                content=f"Updated <t:{int(time.time())}:R> (<t:{int(time.time())}:f>)",
                embed=embed
            )
    except:
        traceback.print_exc()
        

async def generate_stats_embed(guild):
    req = requests.get(
        "https://api.hypixel.net/guild?name=S1LLY",
        headers={
            "API-Key": get_api_key()
        }
    )

    embed = discord.Embed(
        title="S1LLY — Guild Info",
        # description = ""
    )
    embed.url = "https://plancke.io/hypixel/guild/name/S1LLY"
    

    games = req.json()["guild"]["guildExpByGameType"]
    valid_games = {}

    for (game_name, game_pts) in games.items():
        if game_pts != 0:
            valid_games[game_name] = game_pts

    embed.set_thumbnail(url=guild.icon.url)
    earned_yesterday = 0
    earned_today = 0
    online_players = 0
    MEMBERS = {}
    for member in req.json()['guild']['members']:
        # get first key/value of the dict
        if member['expHistory'] != {}:
            earned_yesterday += member['expHistory'][list(member['expHistory'].keys())[1]]
            earned_today += member['expHistory'][list(member['expHistory'].keys())[0]]

        m_req = requests.get(
            "https://api.hypixel.net/status?uuid=" + member['uuid'],
            headers={
                "API-Key": get_api_key()
            }
        )
        moj_req = requests.get(
            "https://sessionserver.mojang.com/session/minecraft/profile/" + member['uuid'],
        )
        print(json.dumps(m_req.json(),indent=4))


        MEMBERS[member['uuid']] = {
            "name": moj_req.json()['name'],
            "guild_rank": member['rank'],
#            "exp_history": m_req.json()['player']['expHistory'],
            "status": m_req.json()['session']['online'],
        }
        online_players += 1 if m_req.json()['session']['online'] else 0
        if MEMBERS[member['uuid']]['status']:
            #"gameType": m_req.json()['session']['gameType'],
            #"mode": m_req.json()['session']['mode']
            MEMBERS[member['uuid']]['gameType'] = m_req.json()['session']['gameType']
            if 'mode' in m_req.json()['session']:
                MEMBERS[member['uuid']]['mode'] = m_req.json()['session']['mode']
            else:
                MEMBERS[member['uuid']]['mode'] = 'Map'

    print(MEMBERS)
    e = "\n"
    # sort the dict by value
    valid_games = dict(sorted(valid_games.items(), key=lambda item: item[1], reverse=True))
    embed.add_field(
        name="✨ Global Experience",
        value='**' + format_points(req.json()["guild"]["exp"]) + f'** exp\n_{format_points(earned_today)} exp earned today_\n_{format_points(earned_yesterday)} exp earned yesterday_'
    )
    embed.add_field(
        name="🎮 Top Games",
        value="\n".join(["**" + DBTOCLEAR[game_name] + "**: " + format_points(valid_games[game_name]) + ' exp' for game_name in valid_games.keys()]), # TODO: make this look better
        inline=True
    )
    embed.description = '## 👥 Guild Members\n'
    embed.description += f"**{online_players} member{'s' if online_players>1 else ''}** online\n{e.join(('<:online:1145331611789955142> **' if member['status'] else '<:offline:1145331735664533606> ') + '[' + member['name'] + f'](https://plancke.io/hypixel/player/stats/' + member['name'] + ')' + ('**' if member['status'] else '') + ' [' + member['guild_rank'] + ']' + (' online in **'+DBTOCLEAR[member['gameType']] + ' ' + ('Lobby' if member['mode'] == 'LOBBY' else 'Game') + '**' if member['status'] else '') for (uuid,member) in MEMBERS.items())}"

    
    
    embed.color = discord.Color.blurple()
    return embed


@tree.command(
    name="guild_info",
    guild=discord.Object(id=1145009611481559110),
)
async def guild_info(interaction: discord.Interaction):
    await interaction.response.send_message(
        embed=generate_stats_embed(interaction.guild)
    )


app.run(os.environ['TOKEN'])
