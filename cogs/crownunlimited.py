import time
from operator import floordiv
from discord import guild, message
from re import T
import discord
from discord.ext import commands
import db
import dcf_file as data
import destiny as d
import messages as m
import numpy as np
import help_commands as h
# Converters
from discord import User
from discord import Member
import DiscordUtils
from PIL import Image, ImageFont, ImageDraw
import requests
import random
from collections import ChainMap
now = time.asctime()
import base64
from io import BytesIO
import io
import asyncio
import textwrap
import bot as main
import crown_utilities
from .classes.player_class import Player
from .classes.card_class import Card
from .classes.title_class import Title
from .classes.arm_class import Arm
from .classes.summon_class import Summon
from .classes.battle_class  import Battle
from discord import Embed
from discord_slash import cog_ext, SlashContext
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_commands import create_option, create_choice
from dinteractions_Paginator import Paginator
import typing
from pilmoji import Pilmoji
import destiny as d


class CrownUnlimited(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._cd = commands.CooldownMapping.from_cooldown(1, 3000, commands.BucketType.member)  # Change accordingly. Currently every 8 minutes (3600 seconds == 60 minutes)
        self._lvl_cd = commands.CooldownMapping.from_cooldown(1, 3000, commands.BucketType.member)
    co_op_modes = ['CTales', 'DTales', 'CDungeon', 'DDungeon']
    ai_co_op_modes = ['DTales', 'DDungeon']
    U_modes = ['ATales', 'Tales', 'CTales', 'DTales']
    D_modes = ['CDungeon', 'DDungeon', 'Dungeon', 'ADungeon']
    solo_modes = ['ATales', 'Tales', 'Dungeon', 'Boss']
    opponent_pet_modes = ['Dungeon', 'DDungeon', 'CDungeon']
    max_items = 150

    @commands.Cog.listener()
    async def on_ready(self):
        print('Anime 🆚+ Cog is ready!')

    async def cog_check(self, ctx):
        return await main.validate_user(ctx)

    async def companion(user):
        user_data = db.queryUser({'DID': str(user.id)})
        companion = user_data['DISNAME']
        return companion

    def get_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
        """Returns the ratelimit left"""
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()

    def get_lvl_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
        """Returns the level ratelimit left"""
        bucket = self._lvl_cd.get_bucket(message)
        return bucket.update_rate_limit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == main.bot.user:
            return
        level_ratelimit = self.get_lvl_ratelimit(message)
        ratelimit = self.get_ratelimit(message)

        if level_ratelimit is None:
            try:
                player_that_leveled = db.queryUser({'DID': str(message.author.id)})
                if player_that_leveled:
                    card_that_leveled = db.queryCard({'NAME': player_that_leveled['CARD']})
                    uni = card_that_leveled['UNIVERSE']
                    nam = card_that_leveled['NAME']
                    mode = "Tales"
                    u = await main.bot.fetch_user(str(message.author.id))
                    await crown_utilities.cardlevel(u, nam, str(message.author.id), mode, uni)
                else:
                    return
            except Exception as e:
                print(f"{str(message.author)} Error in on_message: {e}")

        if ratelimit is None:
            if isinstance(message.channel, discord.channel.DMChannel):
                return

            g = message.author.guild
            channel_list = message.author.guild.text_channels
            channel_names = []
            for channel in channel_list:
                channel_names.append(channel.name)

            server_channel_response = db.queryServer({'GNAME': str(g)})
            server_channel = ""
            if server_channel_response:
                server_channel = str(server_channel_response['EXP_CHANNEL'])
            
            if "explore-encounters" in channel_names:
                server_channel = "explore-encounters"
            
            if not server_channel:
                return

            mode = "EXPLORE"

            # Pull Character Information
            player = db.queryUser({'DID': str(message.author.id)})
            if not player:
                return
            p = Player(player['DISNAME'], player['DID'], player['AVATAR'], player['GUILD'], player['TEAM'], player['FAMILY'], player['TITLE'], player['CARD'], player['ARM'], player['PET'], player['TALISMAN'], player['CROWN_TALES'], player['DUNGEONS'], player['BOSS_WINS'], player['RIFT'], player['REBIRTH'], player['LEVEL'], player['EXPLORE'], player['SAVE_SPOT'], player['PERFORMANCE'], player['TRADING'], player['BOSS_FOUGHT'], player['DIFFICULTY'], player['STORAGE_TYPE'], player['USED_CODES'], player['BATTLE_HISTORY'], player['PVP_WINS'], player['PVP_LOSS'], player['RETRIES'], player['PRESTIGE'], player['PATRON'], player['FAMILY_PET'])    
            battle = Battle(mode, p)
            if p.get_locked_feature(mode):
                return

            if p.explore is False:
                return


            all_universes = db.queryExploreUniverses()
            available_universes = [x for x in all_universes]

            u = len(available_universes) - 1
            rand_universe = random.randint(1, u)
            universetitle = available_universes[rand_universe]['TITLE']
            universe = available_universes[rand_universe]

            # Select Card at Random
            all_available_drop_cards = db.querySpecificDropCards(universetitle)
            cards = [x for x in all_available_drop_cards]

            c = len(cards) - 1
            rand_card = random.randint(1, c)
            selected_card = Card(cards[rand_card]['NAME'], cards[rand_card]['PATH'], cards[rand_card]['PRICE'], cards[rand_card]['EXCLUSIVE'], cards[rand_card]['AVAILABLE'], cards[rand_card]['IS_SKIN'], cards[rand_card]['SKIN_FOR'], cards[rand_card]['HLT'], cards[rand_card]['HLT'], cards[rand_card]['STAM'], cards[rand_card]['STAM'], cards[rand_card]['MOVESET'], cards[rand_card]['ATK'], cards[rand_card]['DEF'], cards[rand_card]['TYPE'], cards[rand_card]['PASS'][0], cards[rand_card]['SPD'], cards[rand_card]['UNIVERSE'], cards[rand_card]['HAS_COLLECTION'], cards[rand_card]['TIER'], cards[rand_card]['COLLECTION'], cards[rand_card]['WEAKNESS'], cards[rand_card]['RESISTANT'], cards[rand_card]['REPEL'], cards[rand_card]['ABSORB'], cards[rand_card]['IMMUNE'], cards[rand_card]['GIF'], cards[rand_card]['FPATH'], cards[rand_card]['RNAME'], cards[rand_card]['RPATH'])
            selected_card.set_affinity_message()
            selected_card.set_passive_values()
            selected_card.set_explore_bounty_and_difficulty()

            battle.set_explore_config(universe, selected_card)

            random_battle_buttons = [
                manage_components.create_button(
                    style=ButtonStyle.blue,
                    label="Glory",
                    custom_id="glory"
                ),
                manage_components.create_button(
                    style=ButtonStyle.blue,
                    label="Gold",
                    custom_id="gold"
                ),
            ]
            random_battle_buttons_action_row = manage_components.create_actionrow(*random_battle_buttons)


            # Send Message
            embedVar = discord.Embed(title=f"**{selected_card.approach_message}{selected_card.name}** has a bounty!",
                                     description=textwrap.dedent(f"""\
            **Bounty** **{selected_card.bounty_message}**
            {selected_card.battle_message}
            """), colour=0xf1c40f)
         
            card_file = showcard("non-battle", cards[rand_card], "none", selected_card.max_health, selected_card.health, selected_card.max_stamina, selected_card.stamina, selected_card.resolved, selected_card._explore_cardtitle, selected_card.focused, selected_card.attack, selected_card.defense, selected_card.turn, selected_card.move1ap, selected_card.move2ap, selected_card.move3ap, selected_card.move4ap, selected_card.move4enh, selected_card.card_lvl, None)

            embedVar.set_image(url="attachment://image.png")
            embedVar.set_thumbnail(url=message.author.avatar_url)

            setchannel = discord.utils.get(channel_list, name=server_channel)
            await setchannel.send(f"{message.author.mention}") 
            msg = await setchannel.send(embed=embedVar, file=card_file, components=[random_battle_buttons_action_row])     

            def check(button_ctx):
                return button_ctx.author == message.author

            try:
                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[
                    random_battle_buttons_action_row], timeout=120, check=check)

                if button_ctx.custom_id == "glory":
                    await button_ctx.defer(ignore=True)
                    battle.explore_type = "glory"
                    await battle_commands(self, ctx, battle, p, _player2=None)
                    await msg.edit(components=[])

                if button_ctx.custom_id == "gold":
                    await button_ctx.defer(ignore=True)
                    battle.explore_type = "gold"
                    await battle_commands(self, ctx, battle, p, _player2=None)
                    await msg.edit(components=[])

            except Exception as ex:
                await msg.edit(components=[])


    @cog_ext.cog_slash(description="Toggle Explore Mode On/Off", guild_ids=main.guild_ids)
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def explore(self, ctx: SlashContext):
        try:
            player = db.queryUser({"DID": str(ctx.author.id)})
            p = Player(player['DISNAME'], player['DID'], player['AVATAR'], player['GUILD'], player['TEAM'], player['FAMILY'], player['TITLE'], player['CARD'], player['ARM'], player['PET'], player['TALISMAN'], player['CROWN_TALES'], player['DUNGEONS'], player['BOSS_WINS'], player['RIFT'], player['REBIRTH'], player['LEVEL'], player['EXPLORE'], player['SAVE_SPOT'], player['PERFORMANCE'], player['TRADING'], player['BOSS_FOUGHT'], player['DIFFICULTY'], player['STORAGE_TYPE'], player['USED_CODES'], player['BATTLE_HISTORY'], player['PVP_WINS'], player['PVP_LOSS'], player['RETRIES'], player['PRESTIGE'], player['PATRON'], player['FAMILY_PET'])
            await ctx.send(f"{p.set_explore()}")
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))


    @cog_ext.cog_slash(description="Set Explore Channel", guild_ids=main.guild_ids)
    async def setexplorechannel(self, ctx: SlashContext):
        if ctx.author.guild_permissions.administrator:
            guild = ctx.guild
            server_channel = ctx.channel
            server_query = {'GNAME': str(guild), 'EXP_CHANNEL': str(server_channel)}
            try:
                response = db.queryServer({'GNAME': str(guild)})
                if response:
                    update_channel = db.updateServer({'GNAME': str(guild)}, {'$set': {'EXP_CHANNEL': str(server_channel)}})
                    await ctx.send(f"Explore Channel updated to **{server_channel}**")
                    return
                else:
                    update_channel = db.createServer(data.newServer(server_query))
                    await ctx.send("Explore Channel set.")
                    return
            except Exception as ex:
                trace = []
                tb = ex.__traceback__
                while tb is not None:
                    trace.append({
                        "filename": tb.tb_frame.f_code.co_filename,
                        "name": tb.tb_frame.f_code.co_name,
                        "lineno": tb.tb_lineno
                    })
                    tb = tb.tb_next
                print(str({
                    'type': type(ex).__name__,
                    'message': str(ex),
                    'trace': trace
                }))
        else:
            await ctx.send("Admin command only.")
            return


    @cog_ext.cog_slash(description="Create Default Server Explore Channel", guild_ids=main.guild_ids)
    async def createexplorechannel(self, ctx: SlashContext):
        guild = ctx.guild
        categoryname = "Explore"
        channelname = "explore-encounters"
        try:
            if ctx.author.guild_permissions.administrator == True:
                category = discord.utils.get(guild.categories, name=categoryname)
                if category is None: #If there's no category matching with the `name`
                    category = await guild.create_category_channel(categoryname)
                    setchannel = await guild.create_text_channel(channelname, category=category)
                    await ctx.send(f"New **Explore** Category and **{channelname}** Channel Created!")
                    await setchannel.send("**Explore Channel Set**")
                    return setchannel

                else: #Else if it found the categoty
                    setchannel = discord.utils.get(guild.text_channels, name=channelname)
                    if channel is None:
                        setchannel = await guild.create_text_channel(channelname, category=category)
                        await ctx.send(f"New Explore Channel is **{channelname}**")
                        await setchannel.send("**Explore Channel Set**")
                    else:
                        await ctx.send(f"Explore Channel Already Exist **{channelname}**")
                        await setchannel.send(f"{ctx.author.mention} Explore Here")            
                
            # else:
            #     print("Not Admin")
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
    

    @cog_ext.cog_slash(description="Duo pve to earn cards, accessories, gold, gems, and more with your AI companion",
                       options=[
                           create_option(
                               name="deck",
                               description="AI Preset (this is from your preset list)",
                               option_type=3,
                               required=True,
                               choices=[
                                   create_choice(
                                       name="Preset 1",
                                       value="1"
                                   ),
                                   create_choice(
                                       name="Preset 2",
                                       value="2"
                                   ),
                                   create_choice(
                                       name="Preset 3",
                                       value="3"
                                   )
                               ]
                           ),
                           create_option(
                               name="mode",
                               description="Difficulty Level",
                               option_type=3,
                               required=True,
                               choices=[
                                   create_choice(
                                       name="⚔️ Duo Tales (Normal)",
                                       value="DTales"
                                   ),
                                   create_choice(
                                       name="🔥 Duo Dungeon (Hard)",
                                       value="DDungeon"
                                   )
                               ]
                           )
                       ]
        , guild_ids=main.guild_ids)
    async def duo(self, ctx: SlashContext, deck: int, mode: str):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        U_modes = ['ATales', 'Tales', 'CTales', 'DTales']
        D_modes = ['CDungeon', 'DDungeon', 'Dungeon', 'ADungeon']
        B_MODES = ['Boss', 'CBoss']
        try:
            # await ctx.defer()
            deck = int(deck)
            if deck != 1 and deck != 2 and deck != 3:
                await ctx.send("Not a valid Deck Option")
                return
            deckNumber = deck - 1
            sowner = db.queryUser({'DID': str(ctx.author.id)})
            oteam = sowner['TEAM']
            ofam = sowner['FAMILY']
            cowner = sowner
            cteam = oteam
            cfam = ofam
            # if sowner['DIFFICULTY'] != "EASY":
            #     if sowner['LEVEL'] < 8:
            #         await ctx.send(f"🔓 Unlock **Duo** by completing **Floor 7** of the 🌑 **Abyss**! Use **Abyss** in /solo to enter the abyss.")
            #         return
            
            if sowner['DIFFICULTY'] == "EASY" and mode in D_modes or mode in B_MODES:
                await ctx.send("Dungeons and Boss fights unavailable on Easy Mode! Use /difficulty to change your difficulty setting.")
                return


            if mode in D_modes and sowner['LEVEL'] < 41 and int(sowner['PRESTIGE']) == 0:
                await ctx.send("🔓 Unlock **Duo Dungeons** by completing **Floor 40** of the 🌑 **Abyss**! Use **Abyss** in /solo to enter the abyss.")
                return



            universe_selection = await select_universe(self, ctx, sowner, oteam, ofam, mode, None)
            if not universe_selection:
                return
            selected_universe = universe_selection['SELECTED_UNIVERSE']
            universe = universe_selection['UNIVERSE_DATA']
            crestlist = universe_selection['CREST_LIST']
            crestsearch = universe_selection['CREST_SEARCH']
            currentopponent =  universe_selection['CURRENTOPPONENT']

            if mode in D_modes:
                completed_universes = universe_selection['COMPLETED_DUNGEONS']
            else:
                completed_universes = universe_selection['COMPLETED_TALES']
            if crestsearch:
                oguild = universe_selection['OGUILD']
            else:
                oguild = "PCG"

            await battle_commands(self, ctx, mode, universe, selected_universe, completed_universes, oguild, crestlist,
                                  crestsearch, sowner, oteam, ofam, currentopponent, cowner, cteam, cfam, deckNumber,
                                  None, None, None, None, None)
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            return


    @cog_ext.cog_slash(description="Co-op pve to earn cards, accessories, gold, gems, and more with friends",
                       options=[
                           create_option(
                               name="user",
                               description="player you want to co-op with",
                               option_type=6,
                               required=True
                           ),
                           create_option(
                               name="mode",
                               description="Difficulty Level",
                               option_type=3,
                               required=True,
                               choices=[
                                   create_choice(
                                       name="⚔️ Co-Op Tales (Normal)",
                                       value="CTales"
                                   ),
                                   create_choice(
                                       name="🔥 Co-Op Dungeon (Hard)",
                                       value="CDungeon"
                                   ),
                                   create_choice(
                                       name="👹 Co-Op Boss Enounter (Extreme)",
                                       value="CBoss"
                                   ),
                               ]
                           )
                       ]
        , guild_ids=main.guild_ids)
    async def coop(self, ctx: SlashContext, user: User, mode: str):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        try:
            player = db.queryUser({'DID': str(ctx.author.id)})
            player2 = db.queryUser({'DID': str(user.id)})
            p1 = Player(player['DISNAME'], player['DID'], player['AVATAR'], player['GUILD'], player['TEAM'], player['FAMILY'], player['TITLE'], player['CARD'], player['ARM'], player['PET'], player['TALISMAN'], player['CROWN_TALES'], player['DUNGEONS'], player['BOSS_WINS'], player['RIFT'], player['REBIRTH'], player['LEVEL'], player['EXPLORE'], player['SAVE_SPOT'], player['PERFORMANCE'], player['TRADING'], player['BOSS_FOUGHT'], player['DIFFICULTY'], player['STORAGE_TYPE'], player['USED_CODES'], player['BATTLE_HISTORY'], player['PVP_WINS'], player['PVP_LOSS'], player['RETRIES'], player['PRESTIGE'], player['PATRON'], player['FAMILY_PET'])    
            p2 = Player(player2['DISNAME'], player2['DID'], player2['AVATAR'], player2['GUILD'], player2['TEAM'], player2['FAMILY'], player2['TITLE'], player2['CARD'], player2['ARM'], player2['PET'], player2['TALISMAN'], player2['CROWN_TALES'], player2['DUNGEONS'], player2['BOSS_WINS'], player2['RIFT'], player2['REBIRTH'], player2['LEVEL'], player2['EXPLORE'], player2['SAVE_SPOT'], player2['PERFORMANCE'], player2['TRADING'], player2['BOSS_FOUGHT'], player2['DIFFICULTY'], player2['STORAGE_TYPE'], player2['USED_CODES'], player2['BATTLE_HISTORY'], player2['PVP_WINS'], player2['PVP_LOSS'], player2['RETRIES'], player2['PRESTIGE'], player2['PATRON'], player2['FAMILY_PET'])    
            battle = Battle(mode, p1)


            universe_selection = await select_universe(self, ctx, p1, mode, p2)
            if not universe_selection:
                return

            await battle_commands(self, ctx, battle, p1, p2)
        
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            return


    @cog_ext.cog_slash(description="pve to earn cards, accessories, gold, gems, and more as a solo player",
                    options=[
                        create_option(
                            name="mode",
                            description="abyss: climb ladder, tales: normal pve mode, dungeon: hard pve run, and boss: extreme encounters",
                            option_type=3,
                            required=True,
                            choices=[
                                create_choice(
                                    name="🆘 The Tutorial",
                                    value="Tutorial"
                                ),
                                create_choice(
                                    name="🌑 The Abyss!",
                                    value="Abyss"
                                ),
                                create_choice(
                                    name="⚔️ Tales & Scenario Battles!",
                                    value="Tales"
                                ),
                                create_choice(
                                    name="🔥 Dungeon Run!",
                                    value="Dungeon"
                                ),
                                create_choice(
                                    name="👹 Boss Encounter!",
                                    value="Boss"
                                ),
                            ]
                        )
                    ]
        , guild_ids=main.guild_ids)
    async def solo(self, ctx: SlashContext, mode: str):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return
        
        try:
            # await ctx.defer()

            player = db.queryUser({'DID': str(ctx.author.id)})
            p = Player(player['DISNAME'], player['DID'], player['AVATAR'], player['GUILD'], player['TEAM'], player['FAMILY'], player['TITLE'], player['CARD'], player['ARM'], player['PET'], player['TALISMAN'], player['CROWN_TALES'], player['DUNGEONS'], player['BOSS_WINS'], player['RIFT'], player['REBIRTH'], player['LEVEL'], player['EXPLORE'], player['SAVE_SPOT'], player['PERFORMANCE'], player['TRADING'], player['BOSS_FOUGHT'], player['DIFFICULTY'], player['STORAGE_TYPE'], player['USED_CODES'], player['BATTLE_HISTORY'], player['PVP_WINS'], player['PVP_LOSS'], player['RETRIES'], player['PRESTIGE'], player['PATRON'], player['FAMILY_PET'])    

                         
            if p.get_locked_feature(mode):
                await ctx.send(p._locked_feature_message)
                return

            universe_selection = await select_universe(self, ctx, p, mode, None)
            
            if universe_selection == None:
                return

            battle = Battle(mode, p)


            if battle.mode == "Abyss":
                await abyss(self, ctx)
                return

            if battle.mode == "Tutorial":
                await tutorial(self, ctx)
                return

            battle.set_universe_selection_config(universe_selection)
                
            await battle_commands(self, ctx, battle, p, _player2=None)
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            guild = self.bot.get_guild(main.guild_id)
            channel = guild.get_channel(main.guild_channel)
            await channel.send(f"'PLAYER': **{str(ctx.author)}**, 'GUILD': **{str(ctx.author.guild)}**,  TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")
            return


    @cog_ext.cog_slash(description="pvp battle against a friend or rival", guild_ids=main.guild_ids)
    async def pvp(self, ctx: SlashContext, opponent: User):
        try:
            await ctx.defer()

            a_registered_player = await crown_utilities.player_check(ctx)
            if not a_registered_player:
                return
            mode = "PVP"
            player = db.queryUser({'DID': str(ctx.author.id)})
            player2 = db.queryUser({'DID': str(opponent.id)})
            p1 = Player(player['DISNAME'], player['DID'], player['AVATAR'], player['GUILD'], player['TEAM'], player['FAMILY'], player['TITLE'], player['CARD'], player['ARM'], player['PET'], player['TALISMAN'], player['CROWN_TALES'], player['DUNGEONS'], player['BOSS_WINS'], player['RIFT'], player['REBIRTH'], player['LEVEL'], player['EXPLORE'], player['SAVE_SPOT'], player['PERFORMANCE'], player['TRADING'], player['BOSS_FOUGHT'], player['DIFFICULTY'], player['STORAGE_TYPE'], player['USED_CODES'], player['BATTLE_HISTORY'], player['PVP_WINS'], player['PVP_LOSS'], player['RETRIES'], player['PRESTIGE'], player['PATRON'], player['FAMILY_PET'])    
            p2 = Player(player2['DISNAME'], player2['DID'], player2['AVATAR'], player2['GUILD'], player2['TEAM'], player2['FAMILY'], player2['TITLE'], player2['CARD'], player2['ARM'], player2['PET'], player2['TALISMAN'], player2['CROWN_TALES'], player2['DUNGEONS'], player2['BOSS_WINS'], player2['RIFT'], player2['REBIRTH'], player2['LEVEL'], player2['EXPLORE'], player2['SAVE_SPOT'], player2['PERFORMANCE'], player2['TRADING'], player2['BOSS_FOUGHT'], player2['DIFFICULTY'], player2['STORAGE_TYPE'], player2['USED_CODES'], player2['BATTLE_HISTORY'], player2['PVP_WINS'], player2['PVP_LOSS'], player2['RETRIES'], player2['PRESTIGE'], player2['PATRON'], player2['FAMILY_PET'])    
            battle = Battle(mode, p1)
            battle.set_tutorial(p2.did)
            
            if p1.did == p2.did:
                await ctx.send("You cannot PVP against yourself.", hidden=True)
                return
            await ctx.send("🆚 Building PVP Match...", delete_after=10)

            starttime = time.asctime()
            h_gametime = starttime[11:13]
            m_gametime = starttime[14:16]
            s_gametime = starttime[17:19]

            if p1.get_locked_feature(mode):
                await ctx.send(p1._locked_feature_message)
                return
            if p2.get_locked_feature(mode):
                await ctx.send(p2._locked_feature_message)
                return

            await battle_commands(self, ctx, mode, battle, p1, p2)

        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'PLAYER': str(ctx.author),
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            guild = self.bot.get_guild(main.guild_id)
            channel = guild.get_channel(main.guild_channel)
            await channel.send(f"'PLAYER': **{str(ctx.author)}**, 'GUILD': **{str(ctx.author.guild)}**,  TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")
            return


    @cog_ext.cog_slash(description="Start an Association Raid", guild_ids=main.guild_ids)
    async def raid(self, ctx: SlashContext, guild: str):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        try:
            guildname = guild
            private_channel = ctx
            if isinstance(private_channel.channel, discord.channel.DMChannel):
                await private_channel.send(m.SERVER_FUNCTION_ONLY)
                return
            starttime = time.asctime()
            h_gametime = starttime[11:13]
            m_gametime = starttime[14:16]
            s_gametime = starttime[17:19]

            # Get Session Owner Disname for scoring
            sowner = db.queryUser({'DID': str(ctx.author.id)})
            if sowner['DIFFICULTY'] == "EASY":
                await ctx.send("Raiding is unavailable on Easy Mode! Use /difficulty to change your difficulty setting.")
                return

            oteam = sowner['TEAM']
            oteam_info = db.queryTeam({'TEAM_NAME': oteam.lower()})
            oguild_name = "PCG"
            shield_test_active = False
            shield_training_active = False
            if oteam_info:
                oguild_name = oteam_info['GUILD']
                oguild = db.queryGuildAlt({'GNAME': oguild_name})
            player_guild = sowner['GUILD']

            if oguild_name == "PCG":
                await ctx.send(m.NO_GUILD, delete_after=5)
                return
            if oguild['SHIELD'] == sowner['DISNAME']:
                shield_training_active = True
            elif player_guild == guildname:
                shield_test_active = True
                

            guild_query = {'GNAME': guildname}
            guild_info = db.queryGuildAlt(guild_query)
            guild_shield = ""

            if not guild_info:
                await ctx.send(m.GUILD_DOESNT_EXIST, delete_after=5)
                return
            guild_shield = guild_info['SHIELD']
            shield_id = guild_info['SDID']
            guild_hall = guild_info['HALL']
            hall_info = db.queryHall({'HALL': str(guild_hall)})
            hall_def = hall_info['DEFENSE']
            t_user = db.queryUser({'DID': shield_id})
            tteam_name = t_user['TEAM']
            tteam_info = db.queryTeam({'TEAM_NAME': tteam_name.lower()})
            tteam = tteam_info['TEAM_NAME']
            tguild = tteam_info['GUILD']
            if tteam_info:
                tguild = tteam_info['GUILD']
            tarm = db.queryArm({'ARM': t_user['ARM']})
            ttitle = db.queryTitle({'TITLE': t_user['TITLE']})
            
            mode = "RAID"

            # Guild Fees
            title_match_active = False
            fee = hall_info['FEE']
            if oguild_name == tguild:
                title_match_active = True

            o = db.queryCard({'NAME': sowner['CARD']})
            otitle = db.queryTitle({'TITLE': sowner['TITLE']})

            t = db.queryCard({'NAME': t_user['CARD']})
            ttitle = db.queryTitle({'TITLE': t_user['TITLE']})
            
            if private_channel:
                await battle_commands(self, ctx, mode, hall_info, title_match_active, shield_test_active, oguild, shield_training_active, None, sowner, oteam, None, t_user,tteam, tguild, None, None, None, None, None, None, None)
            else:
                await ctx.send("Failed to start raid battle!")
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'PLAYER': str(ctx.author),
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            guild = self.bot.get_guild(main.guild_id)
            channel = guild.get_channel(main.guild_channel)
            await channel.send(f"'PLAYER': **{str(ctx.author)}**, 'GUILD': **{str(ctx.author.guild)}**,  TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")
            return


    @cog_ext.cog_slash(description="View all available Universes and their cards, summons, destinies, and accessories", guild_ids=main.guild_ids)
    async def universes(self, ctx: SlashContext):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        try:
            universe_data = db.queryAllUniverse()
            # user = db.queryUser({'DID': str(ctx.author.id)})
            universe_embed_list = []
            for uni in universe_data:
                available = ""
                # if len(uni['CROWN_TALES']) > 2:
                if uni['CROWN_TALES']:
                    available = f"{crown_utilities.crest_dict[uni['TITLE']]}"
                    
                    tales_list = ", ".join(uni['CROWN_TALES'])

                    embedVar = discord.Embed(title= f"{uni['TITLE']}", description=textwrap.dedent(f"""
                    {crown_utilities.crest_dict[uni['TITLE']]} **Number of Fights**: :crossed_swords: **{len(uni['CROWN_TALES'])}**
                    🎗️ **Universe Title**: {uni['UTITLE']}
                    🦾 **Universe Arm**: {uni['UARM']}
                    🧬 **Universe Summon**: {uni['UPET']}

                    :crossed_swords: **Tales Order**: {tales_list}
                    """))
                    embedVar.set_image(url=uni['PATH'])
                    universe_embed_list.append(embedVar)
                

            buttons = [
                manage_components.create_button(style=3, label="🎴 Cards", custom_id="cards"),
                manage_components.create_button(style=1, label="🎗️ Titles", custom_id="titles"),
                manage_components.create_button(style=1, label="🦾 Arms", custom_id="arms"),
                manage_components.create_button(style=1, label="🧬 Summons", custom_id="summons"),
                manage_components.create_button(style=2, label="✨ Destinies", custom_id="destinies")
            ]
            custom_action_row = manage_components.create_actionrow(*buttons)

            async def custom_function(self, button_ctx):
                universe_name = str(button_ctx.origin_message.embeds[0].title)
                await button_ctx.defer(ignore=True)
                if button_ctx.author == ctx.author:
                    if button_ctx.custom_id == "cards":
                        await cardlist(self, ctx, universe_name)
                        #self.stop = True
                    if button_ctx.custom_id == "titles":
                        await titlelist(self, ctx, universe_name)
                        #self.stop = True
                    if button_ctx.custom_id == "arms":
                        await armlist(self, ctx, universe_name)
                        #self.stop = True
                    if button_ctx.custom_id == "summons":
                        await summonlist(self, ctx, universe_name)
                        #self.stop = True
                    if button_ctx.custom_id == "destinies":
                        await destinylist(self, ctx, universe_name)
                        #self.stop = True
                else:
                    await ctx.send("This is not your command.")


            await Paginator(bot=self.bot, ctx=ctx, useQuitButton=True, deleteAfterTimeout=True, pages=universe_embed_list, customActionRow=[
                custom_action_row,
                custom_function,
            ]).run()


        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))


    @cog_ext.cog_slash(description="View all Homes for purchase", guild_ids=main.guild_ids)
    async def houses(self, ctx: SlashContext):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return


        house_data = db.queryAllHouses()
        user = db.queryUser({'DID': str(ctx.author.id)})

        house_list = []
        for homes in house_data:
            house_list.append(
                f":house: | {homes['HOUSE']}\n:coin: | **COST: **{'{:,}'.format(homes['PRICE'])}\n:part_alternation_mark: | **MULT: **{homes['MULT']}x\n_______________")

        total_houses = len(house_list)
        while len(house_list) % 10 != 0:
            house_list.append("")

        # Check if divisible by 10, then start to split evenly
        if len(house_list) % 10 == 0:
            first_digit = int(str(len(house_list))[:1])
            houses_broken_up = np.array_split(house_list, first_digit)

        # If it's not an array greater than 10, show paginationless embed
        if len(house_list) < 10:
            embedVar = discord.Embed(title=f"House List", description="\n".join(house_list), colour=0x7289da)
            embedVar.set_footer(text=f"{total_houses} Total Houses\n/viewhouse - View House Details")
            await ctx.send(embed=embedVar)

        embed_list = []
        for i in range(0, len(houses_broken_up)):
            globals()['embedVar%s' % i] = discord.Embed(title=f":house: House List",
                                                        description="\n".join(houses_broken_up[i]), colour=0x7289da)
            globals()['embedVar%s' % i].set_footer(text=f"{total_houses} Total Houses\n/view *House Name* `:house: It's a House` - View House Details")
            embed_list.append(globals()['embedVar%s' % i])

        paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
        paginator.add_reaction('⏮️', "first")
        paginator.add_reaction('⬅️', "back")
        paginator.add_reaction('🔐', "lock")
        paginator.add_reaction('➡️', "next")
        paginator.add_reaction('⏭️', "last")
        embeds = embed_list
        await paginator.run(embeds)


    @cog_ext.cog_slash(description="View all Halls for purchase", guild_ids=main.guild_ids)
    async def halls(self, ctx: SlashContext):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return


        hall_data = db.queryAllHalls()
        user = db.queryUser({'DID': str(ctx.author.id)})

        hall_list = []
        for homes in hall_data:
            hall_list.append(
                f":flags: | {homes['HALL']}\n🛡️ | **DEF: **{homes['DEFENSE']}\n:coin: | **COST: **{'{:,}'.format(homes['PRICE'])}\n:part_alternation_mark: | **MULT: **{homes['MULT']}x\n:moneybag: | **SPLIT: **{'{:,}'.format(homes['SPLIT'])}x\n:yen: | **FEE: **{'{:,}'.format(homes['FEE'])}\n_______________")

        total_halls = len(hall_list)
        while len(hall_list) % 10 != 0:
            hall_list.append("")

        # Check if divisible by 10, then start to split evenly
        if len(hall_list) % 10 == 0:
            first_digit = int(str(len(hall_list))[:1])
            halls_broken_up = np.array_split(hall_list, first_digit)

        # If it's not an array greater than 10, show paginationless embed
        if len(hall_list) < 10:
            embedVar = discord.Embed(title=f"Hall List", description="\n".join(hall_list), colour=0x7289da)
            embedVar.set_footer(text=f"{total_halls} Total Halls\n/viewhall - View Hall Details")
            await ctx.send(embed=embedVar)

        embed_list = []
        for i in range(0, len(halls_broken_up)):
            globals()['embedVar%s' % i] = discord.Embed(title=f":flags: Hall List",
                                                        description="\n".join(halls_broken_up[i]), colour=0x7289da)
            globals()['embedVar%s' % i].set_footer(text=f"{total_halls} Total Halls\n/view *Hall Name* `:flags: It's A Hall` - View Hall Details")
            embed_list.append(globals()['embedVar%s' % i])

        paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
        paginator.add_reaction('⏮️', "first")
        paginator.add_reaction('⬅️', "back")
        paginator.add_reaction('🔐', "lock")
        paginator.add_reaction('➡️', "next")
        paginator.add_reaction('⏭️', "last")
        embeds = embed_list
        await paginator.run(embeds)


async def tutorial(self, ctx: SlashContext):
    try:
        await ctx.defer()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        await ctx.send("🆚 Building Tutorial Match...", delete_after=10)
        private_channel = ctx
        starttime = time.asctime()
        h_gametime = starttime[11:13]
        m_gametime = starttime[14:16]
        s_gametime = starttime[17:19]

        # Tutorial Code
        tutorialbot = '837538366509154407'
        legendbot = '845672426113466395'
        tutorial_user = await self.bot.fetch_user(tutorialbot)
        opponent = db.queryUser({'DISNAME': str(tutorial_user)})
        oppDID = opponent['DID']
        tutorial = False
        if oppDID == tutorialbot or oppDID == legendbot:
            tutorial = True
        mode = "PVP"

        # Get Session Owner Disname for scoring
        sowner = db.queryUser({'DID': str(ctx.author.id)})
        opponent = db.queryUser({'DISNAME': str(tutorial_user)})
        oteam = sowner['TEAM']
        tteam = opponent['TEAM']
        oteam_info = db.queryTeam({'TEAM_NAME':str(oteam)})
        tteam_info = db.queryTeam({'TEAM_NAME':str(tteam)})
        if oteam_info:
            oguild = oteam_info['GUILD']
        else:
            oguild ="PCG"
        if tteam_info:
            tguild = tteam_info['GUILD']
        else:
            tguild ="PCG"

        o = db.queryCard({'NAME': sowner['CARD']})
        otitle = db.queryTitle({'TITLE': sowner['TITLE']})

        t = db.queryCard({'NAME': opponent['CARD']})
        ttitle = db.queryTitle({'TITLE': opponent['TITLE']})

        # universe = "Naruto"
        # selected_universe = {"TITLE": "Naruto"}
        if private_channel:
            await battle_commands(self, ctx, mode, None, None, None, oguild, None, None, sowner, oteam, None, opponent, tteam, tguild, None, None, None, None, None, "Tutorial", None)
        else:
            await ctx.send("Failed to start battle!")
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'PLAYER': str(ctx.author),
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        guild = self.bot.get_guild(main.guild_id)
        channel = guild.get_channel(main.guild_channel)
        await channel.send(f"'PLAYER': **{str(ctx.author)}**, 'GUILD': **{str(ctx.author.guild)}**,  TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")
        return


async def score(owner, user: User):
    session_query = {"OWNER": str(owner), "AVAILABLE": True, "KINGSGAMBIT": False}
    session_data = db.querySession(session_query)
    teams = [x for x in session_data['TEAMS']]
    winning_team = {}
    for x in teams:
        if str(user) in x['TEAM']:
            winning_team = x
    new_score = winning_team['SCORE'] + 1
    update_query = {'$set': {'TEAMS.$.SCORE': new_score}}
    query = {"_id": session_data["_id"], "TEAMS.TEAM": str(user)}
    response = db.updateSession(session_query, query, update_query)
    reciever = db.queryUser({'DISNAME': str(user)})
    name = reciever['DISNAME']
    message = ":one: You Scored, Don't Let Up :one:"

    if response:
        message = ":one:"
    else:
        message = "Score not added. Please, try again. "

    return message


async def quest(player, opponent, mode):
    user_data = db.queryVault({'DID': str(player.id)})
    quest_data = {}
    try:
        if user_data['QUESTS']:
            for quest in user_data['QUESTS']:
                if opponent == quest['OPPONENT']:
                    quest_data = quest

            if quest_data == {}:
                return
            completion = quest_data['GOAL'] - (quest_data['WINS'] + 1)
            reward = int(quest_data['REWARD'])

            if str(mode) == "Dungeon" and completion >= 0:
                message = "Quest progressed!"
                if completion == 0:
                    await crown_utilities.bless(reward, player.id)
                    message = f"Quest Completed! :coin:{reward} has been added to your balance."

                    # server_query = {'GNAME': str(player.guild)}
                    # update_server_query = {
                    #     '$inc': {'SERVER_BALANCE': 10000}
                    # }
                    # updated_server = db.updateServer(server_query, update_server_query)

                query = {'DID': str(player.id)}
                update_query = {'$inc': {'QUESTS.$[type].' + "WINS": 2}}
                filter_query = [{'type.' + "OPPONENT": opponent}]
                resp = db.updateVault(query, update_query, filter_query)
                return message

            elif str(mode) == "Tales" and completion >= 0:
                message = "Quest progressed!"
                if completion == 0:
                    await crown_utilities.bless(reward, player.id)
                    message = f"Quest Completed! :coin:{reward} has been added to your balance."
                    # server_query = {'GNAME': str(player.guild)}
                    # update_server_query = {
                    #     '$inc': {'SERVER_BALANCE': 5000}
                    # }
                    # updated_server = db.updateServer(server_query, update_server_query)

                query = {'DID': str(player.id)}
                update_query = {'$inc': {'QUESTS.$[type].' + "WINS": 1}}
                filter_query = [{'type.' + "OPPONENT": opponent}]
                resp = db.updateVault(query, update_query, filter_query)

                return message
            else:
                return False
        else:
            return False
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        return


async def destiny(player, opponent, mode):
    vault = db.queryVault({'DID': str(player.id)})
    user = db.queryUser({"DID": str(player.id)})
    vault_query = {'DID': str(player.id)}
    card_info = db.queryCard({"NAME": str(user['CARD'])})
    skin_for = card_info['SKIN_FOR']
    
    hand_limit = 25
    storage_allowed_amount = user['STORAGE_TYPE'] * 15
    storage_amount = len(vault['STORAGE'])
    hand_length = len(vault['CARDS'])
    list1 = vault['CARDS']
    list2 = vault['STORAGE']
    current_cards = list1.extend(list2)

    if hand_length >= hand_limit and storage_amount >= storage_allowed_amount:
        message = f"Your storage is full. You are unable to complete the destinies until you have available storage for rewarded destiny cards."
        return message



    owned_destinies = []
    for destiny in vault['DESTINY']:
        owned_destinies.append(destiny['NAME'])

    owned_card_levels_list = []
    for c in vault['CARD_LEVELS']:
        owned_card_levels_list.append(c['CARD'])
    message = ""
    completion = 1
    try:
        if vault['DESTINY']:
            # TALES
            for destiny in vault['DESTINY']:
                if (user['CARD'] in destiny['USE_CARDS'] or skin_for in destiny['USE_CARDS']) and opponent == destiny['DEFEAT'] and mode == "Tales":
                    if destiny['WINS'] < destiny['REQUIRED']:
                        message = f"Secured a win toward **{destiny['NAME']}**. Keep it up!"
                        completion = destiny['REQUIRED'] - (destiny['WINS'] + 1)

                    if completion == 0:
                        try:
                            if destiny['EARN'] not in owned_card_levels_list:
                                # Add the CARD_LEVELS for Destiny Card
                                update_query = {'$addToSet': {
                                    'CARD_LEVELS': {'CARD': str(destiny['EARN']), 'LVL': 0, 'TIER': 0, 'EXP': 0,
                                                    'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0}}}
                                db.updateVaultNoFilter(vault_query, update_query)
                                #
                        except Exception as ex:
                            print(f"Error in Completing Destiny: {ex}")

                        if len(list1) >= 25 and storage_amount < storage_allowed_amount:
                            response = db.updateVaultNoFilter(vault_query, {'$addToSet': {'STORAGE': str(destiny['EARN'])}})
                            message = f"**{destiny['NAME']}** completed! **{destiny['EARN']}** has been added to your storage!"
                        else:
                            response = db.updateVaultNoFilter(vault_query, {'$addToSet': {'CARDS': str(destiny['EARN'])}})
                            message = f"**{destiny['NAME']}** completed! **{destiny['EARN']}** has been added to your vault!"
                        query = {'DID': str(player.id)}
                        update_query = {'$pull': {'DESTINY': {'NAME': destiny['NAME']}}}
                        resp = db.updateVaultNoFilter(query, update_query)

                        for dest in d.destiny:
                            if destiny['EARN'] in dest["USE_CARDS"] and dest['NAME'] not in owned_destinies:
                                db.updateVaultNoFilter(vault_query, {'$addToSet': {'DESTINY': dest}})
                                message = f"**DESTINY AWAITS!**\n**New Destinies** have been added to your vault."
                        await player.send(message)
                        return message

                    query = {'DID': str(player.id)}
                    update_query = {'$inc': {'DESTINY.$[type].' + "WINS": 1}}
                    filter_query = [{'type.' + "DEFEAT": opponent, 'type.' + 'USE_CARDS':user['CARD']}]
                    if user['CARD'] not in destiny['USE_CARDS']:
                        filter_query = [{'type.' + "DEFEAT": opponent, 'type.' + 'USE_CARDS':skin_for}]
                    resp = db.updateVault(query, update_query, filter_query)
                    await player.send(message)
                    return message

            # Dungeon
            for destiny in vault['DESTINY']:
                if user['CARD'] in destiny['USE_CARDS'] and opponent == destiny['DEFEAT'] and mode == "Dungeon":
                    message = f"Secured a win toward **{destiny['NAME']}**. Keep it up!"
                    completion = destiny['REQUIRED'] - (destiny['WINS'] + 3)

                    if completion <= 0:
                        try:
                            if destiny['EARN'] not in owned_card_levels_list:
                                # Add the CARD_LEVELS for Destiny Card
                                update_query = {'$addToSet': {
                                    'CARD_LEVELS': {'CARD': str(destiny['EARN']), 'LVL': 0, 'TIER': 0, 'EXP': 0,
                                                    'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0}}}
                                db.updateVaultNoFilter(vault_query, update_query)
                                #
                        except Exception as ex:
                            print(f"Error in Completing Destiny: {ex}")

                        if len(list1) >= 25 and storage_amount < storage_allowed_amount:
                            response = db.updateVaultNoFilter(vault_query, {'$addToSet': {'STORAGE': str(destiny['EARN'])}})
                            message = f"**{destiny['NAME']}** completed! **{destiny['EARN']}** has been added to your storage!"
                        else:
                            response = db.updateVaultNoFilter(vault_query, {'$addToSet': {'CARDS': str(destiny['EARN'])}})
                            message = f"**{destiny['NAME']}** completed! **{destiny['EARN']}** has been added to your vault!"
                        query = {'DID': str(player.id)}
                        update_query = {'$pull': {'DESTINY': {'NAME': destiny['NAME']}}}
                        resp = db.updateVaultNoFilter(query, update_query)

                        for dest in d.destiny:
                            if destiny['EARN'] in dest["USE_CARDS"] and dest['NAME'] not in owned_destinies:
                                db.updateVaultNoFilter(vault_query, {'$addToSet': {'DESTINY': dest}})
                                message = f"**DESTINY AWAITS!**\n**New Destinies** have been added to your vault."
                        await player.send(message)
                        return message

                    query = {'DID': str(player.id)}
                    update_query = {'$inc': {'DESTINY.$[type].' + "WINS": 3}}
                    filter_query = [{'type.' + "DEFEAT": opponent}]
                    resp = db.updateVault(query, update_query, filter_query)
                    await player.send(message)
                    return message
        
        else:
            return False
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        await player.send(
            "There's an issue with your Destiny. Alert support.")
        return


async def summonlevel(pet, player):
    vault = db.queryVault({'DID': str(player.id)})
    player_info = db.queryUser({'DID': str(player.id)})
    family_name = player_info['FAMILY']
    
    if family_name != 'PCG':
        family_info = db.queryFamily({'HEAD':str(family_name)})
        family_summon = family_info['SUMMON']
        if family_summon['NAME'] == str(pet):
            return False
    petinfo = {}
    try:
        for x in vault['PETS']:
            if x['NAME'] == str(pet):
                petinfo = x

        lvl = petinfo['LVL']  # To Level Up -(lvl * 10 = xp required)
        lvl_req = lvl * 10
        exp = petinfo['EXP']
        petmove_text = list(petinfo.keys())[3]  # Name of the ability
        petmove_ap = list(petinfo.values())[3]  # Ability Power
        petmove_type = petinfo['TYPE']
        bond = petinfo['BOND']
        bondexp = petinfo['BONDEXP']
        bond_req = ((petmove_ap * 5) * (bond + 1))

        if lvl < 10:
            # Non Level Up Code
            if exp < (lvl_req - 1):
                query = {'DID': str(player.id)}
                update_query = {'$inc': {'PETS.$[type].' + "EXP": 1}}
                filter_query = [{'type.' + "NAME": str(pet)}]
                response = db.updateVault(query, update_query, filter_query)

            # Level Up Code
            if exp >= (lvl_req - 1):
                query = {'DID': str(player.id)}
                update_query = {'$set': {'PETS.$[type].' + "EXP": 0}, '$inc': {'PETS.$[type].' + "LVL": 1}}
                filter_query = [{'type.' + "NAME": str(pet)}]
                response = db.updateVault(query, update_query, filter_query)

        if bond < 3:
            # Non Bond Level Up Code
            if bondexp < (bond_req - 1):
                query = {'DID': str(player.id)}
                update_query = {'$inc': {'PETS.$[type].' + "BONDEXP": 1}}
                filter_query = [{'type.' + "NAME": str(pet)}]
                response = db.updateVault(query, update_query, filter_query)

            # Bond Level Up Code
            if bondexp >= (bond_req - 1):
                query = {'DID': str(player.id)}
                update_query = {'$set': {'PETS.$[type].' + "BONDEXP": 0}, '$inc': {'PETS.$[type].' + "BOND": 1}}
                filter_query = [{'type.' + "NAME": str(pet)}]
                response = db.updateVault(query, update_query, filter_query)
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        await ctx.send(
            "There's an issue with leveling your Summon. Alert support.")
        return


async def savematch(player, card, path, title, arm, universe, universe_type, exclusive):
    matchquery = {'PLAYER': player, 'CARD': card, 'PATH': path, 'TITLE': title, 'ARM': arm, 'UNIVERSE': universe,
                  'UNIVERSE_TYPE': universe_type, 'EXCLUSIVE': exclusive}
    save_match = db.createMatch(data.newMatch(matchquery))


def starting_position(o, t):
    if o > t:
        return True
    else:
        return False


async def abyss_level_up_message(did, floor, card, title, arm):
    try:
        message = ""
        drop_message = []
        maxed_out_messages = []
        new_unlock = False
        vault_query = {'DID': did}
        vault = db.altQueryVault(vault_query)
        owned_destinies = []
        for destiny in vault['DESTINY']:
            owned_destinies.append(destiny['NAME'])
        card_info = db.queryCard({'NAME': str(card)})
        title_info = db.queryTitle({'TITLE': str(title)})
        arm = db.queryArm({'ARM':str(arm)})
        arm_arm = arm['ARM']
        floor_val = int(floor)
        coin_drop = round(100000 + (floor_val * 10000))
        durability = random.randint(75, 125)
        card_drop = card
        title_drop = title
        arm_drop = arm
        # Determine first to beat floor 100
        if floor == 100:
            all_users = db.queryAllUsers()
            first = True
            for user in all_users:
                if user['LEVEL'] == 101:
                    first = False
            if first:
                winner = {
                    'PLAYER': vault['OWNER'],
                    'DID': vault['DID'],
                    'CARD': card,
                    'TITLE': title,
                    'ARM': arm
                }
                rr = db.createGods(data.newGods(winner))

        
        if floor in abyss_floor_reward_list:
            u = await main.bot.fetch_user(did)
            tresponse = await crown_utilities.store_drop_card(u, did, title_drop, title_info['UNIVERSE'], vault, owned_destinies, coin_drop, coin_drop, "Abyss", False, 0, "titles")
            # current_titles = vault['TITLES']
            # if len(current_titles) >=25:
            #     drop_message.append("You have max amount of Titles. You did not receive the **Floor Title**.")
            # elif title in current_titles:
            #     maxed_out_messages.append(f"You already own {title_drop} so you did not receive it.")
            # else:
            #     db.updateVaultNoFilter(vault_query,{'$addToSet':{'TITLES': str(title_drop)}}) 
            #     drop_message.append(f"🎗️ **{title_drop}**")

            aresponse = await crown_utilities.store_drop_card(u, did, arm_arm, arm['UNIVERSE'], vault, durability, coin_drop, coin_drop, "Abyss", False, 0, "arms")
            # current_arms = []
            # for arm in vault['ARMS']:
            #     current_arms.append(arm['ARM'])
            # if len(current_arms) >=25:
            #     maxed_out_messages.append("You have max amount of Arms. You did not receive the **Floor Arm**.")
            # elif arm_arm in current_arms:
            #     maxed_out_messages.append(f"You already own {arm_drop['ARM']} so you did not receive it.")
            # else:
            #     db.updateVaultNoFilter(vault_query,{'$addToSet':{'ARMS': {'ARM': str(arm_drop['ARM']), 'DUR': 25}}})
            #     drop_message.append(f"🦾 **{arm_drop['ARM']}**")
            
            cresponse = await crown_utilities.store_drop_card(u, did, card_drop, card_info['UNIVERSE'], vault, owned_destinies, coin_drop, coin_drop, "Abyss", False, 0, "cards")
            drop_message.append(tresponse)
            drop_message.append(aresponse)
            drop_message.append(cresponse)
            # current_cards = vault['CARDS']
            # if len(current_cards) >= 25:
            #     maxed_out_messages.append("You have max amount of Cards. You did not earn receive **Floor Card**.")
            # elif card in current_cards:
            #     maxed_out_messages.append(f"You already own {card_drop} so you did not receive it.")
            # else:
            #     db.updateVaultNoFilter(vault_query,{'$addToSet': {'CARDS': str(card_drop)}})
            #     drop_message.append(f"🎴 **{card_drop}**")

            
            # owned_card_levels_list = []
            # for c in vault['CARD_LEVELS']:
            #     owned_card_levels_list.append(c['CARD'])

            # owned_destinies = []
            # for destiny in vault['DESTINY']:
            #     owned_destinies.append(destiny['NAME'])
            
            # if card not in owned_card_levels_list:
            #     update_query = {'$addToSet': {'CARD_LEVELS': {'CARD': str(card), 'LVL': 0, 'TIER': 0, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0}}}
            #     r = db.updateVaultNoFilter(vault_query, update_query)

            # counter = 2
            # for destiny in d.destiny:
            #     if card in destiny["USE_CARDS"] and destiny['NAME'] not in owned_destinies:
            #         counter = counter - 1
            #         db.updateVaultNoFilter(vault_query, {'$addToSet': {'DESTINY': destiny}})
            #         if counter >=1:
            #             drop_message.append(f"**DESTINY AWAITS!**")
        else:
            drop_message.append(f":coin: **{'{:,}'.format(coin_drop)}** has been added to your vault!")

        # if floor == 0:
        #     message = "🎊 Congratulations! 🎊 You unlocked **Shop!**. Use the **/shop** command to purchase Cards, Titles and Arms!"
        #     new_unlock = True
        
        # if floor == 2:
        #     message = "🎊 Congratulations! 🎊 You unlocked **Tales! and Scenarios!**. Use the **/solo** command to battle through Universes to earn Cards, Titles, Arms, Summons, and Money!"
        #     new_unlock = True

        # if floor == 8:
        #     message = "🎊 Congratulations! 🎊 You unlocked **Crafting!**. Use the **/craft** command to craft Universe Items such as Universe Souls, or even Destiny Line Wins toward Destiny Cards!"
        #     new_unlock = True

        if floor == 3:
            message = "🎊 Congratulations! 🎊 You unlocked **PVP and Guilds**. Use /pvp to battle another player or join together to form a Guild! Use /help to learn more.!"
            new_unlock = True

        if floor == 31:
            message = "🎊 Congratulations! 🎊 You unlocked **Marriage**. You're now able to join Families!Share summons and purchase houses.Use /help to learn more about  Family commands!"
            new_unlock = True
            
        if floor == 10:
            message = "🎊 Congratulations! 🎊 You unlocked **Trading**. Use the **/trade** command to Trade Cards, Titles and Arms with other players!"
            new_unlock = True

        # if floor == 3:
        #     message = "🎊 Congratulations! 🎊 You unlocked **PVP**. \nUse the /**pvp** command to PVP against other players!"
        #     new_unlock = True

        if floor == 20:
            message = "🎊 Congratulations! 🎊 You unlocked **Gifting**. Use the **/gift** command to gift players money!"
            new_unlock = True
        
        # if floor == 3:
        #     message = "🎊 Congratulations! 🎊 You unlocked **Co-Op**. Use the **/coop** to traverse Tales with other players!"
        #     new_unlock = True
            
        if floor == 15:
            message = "🎊 Congratulations! 🎊 You unlocked **Associations**. Use the **/oath** to create an association with another Guild Owner!"
            new_unlock = True

        if floor == 25:
            message = "🎊 Congratulations! 🎊 You unlocked **Explore Mode**. Explore Mode allows for Cards to spawn randomly with Bounties! If you defeat the Card you will earn that Card + it's Bounty! Happy Hunting!"
            new_unlock = True

        if floor == 40:
            message = "🎊 Congratulations! 🎊 You unlocked **Dungeons**. Use the **/solo** command and select Dungeons to battle through the Hard Mode of Universes to earn super rare Cards, Titles, and Arms!"
            new_unlock = True
            
        # if floor == 7:
        #     message = "🎊 Congratulations! 🎊 You unlocked **Duo**. Use the **/duo** command and select a Difficulty and a Preset to bring into Tales with you!"
        #     new_unlock = True

        if floor == 60:
            message = "🎊 Congratulations! 🎊 You unlocked **Bosses**. Use the **/solo** command and select Boss to battle Universe Bosses too earn ultra rare Cards, Titles, and Arms!"
            new_unlock = True
            
        if floor == 100:
            message = "🎊 Congratulations! 🎊 You unlocked **Soul Exchange**. Use the **/exchange** command and Exchange any boss souls for cards from their respective universe! This will Reset your Abyss Level!"
            new_unlock = True


        return {"MESSAGE": message, "NEW_UNLOCK": new_unlock, "DROP_MESSAGE": drop_message}
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        return         

# DONT REMOVE THIS
cache = dict()

def get_card(url, cardname, cardtype):
    try:
        # save_path = f"image_cache/{str(cardtype)}/{str(cardname)}.png"
        # # print(save_path)
        
        # if url not in cache:
        #     # print("Not in Cache")
        #     cache[url] = save_path
        #     im = Image.open(requests.get(url, stream=True).raw)
        #     im.save(f"{save_path}", "PNG")
        #     # print(f"NO : {cardname}")
        #     return im

        # else:
        #     # print("In Cache")
        #     im = Image.open(cache[url])
        #     # print(f"YES : {cardname}")
        #     return im
        im = Image.open(requests.get(url, stream=True).raw)
        return im
           
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        return         
          
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        return

     
def showsummon(url, summon, message, lvl, bond):
    # Card Name can be 16 Characters before going off Card
    # Lower Card Name Font once after 16 characters
    try:
        im = Image.open(requests.get(url, stream=True).raw)

        draw = ImageDraw.Draw(im)

        # Font Size Adjustments
        # Name not go over Card
        name_font_size = 80
        if len(list(summon)) >= 10:
            name_font_size = 45
        if len(list(summon)) >= 14:
            name_font_size = 36
        

        header = ImageFont.truetype("YesevaOne-Regular.ttf", name_font_size)
        s = ImageFont.truetype("Roboto-Bold.ttf", 22)
        h = ImageFont.truetype("YesevaOne-Regular.ttf", 37)
        m = ImageFont.truetype("Roboto-Bold.ttf", 25)
        r = ImageFont.truetype("Freedom-10eM.ttf", 40)
        lvl_font = ImageFont.truetype("Neuton-Bold.ttf", 68)
        health_and_stamina_font = ImageFont.truetype("Neuton-Light.ttf", 41)
        attack_and_shield_font = ImageFont.truetype("Neuton-Bold.ttf", 48)
        moveset_font = ImageFont.truetype("antonio.regular.ttf", 40)
        rhs = ImageFont.truetype("destructobeambb_bold.ttf", 35)
        stats = ImageFont.truetype("Freedom-10eM.ttf", 30)
        card_details_font_size = ImageFont.truetype("destructobeambb_bold.ttf", 25)
        card_levels = ImageFont.truetype("destructobeambb_bold.ttf", 40)

        # Pet Name
        draw.text((600, 160), summon, (255, 255, 255), font=header, stroke_width=1, stroke_fill=(0, 0, 0),
                    align="left")

        # Level
        lvl_sizing = (89, 70)
        if int(lvl) > 9:
            lvl_sizing = (75, 70)
 
        draw.text(lvl_sizing, f"{lvl}", (255, 255, 255), font=lvl_font, stroke_width=1, stroke_fill=(0, 0, 0),
                    align="center")
        draw.text((1096, 65), f"{bond}", (255, 255, 255), font=lvl_font, stroke_width=1, stroke_fill=(0, 0, 0),
                    align="center")

        lines = textwrap.wrap(message, width=28)
        y_text = 330
        for line in lines:
            font=moveset_font
            width, height = font.getsize(line)
            with Pilmoji(im) as pilmoji:
                pilmoji.text(((1730 - width) / 2, y_text), line, (255, 255, 255), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
            y_text += height


        with BytesIO() as image_binary:
            im.save(image_binary, "PNG")
            image_binary.seek(0)
            # await ctx.send(file=discord.File(fp=image_binary,filename="image.png"))
            file = discord.File(fp=image_binary,filename="pet.png")
            return file

    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        return


def setup(bot):
    bot.add_cog(CrownUnlimited(bot))



async def abyss(self, ctx: SlashContext, _player):
    await ctx.defer()
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return

    mode = "ABYSS"
    if isinstance(ctx.channel, discord.channel.DMChannel):
        await ctx.send(m.SERVER_FUNCTION_ONLY)
        return

    try:
        # Use Battle Class Method "set_abyss_config" here which populates
        abyss = Battle(mode, _player)

        abyss_embed = abyss.set_abyss_config(_player)

        abyss_buttons = [
            manage_components.create_button(
                style=ButtonStyle.blue,
                label="Begin",
                custom_id="Yes"
            ),
            manage_components.create_button(
                style=ButtonStyle.red,
                label="Quit",
                custom_id="No"
            )
        ]

        abyss_buttons_action_row = manage_components.create_actionrow(*abyss_buttons)


        msg = await ctx.send(embed=abyss_embed, components=[abyss_buttons_action_row])

        def check(button_ctx):
            return button_ctx.author == ctx.author

        try:
            button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[
                abyss_buttons_action_row, abyss_buttons], timeout=120, check=check)

            if button_ctx.custom_id == "Yes":
                await button_ctx.defer(ignore=True)
                await msg.edit(components=[])

                if abyss.abyss_player_card_tier_is_banned:
                    await ctx.send(
                        f":x: We're sorry! The tier of your equipped card is banned on floor {floor}. Please, try again with another card.")
                    return
                
                await battle_commands(self, ctx, abyss, _player, _player2=None)

            elif button_ctx.custom_id == "No":
                await button_ctx.send("Leaving the Abyss...")
                await msg.edit(components=[])
                return
            else:
                await button_ctx.send("Leaving the Abyss...")
                await msg.edit(components=[])
                return
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            guild = self.bot.get_guild(main.guild_id)
            channel = guild.get_channel(main.guild_channel)
            await channel.send(f"'PLAYER': **{str(ctx.author)}**, 'GUILD': **{str(ctx.author.guild)}**,  TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")
            return
    
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        guild = self.bot.get_guild(main.guild_id)
        channel = guild.get_channel(main.guild_channel)
        await channel.send(f"'PLAYER': **{str(ctx.author)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")
        return


async def scenario(self, ctx: SlashContext, _player, universe: str):
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return

    mode = "SCENARIO"
    try:
        scenario = Battle(mode, _player)
        scenario._selected_universe = universe
        embed_list = scenario.set_scenario_selection()
        
        if not embed_list:
            await ctx.send(f"There are currently no Scenario battles available in **{universe}**.")

        buttons = [
            manage_components.create_button(style=3, label="Start This Scenario Battle!", custom_id="start"),
        ]
        custom_action_row = manage_components.create_actionrow(*buttons)


        async def custom_function(self, button_ctx):
            if button_ctx.author == ctx.author:
                selected_scenario = str(button_ctx.origin_message.embeds[0].title)
                if button_ctx.custom_id == "start":
                    await button_ctx.defer(ignore=True)
                    selected_scenario = db.queryScenario({'TITLE':selected_scenario})
                    scenario.set_scenario_config(selected_scenario)
                    await battle_commands(self, ctx, scenario, _player, _player2=None)
                    self.stop = True
            else:
                await ctx.send("This is not your prompt! Shoo! Go Away!")


        await Paginator(bot=self.bot, ctx=ctx, useQuitButton=True, pages=embed_list, timeout=60, customActionRow=[
            custom_action_row,
            custom_function,
        ]).run()

    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))


async def cardlist(self, ctx: SlashContext, universe: str):
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return

    universe_data = db.queryUniverse({'TITLE': {"$regex": str(universe), "$options": "i"}})
    user = db.queryUser({'DID': str(ctx.author.id)})
    list_of_cards = db.queryAllCardsBasedOnUniverse({'UNIVERSE': {"$regex": str(universe), "$options": "i"}})
    cards = [x for x in list_of_cards]
    dungeon_card_details = []
    tales_card_details = []
    destiny_card_details = []
    for card in cards:
        moveset = card['MOVESET']
        move3 = moveset[2]
        move2 = moveset[1]
        move1 = moveset[0]
        basic_attack_emoji = crown_utilities.set_emoji(list(move1.values())[2])
        super_attack_emoji = crown_utilities.set_emoji(list(move2.values())[2])
        ultimate_attack_emoji = crown_utilities.set_emoji(list(move3.values())[2])


        available = ""
        is_skin = ""
        if card['AVAILABLE'] and card['EXCLUSIVE']:
            available = ":purple_circle:"
        elif card['AVAILABLE'] and not card['HAS_COLLECTION']:
            available = ":green_circle:"
        elif card['HAS_COLLECTION']:
            available = ":blue_circle:"
        else:
            available = "🟠"
        if card['IS_SKIN']:
            is_skin = ":white_circle:"
        if card['EXCLUSIVE'] and not card['HAS_COLLECTION']:
            dungeon_card_details.append(
                f"{is_skin}{available}  :mahjong: {card['TIER']} **{card['NAME']}** {basic_attack_emoji} {super_attack_emoji} {ultimate_attack_emoji}\n:heart: {card['HLT']} :dagger: {card['ATK']}  🛡️ {card['DEF']}\n")
        elif not card['HAS_COLLECTION']:
            tales_card_details.append(
                f"{is_skin}{available} :mahjong: {card['TIER']} **{card['NAME']}** {basic_attack_emoji} {super_attack_emoji} {ultimate_attack_emoji}\n:heart: {card['HLT']} :dagger: {card['ATK']}  🛡️ {card['DEF']}\n")
        elif card['HAS_COLLECTION']:
            destiny_card_details.append(
                f"{is_skin}{available} :mahjong: {card['TIER']} **{card['NAME']}** {basic_attack_emoji} {super_attack_emoji} {ultimate_attack_emoji}\n:heart: {card['HLT']} :dagger: {card['ATK']}  🛡️ {card['DEF']}\n")

    all_cards = []
    if tales_card_details:
        for t in tales_card_details:
            all_cards.append(t)

    if dungeon_card_details:
        for d in dungeon_card_details:
            all_cards.append(d)

    if destiny_card_details:
        for de in destiny_card_details:
            all_cards.append(de)

    total_cards = len(all_cards)

    # Adding to array until divisible by 10
    while len(all_cards) % 10 != 0:
        all_cards.append("")
    # Check if divisible by 10, then start to split evenly

    if len(all_cards) % 10 == 0:
        first_digit = int(str(len(all_cards))[:1])
        if len(all_cards) >= 89:
            if first_digit == 1:
                first_digit = 10
        # first_digit = 10
        cards_broken_up = np.array_split(all_cards, first_digit)

    # If it's not an array greater than 10, show paginationless embed
    if len(all_cards) < 10:
        embedVar = discord.Embed(title=f"{universe} Card List", description="\n".join(all_cards), colour=0x7289da)
        embedVar.set_footer(
            text=f"{total_cards} Total Cards\n🟢 Tale Drop\n🟣 Dungeon Drop\n🔵 Destiny Line\n🟠 Scenario Drop\n⚪ Skin")
        await ctx.send(embed=embedVar)

    embed_list = []
    for i in range(0, len(cards_broken_up)):
        globals()['embedVar%s' % i] = discord.Embed(
            title=f":flower_playing_cards: {universe_data['TITLE']} Card List",
            description="\n".join(cards_broken_up[i]), colour=0x7289da)
        globals()['embedVar%s' % i].set_footer(
            text=f"{total_cards} Total Cards\n🟢 Tale Drop\n🟣 Dungeon Drop\n🔵 Destiny Line\n🟠 Scenario Drop\n⚪ Skin\n/view *Card Name* `🎴 It's A Card`")
        embed_list.append(globals()['embedVar%s' % i])

    paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
    paginator.add_reaction('⏮️', "first")
    paginator.add_reaction('⬅️', "back")
    paginator.add_reaction('🔐', "lock")
    paginator.add_reaction('➡️', "next")
    paginator.add_reaction('⏭️', "last")
    embeds = embed_list
    await paginator.run(embeds)


async def titlelist(self, ctx: SlashContext, universe: str):
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return


    universe_data = db.queryUniverse({'TITLE': {"$regex": universe, "$options": "i"}})
    user = db.queryUser({'DID': str(ctx.author.id)})
    list_of_titles = db.queryAllTitlesBasedOnUniverses({'UNIVERSE': {"$regex": str(universe), "$options": "i"}})
    titles = [x for x in list_of_titles]
    dungeon_titles_details = []
    tales_titles_details = []
    for title in titles:
        title_passive = title['ABILITIES'][0]
        title_passive_type = list(title_passive.keys())[0].title()
        title_passive_value = list(title_passive.values())[0]

        available = ""
        if title['AVAILABLE'] and title['EXCLUSIVE']:
            available = ":purple_circle:"
        elif title['AVAILABLE']:
            available = ":green_circle:"
        else:
            available = ":red_circle:"
        if title['EXCLUSIVE']:
            dungeon_titles_details.append(
                f"{available} :reminder_ribbon: **{title['TITLE']}**\n**{title_passive_type}:** {title_passive_value}\n")
        else:
            tales_titles_details.append(
                f"{available} :reminder_ribbon: **{title['TITLE']}**\n**{title_passive_type}:** {title_passive_value}\n")

    all_titles = []
    if tales_titles_details:
        for t in tales_titles_details:
            all_titles.append(t)

    if dungeon_titles_details:
        for d in dungeon_titles_details:
            all_titles.append(d)

    total_titles = len(all_titles)

    # Adding to array until divisible by 10
    while len(all_titles) % 10 != 0:
        all_titles.append("")
    # Check if divisible by 10, then start to split evenly
    if len(all_titles) % 10 == 0:
        first_digit = int(str(len(all_titles))[:1])
        if len(all_titles) >= 89:
            if first_digit == 1:
                first_digit = 10
        titles_broken_up = np.array_split(all_titles, first_digit)

    # If it's not an array greater than 10, show paginationless embed
    if len(all_titles) < 10:
        embedVar = discord.Embed(title=f"{universe} Title List", description="\n".join(all_titles), colour=0x7289da)
        # embedVar.set_thumbnail(url={universe_data['PATH']})
        embedVar.set_footer(text=f"{total_titles} Total Titles\n🟢 Tale Drop\n🟣 Dungeon Drop\n🔴 Boss Drop")
        await ctx.send(embed=embedVar)

    embed_list = []
    for i in range(0, len(titles_broken_up)):
        globals()['embedVar%s' % i] = discord.Embed(title=f":reminder_ribbon: {universe_data['TITLE']} Title List",
                                                    description="\n".join(titles_broken_up[i]), colour=0x7289da)
        # globals()['embedVar%s' % i].set_thumbnail(url={universe_data['PATH']})
        globals()['embedVar%s' % i].set_footer(
            text=f"{total_titles} Total Titles\n🟢 Tale Drop\n🟣 Dungeon Drop\n🔴 Boss Drop\n/view *Title Name* `🎗️ It's A Title` - View Title Details")
        embed_list.append(globals()['embedVar%s' % i])

    paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
    paginator.add_reaction('⏮️', "first")
    paginator.add_reaction('⬅️', "back")
    paginator.add_reaction('🔐', "lock")
    paginator.add_reaction('➡️', "next")
    paginator.add_reaction('⏭️', "last")
    embeds = embed_list
    await paginator.run(embeds)


async def armlist(self, ctx: SlashContext, universe: str):
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return


    universe_data = db.queryUniverse({'TITLE': {"$regex": universe, "$options": "i"}})
    user = db.queryUser({'DID': str(ctx.author.id)})
    list_of_arms = db.queryAllArmsBasedOnUniverses({'UNIVERSE': {"$regex": str(universe), "$options": "i"}})
    arms = [x for x in list_of_arms]
    dungeon_arms_details = []
    tales_arms_details = []
    for arm in arms:
        arm_passive = arm['ABILITIES'][0]
        arm_passive_type = list(arm_passive.keys())[0].title()
        arm_passive_value = list(arm_passive.values())[0]

        arm_message = f"🦾 **{arm['ARM']}**\n**{arm_passive_type}:** {arm_passive_value}\n"

        element = arm['ELEMENT']
        element_available = ['BASIC', 'SPECIAL', 'ULTIMATE']
        if element and arm_passive_type.upper() in element_available:
            element_name = element
            element = crown_utilities.set_emoji(element)
            arm_message = f"🦾 **{arm['ARM']}**\n{element} **{arm_passive_type} {element_name.title()} Attack:** {arm_passive_value}\n"

        available = ""
        if arm['AVAILABLE'] and arm['EXCLUSIVE']:
            available = ":purple_circle:"
        elif arm['AVAILABLE']:
            available = ":green_circle:"
        else:
            available = ":red_circle:"

        
        if arm['EXCLUSIVE']:
            dungeon_arms_details.append(
                f"{available} {arm_message}")
        else:
            tales_arms_details.append(
                f"{available} {arm_message}")

    all_arms = []
    if tales_arms_details:
        for t in tales_arms_details:
            all_arms.append(t)

    if dungeon_arms_details:
        for d in dungeon_arms_details:
            all_arms.append(d)

    total_arms = len(all_arms)
    # Adding to array until divisible by 10
    while len(all_arms) % 10 != 0:
        all_arms.append("")
    # Check if divisible by 10, then start to split evenly
    if len(all_arms) % 10 == 0:
        first_digit = int(str(len(all_arms))[:1])
        if len(all_arms) >= 89:
            if first_digit == 1:
                first_digit = 10
        arms_broken_up = np.array_split(all_arms, first_digit)

    # If it's not an array greater than 10, show paginationless embed
    if len(all_arms) < 10:
        embedVar = discord.Embed(title=f"{universe} Arms List", description="\n".join(all_arms), colour=0x7289da)
        embedVar.set_footer(text=f"{total_arms} Total Arms\n🟢 Tale Drop\n🟣 Dungeon Drop\n🔴 Boss Drop")
        await ctx.send(embed=embedVar)

    embed_list = []
    for i in range(0, len(arms_broken_up)):
        globals()['embedVar%s' % i] = discord.Embed(title=f"🦾 {universe_data['TITLE']} Arms List",
                                                    description="\n".join(arms_broken_up[i]), colour=0x7289da)
        globals()['embedVar%s' % i].set_footer(
            text=f"{total_arms} Total Arms\n🟢 Tale Drop\n🟣 Dungeon Drop\n🔴 Boss Drop\n /view *Arm Name* `🦾Its' An Arm`")
        embed_list.append(globals()['embedVar%s' % i])

    paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
    paginator.add_reaction('⏮️', "first")
    paginator.add_reaction('⬅️', "back")
    paginator.add_reaction('🔐', "lock")
    paginator.add_reaction('➡️', "next")
    paginator.add_reaction('⏭️', "last")
    embeds = embed_list
    await paginator.run(embeds)


async def destinylist(self, ctx: SlashContext, universe: str):
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return


    universe_data = db.queryUniverse({'TITLE': {"$regex": universe, "$options": "i"}})
    user = db.queryUser({'DID': str(ctx.author.id)})
    destinies = []
    for destiny in d.destiny:
        if destiny["UNIVERSE"].upper() == universe.upper():
            destinies.append(destiny)

    destiny_details = []
    for de in destinies:
        destiny_details.append(
            f":sparkles: **{de['NAME']}**\nDefeat {de['DEFEAT']} with {' '.join(de['USE_CARDS'])} {str(de['REQUIRED'])} times: Unlock **{de['EARN']}**\n")

    total_destinies = len(destiny_details)
    if total_destinies <= 0:
        await ctx.send(f"There are no current Destinies in **{universe_data['TITLE']}**. Check again later")
        return

    # Adding to array until divisible by 10
    while len(destiny_details) % 10 != 0:
        destiny_details.append("")
    # Check if divisible by 10, then start to split evenly

    if len(destiny_details) % 10 == 0:
        first_digit = int(str(len(destiny_details))[:1])
        if len(destiny_details) >= 89:
            if first_digit == 1:
                first_digit = 10
        destinies_broken_up = np.array_split(destiny_details, first_digit)

    # If it's not an array greater than 10, show paginationless embed
    if len(destiny_details) < 10:
        embedVar = discord.Embed(title=f"{universe} Destiny List", description="\n".join(destiny_details),
                                colour=0x7289da)
        globals()['embedVar%s' % i].set_footer(text=f"{total_destinies} Total Destiny Lines")
        await ctx.send(embed=embedVar)

    embed_list = []
    for i in range(0, len(destinies_broken_up)):
        globals()['embedVar%s' % i] = discord.Embed(title=f":rosette: {universe_data['TITLE']} Destiny List",
                                                    description="\n".join(destinies_broken_up[i]), colour=0x7289da)
        globals()['embedVar%s' % i].set_footer(text=f"{total_destinies} Total Destiny Lines")
        embed_list.append(globals()['embedVar%s' % i])

    paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
    paginator.add_reaction('⏮️', "first")
    paginator.add_reaction('⬅️', "back")
    paginator.add_reaction('🔐', "lock")
    paginator.add_reaction('➡️', "next")
    paginator.add_reaction('⏭️', "last")
    embeds = embed_list
    await paginator.run(embeds)


async def summonlist(self, ctx: SlashContext, universe: str):
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return


    universe_data = db.queryUniverse({'TITLE': {"$regex": universe, "$options": "i"}})
    user = db.queryUser({'DID': str(ctx.author.id)})
    list_of_pets = db.queryAllPetsBasedOnUniverses({'UNIVERSE': {"$regex": str(universe), "$options": "i"}})
    pets = [x for x in list_of_pets]
    dungeon_pets_details = []
    tales_pets_details = []
    for pet in pets:
        pet_ability = list(pet['ABILITIES'][0].keys())[0]
        pet_ability_power = list(pet['ABILITIES'][0].values())[0]
        pet_ability_type = list(pet['ABILITIES'][0].values())[1]
        available = ""
        if pet['AVAILABLE'] and pet['EXCLUSIVE']:
            available = ":purple_circle:"
        elif pet['AVAILABLE']:
            available = ":green_circle:"
        else:
            available = ":red_circle:"
        if pet['EXCLUSIVE']:
            dungeon_pets_details.append(
                f"{available} 🧬 **{pet['PET']}**\n**{pet_ability}:** {pet_ability_power}\n**Type:** {pet_ability_type}\n")
        else:
            tales_pets_details.append(
                f"{available} 🧬 **{pet['PET']}**\n**{pet_ability}:** {pet_ability_power}\n**Type:** {pet_ability_type}\n")

    all_pets = []
    if tales_pets_details:
        for t in tales_pets_details:
            all_pets.append(t)

    if dungeon_pets_details:
        for d in dungeon_pets_details:
            all_pets.append(d)

    total_pets = len(all_pets)

    # Adding to array until divisible by 10
    while len(all_pets) % 10 != 0:
        all_pets.append("")

    # Check if divisible by 10, then start to split evenly
    if len(all_pets) % 10 == 0:
        first_digit = int(str(len(all_pets))[:1])
        if len(all_pets) >= 89:
            if first_digit == 1:
                first_digit = 10
        pets_broken_up = np.array_split(all_pets, first_digit)

    # If it's not an array greater than 10, show paginationless embed
    if len(all_pets) < 10:
        embedVar = discord.Embed(title=f"{universe} Summon List", description="\n".join(all_pets), colour=0x7289da)
        embedVar.set_footer(text=f"{total_pets} Total Summons\n🟢 Tale Drop\n🟣 Dungeon Drop\n🔴 Boss Drop")
        await ctx.send(embed=embedVar)

    embed_list = []
    for i in range(0, len(pets_broken_up)):
        globals()['embedVar%s' % i] = discord.Embed(title=f"🧬 {universe_data['TITLE']} Summon List",
                                                    description="\n".join(pets_broken_up[i]), colour=0x7289da)
        globals()['embedVar%s' % i].set_footer(
            text=f"{total_pets} Total Summons\n🟢 Tale Drop\n🟣 Dungeon Drop\n🔴 Boss Drop\n/view *Summon Name* `:dna: It's A Summon`")
        embed_list.append(globals()['embedVar%s' % i])

    paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
    paginator.add_reaction('⏮️', "first")
    paginator.add_reaction('⬅️', "back")
    paginator.add_reaction('🔐', "lock")
    paginator.add_reaction('➡️', "next")
    paginator.add_reaction('⏭️', "last")
    embeds = embed_list
    await paginator.run(embeds)


async def select_universe(self, ctx, p: object, mode: str, p2: None):
    p.set_rift_on()
    await p.set_guild_data()

    if mode in crown_utilities.CO_OP_M:
        await ctx.send(f"{p.name} needs your help! React in server to join their Coop Tale!!")
        coop_buttons = [
                    manage_components.create_button(
                        style=ButtonStyle.green,
                        label="Join Battle!",
                        custom_id="yes"
                    ),
                    manage_components.create_button(
                        style=ButtonStyle.red,
                        label="Decline",
                        custom_id="no"
                    )
                ]
        coop_buttons_action_row = manage_components.create_actionrow(*coop_buttons)
        msg = await ctx.send(f"{p2.did.mention} Do you accept the **Coop Invite**?", components=[coop_buttons_action_row])
        def check(button_ctx):
            return button_ctx.author.id == p2.did
        try:
            button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[coop_buttons_action_row], timeout=120, check=check)

            if button_ctx.custom_id == "no":
                await button_ctx.send("Coop **Declined**")
                self.stop = True
                return
            
            if button_ctx.custom_id == "yes":
                await button_ctx.defer(ignore=True)
        
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            guild = self.bot.get_guild(main.guild_id)
            channel = guild.get_channel(main.guild_channel)
            await channel.send(f"'PLAYER': **{str(ctx.author)}**, 'GUILD': **{str(ctx.author.guild)}**,  TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")
            return
    
    
    if p.set_auto_battle_on(mode):
        embedVar = discord.Embed(title=f"Auto-Battles Locked", description=f"To Unlock Auto-Battles Join Patreon!",
                                 colour=0xe91e63)
        embedVar.add_field(
            name=f"Check out the #patreon channel!\nThank you for supporting the development of future games!",
            value="-Party Chat Dev Team")
        await ctx.send(embed=embedVar)
        return

    if mode in crown_utilities.TALE_M or mode in crown_utilities.DUNGEON_M:
        available_universes = p.set_selectable_universes(ctx, mode)

        buttons = [
            manage_components.create_button(style=3, label="Start Battle!", custom_id="start"),
            manage_components.create_button(style=1, label="View Available Scenario Battles!", custom_id="scenario"),
        ]
        custom_action_row = manage_components.create_actionrow(*buttons)        


        async def custom_function(self, button_ctx):
            if button_ctx.author == ctx.author:
                if button_ctx.custom_id == "scenario":
                    await button_ctx.defer(ignore=True)
                    universe = str(button_ctx.origin_message.embeds[0].title)
                    await scenario(self, ctx, p, universe)
                    self.stop = True
                    return
                elif button_ctx.custom_id == "start":                
                    await button_ctx.defer(ignore=True)
                    selected_universe = custom_function
                    custom_function.selected_universe = str(button_ctx.origin_message.embeds[0].title)
                    self.stop = True
            else:
                await ctx.send("This is not your button.", hidden=True)

        await Paginator(bot=self.bot, ctx=ctx, useQuitButton=True, deleteAfterTimeout=True, pages=available_universes, timeout=60, customActionRow=[
            custom_action_row,
            custom_function,
        ]).run()
        

        try:
            # print(custom_function.selected_universez
            selected_universe = custom_function.selected_universe
            if selected_universe == "":
                return

            universe = db.queryUniverse({'TITLE': str(selected_universe)})
            universe_owner = universe['GUILD']

            #Universe Cost
            entrance_fee = 1000


            if mode in crown_utilities.DUNGEON_M:
                entrance_fee = 5000
                
            if selected_universe in p.crestlist:
                await ctx.send(f"{crown_utilities.crest_dict[selected_universe]} | :flags: {p.association} {selected_universe} Crest Activated! No entrance fee!")
            else:
                if int(p._balance) <= entrance_fee:
                    await ctx.send(f"Tales require an :coin: {'{:,}'.format(entrance_fee)} entrance fee!", delete_after=5)
                    db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'AVAILABLE': True}})
                    return
                else:
                    await crown_utilities.curse(entrance_fee, str(ctx.author.id))
                    if universe_owner != 'PCG':
                        crest_guild = db.queryGuildAlt({'GNAME' : universe_owner})
                        if crest_guild:
                            await crown_utilities.blessguild(entrance_fee, universe['GUILD'])
                            await ctx.send(f"{crown_utilities.crest_dict[selected_universe]} | {crest_guild['GNAME']} Universe Toll Paid! :coin:{'{:,}'.format(entrance_fee)}")
            
            currentopponent = 0
            if p.difficulty != "EASY":
                currentopponent = update_save_spot(self, ctx, p.save_spot, selected_universe, crown_utilities.TALE_M)
                if mode in crown_utilities.DUNGEON_M:
                    currentopponent = update_save_spot(self, ctx, p.save_spot, selected_universe, crown_utilities.DUNGEON_M)
            else:
                currentopponent = 0

            if p.rift_on:
                update_team_response = db.updateTeam(p.filter_query, p.guild_buff_update_query)

            response = {'SELECTED_UNIVERSE': selected_universe,
                    'UNIVERSE_DATA': universe, 'CREST_LIST': p.crestlist, 'CREST_SEARCH': p.crestsearch,
                    'COMPLETED_TALES': p.completed_tales, 'OGUILD': p.association_info, 'CURRENTOPPONENT': currentopponent}
            
            if mode in crown_utilities.DUNGEON_M:
                response.update({'COMPLETED_DUNGEONS': p.completed_dungeons})

            return response
            
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))

    if mode in crown_utilities.BOSS_M:
        completed_crown_tales = p.completed_tales
        all_universes = db.queryAllUniverse()
        available_universes = []
        selected_universe = ""
        universe_menu = []
        universe_embed_list = []
        for uni in p.completed_dungeons:
            if uni != "":
                searchUni = db.queryUniverse({'TITLE': str(uni)})
                if searchUni['GUILD'] != "PCG":
                    owner_message = f"{crown_utilities.crest_dict[searchUni['TITLE']]} **Crest Owned**: {searchUni['GUILD']}"
                else: 
                    owner_message = f"{crown_utilities.crest_dict[searchUni['TITLE']]} *Crest Unclaimed*"
                if searchUni['UNIVERSE_BOSS'] != "":
                    boss_info = db.queryBoss({"NAME": searchUni['UNIVERSE_BOSS']})
                    if boss_info:
                        embedVar = discord.Embed(title= f"{uni}", description=textwrap.dedent(f"""
                        {crown_utilities.crest_dict[uni]} **Boss**: :japanese_ogre: **{boss_info['NAME']}**
                        🎗️ **Boss Title**: {boss_info['TITLE']}
                        🦾 **Boss Arm**: {boss_info['ARM']}
                        🧬 **Boss Summon**: {boss_info['PET']}
                        
                        {owner_message}
                        """))
                        embedVar.set_image(url=boss_info['PATH'])
                        embedVar.set_thumbnail(url=ctx.author.avatar_url)
                        embedVar.set_footer(text="📿| Boss Talismans ignore all Affinities. Be Prepared")
                        universe_embed_list.append(embedVar)
        if not universe_embed_list:
            await ctx.send("No available Bosses for you at this time!")
            return
        
        custom_button = manage_components.create_button(style=3, label="Select")

        async def custom_function(self, button_ctx):
            if button_ctx.author == ctx.author:
                await button_ctx.defer(ignore=True)
                selected_universe = custom_function
                custom_function.selected_universe = str(button_ctx.origin_message.embeds[0].title)
                self.stop = True
            else:
                await ctx.send("This is not your button.", hidden=True)

        await Paginator(bot=self.bot, ctx=ctx, useQuitButton=True, deleteAfterTimeout=True, pages=universe_embed_list, timeout=60,  customButton=[
            custom_button,
            custom_function,
        ]).run()

        try:
            # Universe Cost
            selected_universe = custom_function.selected_universe
            universe = db.queryUniverse({'TITLE': str(selected_universe)})
            universe_owner = universe['GUILD']
            #Universe Cost
            entrance_fee = 10000
            if selected_universe in crestlist:
                await ctx.send(f"{crown_utilities.crest_dict[selected_universe]} | :flags: {guildname} {selected_universe} Crest Activated! No entrance fee!")
            else:
                if p._balance <= entrance_fee:
                    await ctx.send(f"Tales require an :coin: {'{:,}'.format(entrance_fee)} entrance fee!", delete_after=5)
                    db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'AVAILABLE': True}})
                    return
                else:
                    await crown_utilities.curse(entrance_fee, str(ctx.author.id))
                    if universe['GUILD'] != 'PCG':
                        crest_guild = db.queryGuildAlt({'GNAME' : universe['GUILD']})
                        if crest_guild:
                            await crown_utilities.blessguild(entrance_fee, universe['GUILD'])
                            await ctx.send(f"{crown_utilities.crest_dict[selected_universe]} | {crest_guild['GNAME']} Universe Toll Paid! :coin:{'{:,}'.format(entrance_fee)}")
            categoryname = "Crown Unlimited"
            #category = discord.utils.get(guild.categories, name=categoryname)

            # if category is None: #If there's no category matching with the `name`
            #     category = await guild.create_category_channel(categoryname)
            # private_channel = await guild.create_text_channel(f'{str(ctx.author)}-{mode}-fight', overwrites=overwrites, category=category)
            # await private_channel.send(f"{ctx.author.mention} private channel has been opened for you.")

            currentopponent = 0
            return {'SELECTED_UNIVERSE': selected_universe,
                    'UNIVERSE_DATA': universe, 'CREST_LIST': p.crestlist, 'CREST_SEARCH': p.crestsearch,
                    'COMPLETED_DUNGEONS': p.completed_dungeons, 'OGUILD': p.association_info, 'BOSS_NAME': universe['UNIVERSE_BOSS'],
                    'CURRENTOPPONENT': currentopponent}
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'PLAYER': str(ctx.author),
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            #embedVar = discord.Embed(title=f"Unable to start boss fight. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", delete_after=30, colour=0xe91e63)
            #await ctx.send(embed=embedVar)
            guild = self.bot.get_guild(main.guild_id)
            channel = guild.get_channel(main.guild_channel)
            await channel.send(f"'PLAYER': **{str(ctx.author)}**, 'GUILD': **{str(ctx.author.guild)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")
            return


async def battle_commands(self, ctx, _battle, _player, _player2=None):
    
    private_channel = ctx.channel

    try:
        starttime = time.asctime()
        h_gametime = starttime[11:13]
        m_gametime = starttime[14:16]
        s_gametime = starttime[17:19]

        continued = True

        while continued == True:
            opponent_talisman_emoji = ""
            # While "continued" is True, Create Class for Players and Opponents anew
            # Opponent card will be based on list of enemies[current oppponent]
            # If player changes their equipment after a round the new class will pick it up
            player1 = _player
            player1.get_battle_ready()
            player1_card = Card(player1._equipped_card_data['NAME'], player1._equipped_card_data['PATH'], player1._equipped_card_data['PRICE'], player1._equipped_card_data['EXCLUSIVE'], player1._equipped_card_data['AVAILABLE'], player1._equipped_card_data['IS_SKIN'], player1._equipped_card_data['SKIN_FOR'], player1._equipped_card_data['HLT'], player1._equipped_card_data['HLT'], player1._equipped_card_data['STAM'], player1._equipped_card_data['STAM'], player1._equipped_card_data['MOVESET'], player1._equipped_card_data['ATK'], player1._equipped_card_data['DEF'], player1._equipped_card_data['TYPE'], player1._equipped_card_data['PASS'][0], player1._equipped_card_data['SPD'], player1._equipped_card_data['UNIVERSE'], player1._equipped_card_data['HAS_COLLECTION'], player1._equipped_card_data['TIER'], player1._equipped_card_data['COLLECTION'], player1._equipped_card_data['WEAKNESS'], player1._equipped_card_data['RESISTANT'], player1._equipped_card_data['REPEL'], player1._equipped_card_data['ABSORB'], player1._equipped_card_data['IMMUNE'], player1._equipped_card_data['GIF'], player1._equipped_card_data['FPATH'], player1._equipped_card_data['RNAME'], player1._equipped_card_data['RPATH'])
            player1_title = Title(player1._equipped_title_data['TITLE'], player1._equipped_title_data['UNIVERSE'], player1._equipped_title_data['PRICE'], player1._equipped_title_data['EXCLUSIVE'], player1._equipped_title_data['AVAILABLE'], player1._equipped_title_data['ABILITIES'])            
            player1_arm = Arm(player1._equipped_arm_data['ARM'], player1._equipped_arm_data['UNIVERSE'], player1._equipped_arm_data['PRICE'], player1._equipped_arm_data['ABILITIES'], player1._equipped_arm_data['EXCLUSIVE'], player1._equipped_arm_data['AVAILABLE'], player1._equipped_arm_data['ELEMENT'])

            player1_arm.set_durability(player1.equipped_arm, player1._arms)
            player1_card.set_card_level_buffs(player1._card_levels)
            player1_card.set_arm_config(player1_arm.passive_type, player1_arm.name, player1_arm.passive_value, player1_arm.element)
            player1_card.set_affinity_message()
            player1.get_summon_ready(player1_card)
            player1.get_talisman_ready(player1_card)

            if _battle.mode in crown_utilities.PVP_M:
                _player2.get_battle_ready()
                player2_card = Card(_player2._equipped_card_data['NAME'], _player2._equipped_card_data['PATH'], _player2._equipped_card_data['PRICE'], _player2._equipped_card_data['EXCLUSIVE'], _player2._equipped_card_data['AVAILABLE'], _player2._equipped_card_data['IS_SKIN'], _player2._equipped_card_data['SKIN_FOR'], _player2._equipped_card_data['HLT'], _player2._equipped_card_data['HLT'], _player2._equipped_card_data['STAM'], _player2._equipped_card_data['STAM'], _player2._equipped_card_data['MOVESET'], _player2._equipped_card_data['ATK'], _player2._equipped_card_data['DEF'], _player2._equipped_card_data['TYPE'], _player2._equipped_card_data['PASS'][0], _player2._equipped_card_data['SPD'], _player2._equipped_card_data['UNIVERSE'], _player2._equipped_card_data['HAS_COLLECTION'], _player2._equipped_card_data['TIER'], _player2._equipped_card_data['COLLECTION'], _player2._equipped_card_data['WEAKNESS'], _player2._equipped_card_data['RESISTANT'], _player2._equipped_card_data['REPEL'], _player2._equipped_card_data['ABSORB'], _player2._equipped_card_data['IMMUNE'], _player2._equipped_card_data['GIF'], _player2._equipped_card_data['FPATH'], _player2._equipped_card_data['RNAME'], _player2._equipped_card_data['RPATH'])
                player2_title = Title(_player2._equipped_title_data['TITLE'], _player2._equipped_title_data['UNIVERSE'], _player2._equipped_title_data['PRICE'], _player2._equipped_title_data['EXCLUSIVE'], _player2._equipped_title_data['AVAILABLE'], _player2._equipped_title_data['ABILITIES'])            
                player2_arm = Arm(_player2._equipped_arm_data['ARM'], _player2._equipped_arm_data['UNIVERSE'], _player2._equipped_arm_data['PRICE'], _player2._equipped_arm_data['ABILITIES'], _player2._equipped_arm_data['EXCLUSIVE'], _player2._equipped_arm_data['AVAILABLE'], _player2._equipped_arm_data['ELEMENT'])
                opponent_talisman_emoji = crown_utilities.set_emoji(_player2.equipped_talisman)
                player2_arm.set_durability(_player2.equipped_arm, _player2._arms)
                player2_card.set_card_level_buffs(player2._card_levels)
                player2_card.set_arm_config(player2_arm.passive_type, player2_arm.name, player2_arm.passive_value, player2_arm.element)
                player2_card.set_solo_leveling_config(player1_card._shield_active, player1_card._shield_value, player1_card._barrier_active, player1_card._barrier_value, player1_card._parry_active, player1_card._parry_value)
                player2_card.set_affinity_message()
                player2.get_summon_ready(player2_card)
                player2.get_talisman_ready(player2_card)


            if _battle.mode in crown_utilities.CO_OP_M:
                _player3.get_battle_ready()
                player3_card = Card(_player3._equipped_card_data['NAME'], _player3._equipped_card_data['PATH'], _player3._equipped_card_data['PRICE'], _player3._equipped_card_data['EXCLUSIVE'], _player3._equipped_card_data['AVAILABLE'], _player3._equipped_card_data['IS_SKIN'], _player3._equipped_card_data['SKIN_FOR'], _player3._equipped_card_data['HLT'], _player3._equipped_card_data['HLT'], _player3._equipped_card_data['STAM'], _player3._equipped_card_data['STAM'], _player3._equipped_card_data['MOVESET'], _player3._equipped_card_data['ATK'], _player3._equipped_card_data['DEF'], _player3._equipped_card_data['TYPE'], _player3._equipped_card_data['PASS'][0], _player3._equipped_card_data['SPD'], _player3._equipped_card_data['UNIVERSE'], _player3._equipped_card_data['HAS_COLLECTION'], _player3._equipped_card_data['TIER'], _player3._equipped_card_data['COLLECTION'], _player3._equipped_card_data['WEAKNESS'], _player3._equipped_card_data['RESISTANT'], _player3._equipped_card_data['REPEL'], _player3._equipped_card_data['ABSORB'], _player3._equipped_card_data['IMMUNE'], _player3._equipped_card_data['GIF'], _player3._equipped_card_data['FPATH'], _player3._equipped_card_data['RNAME'], _player3._equipped_card_data['RPATH'])
                player3_title = Title(_player3._equipped_title_data['TITLE'], _player3._equipped_title_data['UNIVERSE'], _player3._equipped_title_data['PRICE'], _player3._equipped_title_data['EXCLUSIVE'], _player3._equipped_title_data['AVAILABLE'], _player3._equipped_title_data['ABILITIES'])            
                player3_arm = Arm(_player3._equipped_arm_data['ARM'], _player3._equipped_arm_data['UNIVERSE'], _player3._equipped_arm_data['PRICE'], _player3._equipped_arm_data['ABILITIES'], _player3._equipped_arm_data['EXCLUSIVE'], _player3._equipped_arm_data['AVAILABLE'], _player3._equipped_arm_data['ELEMENT'])
                player3_talisman_emoji = crown_utilities.set_emoji(_player3.equipped_talisman)
                player3_arm.set_durability(_player3.equipped_arm, _player3._arms)
                player3_card.set_card_level_buffs()
                player3_card.set_arm_config(player3_arm.passive_type, player3_arm.name, player3_arm.passive_value, player3_arm.element)
                player3_card.set_solo_leveling_config(player1._shield_active, player1._shield_value, player1._barrier_active, player1._barrier_value, player1._parry_active, player1._parry_value)
                player3_card.set_affinity_message()
                player3.get_summon_ready(player3_card)
                player3.get_talisman_ready(player3_card)
            
            
            if _battle.is_ai_opponent:
                _battle.get_ai_battle_ready()
                player2_card = Card(_battle._ai_opponent_card_data['NAME'], _battle._ai_opponent_card_data['PATH'], _battle._ai_opponent_card_data['PRICE'], _battle._ai_opponent_card_data['EXCLUSIVE'], _battle._ai_opponent_card_data['AVAILABLE'], _battle._ai_opponent_card_data['IS_SKIN'], _battle._ai_opponent_card_data['SKIN_FOR'], _battle._ai_opponent_card_data['HLT'], _battle._ai_opponent_card_data['HLT'], _battle._ai_opponent_card_data['STAM'], _battle._ai_opponent_card_data['STAM'], _battle._ai_opponent_card_data['MOVESET'], _battle._ai_opponent_card_data['ATK'], _battle._ai_opponent_card_data['DEF'], _battle._ai_opponent_card_data['TYPE'], _battle._ai_opponent_card_data['PASS'][0], _battle._ai_opponent_card_data['SPD'], _battle._ai_opponent_card_data['UNIVERSE'], _battle._ai_opponent_card_data['HAS_COLLECTION'], _battle._ai_opponent_card_data['TIER'], _battle._ai_opponent_card_data['COLLECTION'], _battle._ai_opponent_card_data['WEAKNESS'], _battle._ai_opponent_card_data['RESISTANT'], _battle._ai_opponent_card_data['REPEL'], _battle._ai_opponent_card_data['ABSORB'], _battle._ai_opponent_card_data['IMMUNE'], _battle._ai_opponent_card_data['GIF'], _battle._ai_opponent_card_data['FPATH'], _battle._ai_opponent_card_data['RNAME'], _battle._ai_opponent_card_data['RPATH'])
                player2_title = Title(_battle._ai_opponent_title_data['TITLE'], _battle._ai_opponent_title_data['UNIVERSE'], _battle._ai_opponent_title_data['PRICE'], _battle._ai_opponent_title_data['EXCLUSIVE'], _battle._ai_opponent_title_data['AVAILABLE'], _battle._ai_opponent_title_data['ABILITIES'])            
                player2_arm = Arm(_battle._ai_opponent_arm_data['ARM'], _battle._ai_opponent_arm_data['UNIVERSE'], _battle._ai_opponent_arm_data['PRICE'], _battle._ai_opponent_arm_data['ABILITIES'], _battle._ai_opponent_arm_data['EXCLUSIVE'], _battle._ai_opponent_arm_data['AVAILABLE'], _battle._ai_opponent_arm_data['ELEMENT'])
                opponent_talisman_emoji = ""
                player2_card.set_ai_card_buffs(_battle._ai_opponent_card_lvl, _battle.stat_buff, _battle.stat_debuff, _battle.health_buff, _battle.health_debuff, _battle.ap_buff, _battle.ap_debuff)
                player2_card.set_arm_config(player2_arm.passive_type, player2_arm.name, player2_arm.passive_value, player2_arm.element)
                player2_card.set_affinity_message()
                # Set potential boss descriptions
                _battle.set_boss_descriptions(player2_card.name)
                player2_card.set_solo_leveling_config(player1_card._shield_active, player1_card._shield_value, player1_card._barrier_active, player1_card._barrier_value, player1_card._parry_active, player1_card._parry_value)
                player1_card.set_solo_leveling_config(player2_card._shield_active, player2_card._shield_value, player2_card._barrier_active, player2_card._barrier_value, player2_card._parry_active, player2_card._parry_value)
                _battle.get_ai_summon_ready(player1_card)

                if _battle.mode in crown_utilities.CO_OP_M:
                    player2_card.set_solo_leveling_config(player3_card._shield_active, player3_card._shield_value, player3_card._barrier_active, player3_card._barrier_value, player3_card._parry_active, player3_card._parry_value)
            

            if _battle.mode in crown_utilities.PVP_M:
                player1_card.set_solo_leveling_config(player2_card._shield_active, player2_card._shield_value, player2_card._barrier_active, player2_card._barrier_value, player2_card._parry_active, player2_card._parry_value)


            if _battle.mode == "RAID":
                raidActive = True
                botActive= False

            options = [1, 2, 3, 4, 5, 0]

            
            start_tales_buttons = [
                manage_components.create_button(
                    style=ButtonStyle.blue,
                    label="Start Match",
                    custom_id="start_tales_yes"
                ),
                manage_components.create_button(
                    style=ButtonStyle.red,
                    label="End",
                    custom_id="start_tales_no"
                ),
            ]

            if _battle._can_auto_battle and not _battle._is_co_op and not _battle._is_duo:
                start_tales_buttons.append(
                    manage_components.create_button(
                        style=ButtonStyle.grey,
                        label="Auto Battle",
                        custom_id="start_auto_tales"
                    )

                )
            
            if not _battle._is_tutorial and _battle.get_can_save_match():
                if _battle._currentopponent > 0:
                    start_tales_buttons.append(
                        manage_components.create_button(
                            style=ButtonStyle.green,
                            label="Save Game",
                            custom_id="save_tales_yes"
                        )
                    )

            start_tales_buttons_action_row = manage_components.create_actionrow(*start_tales_buttons)            
            
            # Collect Discord info for users
            _battle.set_who_starts_match(player1_card.speed, player2_card.speed)
            user1 = await main.bot.fetch_user(player1.did)

            if _battle._is_pvp_match and not _battle._is_tutorial:
                user2 = await main.bot.fetch_user(_player2.did)
                battle_ping_message = await private_channel.send(f"{player_1_fetched_user.mention} 🆚 {player_2_fetched_user.mention} ")
            
            embedVar = discord.Embed(title=f"{_battle.starting_match_title}")
            embedVar.add_field(name=f"__Your Affinities: {crown_utilities.set_emoji(player1.equipped_talisman)}__", value=f"{player1_card.affinity_message}")
            embedVar.add_field(name=f"__Opponent Affinities: {opponent_talisman_emoji}__", value=f"{player2_card.affinity_message}")
            embedVar.set_image(url="attachment://image.png")
            embedVar.set_thumbnail(url=ctx.author.avatar_url)
            battle_msg = await private_channel.send(embed=embedVar, components=[start_tales_buttons_action_row], file=player2_card.showcard(_battle.mode, player2_arm, player2_title, _battle._turn_total, player1_card.defense))                

            def check(button_ctx):
                if _battle._is_pvp_match:
                    if _battle._is_tutorial:
                        return button_ctx.author == ctx.author
                    else:
                        return button_ctx.author == _player2.did
                elif _battle._is_co_op:
                    return button_ctx.author == ctx.author
                else:
                    return button_ctx.author == ctx.author

            try:
                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[
                            start_tales_buttons_action_row], timeout=300, check=check)

                if button_ctx.custom_id == "start_tales_no":
                    await battle_msg.delete()
                    await battle_ping_message.delete()
                    return

                if button_ctx.custom_id == "save_tales_yes":
                    await battle_msg.delete()
                    # await battle_ping_message.delete()
                    await save_spot(self, ctx, _battle._selected_universe, _battle.mode, _battle._currentopponent)
                    await button_ctx.send(f"Game has been saved.")
                    return
                
                if button_ctx.custom_id == "start_tales_yes" or button_ctx.custom_id == "start_auto_tales":
                    # await battle_ping_message.delete()
                    if button_ctx.custom_id == "start_auto_tales":
                        _battle._is_auto_battle = True
                        embedVar = discord.Embed(title=f"Auto Battle has started", color=0xe74c3c)
                        embedVar.set_thumbnail(url=ctx.author.avatar_url)
                        await battle_msg.delete(delay=2)
                        await asyncio.sleep(2)
                        battle_msg = await private_channel.send(embed=embedVar)
                    # await button_ctx.defer(ignore=True)
                    tmove_issue = False
                    omove_issue = False

                    
                    
                    while (_battle.game_over(player1_card, player2_card) is not True):
                        print(f"Top of battle commands turn: {str(_battle._is_turn)}")
                        if _battle.previous_moves:
                            _battle.previous_moves_len = len(_battle.previous_moves)
                            if _battle.previous_moves_len >= player1.battle_history:
                                _battle.previous_moves = _battle.previous_moves[-player1.battle_history:]
                        
                        if _battle._is_turn == 0:
                            player1_card.reset_stats_to_limiter(player2_card)

                            player1_card.yuyu_hakusho_attack_increase()
                            
                            player1_card.activate_chainsawman_trait(_battle)

                            _battle.add_battle_history_messsage(player1_card.set_bleed_hit(_battle._turn_total, player2_card))

                            _battle.add_battle_history_messsage(player1_card.set_burn_hit(player2_card))
                            
                            if player2_card.freeze_enh:
                                new_turn = player1_card.frozen(_battle, player2_card)
                                _battle._is_turn = new_turn['MESSAGE']
                                _battle.add_battle_history_messsage(new_turn['TURN'])
                                continue
                            player1_card.freeze_enh = False
                            
                            if _battle._is_co_op:
                                player3_card.freeze_enh = False

                            _battle.add_battle_history_messsage(player1_card.set_poison_hit(player2_card))
                                
                            player1_card.set_gravity_hit()

                            player1_title.activate_title_passive(_battle, player1_card, player2_card)
                            
                            player1_card.activate_card_passive(player2_card)

                            player1_card.activate_demon_slayer_trait(_battle, player2_card)

                            player2_card.activate_demon_slayer_trait(_battle, player1_card)


                            if player1_card.used_block == True:
                                player1_card.defense = int(player1_card.defense / 2)
                                player1_card.used_block = False
                            if player1_card.used_defend == True:
                                player1_card.defense = int(player1_card.defense / 2)
                                player1_card.used_defend = False

                            player1_card.set_deathnote_message(_battle)
                            player2_card.set_deathnote_message(_battle)
                            if _battle._is_co_op:
                                player3_card.set_deathnote_message(_battle)                            

                            if _battle._turn_total == 0:
                                if _battle._is_tutorial:
                                    embedVar = discord.Embed(title=f"Welcome to **Anime VS+**!",
                                                            description=f"Follow the instructions to learn how to play the Game!",
                                                            colour=0xe91e63)
                                    embedVar.add_field(name="**Moveset**",value=f"{player1_card.move1_emoji} - **Basic Attack** *10 :zap:ST*\n{player1_card.move2_emoji} - **Special Attack** *30 :zap:ST*\n{player1_card.move3_emoji} - **Ultimate Move** *80 :zap:ST*\n🦠 - **Enhancer** *20 :zap:ST*\n🛡️ - **Block** *20 :zap:ST*\n:zap: - **Resolve** : Heal and Activate Resolve\n:dna: - **Summon** : {player1.equipped_summon}")
                                    embedVar.set_footer(text="Focus State : When card deplete to 0 stamina, they focus to Heal they also gain ATK and DEF ")
                                    await private_channel.send(embed=embedVar)
                                    await asyncio.sleep(2)
                                if _battle._is_boss:
                                    embedVar = discord.Embed(title=f"**{player2_card.name}** Boss of `{player2_card.universe}`",
                                                            description=f"*{_battle._description_boss_description}*", colour=0xe91e63)
                                    embedVar.add_field(name=f"{_battle._arena_boss_description}", value=f"{_battle._arenades_boss_description}")
                                    embedVar.add_field(name=f"Entering the {_battle._arena_boss_description}", value=f"{_battle._entrance_boss_description}", inline=False)
                                    embedVar.set_footer(text=f"{player1_card.name} waits for you to strike....")
                                    await ctx.send(embed=embedVar)
                                    await asyncio.sleep(2)
                                
                            if player1_card.stamina < 10:
                                player1_card.focusing(player1_title, player2_title, player2_card, _battle)
                                
                                if _battle._is_tutorial and tutorial_focus ==False:
                                    await ctx.send(embed=_battle._tutorial_message)
                                    await asyncio.sleep(2)

                                if _battle._is_boss:
                                    await ctx.send(embed=_boss_embed_message)
                                    
                            else:
                                if _battle._is_auto_battle:                                    
                                    player1_card.set_battle_arm_messages(player2_card)

                                    player1_card.activate_solo_leveling_trait(_battle, player2_card)
                                            
                                    embedVar = discord.Embed(title=f"➡️ **Current Turn** {_battle._turn_total}", description=textwrap.dedent(f"""\
                                    {_battle.get_previous_moves_embed()}
                                    
                                    """), color=0xe74c3c)
                                    await asyncio.sleep(2)
                                    embedVar.set_thumbnail(url=ctx.author.avatar_url)
                                    embedVar.set_footer(
                                        text=f"{_battle.get_battle_window_title_text(player2_card, player1_card)}",
                                        icon_url="https://cdn.discordapp.com/emojis/789290881654980659.gif?v=1")
                                    await battle_msg.edit(embed=embedVar, components=[])

                                    
                                    
                                    selected_move = _battle.ai_battle_command(player1_card, player2_card)

                                    damage_calculation_response = player1_card.damage_cal(selected_move, _battle, player2_card)

                                    if selected_move == 5:
                                        player1_card.resolving(_battle, player2_card, player1)
                                        if _battle._is_boss:
                                            await button_ctx.send(embed=_battle._boss_embed_message)

                                    elif selected_move == 6:
                                        # Resolve Check and Calculation
                                        player1_card.use_summon(_battle, player2_card)
                                    
                                    if selected_move == 0:
                                        player1_card.use_block(_battle, damage_calculation_response, player2_card)
                                    
                                    if selected_move != 5 and selected_move != 6 and selected_move != 0:
                                        player1_card.damage_done(_battle, damage_calculation_response, player2_card)                                        

                                else:
                                    player1_card.set_battle_arm_messages(player2_card)

                                    player1_card.activate_solo_leveling_trait(_battle, player2_card)

                                    _battle.set_battle_options(player1_card, player2_card)

                                    battle_action_row = manage_components.create_actionrow(*_battle.battle_buttons)
                                    util_action_row = manage_components.create_actionrow(*_battle.utility_buttons)
                                    
                                    if _battle._is_co_op:
                                        coop_util_action_row = manage_components.create_actionrow(*_battle.co_op_util_buttons)
                                        player3_card.set_battle_arm_messages(player2_card)
                                        if carm_barrier_active:
                                            carm_message = f"💠{cbarrier_count}"
                                        elif carm_shield_active:
                                            carm_message = f"🌐{cshield_value}"
                                        elif carm_parry_active:
                                            carm_message = f"🔄{cparry_count}"
                                        if player1_card.stamina >= 20:
                                            components = [battle_action_row, coop_util_action_row, util_action_row]
                                        else:
                                            components = [battle_action_row, util_action_row]
                                        companion_stats = f"\n{player3_card.name}: ❤️{round(player3_card.health)} 🌀{round(player3_card.stamina)} 🗡️{round(player3_card.attack)}/🛡️{round(player3_card.defense)} {player3_card._arm_message}"

                                    else:
                                        components = [battle_action_row, util_action_row]

                                    player1_card.set_battle_arm_messages(player2_card)
                                    embedVar = discord.Embed(title=f"", description=textwrap.dedent(f"""\
                                    {_battle.get_previous_moves_embed()}
                                    
                                    """), color=0xe74c3c)
                                    embedVar.set_author(name=f"{player1_card._arm_message}\n{player1_card.summon_resolve_message}\n")
                                    embedVar.add_field(name=f"➡️ **Current Turn** {_battle._turn_total}", value=f"{ctx.author.mention} Select move below!")
                                    # await asyncio.sleep(2)
                                    embedVar.set_image(url="attachment://image.png")
                                    embedVar.set_thumbnail(url=ctx.author.avatar_url)
                                    embedVar.set_footer(
                                        text=f"{_battle.get_battle_footer_text(player2_card, player1_card)}",
                                        icon_url="https://cdn.discordapp.com/emojis/789290881654980659.gif?v=1")
                                    await battle_msg.delete(delay=2)
                                    await asyncio.sleep(2)
                                    battle_msg = await private_channel.send(embed=embedVar, components=components, file=player1_card.showcard(_battle.mode, player1_arm, player1_title, _battle._turn_total, player2_card.defense))

                                    # Make sure user is responding with move
                                    def check(button_ctx):
                                        return button_ctx.author == user1 and button_ctx.custom_id in _battle.battle_options

                                    try:
                                        button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot,
                                                                                                                components=components,
                                                                                                                timeout=120,
                                                                                                                check=check)
                                        
                                        if button_ctx.custom_id == "s":
                                            try:
                                                player1_card.health = 0
                                                _battle.game_over = True
                                                await save_spot(self, ctx, _battle._selected_universe, _battle.mode, _battle._currentopponent)
                                                await battle_msg.delete(delay=1)
                                                await asyncio.sleep(1)
                                                battle_msg = await private_channel.send(content="Your game has been saved.")
                                                return
                                            except Exception as ex:
                                                trace = []
                                                tb = ex.__traceback__
                                                while tb is not None:
                                                    trace.append({
                                                        "filename": tb.tb_frame.f_code.co_filename,
                                                        "name": tb.tb_frame.f_code.co_name,
                                                        "lineno": tb.tb_lineno
                                                    })
                                                    tb = tb.tb_next
                                                print(str({
                                                    'type': type(ex).__name__,
                                                    'message': str(ex),
                                                    'trace': trace
                                                }))
                                                guild = self.bot.get_guild(main.guild_id)
                                                channel = guild.get_channel(main.guild_channel)
                                                await channel.send(f"'PLAYER': **{str(ctx.author)}**, 'GUILD': **{str(ctx.author.guild)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")
                                                
                                        if button_ctx.custom_id == "b":
                                            c_stamina = c_stamina + 10
                                            c_health = c_health + 50
                                            boost_message = f"**{o_card}** Boosted **{c_card}** +10 🌀 +100 :heart:"
                                            o_block_used = True
                                            player1_card.stamina = player1_card.stamina - 20
                                            o_defense = round(o_defense * 2)
                                            embedVar = discord.Embed(title=f"{boost_message}", colour=0xe91e63)

                                            previous_moves.append(f"(**{turn_total}**) {boost_message}")
                                            # await button_ctx.defer(ignore=True)
                                            turn_total = turn_total + 1
                                            turn = 1
                                        
                                        if button_ctx.custom_id == "q" or button_ctx.custom_id == "Q":
                                            player1_card.health = 0
                                            _battle.game_over = True
                                            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) 💨 **{player1_card.name}** Fled...")
                                            await battle_msg.delete(delay=1)
                                            await asyncio.sleep(1)
                                            battle_msg = await private_channel.send(content=f"{ctx.author.mention} has fled.")
                                        
                                        if button_ctx.custom_id == "1":
                                            if _battle._is_tutorial and _battle.tutorial_basic == False:
                                                _battle.tutorial_basic =True
                                                embedVar = discord.Embed(title=f":boom:Basic Attack!",
                                                                        description=f":boom:**Basic Attack** cost **10 ST(Stamina)** to deal decent Damage!",
                                                                        colour=0xe91e63)
                                                embedVar.add_field(
                                                    name=f"Your Basic Attack: {player1_card.move1_emoji} {player1_card.move1} inflicts {player1_card.move1_element}",
                                                    value=f"**{player1_card.move1_element}** : *{element_mapping[player1_card.move1_element]}*")
                                                embedVar.set_footer(
                                                    text=f"Basic Attacks are great when you are low on stamina. Enter Focus State to Replenish!")
                                                await button_ctx.send(embed=embedVar, components=[])
                                                await asyncio.sleep(2)

                                            damage_calculation_response = player1_card.damage_cal(int(button_ctx.custom_id), _battle, player2_card)
                                        
                                        elif button_ctx.custom_id == "2":
                                            if _battle._is_tutorial and _battle.tutorial_special==False:
                                                _battle.tutorial_special = True
                                                embedVar = discord.Embed(title=f":comet:Special Attack!",
                                                                        description=f":comet:**Special Attack** cost **30 ST(Stamina)** to deal great Damage!",
                                                                        colour=0xe91e63)
                                                embedVar.add_field(
                                                    name=f"Your Special Attack: {player1_card.move2_emoji} {player1_card.move2} inflicts {player1_card.move2_element}",
                                                    value=f"**{player1_card.move2_element}** : *{element_mapping[player1_card.move2_element]}*")
                                                embedVar.set_footer(
                                                    text=f"Special Attacks are great when you need to control the Focus game! Use Them to Maximize your Focus and build stronger Combos!")
                                                await button_ctx.send(embed=embedVar)
                                                await asyncio.sleep(2)
                                            
                                            damage_calculation_response = player1_card.damage_cal(int(button_ctx.custom_id), _battle, player2_card)
                                        
                                        elif button_ctx.custom_id == "3":
                                            if _battle._is_tutorial and _battle.tutorial_ultimate==False:
                                                _battle.tutorial_ultimate=True
                                                embedVar = discord.Embed(title=f":rosette:Ultimate Move!",
                                                                        description=f":rosette:**Ultimate Move** cost **80 ST(Stamina)** to deal incredible Damage!",
                                                                        colour=0xe91e63)
                                                embedVar.add_field(
                                                    name=f"Your Ultimate: {player1_card.move3_emoji} {player1_card.move3} inflicts {player1_card.move3_element}",
                                                    value=f"**{player1_card.move3_element}** : *{element_mapping[player1_card.move3_element]}*")
                                                embedVar.add_field(name=f"Ultimate GIF",
                                                                value="Using your ultimate move also comes with a bonus GIF to deliver that final blow!\n*Enter performance mode to disable GIFs\n/performace*")
                                                embedVar.set_footer(
                                                    text=f"Ultimate moves will consume most of your ST(Stamina) for Incredible Damage! Use Them Wisely!")
                                                await button_ctx.send(embed=embedVar)
                                                await asyncio.sleep(2)
                                           
                                            damage_calculation_response = player1_card.damage_cal(int(button_ctx.custom_id), _battle, player2_card)
                                            if player1_card.gif != "N/A" and not player1.performance:
                                                # await button_ctx.defer(ignore=True)
                                                await battle_msg.delete(delay=None)
                                                # await asyncio.sleep(1)
                                                battle_msg = await private_channel.send(f"{player1_card.gif}")
                                                
                                                await asyncio.sleep(2)
                                        
                                        elif button_ctx.custom_id == "4":
                                            if _battle._is_tutorial and _battle.tutorial_enhancer==False:
                                                _battle.tutorial_enhancer = True
                                                embedVar = discord.Embed(title=f"🦠Enhancers!",
                                                                        description=f"🦠**Enhancers** cost **20 ST(Stamina)** to Boost your Card or Debuff Your Opponent!",
                                                                        colour=0xe91e63)
                                                embedVar.add_field(
                                                    name=f"Your Enhancer:🦠 {player1_card.move4} is a {player1_card.move4enh}",
                                                    value=f"**{player1_card.move4enh}** : *{enhancer_mapping[player1_card.move4enh]}*")
                                                embedVar.set_footer(
                                                    text=f"Use /enhancers to view a full list of Enhancers! Look for the {player1_card.move4enh} Enhancer")
                                                await button_ctx.send(embed=embedVar)
                                                await asyncio.sleep(2)

                                            damage_calculation_response = player1_card.damage_cal(int(button_ctx.custom_id), _battle, player2_card)

                                        elif button_ctx.custom_id == "5":
                                            # Resolve Check and Calculation
                                            if not player1_card.used_resolve and player1_card.used_focus:
                                                if _battle._is_tutorial and _battle.tutorial_resolve == False:
                                                    _battle.tutorial_resolve = True
                                                    embedVar = discord.Embed(title=f"⚡**Resolve Transformation**!",
                                                                            description=f"**Heal**, Boost **ATK**, and 🧬**Summon**!",
                                                                            colour=0xe91e63)
                                                    embedVar.add_field(name=f"Trade Offs!",
                                                                    value="Sacrifice **DEF** and **Focusing** will not increase **ATK** or **DEF**")
                                                    embedVar.add_field(name=f"🧬Your Summon",
                                                                    value=f"**{player1_card._summon_name}**")
                                                    embedVar.set_footer(
                                                        text=f"You can only enter ⚡Resolve once per match! Use the Heal Wisely!!!")
                                                    await button_ctx.send(embed=embedVar)
                                                    await asyncio.sleep(2)

                                                player1_card.resolving(_battle, player2_card, player1)
                                                if _battle._is_boss:
                                                    await button_ctx.send(embed=_battle._boss_embed_message)
                                            else:
                                                emessage = m.CANNOT_USE_RESOLVE
                                                embedVar = discord.Embed(title=emessage, colour=0xe91e63)
                                                previous_moves.append(f"(**{_battle._turn_total}**) **{player1_card.name}** cannot resolve")
                                                await button_ctx.defer(ignore=True)
                                                _battle._is_turn = _battle._repeat_turn()
                                        
                                        elif button_ctx.custom_id == "6":
                                            # Resolve Check and Calculation
                                            if player1_card.used_resolve and player1_card.used_focus and not player1_card.used_summon:
                                                if _battle._is_tutorial and _battle.tutorial_summon == False:
                                                    _battle.tutorial_summon = True
                                                    embedVar = discord.Embed(title=f"{player1_card.name} Summoned 🧬 **{player1_card._summon_name}**",colour=0xe91e63)
                                                    embedVar.add_field(name=f"🧬**Summon Enhancers**!",
                                                                    value="You can use 🧬**Summons** once per Focus without losing a turn!")
                                                    embedVar.add_field(name=f"Resting",
                                                                    value="🧬**Summons** need to rest after using their ability! **Focus** to Replenish your 🧬**Summon**")
                                                    embedVar.set_footer(
                                                        text=f"🧬Summons will Level Up and build Bond as you win battles! Train up your 🧬summons to perform better in the field!")
                                                    await button_ctx.send(embed=embedVar)
                                                    await asyncio.sleep(2)
                                            summon_response = player1_card.use_summon(_battle, player2_card)
                                            
                                            if not player1.performance and summon_response['CAN_USE_MOVE']:
                                                await battle_msg.delete(delay=2)
                                                tsummon_file = showsummon(player2_card.summon_image, player2_card.summon_name, summon_response['MESSAGE'], player2_card.summon_lvl, player2_card.summon_bond)
                                                embedVar.set_image(url="attachment://pet.png")
                                                await asyncio.sleep(2)
                                                battle_msg = await private_channel.send(embed=embedVar, file=tsummon_file)
                                                await asyncio.sleep(2)
                                                await battle_msg.delete(delay=2)

                                        elif _battle._is_co_op:
                                            if button_ctx.custom_id == "7":
                                                player1_card.use_companion_enhancer(_battle, player2_card, player3_card)
                                            
                                            elif button_ctx.custom_id == "8":
                                                # Use companion enhancer on you
                                                player3_card.use_companion_enhancer(_battle, player2_card, player1_card)

                                            elif button_ctx.custom_id == "9":
                                                player3_card.use_block(_battle, player2_card, player1_card)

                                        if button_ctx.custom_id == "0":
                                            if _battle._is_tutorial and _battle.tutorial_block==False:
                                                _battle.tutorial_block=True
                                                embedVar = discord.Embed(title=f"🛡️Blocking!",
                                                                        description=f"🛡️**Blocking** cost **20 ST(Stamina)** to Double your **DEF** until your next turn!",
                                                                        colour=0xe91e63)
                                                embedVar.add_field(name=f"**Engagements**",
                                                                value="You will take less DMG when your **DEF** is greater than your opponenents **ATK**")
                                                embedVar.add_field(name=f"**Engagement Insight**",
                                                                value="💢: %33-%50 of AP\n❕: %50-%75 AP\n‼️: %75-%120 AP\n〽️x1.5: %120-%150 AP\n❌x2: $150-%200 AP")
                                                embedVar.set_footer(
                                                    text=f"Use 🛡️Block strategically to defend against your opponents strongest abilities!")
                                                await button_ctx.send(embed=embedVar)
                                                await asyncio.sleep(2)
                                            
                                            player1_card.use_block(_battle, player2_card)                                            

                                        if button_ctx.custom_id in _battle.main_battle_options:
                                            player1_card.damage_done(_battle, damage_calculation_response, player2_card)
                                    
                                    except asyncio.TimeoutError:
                                        await battle_msg.delete()
                                        if not _battle._is_abyss and not _battle._is_scenario and not _battle._is_explore and not _battle._is_pvp_match and not _battle._is_tutorial:
                                            await save_spot(self, ctx, _battle._selected_universe, _battle.mode, _battle._currentopponent)
                                        
                                        await ctx.send(f"{ctx.author.mention} {_battle.error_end_match_message()}")
                                    except Exception as ex:
                                        trace = []
                                        tb = ex.__traceback__
                                        while tb is not None:
                                            trace.append({
                                                "filename": tb.tb_frame.f_code.co_filename,
                                                "name": tb.tb_frame.f_code.co_name,
                                                "lineno": tb.tb_lineno
                                            })
                                            tb = tb.tb_next
                                        print(str({
                                            'type': type(ex).__name__,
                                            'message': str(ex),
                                            'trace': trace
                                        }))
                                        guild = self.bot.get_guild(main.guild_id)
                                        channel = guild.get_channel(main.guild_channel)
                                        await channel.send(f"'PLAYER': **{str(ctx.author)}**, 'GUILD': **{str(ctx.author.guild)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")

                        if _battle._is_turn == 1:
                            player2_card.reset_stats_to_limiter(player1_card)

                            player2_card.yuyu_hakusho_attack_increase()

                            player2_card.activate_chainsawman_trait(_battle)

                            _battle.add_battle_history_messsage(player2_card.set_bleed_hit(_battle._turn_total, player1_card))

                            _battle.add_battle_history_messsage(player2_card.set_burn_hit(player1_card))

                            if player1_card.freeze_enh:
                                new_turn = player2_card.frozen(_battle, player1_card)
                                _battle._is_turn = new_turn['MESSAGE']
                                _battle.add_battle_history_messsage(new_turn['TURN'])
                                continue
                            player2_card.freeze_enh = False

                            _battle.add_battle_history_messsage(player1_card.set_poison_hit(player1_card))
                                
                            player2_card.set_gravity_hit()


                            player2_title.activate_title_passive(_battle, player2_card, player1_card)
                            
                            player2_card.activate_card_passive(player1_card)

                            player2_card.activate_demon_slayer_trait(_battle, player1_card)

                            player1_card.activate_demon_slayer_trait(_battle, player2_card)

                            if player2_card.used_block == True:
                                player2_card.defense = int(player2_card.defense / 2)
                                player2_card.used_block = False
                            if player2_card.used_defend == True:
                                player2_card.defense = int(player2_card.defense / 2)
                                player2_card.used_defend = False

                            player1_card.set_deathnote_message(_battle)
                            player2_card.set_deathnote_message(_battle)
                            if _battle._is_co_op:
                                player3_card.set_deathnote_message(_battle)                            
                            

                            # Focus
                            if player2_card.stamina < 10:
                                player2_card.focusing(player2_title, player1_title, player1_card, _battle)

                                if _battle._is_boss:
                                    embedVar = discord.Embed(title=f"**{player2_card.name}** Enters Focus State",
                                                            description=f"{_battle._powerup_boss_description}", colour=0xe91e63)
                                    embedVar.add_field(name=f"A great aura starts to envelop **{player2_card.name}** ",
                                                    value=f"{_battle._aura_boss_description}")
                                    embedVar.set_footer(text=f"{player2_card.name} Says: 'Now, are you ready for a real fight?'")
                                    await ctx.send(embed=embedVar)
                                    previous_moves.append(f"(**{_battle._turn_total}**) 🌀 **{player2_card.name}** focused")
                                    # await asyncio.sleep(2)
                                    if player2_card.universe == "Digimon" and player2_card.used_resolve is False:
                                        embedVar = discord.Embed(title=f"(**{_battle._turn_total}**) :zap: **{player2_card.name}** Resolved!", description=f"{_battle._rmessage_boss_description}",
                                                                colour=0xe91e63)
                                        embedVar.set_footer(text=f"{player1_card.name} this will not be easy...")
                                        await ctx.send(embed=embedVar)
                                        await asyncio.sleep(2)

                            else:
                                player2_card.set_battle_arm_messages(player1_card)

                                player2_card.activate_solo_leveling_trait(_battle, player1_card)
                                                                
                                embedVar = discord.Embed(title=f"➡️ **Opponent Turn** {_battle._turn_total}", description=textwrap.dedent(f"""\
                                {_battle.get_previous_moves_embed()}
                                
                                """), color=0xe74c3c)
                                embedVar.set_footer(
                                    text=f"_battle.get_battle_window_title_text(player2_card, player1_card)",
                                    icon_url="https://cdn.discordapp.com/emojis/789290881654980659.gif?v=1")


                                if _battle._is_pvp_match:
                                    _battle.set_battle_options(player1_card, player2_card)
                                    # Check If Playing Bot
                                    if not _battle.is_ai_opponent:

                                        battle_action_row = manage_components.create_actionrow(*_battle.battle_buttons)
                                        util_action_row = manage_components.create_actionrow(*_battle.utility_buttons)

                                        player2_card.set_battle_arm_messages(player2_card)

                                        components = [battle_action_row, util_action_row]
                                        embedVar = discord.Embed(title=f"", description=textwrap.dedent(f"""\
                                        {_battle.get_previous_moves_embed()}

                                        """), color=0xe74c3c)
                                        embedVar.set_author(name=f"{player2_card._arm_message}\n{player2_card.summon_resolve_message}\n")
                                        embedVar.add_field(name=f"➡️ **Current Turn** {_battle._turn_total}", value=f"{user2.mention} Select move below!")
                                        embedVar.set_image(url="attachment://image.png")
                                        embedVar.set_footer(
                                            text=f"{_battle.get_battle_footer_text(player1_card, player2_card)}",
                                            icon_url="https://cdn.discordapp.com/emojis/789290881654980659.gif?v=1")
                                        await battle_msg.delete(delay=1)
                                        await asyncio.sleep(1)
                                        battle_msg = await private_channel.send(embed=embedVar, components=components, file=player2_card.showcard(_battle.mode, player2_arm, player2_title, _battle._turn_total, player1_card.defense))

                                        # Make sure user is responding with move
                                        def check(button_ctx):
                                            return button_ctx.author == user2 and button_ctx.custom_id in options

                                        try:
                                            button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot,
                                                                                                                    components=[
                                                                                                                        battle_action_row,
                                                                                                                        util_action_row],
                                                                                                                    timeout=120,
                                                                                                                    check=check)

                                            if button_ctx.custom_id == "q" or button_ctx.custom_id == "Q":
                                                player2_card.health = 0
                                                _battle.game_over = True
                                                await battle_msg.delete(delay=1)
                                                await asyncio.sleep(1)
                                                battle_msg = await private_channel.send(content=f"{user2.mention} has fled.")

                                                #return
                                            if button_ctx.custom_id == "1":
                                                damage_calculation_response = player2_card.damage_cal(int(button_ctx.custom_id), _battle, player1_card)
                                            
                                            elif button_ctx.custom_id == "2":
                                                damage_calculation_response = player2_card.damage_cal(int(button_ctx.custom_id), _battle, player1_card)
                                            
                                            elif button_ctx.custom_id == "3":

                                                damage_calculation_response = player2_card.damage_cal(int(button_ctx.custom_id), _battle, player1_card)
                                                if player2_card.gif != "N/A" and not player1.performance:
                                                    # await button_ctx.defer(ignore=True)
                                                    await battle_msg.delete(delay=None)
                                                    # await asyncio.sleep(1)
                                                    battle_msg = await private_channel.send(f"{player2_card.gif}")
                                                    
                                                    await asyncio.sleep(2)
                                            elif button_ctx.custom_id == "4":
                                                damage_calculation_response = player2_card.damage_cal(int(button_ctx.custom_id), _battle, player1_card)
                                            
                                            elif button_ctx.custom_id == "5":
                                                player2_card.resolving(_battle, player1_card, player2)
                                            
                                            elif button_ctx.custom_id == "6" and not _battle._is_raid:
                                                player2_card.use_summon(_battle, player1_card)
                                            
                                            elif button_ctx.custom_id == "0":
                                                player2_card.use_block(_battle, player1_card)                                            

                                            if button_ctx.custom_id in _battle.main_battle_options:
                                                player2_card.damage_done(_battle, damage_calculation_response, player1_card)
                                        
                                        except Exception as ex:
                                            trace = []
                                            tb = ex.__traceback__
                                            while tb is not None:
                                                trace.append({
                                                    "filename": tb.tb_frame.f_code.co_filename,
                                                    "name": tb.tb_frame.f_code.co_name,
                                                    "lineno": tb.tb_lineno
                                                })
                                                tb = tb.tb_next
                                            print(str({
                                                'type': type(ex).__name__,
                                                'message': str(ex),
                                                'trace': trace
                                            }))
                                            guild = self.bot.get_guild(main.guild_id)
                                            channel = guild.get_channel(main.guild_channel)
                                            await channel.send(f"'PLAYER': **{str(ctx.author)}**, 'GUILD': **{str(ctx.author.guild)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")

                                    # Play Bot
                                    else:
                                        player2_card.set_battle_arm_messages(player1_card)

                                        player2_card.activate_solo_leveling_trait(_battle, player1_card)

                                        _battle.set_battle_options(player2_card, player1_card)

                                        tembedVar = discord.Embed(title=f"_Turn_ {_battle._turn_total}", description=textwrap.dedent(f"""\
                                        {_battle.get_previous_moves_embed()}
                                        """), color=0xe74c3c)
                                        tembedVar.set_image(url="attachment://image.png")
                                        await battle_msg.delete(delay=2)
                                        await asyncio.sleep(2)
                                        battle_msg = await private_channel.send(embed=tembedVar, file=player2_card.showcard(_battle.mode, player2_arm, player2_title, _battle._turn_total, player1_card.defense))
                                        await asyncio.sleep(3)
                                        
                                        selected_move = _battle.ai_battle_command(player2_card, player1_card)

                                        damage_calculation_response = player2_card.damage_cal(selected_move, _battle, player1_card)

                                        if selected_move == 5:
                                            player2_card.resolving(_battle, player1_card, player2)
                                            if _battle._is_boss:
                                                await button_ctx.send(embed=_battle._boss_embed_message)

                                        elif selected_move == 6:
                                            # Resolve Check and Calculation
                                            player2_card.use_summon(_battle, player1_card)
                                        
                                        if selected_move == 7:
                                            player2_card.use_block(_battle, damage_calculation_response, player1_card)

                                        if selected_move != 5 and selected_move != 6 and selected_move != 0:
                                            player2_card.damage_done(_battle, damage_calculation_response, player1_card)                                        

                                if not _battle._is_pvp_match:
                                    if _battle._is_auto_battle:
                                        await asyncio.sleep(2)
                                        embedVar.set_thumbnail(url=ctx.author.avatar_url)
                                        await battle_msg.edit(embed=embedVar, components=[])
                                    
                                    if not _battle._is_auto_battle:
                                        player2_card.set_battle_arm_messages(player1_card)

                                        player2_card.activate_solo_leveling_trait(_battle, player1_card)
                                        tembedVar = discord.Embed(title=f"_Turn_ {_battle._turn_total}", description=textwrap.dedent(f"""\
                                        {_battle.get_previous_moves_embed()}
                                        """), color=0xe74c3c)
                                        tembedVar.set_image(url="attachment://image.png")
                                        await battle_msg.delete(delay=None)
                                        # await asyncio.sleep(2)
                                        battle_msg = await private_channel.send(embed=tembedVar, file=player2_card.showcard(_battle.mode, player2_arm, player2_title, _battle._turn_total, player1_card.defense))


                                    selected_move = _battle.ai_battle_command(player2_card, player1_card)
                                    
                                    damage_calculation_response = player1_card.damage_cal(selected_move, _battle, player1_card)
                                    
                                    if int(selected_move) == 3:                                    

                                        if _battle._is_ai_battle:
                                            if player2_card.gif != "N/A"  and not player1.performance:
                                                await battle_msg.delete(delay=2)
                                                await asyncio.sleep(2)
                                                battle_msg = await private_channel.send(f"{player2_card.gif}")
                                                await asyncio.sleep(2)

                                    elif int(selected_move) == 5:
                                        player2_card.resolving(_battle, player1_card, player2)
                                        if _battle._is_boss:
                                            await button_ctx.send(embed=_battle._boss_embed_message)

                                    elif int(selected_move) == 6:
                                        # Resolve Check and Calculation
                                        if player2_card.used_resolve and player2_card.used_focus and not player2_card.used_summon:
                                            if _battle._is_co_op:
                                                if player3_card.used_defend == True:
                                                    summon_response = player2_card.use_summon(_battle, player3_card)
                                                    if not player1.performance and summon_response['CAN_USE_MOVE']:
                                                        await battle_msg.delete(delay=2)
                                                        tsummon_file = showsummon(player2_card.summon_image, player2_card.summon_name, summon_response['MESSAGE'], player2_card.summon_lvl, player2_card.summon_bond)
                                                        embedVar.set_image(url="attachment://pet.png")
                                                        await asyncio.sleep(2)
                                                        battle_msg = await private_channel.send(embed=embedVar, file=tsummon_file)
                                                        await asyncio.sleep(2)
                                                        await battle_msg.delete(delay=2)

                                                else:
                                                    summon_response = player2_card.use_summon(_battle, player1_card)
                                                    if not player1.performance and summon_response['CAN_USE_MOVE']:
                                                        await battle_msg.delete(delay=2)
                                                        tsummon_file = showsummon(player2_card.summon_image, player2_card.summon_name, summon_response['MESSAGE'], player2_card.summon_lvl, player2_card.summon_bond)
                                                        embedVar.set_image(url="attachment://pet.png")
                                                        await asyncio.sleep(2)
                                                        battle_msg = await private_channel.send(embed=embedVar, file=tsummon_file)
                                                        await asyncio.sleep(2)
                                                        await battle_msg.delete(delay=2)

                                            else:
                                                summon_response = player2_card.use_summon(_battle, player1_card)
                                                if not player1.performance and summon_response['CAN_USE_MOVE']:
                                                    await battle_msg.delete(delay=2)
                                                    tsummon_file = showsummon(player2_card.summon_image, player2_card.summon_name, summon_response['MESSAGE'], player2_card.summon_lvl, player2_card.summon_bond)
                                                    embedVar.set_image(url="attachment://pet.png")
                                                    await asyncio.sleep(2)
                                                    battle_msg = await private_channel.send(embed=embedVar, file=tsummon_file)
                                                    await asyncio.sleep(2)
                                                    await battle_msg.delete(delay=2)

                                        else:
                                            _battle.add_battle_history_messsage(f"(**{_battle._turn_total}**) {player2_card.name} Could not summon 🧬 **{player2_card.name}**. Needs rest")
                                    elif int(selected_move) == 0:
                                        player2_card.use_block(_battle, player1_card)                                            
                                    if int(selected_move) != 5 and int(selected_move) != 6 and int(selected_move) != 7:

                                        # If you have enough stamina for move, use it
                                        # if c used block
                                        if _battle._is_co_op:
                                            if player3_card.used_defend == True:
                                                player2_card.damage_done(_battle, damage_calculation_response, player3_card)
                                            else:
                                                player2_card.damage_done(_battle, damage_calculation_response, player1_card)
                                        else:
                                            player2_card.damage_done(_battle, damage_calculation_response, player1_card)


                        elif _battle._is_co_op and turn != (0 or 1):
                            if c_ap_buff > 500:
                                c_ap_buff = 500

                            # Companion Turn Start
                            if turn == 2:
                                if c_universe == "YuYu Hakusho":
                                    c_attack = c_attack + c_stamina

                                if t_bleed_hit:
                                    t_bleed_hit = False
                                    bleed_dmg = 10 * turn_total
                                    c_health = c_health - bleed_dmg
                                    previous_moves.append(f"🩸 **{c_card}** shredded for **{round(bleed_dmg)}** bleed dmg...")
                                    if c_health <= 0:
                                        continue

                                if t_burn_dmg > 3:
                                    c_health = c_health - t_burn_dmg
                                    previous_moves.append(f"🔥 **{c_card}** burned for **{round(t_burn_dmg)}** dmg...")
                                    if c_health <= 0:
                                        continue

                                if t_freeze_enh:
                                    previous_moves.append(f"❄️ **{c_card}** has been frozen for a turn...")
                                    turn_total = turn_total + 1
                                    turn = 3
                                    continue
                                if t_poison_dmg:
                                    c_health = c_health - t_poison_dmg
                                    previous_moves.append(f"🧪 **{c_card}** poisoned for **{t_poison_dmg}** dmg...")
                                    if c_health <= 0:
                                        continue


                                if c_gravity_hit:
                                    c_gravity_hit = False
                                
                                t_burn_dmg = round(t_burn_dmg / 2)
                                c_freeze_enh = False
                                o_freeze_enh = False

                                if c_title_passive_type:
                                    if c_title_passive_type == "HLT":
                                        if c_max_health > c_health:
                                            c_health = round(c_health + ((c_title_passive_value / 100) * c_health))
                                    if c_title_passive_type == "LIFE":
                                        if c_max_health > c_health:
                                            t_health = round(t_health - ((c_title_passive_value / 100) * t_health))
                                            c_health = round(c_health + ((c_title_passive_value / 100) * t_health))
                                    if c_title_passive_type == "ATK":
                                        c_attack = c_attack + c_title_passive_value
                                    if c_title_passive_type == "DEF":
                                        c_defense = c_defense + c_title_passive_value
                                    if c_title_passive_type == "STAM":
                                        if c_stamina > 15:
                                            c_stamina = c_stamina + c_title_passive_value
                                    if c_title_passive_type == "DRAIN":
                                        if c_stamina > 15:
                                            t_stamina = t_stamina - c_title_passive_value
                                            c_stamina = c_stamina + c_title_passive_value
                                    if c_title_passive_type == "FLOG":
                                        t_attack = round(t_attack - ((c_title_passive_value / 100) * t_attack))
                                        c_attack = round(c_attack + ((c_title_passive_value / 100) * t_attack))
                                    if c_title_passive_type == "WITHER":
                                        t_defense = round(t_defense - ((c_title_passive_value / 100) * t_defense))
                                        c_defense = round(c_defense + ((c_title_passive_value / 100) * t_defense))
                                    if c_title_passive_type == "RAGE":
                                        c_defense = round(c_defense - ((c_title_passive_value / 100) * c_defense))
                                        c_ap_buff = round(c_ap_buff + ((c_title_passive_value / 100) * c_defense))
                                    if c_title_passive_type == "BRACE":
                                        c_ap_buff = round(c_ap_buff + ((c_title_passive_value / 100) * c_attack))
                                        c_attack = round(c_attack - ((c_title_passive_value / 100) * c_attack))
                                    if c_title_passive_type == "BZRK":
                                        c_health = round(c_health - ((c_title_passive_value / 100) * c_health))
                                        c_attack = round(c_attack + ((c_title_passive_value / 100) * c_health))
                                    if c_title_passive_type == "CRYSTAL":
                                        c_health = c_health - c_title_passive_value
                                        c_defense = c_defense + c_title_passive_value
                                    if c_title_passive_type == "FEAR":
                                        if c_universe != "Chainsawman":
                                            c_max_health = c_max_health - (c_max_health * .03)
                                        t_defense = t_defense - c_title_passive_value
                                        t_attack = t_attack - c_title_passive_value
                                        t_ap_buff = t_ap_buff - c_title_passive_value
                                    if c_title_passive_type == "GROWTH":
                                        c_max_health = c_max_health - (c_max_health * .03)
                                        c_defense = c_defense + c_title_passive_value
                                        c_attack = c_attack + c_title_passive_value
                                        c_ap_buff = c_ap_buff + c_title_passive_value
                                    if c_title_passive_type == "SLOW":
                                        if turn_total != 0:
                                            turn_total = turn_total - 1
                                    if c_title_passive_type == "HASTE":
                                        turn_total = turn_total + 1
                                    if c_title_passive_type == "STANCE":
                                        tempattack = c_attack + c_title_passive_value
                                        c_attack = c_defense
                                        c_defense = tempattack
                                    if c_title_passive_type == "CONFUSE":
                                        tempattack = c_attack - c_title_passive_value
                                        t_attack = c_defense
                                        t_defense = tempattack
                                    if c_title_passive_type == "BLINK":
                                        c_stamina = c_stamina + c_title_passive_value
                                        if t_stamina >=10:
                                            t_stamina = t_stamina - c_title_passive_value
                                    if c_title_passive_type == "CREATION":
                                        c_max_health = round(round(c_max_health + ((c_title_passive_value / 100) * c_max_health)))
                                    if c_title_passive_type == "DESTRUCTION":
                                        t_max_health = round(t_max_health - ((c_title_passive_value / 100) * t_max_health))
                                    if c_title_passive_type == "BLAST":
                                        t_health = round(t_health - c_title_passive_value)
                                    if c_title_passive_type == "WAVE":
                                        if turn_total % 10 == 0:
                                            t_health = round(t_health - 100)


                                if c_card_passive_type:
                                    c_value_for_passive = c_card_tier * .5
                                    c_flat_for_passive = 10 * (c_card_tier * .5)
                                    c_stam_for_passive = 5 * (c_card_tier * .5)
                                    if c_card_passive_type == "HLT":
                                        if c_max_health > c_health:
                                            c_health = round(round(c_health + ((c_value_for_passive / 100) * c_health)))
                                    if c_card_passive_type == "CREATION":
                                        c_max_health = round(round(c_max_health + ((c_value_for_passive / 100) * c_max_health)))
                                    if c_card_passive_type == "DESTRUCTION":
                                        t_max_health = round(round(t_max_health - ((c_value_for_passive / 100) * t_max_health)))
                                    if c_card_passive_type == "LIFE":
                                        if c_max_health > c_health:
                                            t_health = round(t_health - ((c_value_for_passive / 100) * t_health))
                                            c_health = round(c_health + ((c_value_for_passive / 100) * t_health))
                                    if c_card_passive_type == "ATK":
                                        c_attack = round(c_attack + ((c_value_for_passive / 100) * c_attack))
                                    if c_card_passive_type == "DEF":
                                        c_defense = round(c_defense + ((c_value_for_passive / 100) * c_defense))
                                    if c_card_passive_type == "STAM":
                                        if c_stamina > 15:
                                            c_stamina = c_stamina + c_stam_for_passive
                                    if c_card_passive_type == "DRAIN":
                                        if c_stamina > 15:
                                            t_stamina = t_stamina - c_stam_for_passive
                                            c_stamina = c_stamina + c_stam_for_passive
                                    if c_card_passive_type == "FLOG":
                                        t_attack = round(t_attack - ((c_value_for_passive / 100) * t_attack))
                                        c_attack = round(c_attack + ((c_value_for_passive / 100) * t_attack))
                                    if c_card_passive_type == "WITHER":
                                        t_defense = round(t_defense - ((c_value_for_passive / 100) * t_defense))
                                        c_defense = round(c_defense + ((c_value_for_passive / 100) * t_defense))
                                    if c_card_passive_type == "RAGE":
                                        c_defense = round(c_defense - ((c_value_for_passive / 100) * c_defense))
                                        t_ap_buff = round(t_ap_buff + ((c_value_for_passive / 100) * c_defense))
                                    if c_card_passive_type == "BRACE":
                                        t_ap_buff = round(t_ap_buff + ((c_value_for_passive / 100) * c_attack))
                                        c_attack = round(c_attack - ((c_value_for_passive / 100) * c_attack))
                                    if c_card_passive_type == "BZRK":
                                        c_health = round(c_health - ((c_value_for_passive / 100) * c_health))
                                        c_attack = round(c_attack + ((c_value_for_passive / 100) * c_health))
                                    if c_card_passive_type == "CRYSTAL":
                                        c_health = round(c_health - ((c_value_for_passive / 100) * c_health))
                                        c_defense = round(c_defense + ((c_value_for_passive / 100) * c_health))
                                    if c_card_passive_type == "FEAR":
                                        if c_universe != "Chainsawman":
                                            c_max_health = c_max_health - (c_max_health * .05)
                                        t_defense = t_defense - c_flat_for_passive
                                        t_attack = t_attack - c_flat_for_passive
                                        t_ap_buff = t_ap_buff - c_flat_for_passive
                                    if c_card_passive_type == "GROWTH":
                                        c_max_health = c_max_health - (c_max_health * .05)
                                        c_defense = c_defense + c_flat_for_passive
                                        c_attack = c_attack + c_flat_for_passive
                                        c_ap_buff = c_ap_buff + c_flat_for_passive
                                    if c_card_passive_type == "SLOW":
                                        if turn_total != 0:
                                            turn_total = turn_total - 1
                                    if c_card_passive_type == "HASTE":
                                        turn_total = turn_total + 1
                                    if c_card_passive_type == "STANCE":
                                        tempattack = c_attack + c_flat_for_passive
                                        c_attack = c_defense
                                        c_defense = tempattack
                                    if c_card_passive_type == "CONFUSE":
                                        tempattack = t_attack - c_flat_for_passive
                                        t_attack = t_defense
                                        t_defense = tempattack
                                    if c_card_passive_type == "BLINK":
                                        c_stamina = c_stamina - c_stam_for_passive
                                        if t_stamina >= 10:
                                            t_stamina = t_stamina + c_stam_for_passive
                                    if c_card_passive_type == "BLAST":
                                        t_health = round(t_health - c_value_for_passive)
                                    if c_card_passive_type == "WAVE":
                                        if turn_total % 10 == 0:
                                            t_health = round(t_health - 100)



                                # await asyncio.sleep(2)
                                if player3_card.used_defend == True:
                                    c_defense = int(c_defense / 2)
                                    player3_card.used_defend = False
                                if c_attack <= 25:
                                    c_attack = 25
                                if c_defense <= 30:
                                    c_defense = 30
                                if c_attack > 9999:
                                    c_attack = 9999
                                if c_defense > 9999:
                                    c_defense = 9999
                                if c_health >= c_max_health:
                                    c_health = c_max_health
                                # Tutorial Instructions
                                if _battle._turn_total == 0 and botActive:
                                    embedVar = discord.Embed(title=f"MATCH START",
                                                            description=f"`{c_card} Says:`\n{c_greeting_description}",
                                                            colour=0xe91e63)
                                    await private_channel.send(embed=embedVar)

                                if c_health <= (c_max_health * .25):
                                    embed_color_c = 0xe74c3c
                                    if c_chainsaw == True:
                                        if c_atk_chainsaw == False:
                                            c_atk_chainsaw = True
                                            c_chainsaw = False
                                            c_defense = c_defense * 2
                                            c_attack = c_attack * 2
                                            c_max_health = c_max_health * 2
                                            embedVar = discord.Embed(title=f"{c_card}'s Devilization",
                                                                    description=f"**{c_card}** Doubles ATK, DEF, and MAX HEALTH",
                                                                    colour=0xe91e63)
                                            await private_channel.send(embed=embedVar)

                                elif c_health <= (c_max_health * .50):
                                    embed_color_c = 0xe67e22
                                    if c_chainsaw == True:
                                        if c_atk_chainsaw == False:
                                            c_atk_chainsaw = True
                                            c_chainsaw = False
                                            c_defense = c_defense * 2
                                            c_attack = c_attack * 2
                                            c_max_health = c_max_health * 2
                                            embedVar = discord.Embed(title=f"{c_card}'s Devilization",
                                                                    description=f"**{c_card}** Doubles ATK, DEF, and MAX HEALTH",
                                                                    colour=0xe91e63)
                                            await private_channel.send(embed=embedVar)
                                elif c_health <= (c_max_health * .75):
                                    embed_color_c = 0xf1c40f

                                else:
                                    embed_color_c = 0x2ecc71

                                if c_stamina < 10:
                                    c_pet_used = False
                                    c_focus_count = c_focus_count + 1
                                    # fortitude or luck is based on health
                                    fortitude = round(c_health * .1)
                                    if fortitude <= 50:
                                        fortitude = 50

                                    c_stamina = c_focus
                                    c_healthcalc = round(fortitude)
                                    c_attackcalc = round(fortitude * (c_card_tier / 10))
                                    c_defensecalc = round(fortitude * (c_card_tier / 10))
                                    # check if user is at max health and sets messages and focus health value
                                    c_newhealth = 0
                                    healmessage = ""
                                    messagenumber = 0

                                    if c_universe == "One Piece" and (c_card_tier in low_tier_cards or c_card_tier in mid_tier_cards or c_card_tier in high_tier_cards):
                                        c_attackcalc = c_attackcalc + c_attackcalc
                                        c_defensecalc = c_defensecalc + c_defensecalc


                                    if c_title_passive_type:
                                        if c_title_passive_type == "GAMBLE":
                                            c_healthcalc = c_title_passive_value
                                        if c_title_passive_type == "SOULCHAIN":
                                            c_stamina = c_title_passive_value
                                            t_stamina = c_title_passive_value
                                            player1_card.stamina = c_title_passive_value
                                        if c_title_passive_type == "BLAST":
                                            t_health = t_health - (c_title_passive_value * turn_total)

                                    if o_title_passive_type:
                                        if o_title_passive_type == "GAMBLE":
                                            c_healthcalc = o_title_passive_value
                                    
                                    if t_title_passive_type:
                                        if t_title_passive_type == "GAMBLE":
                                            c_healthcalc = t_title_passive_value


                                    if c_universe == "Crown Rift Madness":
                                        healmessage = "yet inner **Madness** drags on..."
                                        messagenumber = 3
                                    else:
                                        if c_health <= c_max_health:
                                            c_newhealth = c_health + c_healthcalc
                                            if c_newhealth > c_max_health:
                                                healmessage = "the injuries dissapeared!"
                                                messagenumber = 1
                                                c_health = c_max_health
                                            else:
                                                healmessage = "regained some vitality."
                                                messagenumber = 2
                                                c_health = c_newhealth
                                        else:
                                            healmessage = f"**{t_card}**'s blows don't appear to have any effect!"
                                            messagenumber = 0
                                    if not c_used_resolve:
                                        c_attack = c_attack + c_attackcalc
                                        c_defense = c_defense + c_defensecalc
                                    c_used_focus = True

                                    embedVar = discord.Embed(title=f"{c_card} FOCUSED",
                                                            description=f"**{c_card} says**\n{c_focus_description}",
                                                            colour=0xe91e63)
                                    embedVar.add_field(name=f"{c_card} focused and {healmessage}",
                                                    value="All stats & stamina increased")
                                    #await private_channel.send(embed=embedVar)
                                    previous_moves.append(f"(**{turn_total}**) 🌀 **{c_card}** focused and {healmessage}")
                                    if not c_used_resolve and c_used_focus and c_universe == "Digimon":  # Digimon Universal Trait
                                        embedVar = discord.Embed(title=f"{c_card} STRENGTHENED RESOLVE :zap:",
                                                                description=f"**{c_card} says**\n{c_resolve_description}",
                                                                colour=0xe91e63)
                                        embedVar.add_field(name=f"Transformation: Digivolve", value="On Focus you Resolve.")
                                        #await private_channel.send(embed=embedVar)
                                        # fortitude or luck is based on health
                                        fortitude = 0.0
                                        low = o_health - (o_health * .75)
                                        high = o_health - (o_health * .66)
                                        fortitude = round(random.randint(int(low), int(high)))
                                        # Resolve Scaling
                                        c_resolve_health = round(fortitude + (.5 * c_resolve))
                                        c_resolve_attack = round((.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                        c_resolve_defense = round((.30 * c_defense) * (c_resolve / (.50 * c_defense)))

                                        c_stamina = c_stamina + c_resolve
                                        c_health = c_health + c_resolve_health
                                        c_attack = round(c_attack + c_resolve_attack)
                                        c_defense = round(c_defense - c_resolve_defense)
                                        c_used_resolve = True
                                        c_pet_used = False
                                        
                                        c_attack = round(c_attack * 1.5)
                                        c_defense = round(c_defense * 1.5)
                                        if turn_total <=5:
                                            c_attack = round(c_attack * 2)
                                            c_defense = round(c_defense * 2 )
                                            c_health = c_health + 500
                                            c_max_health = c_max_health + 500
                                            previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Transformation: Mega Digivolution!!!")
                                        else:
                                            previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Transformation: Digivolve")


                                    elif c_universe == "League Of Legends":
                                        embedVar = discord.Embed(title=f"Turret Shot hits {t_card} for **{60 + turn_total}** Damage 💥",
                                                                colour=0xe91e63)
                                        #await private_channel.send(embed=embedVar)
                                        previous_moves.append(f"(**{turn_total}**) 🩸 Turret Shot hits **{t_card}** for **{60 + turn_total}** Damage 💥")
                                        t_health = round(t_health - (60 + turn_total))

                                    elif c_universe == "Dragon Ball Z":
                                        c_health = c_health + t_stamina + turn_total
                                        previous_moves.append(f"(**{turn_total}**) 🩸 Saiyan Spirit... You heal for **{t_stamina + turn_total}** ❤️")


                                    elif c_universe == "Solo Leveling":
                                        embedVar = discord.Embed(
                                            title=f"Ruler's Authority... {t_card} loses **{30 + turn_total}** 🛡️ 🔻",
                                            colour=0xe91e63)
                                        #await private_channel.send(embed=embedVar)
                                        previous_moves.append(f"(**{turn_total}**) 🩸 Ruler's Authority... {t_card} loses **{30 + turn_total}** 🛡️ 🔻")
                                        t_defense = round(t_defense - (30 + turn_total))

                                    elif c_universe == "Black Clover":
                                        embedVar = discord.Embed(title=f"Mana Zone! {c_card} Increased Stamina 🌀",
                                                                colour=0xe91e63)
                                        #await private_channel.send(embed=embedVar)
                                        previous_moves.append(f"(**{turn_total}**) 🩸 Mana Zone! **{c_card}** Increased AP & Stamina 🌀")
                                        c_stamina = 100
                                        ccard_lvl_ap_buff = ccard_lvl_ap_buff + 30
                                    elif c_universe == "Death Note":
                                        if turn_total >= 100:
                                            embedVar = discord.Embed(title=f"{t_card}'s' Scheduled Death 📓",
                                                                    description=f"**{c_card} says**\n**Delete**",
                                                                    colour=0xe91e63)
                                            embedVar.add_field(name=f"{t_card} had a heart attack and died",
                                                            value=f"Death....")
                                            #await private_channel.send(embed=embedVar)
                                            previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 had a heart attack and died")
                                            t_health = 0

                                    if t_universe == "One Punch Man" and c_universe != "Death Note":
                                        embedVar = discord.Embed(
                                            title=f"Hero Reinforcements! **{t_card}**  Increased Health & Max Health ❤️",
                                            colour=0xe91e63)
                                        #await private_channel.send(embed=embedVar)
                                        previous_moves.append(f"(**{turn_total}**) Hero Reinforcements! **{t_card}** Increased Health!  ❤️")
                                        t_health = round(t_health + 100)
                                        t_max_health = round(t_max_health + 100)

                                    elif t_universe == "7ds":
                                        embedVar = discord.Embed(
                                            title=f"Power Of Friendship! 🧬 **{tpet_name}** Rested, **{t_card}** Increased Stamina 🌀", colour=0xe91e63)
                                        #await private_channel.send(embed=embedVar)
                                        previous_moves.append(f"(**{turn_total}**) 🩸 Power Of Friendship! 🧬 **{tpet_name}** Rested, **{t_card}** Increased Stamina 🌀")
                                        t_stamina = t_stamina + 60
                                        t_pet_used = False

                                    elif t_universe == "Souls":
                                        embedVar = discord.Embed(
                                            title=f"Combo Recognition! **{t_card}** Increased Attack by **{60 + turn_total}** 🔺 ",
                                            colour=0xe91e63)
                                        #await private_channel.send(embed=embedVar)
                                        previous_moves.append(f"(**{turn_total}**) 🩸 Combo Recognition! **{o_card}** Increased Attack by **{60 + turn_total}** 🔺")
                                        t_attack = round(t_attack + (60 + turn_total))

                                    else:
                                        turn_total = turn_total + 1
                                        if c_universe != "Crown Rift Madness":
                                            turn = 3
                                        else:
                                            turn = 2
                                    turn_total = turn_total + 1
                                    if c_universe != "Crown Rift Madness":
                                        turn = 3
                                    else:
                                        turn = 2
                                else:
                                    if mode in ai_co_op_modes:
                                        # UNIVERSE CARD
                                        cap1 = list(c_1.values())[0] + ccard_lvl_ap_buff + c_shock_buff + c_basic_water_buff + c_ap_buff
                                        cap2 = list(c_2.values())[0] + ccard_lvl_ap_buff + c_shock_buff + c_special_water_buff + c_ap_buff
                                        cap3 = list(c_3.values())[0] + ccard_lvl_ap_buff + cdemon_slayer_buff + c_shock_buff + c_ultimate_water_buff + c_ap_buff
                                        cenh1 = list(c_enhancer.values())[0]
                                        cenh_name = list(c_enhancer.values())[2]
                                        cpet_enh_name = list(cpet_move.values())[2]
                                        cpet_msg_on_resolve = ""

                                        if cap1 < 150:
                                            cap1 = 150
                                        if cap2 < 150:
                                            cap2 = 150            
                                        if cap3 < 150:
                                            cap3 = 150

                                        if c_universe == "Souls" and c_used_resolve:
                                            companion_card = showcard("battle", c, carm,c_max_health, c_health, c_max_stamina, c_stamina,
                                                                c_used_resolve, ctitle, c_used_focus, c_attack, c_defense,
                                                                turn_total, cap2, cap3, cap3, cenh1, cenh_name, ccard_lvl, t_defense)
                                        else:
                                            companion_card = showcard("battle", c, carm,c_max_health, c_health, c_max_stamina, c_stamina,
                                                                    c_used_resolve, ctitle, c_used_focus, c_attack, c_defense,
                                                                    turn_total, cap1, cap2, cap3, cenh1, cenh_name, ccard_lvl, t_defense)

                                        if c_universe == "Solo Leveling" and not c_swapped:
                                            if temp_tarm_shield_active and not tarm_shield_active:
                                                if carm_shield_active:
                                                    cshield_value = cshield_value + temp_tshield_value
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 **ARISE!** *{tarm_name}* is now yours")
                                                    c_swapped = True
                                                elif not carm_shield_active:
                                                    carm_shield_active = True
                                                    cshield_value = temp_tshield_value
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 **ARISE!** *{tarm_name}* is now yours")
                                                    c_swapped = True
                                            elif temp_tarm_barrier_active and not tarm_barrier_active:
                                                if carm_barrier_active:
                                                    cbarrier_count = cbarrier_count + temp_tbarrier_count
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 **ARISE!** *{tarm_name}* is now yours")
                                                    c_swapped = True
                                                elif not carm_barrier_active:
                                                    carm_barrier_active = True
                                                    cbarrier_count = temp_tbarrier_count
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 **ARISE!** *{tarm_name}* is now yours")
                                                    c_swapped = True
                                            elif temp_tarm_parry_active and not tarm_parry_active:
                                                if carm_parry_active:
                                                    cparry_count = cparry_count + temp_tparry_count
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 **ARISE!** *{tarm_name}* is now yours")
                                                    c_swapped = True
                                                elif not carm_parry_active:
                                                    carm_parry_active = True
                                                    cparry_count = temp_tparry_count
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 **ARISE!** *{tarm_name}* is now yours")
                                                    c_swapped = True

                                        #await private_channel.send(file=companion_card)
                                        tembedVar = discord.Embed(title=f"_Turn_ {turn_total}", description=textwrap.dedent(f"""\
                                        {previous_moves_into_embed}
                                        """), color=0xe74c3c)
                                        tembedVar.set_image(url="attachment://image.png")
                                        await battle_msg.delete(delay=None)
                                        # await asyncio.sleep(2)
                                        battle_msg = await private_channel.send(embed=tembedVar, file=companion_card)
                                        selected_move = 0

                                        if c_used_resolve and not c_pet_used:
                                            selected_move = 6
                                        elif t_enhancer['TYPE'] == "WAVE" and (turn_total % 10 == 0 or turn_total == 0 or turn_total == 1):
                                            if t_stamina >=20:
                                                selected_move =4
                                        elif carm_barrier_active: #Ai Barrier Checks
                                            if c_stamina >=20: #Stamina Check For Enhancer
                                                selected_move = await ai_enhancer_moves(turn_total,c_used_focus,c_used_resolve,c_pet_used,c_stamina,
                                                                        c_enhancer['TYPE'],c_health,c_max_health,c_attack,
                                                                        c_defense,t_stamina,t_attack,t_defense, o_health)
                                            else:
                                                selected_move = 1
                                        elif t_health <=350: #Killing Blow
                                            if c_enhancer['TYPE'] == "BLAST":
                                                if c_stamina >=20:
                                                    selected_move =4
                                                else:
                                                    selected_move =1
                                            elif c_enhancer['TYPE'] == "WAVE" and (turn_total % 10 == 0 or turn_total == 0 or turn_total == 1):
                                                if c_stamina >=20:
                                                    selected_move =4
                                                else:
                                                    selected_move =1
                                            else:
                                                if c_stamina >= 90:
                                                    selected_move = 1
                                                elif c_stamina >= 80:
                                                    selected_move =3
                                                elif c_stamina >=30:
                                                    selected_move=2
                                                else:
                                                    selected_move=1
                                        elif t_stamina < 10:
                                            selected_move = 1
                                        elif c_health <= (.50 * c_max_health) and c_used_resolve == False and c_used_focus:
                                            selected_move = 5
                                        elif c_stamina >= 160 and (c_health >= t_health):
                                            if o_health <= t_health:
                                                if cmove_enhanced_text in Healer_Enhancer_Check:
                                                    selected_move = 8
                                                else:
                                                    selected_move = 3
                                            else:
                                                selected_move = 3
                                        elif c_stamina >= 160:
                                            selected_move = 3
                                        elif c_stamina >= 150 and (c_health >= t_health):
                                            selected_move = 1
                                        elif c_stamina >= 150:
                                            selected_move = 1
                                        elif c_stamina >= 140 and (c_health >= t_health):
                                            selected_move = 1
                                        elif c_stamina >= 140:
                                            selected_move = 3
                                        elif c_stamina >= 130 and (c_health >= t_health):
                                            selected_move = 1
                                        elif c_stamina >= 130:
                                            selected_move = 3
                                        elif c_stamina >= 120 and (c_health >= t_health):
                                            if o_health <= t_health:
                                                if cmove_enhanced_text in Healer_Enhancer_Check:
                                                    selected_move = 8
                                                else:
                                                    selected_move = 2
                                            else:
                                                selected_move = 2
                                        elif c_stamina >= 120:
                                            selected_move = 3
                                        elif c_stamina >= 110 and (c_health >= t_health):
                                            selected_move = 1
                                        elif c_stamina >= 110:
                                            selected_move = 2
                                        elif c_stamina >= 100 and (c_health >= t_health):
                                            if o_health <= t_health:
                                                if cmove_enhanced_text in Healer_Enhancer_Check:
                                                    selected_move = 8
                                                else:
                                                    selected_move = 8
                                            else:
                                                if cmove_enhanced_text in Healer_Enhancer_Check:
                                                    selected_move = 8
                                                else:
                                                    selected_move = 2
                                        elif c_stamina >= 100:
                                            if c_health >= o_health:
                                                selected_move = 8
                                            else:
                                                selected_move = 1
                                        elif c_stamina >= 90 and (c_health >= t_health):
                                            if o_health <= t_health:
                                                if c_health >= o_health:
                                                    selected_move = 7
                                                else:
                                                    if cmove_enhanced_text in Healer_Enhancer_Check:
                                                        selected_move = 8
                                                    else:
                                                        selected_move = 2
                                            else:
                                                if c_health >= o_health:
                                                    selected_move = 7
                                                else:
                                                    selected_move = 1
                                        elif c_stamina >= 90:
                                            if c_health >= o_health:
                                                selected_move = 8
                                            else:
                                                if cmove_enhanced_text in Healer_Enhancer_Check or cmove_enhanced_text in Support_Enhancer_Check:
                                                    selected_move = 8
                                                else:
                                                    selected_move = 2
                                        elif c_stamina >= 80 and (c_health >= t_health):
                                            if o_health <= t_health:
                                                if cmove_enhanced_text in Healer_Enhancer_Check:
                                                    selected_move = 8
                                                else:
                                                    selected_move = 2
                                            else:
                                                selected_move = 1
                                        elif c_stamina >= 80:
                                            if o_health <= t_health:
                                                if cmove_enhanced_text in Healer_Enhancer_Check:
                                                    selected_move = 8
                                                else:
                                                    selected_move = 2
                                            else:
                                                selected_move = 3
                                        elif c_stamina >= 70 and (c_health >= t_health):
                                            if cmove_enhanced_text in Healer_Enhancer_Check:
                                                selected_move = 8
                                            else:
                                                selected_move = 2
                                        elif c_stamina >= 70:
                                            selected_move = 1
                                        elif c_stamina >= 60 and (c_health >= t_health):
                                            if c_used_resolve == False and c_used_focus:
                                                selected_move = 5
                                            elif c_used_focus == False:
                                                selected_move = 2
                                            else:
                                                selected_move = 1
                                        elif c_stamina >= 60:
                                            if c_used_resolve == False and c_used_focus:
                                                selected_move = 5
                                            elif c_used_focus == False:
                                                selected_move = 2
                                            else:
                                                selected_move = 1
                                        elif c_stamina >= 50 and (c_health >= t_health):
                                            if c_stamina >= player1_card.stamina:
                                                if c_health >= o_health:
                                                    selected_move = 8
                                                else:
                                                    if cmove_enhanced_text in Healer_Enhancer_Check or cmove_enhanced_text in Support_Enhancer_Check:
                                                        selected_move = 8
                                                    else:
                                                        selected_move = 2
                                            else:
                                                if c_health >= o_health:
                                                    selected_move = 8
                                                else:
                                                    selected_move = 1
                                        elif c_stamina >= 50:
                                            selected_move = 2
                                        elif c_stamina >= 40 and (c_health >= t_health):
                                            if o_health <= t_health:
                                                if cmove_enhanced_text in Healer_Enhancer_Check or cmove_enhanced_text in Support_Enhancer_Check:
                                                    selected_move = 8
                                                else:
                                                    selected_move = 2
                                            else:
                                                selected_move = 1
                                        elif c_stamina >= 40:
                                            selected_move = 2
                                        elif c_stamina >= 30 and (c_health >= t_health):
                                            if o_health <= t_health:
                                                if cmove_enhanced_text in Healer_Enhancer_Check or cmove_enhanced_text in Support_Enhancer_Check:
                                                    selected_move = 8
                                                else:
                                                    selected_move = 2
                                            else:
                                                selected_move = await ai_enhancer_moves(turn_total,c_used_focus,c_used_resolve,c_pet_used,c_stamina,
                                                                        c_enhancer['TYPE'],c_health,c_max_health,c_attack,
                                                                        c_defense,t_stamina,t_attack,t_defense, t_health)
                                        elif c_stamina >= 30:
                                            selected_move = 2
                                        elif c_stamina >= 20 and (c_health >= t_health):
                                            if c_health >= o_health:
                                                selected_move = 8
                                            else:
                                                selected_move = 1
                                        elif c_stamina >= 20:
                                            if c_health >= o_health:
                                                selected_move = 8
                                            else:
                                                if cmove_enhanced_text in Healer_Enhancer_Check or cmove_enhanced_text in Support_Enhancer_Check:
                                                    selected_move = 8
                                                else:
                                                    selected_move = 1
                                        elif c_stamina >= 10:
                                            selected_move = 1
                                        else:
                                            selected_move = 0

                                        # calculate data based on selected move
                                        if selected_move == 0:
                                            c_health = 0

                                            if private_channel.guild:
                                                await private_channel.send(f"{user2.mention} has fled the battle...")
                                                previous_moves.append(f"(**{turn_total}**) 💨 **{c_card}** Fled...")
                                                # await discord.TextChannel.delete(private_channel, reason=None)
                                            else:

                                                await private_channel.send(f"You fled the battle...")
                                                previous_moves.append(f"(**{turn_total}**) 💨 **{c_card}** Fled...")
                                            return
                                        if selected_move == 1:
                                            if c_universe == "Souls" and c_used_resolve:
                                                dmg = damage_cal(mode,c_card_tier, c_talisman_dict, cap2, t_for_c_opponent_affinities, special_attack_name, cmove2_element, c_universe, c_card, c_2, c_attack, c_defense, t_defense,
                                                            c_stamina, c_enhancer_used, c_health, t_health, t_stamina,
                                                            c_max_health, t_attack, c_special_move_description, turn_total,
                                                            ccard_lvl_ap_buff, c_1)
                                            else:
                                                dmg = damage_cal(mode,c_card_tier, c_talisman_dict, cap1, t_for_c_opponent_affinities, basic_attack_name, cmove1_element, c_universe, c_card, c_1, c_attack, c_defense, t_defense,
                                                                c_stamina, c_enhancer_used, c_health, t_health, t_stamina,
                                                                c_max_health, t_attack, c_special_move_description, turn_total,
                                                                ccard_lvl_ap_buff, None)
                                        elif selected_move == 2:
                                            if c_universe == "Souls" and c_used_resolve:
                                                dmg = damage_cal(mode,c_card_tier, c_talisman_dict, cap3, t_for_c_opponent_affinities, ultimate_attack_name, cmove3_element, c_universe, c_card, c_3, c_attack, c_defense, t_defense,
                                                            c_stamina, c_enhancer_used, c_health, t_health, t_stamina,
                                                            c_max_health, t_attack, c_special_move_description, turn_total,
                                                            ccard_lvl_ap_buff, c_2)
                                            else:
                                                dmg = damage_cal(mode,c_card_tier, c_talisman_dict, cap2, t_for_c_opponent_affinities, special_attack_name, cmove2_element, c_universe, c_card, c_2, c_attack, c_defense, t_defense,
                                                                c_stamina, c_enhancer_used, c_health, t_health, t_stamina,
                                                                c_max_health, t_attack, c_special_move_description, turn_total,
                                                                ccard_lvl_ap_buff, None)
                                        elif selected_move == 3:

                                            dmg = damage_cal(mode,c_card_tier, c_talisman_dict, cap3, t_for_c_opponent_affinities, ultimate_attack_name, cmove3_element, c_universe, c_card, c_3, c_attack, c_defense, t_defense,
                                                            c_stamina, c_enhancer_used, c_health, t_health, t_stamina,
                                                            c_max_health, t_attack, c_special_move_description, turn_total,
                                                            ccard_lvl_ap_buff, None)
                                            if c_gif != "N/A" and not operformance:
                                                await battle_msg.delete(delay=None)
                                                # await asyncio.sleep(1)
                                                battle_msg = await private_channel.send(f"{c_gif}")
                                                await asyncio.sleep(2)
                                        elif selected_move == 4:
                                            c_enhancer_used = True

                                            dmg = damage_cal(mode,c_card_tier, c_talisman_dict, cap1, t_for_c_opponent_affinities, basic_attack_name, cmove1_element, c_universe, c_card, c_enhancer, c_attack, c_defense, t_defense,
                                                            c_stamina, c_enhancer_used, c_health, t_health, t_stamina,
                                                            c_max_health, t_attack, c_special_move_description, turn_total,
                                                            ccard_lvl_ap_buff, None)
                                            c_enhancer_used = False
                                        elif selected_move == 5:
                                            # Resolve Check and Calculation
                                            if not c_used_resolve and c_used_focus:
                                                if c_universe == "My Hero Academia":  # My Hero Trait
                                                    # fortitude or luck is based on health
                                                    fortitude = 0.0
                                                    low = c_health - (c_health * .75)
                                                    high = c_health - (c_health * .66)
                                                    fortitude = round(random.randint(int(low), int(high)))
                                                    # Resolve Scaling
                                                    c_resolve_health = round(fortitude + (.5 * c_resolve))
                                                    c_resolve_attack = round(
                                                        (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                    c_resolve_defense = round(
                                                        (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                    ccard_lvl_ap_buff = ccard_lvl_ap_buff + 200 + turn_total

                                                    c_stamina = 160
                                                    c_health = c_health + c_resolve_health
                                                    c_attack = round(c_attack + c_resolve_attack)
                                                    c_defense = round(c_defense - c_resolve_defense)
                                                    c_used_resolve = True
                                                    c_pet_used = False
                                                    embedVar = discord.Embed(title=f"{c_card} PLUS ULTRAAA",
                                                                            description=f"**{c_card} says**\n{c_resolve_description}",
                                                                            colour=0xe91e63)
                                                    embedVar.add_field(name=f"Transformation: Plus Ultra",
                                                                    value="You do not lose a turn after you Resolve.")
                                                    #await private_channel.send(embed=embedVar)
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: PLUS ULTRA!")

                                                    turn_total = turn_total + 1
                                                    turn = 2

                                                elif c_universe == "One Piece" and (c_card_tier in high_tier_cards):
                                                    # fortitude or luck is based on health
                                                    fortitude = 0.0
                                                    low = c_health - (c_health * .75)
                                                    high = c_health - (c_health * .66)
                                                    fortitude = round(random.randint(int(low), int(high)))
                                                    # Resolve Scaling
                                                    c_resolve_health = round(fortitude + (.5 * c_resolve))
                                                    c_resolve_attack = round(
                                                        (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                    c_resolve_defense = round(
                                                        (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                    
                                                    t_ap_buff = t_ap_buff - 125

                                                    c_stamina = c_stamina + c_resolve
                                                    c_health = c_health + c_resolve_health
                                                    c_attack = round(c_attack + c_resolve_attack)
                                                    c_defense = round(c_defense - c_resolve_defense)
                                                    c_used_resolve = True
                                                    c_pet_used = False

                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Conquerors Haki!")

                                                    turn_total = turn_total + 1
                                                    turn = 2

                                                elif c_universe == "Demon Slayer": 
                                                    # fortitude or luck is based on health
                                                    fortitude = 0.0
                                                    low = c_health - (c_health * .75)
                                                    high = c_health - (c_health * .66)
                                                    fortitude = round(random.randint(int(low), int(high)))
                                                    # Resolve Scaling
                                                    c_resolve_health = round(fortitude + (.5 * c_resolve))
                                                    c_resolve_attack = round(
                                                        (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                    c_resolve_defense = round(
                                                        (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                    

                                                    c_stamina = c_stamina + c_resolve
                                                    c_health = c_health + c_resolve_health
                                                    c_attack = round(c_attack + c_resolve_attack)
                                                    c_defense = round(c_defense - c_resolve_defense)
                                                    if t_attack > c_attack:
                                                        c_attack = t_attack
                                                    if t_defense > c_defense:
                                                        c_defense = t_defense
                                                    c_used_resolve = True
                                                    c_pet_used = False
                                                    embedVar = discord.Embed(title=f"{c_card} begins Total Concentration Breathing",
                                                                            description=f"**{c_card} says**\n{c_resolve_description}",
                                                                            colour=0xe91e63)
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Total Concentration Breathing!")
                                                    
                                                    turn_total = turn_total + 1
                                                    turn = 0

                                                elif c_universe == "Naruto": 
                                                    # fortitude or luck is based on health
                                                    fortitude = 0.0
                                                    low = c_health - (c_health * .75)
                                                    high = c_health - (c_health * .66)
                                                    fortitude = round(random.randint(int(low), int(high)))
                                                    # Resolve Scaling
                                                    c_resolve_health = round(fortitude + (.5 * c_resolve))
                                                    c_resolve_attack = round(
                                                        (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                    c_resolve_defense = round(
                                                        (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                    

                                                    c_stamina = c_stamina + c_resolve
                                                    c_health = c_health + c_resolve_health
                                                    c_health = c_health + c_naruto_heal_buff
                                                    c_attack = round(c_attack + c_resolve_attack)
                                                    c_defense = round(c_defense - c_resolve_defense)

                                                    c_used_resolve = True
                                                    c_pet_used = False
                                                    embedVar = discord.Embed(title=f"{c_card} Heals from Hashirama Cells",
                                                                            description=f"**{c_card} says**\n{c_resolve_description}",
                                                                            colour=0xe91e63)
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Hashirama Cells heal you for **{c_naruto_heal_buff}**!")
                                                    
                                                    turn_total = turn_total + 1
                                                    turn = 0


                                                elif c_universe == "Attack On Titan":
                                                    # fortitude or luck is based on health
                                                    fortitude = 0.0
                                                    low = c_health - (c_health * .75)
                                                    high = c_health - (c_health * .66)
                                                    fortitude = round(random.randint(int(low), int(high)))
                                                    # Resolve Scaling
                                                    c_resolve_health = round(fortitude + (.5 * c_resolve))
                                                    c_resolve_attack = round(
                                                        (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                    c_resolve_defense = round(
                                                        (.30 * c_defense) * (c_resolve / (.50 * c_defense)))

                                                    c_stamina = c_stamina + c_resolve
                                                    c_health = c_health + c_resolve_health
                                                    c_attack = round(c_attack + c_resolve_attack)
                                                    c_defense = round(c_defense - c_resolve_defense)
                                                    c_used_resolve = True
                                                    c_pet_used = False
                                                    health_boost = 100 * c_focus_count
                                                    c_health = c_health + health_boost
                                                    embedVar = discord.Embed(title=f"{c_card} Titan Mode",
                                                                            description=f"**{c_card} says**\n{c_resolve_description}",
                                                                            colour=0xe91e63)
                                                    embedVar.add_field(name=f"Transformation Complete",
                                                                    value=f"Health increased by **{health_boost}**!")
                                                    #await private_channel.send(embed=embedVar)
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Titan Mode! Health increased by **{health_boost}**!")

                                                    turn_total = turn_total + 1
                                                    turn = 3

                                                elif c_universe == "Bleach":  # Bleach Trait
                                                    # fortitude or luck is based on health
                                                    fortitude = 0.0
                                                    low = c_health - (c_health * .75)
                                                    high = c_health - (c_health * .66)
                                                    fortitude = round(random.randint(int(low), int(high)))
                                                    # Resolve Scaling
                                                    c_resolve_health = round(fortitude + (.5 * c_resolve))
                                                    c_resolve_attack = round(
                                                        (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                    c_resolve_defense = round(
                                                        (.30 * c_defense) * (c_resolve / (.50 * c_defense)))

                                                    c_stamina = c_stamina + c_resolve
                                                    c_health = c_health + c_resolve_health
                                                    c_attack = round((c_attack + (2 * c_resolve_attack))*2 )
                                                    c_defense = round(c_defense - c_resolve_defense)
                                                    # if c_defense >= 120:
                                                    # c_defense = 120
                                                    c_used_resolve = True
                                                    c_pet_used = False
                                                    embedVar = discord.Embed(title=f"{c_card} Bankai! :zap:",
                                                                            description=f"**{c_card} says**\n{c_resolve_description}",
                                                                            colour=0xe91e63)
                                                    embedVar.add_field(name=f"Transformation: Bankai",
                                                                    value="Gain double Attack on Resolve.")
                                                    #await private_channel.send(embed=embedVar)
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Bankai!")
                                                    turn_total = turn_total + 1
                                                    turn = 3
                                                elif c_universe == "God Of War":  # God Of War Trait
                                                    # fortitude or luck is based on health
                                                    fortitude = 0.0
                                                    low = c_health - (c_health * .75)
                                                    high = c_health - (c_health * .66)
                                                    fortitude = round(random.randint(int(low), int(high)))
                                                    # Resolve Scaling
                                                    c_resolve_health = round(fortitude + (.5 * o_resolve))
                                                    c_resolve_attack = round(
                                                        (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                    c_resolve_defense = round(
                                                        (.30 * c_defense) * (c_resolve / (.50 * c_defense)))

                                                    c_stamina = c_stamina + c_resolve
                                                    c_attack = round(c_attack + c_resolve_attack)
                                                    c_defense = round(c_defense - c_resolve_defense)
                                                    c_used_resolve = True
                                                    c_pet_used = False

                                                    
                                                    if c_gow_resolve:
                                                        c_health = c_max_health
                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Ascension!")
                                                    elif not c_gow_resolve:
                                                        c_health = round(c_health + (c_max_health / 2))
                                                        c_used_resolve = False
                                                        c_gow_resolve = True
                                                        
                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Crushed Blood Orb: Health Refill")
                                                    

                                                    embedVar = discord.Embed(title=f"{c_card} ASCENDED :zap:",
                                                                            description=f"**{c_card} says**\n{c_resolve_description}",
                                                                            colour=0xe91e63)
                                                    embedVar.add_field(name=f"Transformation: Ascension",
                                                                    value="On Resolve Refill Health.")
                                                    #await private_channel.send(embed=embedVar)
                                                    
                                                    turn_total = turn_total + 1
                                                    turn = 3
                                                elif c_universe == "Fate":  # Fate Trait
                                                    # fortitude or luck is based on health
                                                    fortitude = 0.0
                                                    low = c_health - (c_health * .75)
                                                    high = c_health - (c_health * .66)
                                                    fortitude = round(random.randint(int(low), int(high)))
                                                    # Resolve Scaling
                                                    c_resolve_health = round(fortitude + (.5 * c_resolve))
                                                    c_resolve_attack = round(
                                                        (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                    c_resolve_defense = round(
                                                        (.30 * c_defense) * (c_resolve / (.50 * c_defense)))

                                                    c_stamina = c_stamina + c_resolve
                                                    c_health = c_health + c_resolve_health
                                                    c_attack = round(c_attack + c_resolve_attack)
                                                    c_defense = round(c_defense - c_resolve_defense)

                                                    dmg = damage_cal(mode,c_card_tier, c_talisman_dict, cap3, t_for_c_opponent_affinities, ultimate_attack_name, cmove3_element, c_universe, c_card, c_3, c_attack, c_defense,
                                                                    t_defense, c_stamina, c_enhancer_used, c_health,
                                                                    t_health, t_stamina, c_max_health, t_attack,
                                                                    c_special_move_description, turn_total,
                                                                    ccard_lvl_ap_buff, None)
                                                    t_health = t_health - dmg['DMG']
                                                    embedVar = discord.Embed(
                                                        title=f"{c_card} COMMAND SEAL :zap:\n\n{dmg['MESSAGE']}",
                                                        description=f"**{c_card} says**\n{c_resolve_description}",
                                                        colour=0xe91e63)
                                                    embedVar.add_field(name=f"Transformation: Command Seal",
                                                                    value="On Resolve, Strike with Ultimate, then Focus.")
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Command Seal! {dmg['MESSAGE']}")
                                                    # previous_moves.append(f"(**{turn_total}**) 🩸  {dmg['MESSAGE']}")
                                                    #await private_channel.send(embed=embedVar)
                                                    # c_stamina = 0
                                                    c_used_resolve = True
                                                    c_pet_used = False
                                                    turn_total = turn_total + 1
                                                    turn = 3
                                                elif c_universe == "Kanto Region" or c_universe == "Johto Region" or c_universe == "Hoenn Region" or c_universe == "Sinnoh Region" or c_universe == "Kalos Region" or c_universe == "Unova Region" or c_universe == "Alola Region" or c_universe == "Galar Region":  # Pokemon Resolves
                                                    # fortitude or luck is based on health
                                                    fortitude = 0.0
                                                    low = c_health - (c_health * .75)
                                                    high = c_health - (c_health * .66)
                                                    fortitude = round(random.randint(int(low), int(high)))
                                                    # Resolve Scaling
                                                    c_resolve_health = round(fortitude + (.5 * o_resolve))
                                                    c_resolve_attack = round(
                                                        (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                    c_resolve_defense = round(
                                                        (.30 * c_defense) * (c_resolve / (.50 * c_defense)))

                                                    c_stamina = c_stamina + c_resolve
                                                    c_health = c_health + c_resolve_health
                                                    c_attack = round(c_attack + c_resolve_attack)
                                                    c_defense = round(c_defense) * 2
                                                    c_used_resolve = True
                                                    c_pet_used = False
                                                    embedVar = discord.Embed(title=f"{c_card} EVOLUTION :zap:",
                                                                            description=f"**{c_card} says**\n{c_resolve_description}",
                                                                            colour=0xe91e63)
                                                    embedVar.add_field(name=f"Transformation: Evolution",
                                                                    value="When you Resolve you do not lose Defense.")
                                                    #await private_channel.send(embed=embedVar)
                                                    if turn_total >= 50:
                                                        c_max_health = c_max_health + 1000
                                                        c_health = c_health + 1000
                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Gigantomax Evolution!!! Gained **1000** HP!!!")
                                                    elif turn_total >= 30:
                                                        c_max_health = c_max_health + 500
                                                        c_health = c_health + 500
                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Mega Evolution!! Gained **500** HP!")
                                                    else:
                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Evolution!")
                                                    turn_total = turn_total + 1
                                                    turn = 3
                                                else:  # Standard Resolve
                                                    # fortitude or luck is based on health
                                                    fortitude = 0.0
                                                    low = c_health - (c_health * .75)
                                                    high = c_health - (c_health * .66)
                                                    fortitude = round(random.randint(int(low), int(high)))
                                                    # Resolve Scaling
                                                    c_resolve_health = round(fortitude + (.5 * c_resolve))
                                                    c_resolve_attack = round(
                                                        (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                    c_resolve_defense = round(
                                                        (.30 * c_defense) * (c_resolve / (.50 * c_defense)))

                                                    c_stamina = c_stamina + c_resolve
                                                    c_health = c_health + c_resolve_health
                                                    c_attack = round(c_attack + c_resolve_attack)
                                                    c_defense = round(c_defense - c_resolve_defense)
                                                    c_used_resolve = True
                                                    c_pet_used = False
                                                    if c_universe == "League Of Legends":
                                                        t_health = t_health - (60 * (c_focus_count + t_focus_count))
                                                        embedVar = discord.Embed(title=f"{c_card} PENTA KILL!",
                                                                                description=f"**{c_card} says**\n{c_resolve_description}",
                                                                                colour=0xe91e63)
                                                        embedVar.add_field(name=f"Nexus Destroyed",
                                                                        value=f"**{c_card}** dealt **{(60 * (c_focus_count + t_focus_count))}** damage.")
                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Pentakill! Dealing {(60 * (c_focus_count + t_focus_count))} damage.")
                                                    elif c_universe == "Souls":
                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Phase 2: Enhanced Moveset!")
                                                        
                                                    else:
                                                        embedVar = discord.Embed(
                                                            title=f"{c_card} STRENGTHENED RESOLVE :zap:",
                                                            description=f"**{c_card} says**\n{c_resolve_description}",
                                                            colour=0xe91e63)
                                                        embedVar.add_field(name=f"Transformation",
                                                                        value="All stats & stamina greatly increased")
                                                        previous_moves.append(f"(**{turn_total}**) ⚡ **{c_card}** Resolved!")
                                                    #await private_channel.send(embed=embedVar)
                                                    turn_total = turn_total + 1
                                                    turn = 3
                                            else:
                                                previous_moves.append(f"(**{turn_total}**) {c_card} cannot resolve!")
                                        elif selected_move == 6:
                                            # Resolve Check and Calculation
                                            if c_used_resolve and c_used_focus and not c_pet_used:
                                                c_enhancer_used = True
                                                dmg = damage_cal(mode,c_card_tier, c_talisman_dict, cap1, t_for_c_opponent_affinities, basic_attack_name, cmove1_element, c_universe, c_card, cpet_move, c_attack, c_defense,
                                                                t_defense, c_stamina, c_enhancer_used, c_health, t_health,
                                                                t_stamina, c_max_health, t_attack,
                                                                c_special_move_description, turn_total, ccard_lvl_ap_buff, None)
                                                c_enhancer_used = False
                                                c_pet_used = True
                                                cpet_dmg = dmg['DMG']
                                                cpet_type = dmg['ENHANCED_TYPE']
                                                if dmg['CAN_USE_MOVE']:
                                                    if cpet_type == 'ATK':
                                                        c_attack = round(c_attack + dmg['DMG'])
                                                    elif cpet_type == 'DEF':
                                                        c_defense = round(c_defense + dmg['DMG'])
                                                    elif cpet_type == 'STAM':
                                                        c_stamina = round(c_stamina + dmg['DMG'])
                                                    elif cpet_type == 'HLT':
                                                        c_health = round(c_health + dmg['DMG'])
                                                    elif cpet_type == 'LIFE':
                                                        c_health = round(c_health + dmg['DMG'])
                                                        t_health = round(t_health - dmg['DMG'])
                                                    elif cpet_type == 'DRAIN':
                                                        c_stamina = round(c_stamina + dmg['DMG'])
                                                        t_stamina = round(t_stamina - dmg['DMG'])
                                                    elif cpet_type == 'FLOG':
                                                        c_attack = round(c_attack + dmg['DMG'])
                                                        t_attack = round(t_attack - dmg['DMG'])
                                                    elif cpet_type == 'WITHER':
                                                        c_defense = round(c_defense + dmg['DMG'])
                                                        t_defense = round(t_defense - dmg['DMG'])
                                                    elif cpet_type == 'RAGE':
                                                        c_defense = round(c_defense - dmg['DMG'])
                                                        c_ap_buff = round(c_ap_buff + dmg['DMG'])
                                                    elif cpet_type == 'BRACE':
                                                        c_ap_buff = round(c_ap_buff + dmg['DMG'])
                                                        c_attack = round(c_attack - dmg['DMG'])
                                                    elif cpet_type == 'BZRK':
                                                        c_health = round(c_health - dmg['DMG'])
                                                        c_attack = round(c_attack + dmg['DMG'])
                                                    elif cpet_type == 'CRYSTAL':
                                                        c_health = round(c_health - dmg['DMG'])
                                                        c_defense = round(c_defense + dmg['DMG'])
                                                    elif cpet_type == 'GROWTH':
                                                        c_max_health = round(c_max_health - (c_max_health * .10))
                                                        c_defense = round(c_defense + dmg['DMG'])
                                                        c_attack = round(c_attack + dmg['DMG'])
                                                        c_ap_buff = round(c_ap_buff + dmg['DMG'])
                                                    elif cpet_type == 'STANCE':
                                                        tempattack = dmg['DMG']
                                                        c_attack = c_defense
                                                        c_defense = tempattack
                                                    elif cpet_type == 'CONFUSE':
                                                        tempattack = dmg['DMG']
                                                        t_attack = t_defense
                                                        t_defense = tempattack
                                                    elif cpet_type == 'BLINK':
                                                        c_stamina = round(c_stamina - dmg['DMG'])
                                                        t_stamina = round(t_stamina + dmg['DMG'])
                                                    elif cpet_type == 'SLOW':
                                                        tempstam = round(t_stamina + dmg['DMG'])
                                                        c_stamina = round(c_stamina - dmg['DMG'])
                                                        t_stamina = c_stamina
                                                        c_stamina = tempstam
                                                    elif cpet_type == 'HASTE':
                                                        tempstam = round(t_stamina - dmg['DMG'])
                                                        c_stamina = round(c_stamina + dmg['DMG'])
                                                        t_stamina = c_stamina
                                                        c_stamina = tempstam
                                                    elif cpet_type == 'SOULCHAIN':
                                                        c_stamina = round(dmg['DMG'])
                                                        t_stamina = c_stamina
                                                    elif cpet_type == 'GAMBLE':
                                                        c_health = round(dmg['DMG'])
                                                        t_health = c_health
                                                    elif cpet_type == 'FEAR':
                                                        if c_universe != "Chainsawman":
                                                            c_max_health = round(c_max_health - (c_max_health * .10))
                                                        t_defense = round(t_defense - dmg['DMG'])
                                                        t_attack= round(t_attack - dmg['DMG'])
                                                        t_ap_buff = round(t_ap_buff - dmg['DMG'])
                                                    elif cpet_type == 'WAVE':
                                                        t_health = round(t_health - dmg['DMG'])
                                                    elif cpet_type == 'BLAST':
                                                        if dmg['DMG'] >= 300:
                                                            dmg['DMG'] = 300
                                                        t_health = round(t_health - dmg['DMG'])
                                                    elif cpet_type == 'CREATION':
                                                        c_max_health = round(c_max_health + dmg['DMG'])
                                                        c_health = round(c_health + dmg['DMG'])
                                                    elif cpet_type == 'DESTRUCTION':
                                                        if dmg['DMG'] >= 300:
                                                            dmg['DMG'] = 300
                                                        t_max_health = round(t_max_health - dmg['DMG'])
                                                        if t_max_health <=1:
                                                            t_max_health = 1

                                                    #c_stamina = c_stamina - int(dmg['STAMINA_USED'])
                                                    if c_universe == "Persona":
                                                        petdmg = damage_cal(mode,c_card_tier, c_talisman_dict, cap1, t_for_c_opponent_affinities, basic_attack_name, cmove1_element, c_universe, c_card, c_1, c_attack, c_defense,
                                                                            t_defense, c_stamina, c_enhancer_used, c_health,
                                                                            t_health, t_stamina, c_max_health, t_attack,
                                                                            c_special_move_description, turn_total,
                                                                            ccard_lvl_ap_buff, None)

                                                        t_health = t_health - petdmg['DMG']

                                                        embedVar = discord.Embed(
                                                            title=f"**PERSONA!**\n{cpet_name} was summoned from {c_card}'s soul dealing **{petdmg['DMG']}** damage!!",
                                                            colour=0xe91e63)
                                                        await battle_msg.delete(delay=2)
                                                        if not operformance: #FindMeT
                                                            csummon_file = showsummon(cpet_image, cpet_name, dmg['MESSAGE'], cpet_lvl, cpet_bond)
                                                            embedVar.set_image(url="attachment://pet.png")
                                                            await asyncio.sleep(2)
                                                            battle_msg = await private_channel.send(embed=embedVar, file=csummon_file)
                                                            await asyncio.sleep(2)
                                                            await battle_msg.delete(delay=None)

                                                        #await private_channel.send(embed=embedVar)
                                                        previous_moves.append(f"(**{turn_total}**) **Persona!** 🩸 : **{cpet_name}** was summoned from **{c_card}'s** soul dealing **{petdmg['DMG']}** damage!")
                                                        t_pet_used=True
                                                    else:
                                                        embedVar = discord.Embed(#Findmet
                                                            title=f"{c_card} Summoned 🧬 {cpet_name}",
                                                            colour=0xe91e63)
                                                        await battle_msg.delete(delay=None)
                                                        if not operformance: #FindMeT
                                                            csummon_file = showsummon(cpet_image, cpet_name, dmg['MESSAGE'], cpet_lvl, cpet_bond)
                                                            embedVar.set_image(url="attachment://pet.png")
                                                            await asyncio.sleep(2)
                                                            battle_msg = await private_channel.send(embed=embedVar, file=csummon_file)
                                                            await asyncio.sleep(2)
                                                            await battle_msg.delete(delay=2)
                                                        
                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}** Summoned 🧬 **{cpet_name}**: {dmg['MESSAGE']}")
                                                        
                                                        
                                                    turn = 2
                                                else:
                                                    #await private_channel.send(f"{cpet_name} needs a turn to rest...")
                                                    previous_moves.append(f"(**{turn_total}**) {c_card} Could not summon 🧬 **{cpet_name}**. Needs rest")
                                                    turn = 2
                                            else:
                                                #await private_channel.send(f"{cpet_name} needs a turn to rest...")
                                                previous_moves.append(f"(**{turn_total}**) {c_card} Could not summon 🧬 **{cpet_name}**. Needs rest")
                                        elif selected_move == 8:
                                            c_enhancer_used = True
                                            dmg = damage_cal(mode,c_card_tier, c_talisman_dict, cap1, t_for_c_opponent_affinities, basic_attack_name, cmove1_element, c_universe, c_card, c_enhancer, c_attack, c_defense, o_defense,
                                                            c_stamina, c_enhancer_used, c_health, o_health, player1_card.stamina,
                                                            c_max_health, o_attack, c_special_move_description, turn_total,
                                                            ccard_lvl_ap_buff, None)
                                            c_enhancer_used = False
                                            cdmg = dmg['DMG']
                                            cenh_type = dmg['ENHANCED_TYPE']
                                            if dmg['CAN_USE_MOVE']:
                                                if cenh_type == 'ATK':
                                                    o_attack = round(o_attack + dmg['DMG'])
                                                elif cenh_type == 'DEF':
                                                    o_defense = round(o_defense + dmg['DMG'])
                                                elif cenh_type == 'STAM':
                                                    player1_card.stamina = round(player1_card.stamina + dmg['DMG'])
                                                elif cenh_type == 'HLT':
                                                    o_health = round(o_health + dmg['DMG'])
                                                elif cenh_type == 'LIFE':
                                                    o_health = round(o_health + dmg['DMG'])
                                                    c_health = round(c_health - dmg['DMG'])
                                                elif cenh_type == 'DRAIN':
                                                    player1_card.stamina = round(player1_card.stamina + dmg['DMG'])
                                                    c_stamina = round(c_stamina - dmg['DMG'])
                                                elif cenh_type == 'FLOG':
                                                    o_attack = round(o_attack + dmg['DMG'])
                                                    t_attack = round(t_attack - dmg['DMG'])
                                                elif cenh_type == 'WITHER':
                                                    o_defense = round(o_defense + dmg['DMG'])
                                                    t_defense = round(t_defense - dmg['DMG'])
                                                elif cenh_type == 'RAGE':
                                                    o_defense = round(o_defense - dmg['DMG'])
                                                    o_ap_buff = round(o_ap_buff + dmg['DMG'])
                                                elif cenh_type == 'BRACE':
                                                    o_ap_buff = round(o_ap_buff + dmg['DMG'])
                                                    o_attack = round(o_attack - dmg['DMG'])
                                                elif cenh_type == 'BZRK':
                                                    o_health = round(o_health - dmg['DMG'])
                                                    o_attack = round(o_attack + dmg['DMG'])
                                                elif cenh_type == 'CRYSTAL':
                                                    o_health = round(o_health - dmg['DMG'])
                                                    o_defense = round(o_defense + dmg['DMG'])
                                                elif cenh_type == 'GROWTH':
                                                    o_max_health = round(o_max_health - (o_max_health * .10))
                                                    o_defense = round(o_defense + dmg['DMG'])
                                                    o_attack= round(o_attack + dmg['DMG'])
                                                    o_ap_buff = round(o_ap_buff + dmg['DMG'])
                                                elif cenh_type == 'STANCE':
                                                    tempattack = dmg['DMG']
                                                    o_attack = o_defense
                                                    o_defense = tempattack
                                                elif cenh_type == 'CONFUSE':
                                                    tempattack = dmg['DMG']
                                                    c_attack = c_defense
                                                    c_defense = tempattack
                                                elif cenh_type == 'BLINK':
                                                    player1_card.stamina = round(player1_card.stamina - dmg['DMG'])
                                                    c_stamina = round(c_stamina + dmg['DMG'])
                                                elif cenh_type == 'SLOW':
                                                    tempstam = round(c_stamina + dmg['DMG'])
                                                    player1_card.stamina = round(player1_card.stamina - dmg['DMG'])
                                                    c_stamina = player1_card.stamina
                                                    player1_card.stamina = tempstam
                                                elif cenh_type == 'HASTE':
                                                    tempstam = round(c_stamina - dmg['DMG'])
                                                    player1_card.stamina = round(player1_card.stamina + dmg['DMG'])
                                                    c_stamina = player1_card.stamina
                                                    player1_card.stamina = tempstam
                                                elif cenh_type == 'SOULCHAIN':
                                                    player1_card.stamina = round(dmg['DMG'])
                                                    c_stamina = player1_card.stamina
                                                elif cenh_type == 'GAMBLE':
                                                    o_health = round(dmg['DMG'])
                                                    c_health = o_health
                                                elif cenh_type == 'FEAR':
                                                    if o_universe != "Chainsawman":
                                                        o_max_health = round(o_max_health - (o_max_health * .10))
                                                    t_defense = round(t_defense - dmg['DMG'])
                                                    t_attack= round(t_attack - dmg['DMG'])
                                                    t_ap_buff = round(t_ap_buff - dmg['DMG'])
                                                elif cenh_type == 'WAVE':
                                                    t_health = round(t_health - dmg['DMG'])
                                                elif cenh_type == 'BLAST':
                                                    if dmg['DMG'] >= 700:
                                                        dmg['DMG'] = 700

                                                    t_health = round(t_health - dmg['DMG'])
                                                elif cenh_type == 'CREATION':
                                                    o_max_health = round(o_max_health + dmg['DMG'])
                                                    o_health = round(o_health + dmg['DMG'])
                                                elif cenh_type == 'DESTRUCTION':
                                                    t_max_health = round(t_max_health - dmg['DMG'])
                                                    # c_max_health = round(c_max_health - dmg['DMG'])
                                                    if t_max_health <=1:
                                                        t_max_health = 1
                                                    # if c_max_health <=1:
                                                    #     c_max_health = 1

                                                        
                                                
                                                if cenh_type in Stamina_Enhancer_Check or cenh_type in Time_Enhancer_Check or cenh_type in Control_Enhancer_Check:
                                                    c_stamina = c_stamina
                                                else:
                                                    c_stamina = c_stamina - int(dmg['STAMINA_USED'])

                                                embedVar = discord.Embed(
                                                    title=f"{c_card} ASSISTED {o_card}", colour=0xe91e63)
                                                embedVar.add_field(name=f"{c_card} used {cmove_enhanced_text}!",
                                                                value=f"Enhanced {cenh_type}")
                                                #await private_channel.send(embed=embedVar)
                                                previous_moves.append(f'(**{turn_total}**) **{c_card}** used {cmove_enhanced_text}:👥 Assisting **{o_card}**')
                                                turn_total = turn_total + 1
                                                turn = 3
                                            else:
                                                #await private_channel.send(m.NOT_ENOUGH_STAMINA)
                                                previous_moves.append(f"(**{turn_total}**) **{c_card}** not enough Stamina to use this move {selected_move}") 
                                                turn = 2
                                        elif selected_move == 7:
                                            if c_stamina >= 20:
                                                player3_card.used_defend = True
                                                c_stamina = c_stamina - 20
                                                c_defense = round(c_defense * 2)
                                                embedVar = discord.Embed(
                                                    title=f"**{c_card}** Defended 🛡️ {o_card}", colour=0xe91e63)

                                                #await private_channel.send(embed=embedVar)
                                                previous_moves.append(f"(**{turn_total}**) **{c_card}**: Defended 🛡️ **{o_card}**")
                                                turn_total = turn_total + 1
                                                turn = 3
                                            else:
                                                #await private_channel.send(f"{c_card} is too tired to block...")
                                                previous_moves.append(f"(**{turn_total}**) **{c_card}** is too tired to block.")
                                                turn = 2

                                        if selected_move != 5 and selected_move != 6 and selected_move != 7 and selected_move != 8:
                                            # If you have enough stamina for move, use it

                                            if dmg['CAN_USE_MOVE']:
                                                if dmg['ENHANCE']:
                                                    enh_type = dmg['ENHANCED_TYPE']

                                                    if enh_type == 'ATK':
                                                        c_attack = round(c_attack + dmg['DMG'])
                                                    elif enh_type == 'DEF':
                                                        c_defense = round(c_defense + dmg['DMG'])
                                                    elif enh_type == 'STAM':
                                                        c_stamina = round(c_stamina + dmg['DMG'])
                                                    elif enh_type == 'HLT':
                                                        c_health = round(c_health + dmg['DMG'])
                                                    elif enh_type == 'LIFE':
                                                        c_health = round(c_health + dmg['DMG'])
                                                        t_health = round(t_health - dmg['DMG'])
                                                    elif enh_type == 'DRAIN':
                                                        c_stamina = round(c_stamina + dmg['DMG'])
                                                        t_stamina = round(t_stamina - dmg['DMG'])
                                                    elif enh_type == 'FLOG':
                                                        c_attack = round(c_attack + dmg['DMG'])
                                                        t_attack = round(t_attack - dmg['DMG'])
                                                    elif enh_type == 'WITHER':
                                                        c_defense = round(c_defense + dmg['DMG'])
                                                        t_defense = round(t_defense - dmg['DMG'])
                                                    elif enh_type == 'RAGE':
                                                        c_defense = round(c_defense - dmg['DMG'])
                                                        c_ap_buff = round(c_ap_buff + dmg['DMG'])
                                                    elif enh_type == 'BRACE':
                                                        c_ap_buff = round(c_ap_buff + dmg['DMG'])
                                                        c_attack = round(c_attack - dmg['DMG'])
                                                    elif enh_type == 'BZRK':
                                                        c_health = round(c_health - dmg['DMG'])
                                                        c_attack = round(c_attack + dmg['DMG'])
                                                    elif enh_type == 'CRYSTAL':
                                                        c_health = round(c_health - dmg['DMG'])
                                                        c_defense = round(c_defense + dmg['DMG'])
                                                    elif enh_type == 'GROWTH':
                                                        c_max_health = round(c_max_health - (c_max_health * .10))
                                                        c_defense = round(c_defense + dmg['DMG'])
                                                        c_attack = round(c_attack + dmg['DMG'])
                                                        c_ap_buff = round(c_ap_buff + dmg['DMG'])
                                                    elif enh_type == 'STANCE':
                                                        tempattack = dmg['DMG']
                                                        c_attack = c_defense
                                                        c_defense = tempattack
                                                    elif enh_type == 'CONFUSE':
                                                        tempattack = dmg['DMG']
                                                        t_attack = t_defense
                                                        t_defense = tempattack
                                                    elif enh_type == 'BLINK':
                                                        c_stamina = round(c_stamina - dmg['DMG'])
                                                        t_stamina = round(t_stamina + dmg['DMG'])
                                                    elif enh_type == 'SLOW':
                                                        tempstam = round(t_stamina + dmg['DMG'])
                                                        c_stamina = round(c_stamina - dmg['DMG'])
                                                        t_stamina = c_stamina
                                                        c_stamina = tempstam
                                                    elif enh_type == 'HASTE':
                                                        tempstam = round(t_stamina - dmg['DMG'])
                                                        c_stamina = round(c_stamina + dmg['DMG'])
                                                        t_stamina = c_stamina
                                                        c_stamina = tempstam
                                                    elif enh_type == 'SOULCHAIN':
                                                        c_stamina = round(dmg['DMG'])
                                                        t_stamina = c_stamina
                                                    elif enh_type == 'GAMBLE':
                                                        if mode in D_modes:
                                                            t_health = round(dmg['DMG']) * 2
                                                            c_health = round(dmg['DMG'])
                                                        elif mode in B_modes:
                                                            t_health = round(dmg['DMG']) * 3
                                                            c_health = round(dmg['DMG'])
                                                        else:
                                                            t_health = round(dmg['DMG'])
                                                            c_health = round(dmg['DMG'])
                                                    elif enh_type == 'FEAR':
                                                        if t_universe != "Chainsawman":
                                                            c_max_health = round(c_max_health - (c_max_health * .10))
                                                        t_defense = round(t_defense - dmg['DMG'])
                                                        t_attack= round(t_attack - dmg['DMG'])
                                                        t_ap_buff = round(t_ap_buff - dmg['DMG'])
                                                    elif enh_type == 'WAVE':
                                                        t_health = round(t_health - dmg['DMG'])
                                                    elif enh_type == 'BLAST':
                                                        if dmg['DMG'] >= 700:
                                                            dmg['DMG'] = 700

                                                        t_health = round(t_health - dmg['DMG'])
                                                    elif enh_type == 'CREATION':
                                                        c_max_health = round(c_max_health + dmg['DMG'])
                                                        c_health = round(c_health + dmg['DMG'])
                                                    elif enh_type == 'DESTRUCTION':
                                                        t_max_health = round(t_max_health - dmg['DMG'])
                                                        # c_max_health = round(c_max_health - dmg['DMG'])
                                                        if t_max_health <=1:
                                                            t_max_health = 1
                                                        # if c_max_health <=1:
                                                        #     c_max_health = 1

                                                    if enh_type in Stamina_Enhancer_Check or enh_type in Time_Enhancer_Check or enh_type in Control_Enhancer_Check:
                                                        c_stamina = c_stamina
                                                    else:
                                                        c_stamina = c_stamina - int(dmg['STAMINA_USED'])

                                                    embedVar = discord.Embed(title=f"{dmg['MESSAGE']}",
                                                                            colour=embed_color_c)
                                                    #await private_channel.send(embed=embedVar)
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}**: 🦠 {dmg['MESSAGE']}")
                                                    turn_total = turn_total + 1
                                                    turn = 3
                                                elif dmg['DMG'] == 0:
                                                    c_stamina = c_stamina - int(dmg['STAMINA_USED'])

                                                    embedVar = discord.Embed(title=f"{dmg['MESSAGE']}", colour=embed_color_c)
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}**: {dmg['MESSAGE']}")
                                                    if carm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                        carm_barrier_active=False
                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}**'s 💠 Barrier Disabled!")
                                                    
                                                    turn_total = turn_total + 1
                                                    turn = 3
                                                else:
                                                    if t_universe == "Naruto" and t_stamina < 10:
                                                        t_stored_damage = round(dmg['DMG'])
                                                        t_naruto_heal_buff = t_naruto_heal_buff + t_stored_damage
                                                        t_health = t_health 
                                                        embedVar = discord.Embed(title=f"{t_card}: Substitution Jutsu", description=f"{c_card} strikes a log", colour=0xe91e63)
                                                        previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸: Substitution Jutsu")
                                                        if not t_used_resolve:
                                                            previous_moves.append(f"(**{turn_total}**) 🩸**{t_stored_damage}** Hasirama Cells stored. 🩸**{t_naruto_heal_buff}** total stored.")
                                                        if carm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                            carm_barrier_active=False
                                                            embedVar.add_field(name=f"{c_card}'s **Barrier** Disabled!", value =f"*Maximize **Barriers** with your Enhancer!*")
                                                            previous_moves.append(f"(**{turn_total}**) **{c_card}**'s 💠 Barrier Disabled!")
                                                        #await private_channel.send(embed=embedVar)
                                                    elif tarm_shield_active and dmg['ELEMENT'] != dark_element:
                                                        
                                                        if dmg['ELEMENT'] == poison_element: #Poison Update
                                                            if c_poison_dmg <= 600:
                                                                c_poison_dmg = c_poison_dmg + 30
                                                            
                                                        
                                                        if tshield_value > 0:
                                                            tshield_value = tshield_value -dmg['DMG']
                                                            t_health = t_health 
                                                            if tshield_value <=0:
                                                                embedVar = discord.Embed(title=f"{t_card}'s' **Shield** Shattered!", description=f"{c_card} breaks the **Shield**!", colour=0xe91e63)
                                                                previous_moves.append(f"(**{turn_total}**) **{t_card}'s** 🌐 Shield Shattered!")
                                                                if carm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                    carm_barrier_active=False
                                                                    embedVar.add_field(name=f"{c_card}'s **Barrier** Disabled!", value =f"*Maximize **Barriers** with your Enhancer!*")
                                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}**'s 💠 Barrier Disabled!")
                                                                #await private_channel.send(embed=embedVar)
                                                                tarm_shield_active = False
                                                            else:
                                                                embedVar = discord.Embed(title=f"{t_card} Activates **Shield** 🌐", description=f"**{c_card}** strikes the Shield 🌐\n**{tshield_value} Shield** Left!", colour=0xe91e63)
                                                                previous_moves.append(f"(**{turn_total}**) **{c_card}** strikes **{t_card}**'s Shield 🌐\n**{tshield_value} Shield** Left!")
                                                                if carm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                    carm_barrier_active=False
                                                                    embedVar.add_field(name=f"{c_card}'s **Barrier** Disabled!", value =f"*Maximize **Barriers** with your Enhancer!*")
                                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}**'s 💠 Barrier Disabled!")
                                                                #await private_channel.send(embed=embedVar)

                                                    elif tarm_barrier_active and dmg['ELEMENT'] != psychic_element :
                                                        if tbarrier_count >1:
                                                            t_health = t_health 
                                                            embedVar = discord.Embed(title=f"{t_card} Activates **Barrier** 💠", description=f"{c_card}'s attack **Nullified**!\n **{tbarrier_count - 1} Barriers** remain!", colour=0xe91e63)
                                                            previous_moves.append(f"(**{turn_total}**) **{t_card}** Activates Barrier 💠 {c_card}'s attack **Nullified**!\n💠 {tbarrier_count - 1} **Barriers** remain!")
                                                            if carm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                carm_barrier_active=False
                                                                embedVar.add_field(name=f"{c_card}'s **Barrier** Disabled!", value =f"*Maximize **Barriers** with your Enhancer!*")
                                                                previous_moves.append(f"(**{turn_total}**) **{c_card}**'s 💠 Barrier Disabled!")
                                                            #await private_channel.send(embed=embedVar)
                                                            tbarrier_count = tbarrier_count - 1
                                                        elif tbarrier_count==1:
                                                            embedVar = discord.Embed(title=f"{t_card}'s **Barrier** Broken!", description=f"{c_card} destroys the **Barrier**", colour=0xe91e63)
                                                            previous_moves.append(f"(**{turn_total}**) **{t_card}**'s Barrier Broken!")
                                                            tbarrier_count = tbarrier_count - 1
                                                            if carm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                carm_barrier_active=False
                                                                embedVar.add_field(name=f"{c_card}'s **Barrier** Disabled!", value =f"*Maximize **Barriers** with your Enhancer!*")
                                                                previous_moves.append(f"(**{turn_total}**) **{c_card}**'s 💠 Barrier Disabled!")
                                                            #await private_channel.send(embed=embedVar)
                                                            tarm_barrier_active = False
                                                    elif tarm_parry_active and dmg['ELEMENT'] != earth_element:
                                                        if tparry_count > 1:
                                                            t_health = t_health
                                                            tparry_damage = round(dmg['DMG'])
                                                            t_health = round(t_health - (tparry_damage * .75))
                                                            c_health = round(c_health - (tparry_damage * .40))
                                                            tparry_count = tparry_count - 1
                                                            embedVar = discord.Embed(title=f"{t_card} Activates **Parry** 🔄", description=f"{c_card} takes {round(tparry_damage * .40)}! DMG\n **{tparry_count} Parries** to go!!", colour=0xe91e63)
                                                            previous_moves.append(f"(**{turn_total}**) **{t_card}** Activates Parry 🔄 after **{round(tparry_damage * .75)}** dmg dealt: {c_card} takes {round(tparry_damage * .40)}! DMG\n **{tparry_count}  Parries** to go!!")
                                                            if carm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                carm_barrier_active=False
                                                                embedVar.add_field(name=f"{c_card}'s **Barrier** Disabled!", value =f"*Maximize **Barriers** with your Enhancer!*")
                                                                previous_moves.append(f"(**{turn_total}**) **{c_card}**'s 💠 Barrier Disabled!")
                                                            #await private_channel.send(embed=embedVar)
                                                            
                                                        elif tparry_count==1:
                                                            t_health = t_health
                                                            tparry_damage = round(dmg['DMG'])
                                                            t_health = round(t_health - (tparry_damage * .75))
                                                            c_health = round(c_health - (tparry_damage * .40))
                                                            embedVar = discord.Embed(title=f"{t_card} **Parry** Penetrated!!", description=f"{c_card} takes {round(tparry_damage * .40)}! DMG and breaks the **Parry**", colour=0xe91e63)
                                                            previous_moves.append(f"(**{turn_total}**) **{t_card}** Parry Penetrated! **{c_card}** takes **{round(tparry_damage * .40)}**! DMG and breaks the **Parry**")
                                                            tparry_count = tparry_count - 1
                                                            if carm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                carm_barrier_active=False
                                                                embedVar.add_field(name=f"{c_card}'s **Barrier** Disabled!", value =f"*Maximize **Barriers** with your Enhancer!*")
                                                                previous_moves.append(f"(**{turn_total}**) **{c_card}**'s 💠 Barrier Disabled!")
                                                            #await private_channel.send(embed=embedVar)
                                                            tarm_parry_active = False
                                                    else:
                                                        if c_universe == "One Piece" and (c_card_tier in low_tier_cards or c_card_tier in mid_tier_cards or c_card_tier in high_tier_cards):
                                                            if c_focus_count == 0:
                                                                dmg['DMG'] = dmg['DMG'] * .6

                                                        if dmg['REPEL']:
                                                            c_health = c_health - int(dmg['DMG'])
                                                        elif dmg['ABSORB']:
                                                            t_health = t_health + int(dmg['DMG'])
                                                        elif dmg['ELEMENT'] == water_element:
                                                            if cmove1_element == water_element:
                                                                c_basic_water_buff = c_basic_water_buff + 40
                                                            if cmove2_element == water_element:
                                                                c_special_water_buff = c_special_water_buff + 40
                                                            if cmove3_element == water_element:
                                                                c_ultimate_water_buff = c_ultimate_water_buff + 40
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == ice_element:
                                                            c_ice_counter = c_ice_counter + 1
                                                            if c_ice_counter == 2:
                                                                c_freeze_enh = True
                                                                c_ice_counter = 0
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == time_element:
                                                            if c_stamina <= 80:
                                                                c_stamina = 0
                                                            player3_card.used_defend = True
                                                            c_defense = round(c_defense * 2)
                                                            previous_moves.append(f"**{c_card}** Blocked 🛡️")

                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == bleed_element:
                                                            c_bleed_counter = c_bleed_counter + 1
                                                            if c_bleed_counter == 3:
                                                                c_bleed_hit = True
                                                                c_bleed_counter = 0
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == recoil_element:
                                                            c_health = c_health - (dmg['DMG'] * .60)
                                                            if c_health <= 0:
                                                                c_health = 1
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == earth_element:
                                                            c_defense = c_defense + (dmg['DMG'] * .25)
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == death_element:
                                                            t_max_health = t_max_health - (dmg['DMG'] * .20)
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == light_element:
                                                            c_stamina = round(c_stamina + (dmg['STAMINA_USED'] / 2))
                                                            c_attack = c_attack + (dmg['DMG'] * .20)
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == dark_element:
                                                            t_stamina = t_stamina - 15
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == life_element:
                                                            c_health = c_health + (dmg['DMG'] * .20)
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == psychic_element:
                                                            t_defense = t_defense - (dmg['DMG'] * .15)
                                                            t_attack = t_attack - (dmg['DMG'] * .15)
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == fire_element:
                                                            c_burn_dmg = c_burn_dmg + round(dmg['DMG'] * .25)
                                                            t_health = t_health - dmg['DMG']


                                                        elif dmg['ELEMENT'] == electric_element:
                                                            c_shock_buff = c_shock_buff +  (dmg['DMG'] * .15)
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == poison_element:
                                                            if c_poison_dmg <= 600:
                                                                c_poison_dmg = c_poison_dmg + 30
                                                            t_health = t_health - dmg['DMG']
                                                            
                                                        elif dmg['ELEMENT'] == gravity_element:
                                                            c_gravity_hit = True
                                                            t_health = t_health - dmg['DMG']
                                                            t_defense = t_defense - (dmg['DMG'] * .25)
                                                        else:
                                                            t_health = t_health - dmg['DMG']

                                                        embedVar = discord.Embed(title=f"{dmg['MESSAGE']}", colour=embed_color_c)
                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}**: {dmg['MESSAGE']}")
                                                        if carm_siphon_active:
                                                            siphon_damage = (dmg['DMG'] * .15) + csiphon_value
                                                            c_health = round(c_health + siphon_damage)
                                                            if c_health >= c_max_health:
                                                                c_health = c_max_health
                                                                previous_moves.append(f"(**{turn_total}**) **{c_card}**: 💉 Siphoned **Full Health!**")
                                                            else:
                                                                previous_moves.append(f"(**{turn_total}**) **{c_card}**: 💉 Siphoned **{round(siphon_damage)}** Health!")
                                                            if mode not in ai_co_op_modes:
                                                                await button_ctx.defer(ignore=True)
                                                        if carm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                            carm_barrier_active=False
                                                            embedVar.add_field(name=f"{c_card}'s **Barrier** Disabled!", value =f"*Maximize **Barriers** with your Enhancer!*")
                                                            previous_moves.append(f"(**{turn_total}**) **{c_card}**'s 💠 Barrier Disabled!")
                                                        #await private_channel.send(embed=embedVar)
                                                    if t_health <= 0:
                                                        if t_final_stand==True:
                                                            if t_universe == "Dragon Ball Z":
                                                                embedVar = discord.Embed(title=f"{t_card}'s LAST STAND", description=f"{t_card} FINDS RESOLVE", colour=0xe91e63)
                                                                embedVar.add_field(name=f"**{t_card}** Resolved and continues to fight", value="All stats & stamina increased")
                                                                previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 Transformation: Last Stand!!!")
                                                                if carm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                    carm_barrier_active=False
                                                                    embedVar.add_field(name=f"{c_card}'s **Barrier** Disabled!", value =f"*Maximize **Barriers** with your Enhancer!*")
                                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}**'s 💠 Barrier Disabled!")
                                                                #await private_channel.send(embed=embedVar)
                                                                t_health = int(.75 * (t_attack + t_defense))
                                                                
                                                                t_used_resolve = True
                                                                t_final_stand = False
                                                                t_used_focus = True
                                                                c_stamina = c_stamina - dmg['STAMINA_USED']
                                                                turn_total = turn_total + 1
                                                                turn = 3
                                                        else:
                                                            t_health = 0
                                                            c_stamina = c_stamina - dmg['STAMINA_USED']
                                                            turn_total = turn_total + 1
                                                    else:
                                                        c_stamina = c_stamina - dmg['STAMINA_USED']
                                                        turn_total = turn_total + 1
                                                        turn = 3
                                            else:
                                                emessage = m.NOT_ENOUGH_STAMINA
                                                embedVar = discord.Embed(title=emessage,
                                                                        description=f"Use abilities to Increase `STAM` or enter `FOCUS STATE`!",
                                                                        colour=0xe91e63)
                                                #await private_channel.send(embed=embedVar)
                                                previous_moves.append(f"(**{turn_total}**) **{c_card}** not enough Stamina to use this move {selected_move}") 
                                                turn = 2
                                    else:
                                        cap1 = list(c_1.values())[0] + ccard_lvl_ap_buff + c_shock_buff + c_basic_water_buff + c_ap_buff
                                        cap2 = list(c_2.values())[0] + ccard_lvl_ap_buff + c_shock_buff + c_special_water_buff + c_ap_buff
                                        cap3 = list(c_3.values())[0] + ccard_lvl_ap_buff + cdemon_slayer_buff + c_shock_buff + c_ultimate_water_buff + c_ap_buff
                                        cenh1 = list(c_enhancer.values())[0]
                                        cenh_name = list(c_enhancer.values())[2]
                                        cpet_enh_name = list(cpet_move.values())[2]
                                        cpet_msg_on_resolve = ""

                                        if cap1 < 150:
                                            cap1 = 150
                                        if cap2 < 150:
                                            cap2 = 150            
                                        if cap3 < 150:
                                            cap3 = 150


                                        if c_universe == "Souls" and c_used_resolve:
                                            companion_card = showcard("battle", c, carm,c_max_health, c_health, c_max_stamina, c_stamina,
                                                                c_used_resolve, ctitle, c_used_focus, c_attack, c_defense,
                                                                turn_total, cap2, cap3, cap3, cenh1, cenh_name, ccard_lvl, t_defense)
                                        else:
                                            companion = showcard("battle", c, carm,c_max_health, c_health, c_max_stamina, c_stamina,
                                                                c_used_resolve, ctitle, c_used_focus, c_attack, c_defense,
                                                                turn_total, cap1, cap2, cap3, cenh1, cenh_name, ccard_lvl, t_defense)

                                        if c_universe == "Solo Leveling" and not c_swapped:
                                            if temp_tarm_shield_active and not tarm_shield_active:
                                                if carm_shield_active:
                                                    cshield_value = cshield_value + temp_tshield_value
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 **ARISE!** *{tarm_name}* is now yours")
                                                    c_swapped = True
                                                elif not carm_shield_active:
                                                    carm_shield_active = True
                                                    cshield_value = temp_tshield_value
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 **ARISE!** *{tarm_name}* is now yours")
                                                    c_swapped = True
                                            elif temp_tarm_barrier_active and not tarm_barrier_active:
                                                if carm_barrier_active:
                                                    cbarrier_count = cbarrier_count + temp_tbarrier_count
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 **ARISE!** *{tarm_name}* is now yours")
                                                    c_swapped = True
                                                elif not carm_barrier_active:
                                                    carm_barrier_active = True
                                                    cbarrier_count = temp_tbarrier_count
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 **ARISE!** *{tarm_name}* is now yours")
                                                    c_swapped = True
                                            elif temp_tarm_parry_active and not tarm_parry_active:
                                                if carm_parry_active:
                                                    cparry_count = cparry_count + temp_tparry_count
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 **ARISE!** *{tarm_name}* is now yours")
                                                    c_swapped = True
                                                elif not carm_parry_active:
                                                    carm_parry_active = True
                                                    cparry_count = temp_tparry_count
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 **ARISE!** *{tarm_name}* is now yours")
                                                    c_swapped = True


                                        # await private_channel.send(file=companion)

                                        if c_used_focus and c_used_resolve:
                                            options = ["q", "Q", "0", "1", "2", "3", "4", "6", "7"]
                                        elif c_used_focus and not c_used_resolve:
                                            options = ["q", "Q", "0", "1", "2", "3", "4", "5", "7"]
                                        else:
                                            options = ["q", "Q", "0", "1", "2", "3", "4", "7"]

                                        battle_buttons = []
                                        util_buttons = []
                                        
                                        if c_stamina >= 10:
                                            if c_universe == "Souls" and c_used_resolve:
                                                battle_buttons.append(
                                                    manage_components.create_button(
                                                        style=ButtonStyle.green,
                                                        label=f"{o_super_emoji} 10",
                                                        custom_id="1"
                                                    )
                                                )
                                            else:
                                                battle_buttons.append(
                                                    manage_components.create_button(
                                                        style=ButtonStyle.green,
                                                        label=f"{c_basic_emoji} 10",
                                                        custom_id="1"
                                                    )
                                                )

                                        if c_stamina >= 30:
                                            if c_universe == "Souls" and c_used_resolve:
                                                battle_buttons.append(
                                                    manage_components.create_button(
                                                        style=ButtonStyle.green,
                                                        label=f"{o_ultimate_emoji} 30",
                                                        custom_id="2"
                                                    )
                                                )
                                            else:
                                                battle_buttons.append(
                                                    manage_components.create_button(
                                                        style=ButtonStyle.green,
                                                        label=f"{c_super_emoji} 30",
                                                        custom_id="2"
                                                    )
                                                )


                                        if c_stamina >= 80:
                                            battle_buttons.append(
                                                manage_components.create_button(
                                                    style=ButtonStyle.green,
                                                    label=f"{c_ultimate_emoji} 80",
                                                    custom_id="3"
                                                )
                                            )

                                        if c_stamina >= 20:
                                            battle_buttons.append(
                                                manage_components.create_button(
                                                    style=ButtonStyle.blue,
                                                    label=f"🦠 20",
                                                    custom_id="4"
                                                )
                                            )

                                            if t_gravity_hit == False:
                                                util_buttons.append(
                                                    manage_components.create_button(
                                                        style=ButtonStyle.blue,
                                                        label="🛡️ Block 20",
                                                        custom_id="0"
                                                    )
                                                )

                                        if c_stamina>=20:
                                            coop_util_buttons = [
                                                manage_components.create_button(
                                                    style=ButtonStyle.blue,
                                                    label="🦠 Enhance Companion 20",
                                                    custom_id="7"
                                                )
                                            ]

                                        if c_used_focus and c_used_resolve and not c_pet_used:
                                            util_buttons.append(
                                                manage_components.create_button(
                                                    style=ButtonStyle.green,
                                                    label="🧬",
                                                    custom_id="6"
                                                )
                                            )

                                        if c_used_focus and not c_used_resolve:
                                            util_buttons.append(
                                                manage_components.create_button(
                                                    style=ButtonStyle.green,
                                                    label="⚡Resolve!",
                                                    custom_id="5"
                                                )
                                            )
                                        util_buttons.append(
                                            manage_components.create_button(
                                                style=ButtonStyle.grey,
                                                label="Quit",
                                                custom_id="q"
                                            ),
                                        )

                                        battle_action_row = manage_components.create_actionrow(*battle_buttons)
                                        util_action_row = manage_components.create_actionrow(*util_buttons)
                                        coop_util_action_row = manage_components.create_actionrow(*coop_util_buttons)

                                        cap1 = list(c_1.values())[0] + ccard_lvl_ap_buff + c_shock_buff + c_basic_water_buff + c_ap_buff
                                        cap2 = list(c_2.values())[0] + ccard_lvl_ap_buff + c_shock_buff + c_special_water_buff + c_ap_buff
                                        cap3 = list(c_3.values())[0] + ccard_lvl_ap_buff + cdemon_slayer_buff + c_shock_buff + c_ultimate_water_buff + c_ap_buff
                                        cenh1 = list(c_enhancer.values())[0]
                                        cenh_name = list(c_enhancer.values())[2]
                                        cpet_enh_name = list(cpet_move.values())[2]
                                        cpet_msg_on_resolve = ""
                                        tarm_message = " "
                                        oarm_message = " "

                                        if cap1 < 150:
                                            cap1 = 150
                                        if cap2 < 150:
                                            cap2 = 150            
                                        if cap3 < 150:
                                            cap3 = 150


                                        if c_used_resolve:
                                            cpet_msg_on_resolve = f"🧬 {enhancer_mapping[pet_enh_name]}"
                                        if tarm_barrier_active:
                                            tarm_message = f"💠{tbarrier_count}"
                                        elif tarm_shield_active:
                                            tarm_message = f"🌐{tshield_value}"
                                        elif tarm_parry_active:
                                            tarm_message = f"🔄{tparry_count}"
                                        elif tarm_passive_type == "SIPHON":
                                            tarm_message = f"💉{tarm_passive_value}"
                                        if oarm_barrier_active:
                                            oarm_message = f"💠{obarrier_count}"
                                        elif oarm_shield_active:
                                            oarm_message = f"🌐{oshield_value}"
                                        elif oarm_parry_active:
                                            oarm_message = f"🔄{oparry_count}"
                                        elif oarm_passive_type == "SIPHON":
                                            oarm_message = f"💉{oarm_passive_value}"
                                        if carm_passive_type == "BARRIER":
                                            if carm_barrier_active:
                                                carm_passive_value = f"{cbarrier_count}"
                                            else:
                                                carm_passive_value = 0
                                        elif carm_passive_type == "SHIELD":
                                            if carm_shield_active:
                                                carm_passive_value = f"{cshield_value}"
                                            else:
                                                carm_passive_value = 0
                                        elif carm_passive_type == "PARRY":
                                            if carm_parry_active:
                                                carm_passive_value = f"{cparry_count}"
                                            else:
                                                carm_passive_value = 0
                                        embedVar = discord.Embed(title=f"", description=textwrap.dedent(f"""\
                                        {previous_moves_into_embed}
                                        
                                        """), color=0xe74c3c)
                                        embedVar.set_author(name=f"🦾 {carm_name} - {carm_passive_type} {carm_passive_value} {enhancer_suffix_mapping[carm_passive_type]}\n{cpet_msg_on_resolve}\n")
                                        embedVar.add_field(name=f"➡️ **Current Turn** {turn_total}", value=f"{user2.mention} Select move below!")
                                        # await asyncio.sleep(2)
                                        embedVar.set_image(url="attachment://image.png")
                                        embedVar.set_footer(
                                            text=f"{t_card}: ❤️{round(t_health)} 🌀{round(t_stamina)} 🗡️{round(t_attack)}/🛡️{round(t_defense)} {tarm_message}\n{o_card}: ❤️{round(o_health)} 🌀{round(player1_card.stamina)} 🗡️{round(o_attack)}/🛡️{round(o_defense)} {oarm_message}",
                                            icon_url="https://cdn.discordapp.com/emojis/789290881654980659.gif?v=1")
                                        await battle_msg.delete(delay=2)
                                        await asyncio.sleep(2)
                                        battle_msg = await private_channel.send(embed=embedVar, components=[battle_action_row, util_action_row,
                                                                            coop_util_action_row], file=companion)
                                        # Make sure user is responding with move
                                        def check(button_ctx):
                                            return button_ctx.author == user and button_ctx.custom_id in options

                                        try:
                                            button_ctx: ComponentContext = await manage_components.wait_for_component(
                                                self.bot,
                                                components=[battle_action_row, util_action_row, coop_util_action_row],
                                                timeout=120, check=check)

                                            # calculate data based on selected move
                                            if button_ctx.custom_id == "q" or button_ctx.custom_id == "Q":
                                                c_health = 0

                                                if private_channel.guild:
                                                    await private_channel.send(f"{user2.mention} has fled the battle...")
                                                    previous_moves.append(f"(**{turn_total}**) 💨 **{c_card}** Fled...")
                                                    # await discord.TextChannel.delete(private_channel, reason=None)
                                                else:
                                                    await private_channel.send(f"You fled the battle...")
                                                    previous_moves.append(f"(**{turn_total}**) 💨 **{c_card}** Fled...")
                                                #return
                                            if button_ctx.custom_id == "1":
                                                if c_universe == "Souls" and c_used_resolve:
                                                    dmg = damage_cal(mode,c_card_tier, c_talisman_dict, cap2, t_for_c_opponent_affinities, special_attack_name, cmove2_element, c_universe, c_card, c_2, c_attack, c_defense, t_defense,
                                                                c_stamina, c_enhancer_used, c_health, t_health, t_stamina,
                                                                c_max_health, t_attack, c_special_move_description, turn_total,
                                                                ccard_lvl_ap_buff, c_1)
                                                else:
                                                    dmg = damage_cal(mode,c_card_tier, c_talisman_dict, cap1, t_for_c_opponent_affinities, basic_attack_name, cmove1_element, c_universe, c_card, c_1, c_attack, c_defense, t_defense,
                                                                    c_stamina, c_enhancer_used, c_health, t_health, t_stamina,
                                                                    c_max_health, t_attack, c_special_move_description,
                                                                    turn_total, ccard_lvl_ap_buff, None)
                                            elif button_ctx.custom_id == "2":
                                                if c_universe == "Souls" and c_used_resolve:
                                                    dmg = damage_cal(mode,c_card_tier, c_talisman_dict, cap3, t_for_c_opponent_affinities, ultimate_attack_name, cmove3_element, c_universe, c_card, c_3, c_attack, c_defense, t_defense,
                                                                c_stamina, c_enhancer_used, c_health, t_health, t_stamina,
                                                                c_max_health, t_attack, c_special_move_description, turn_total,
                                                                ccard_lvl_ap_buff, c_2)
                                                else:
                                                    dmg = damage_cal(mode,c_card_tier, c_talisman_dict, cap2, t_for_c_opponent_affinities, special_attack_name, cmove2_element, c_universe, c_card, c_2, c_attack, c_defense, t_defense,
                                                                    c_stamina, c_enhancer_used, c_health, t_health, t_stamina,
                                                                    c_max_health, t_attack, c_special_move_description,
                                                                    turn_total, ccard_lvl_ap_buff, None)
                                            elif button_ctx.custom_id == "3":

                                                dmg = damage_cal(mode,c_card_tier, c_talisman_dict, cap3, t_for_c_opponent_affinities, ultimate_attack_name, cmove3_element, c_universe, c_card, c_3, c_attack, c_defense, t_defense,
                                                                c_stamina, c_enhancer_used, c_health, t_health, t_stamina,
                                                                c_max_health, t_attack, c_special_move_description,
                                                                turn_total, ccard_lvl_ap_buff, None)
                                                if c_gif != "N/A" and not operformance:
                                                    await battle_msg.delete(delay=None)
                                                    # await asyncio.sleep(1)
                                                    battle_msg = await private_channel.send(f"{c_gif}")
                                                    await asyncio.sleep(2)
                                            elif button_ctx.custom_id == "4":
                                                c_enhancer_used = True

                                                dmg = damage_cal(mode,c_card_tier, c_talisman_dict, cap1, t_for_c_opponent_affinities, basic_attack_name, cmove1_element, c_universe, c_card, c_enhancer, c_attack, c_defense,
                                                                t_defense, c_stamina, c_enhancer_used, c_health, t_health,
                                                                t_stamina, c_max_health, t_attack,
                                                                c_special_move_description, turn_total, ccard_lvl_ap_buff, None)
                                                c_enhancer_used = False
                                            elif button_ctx.custom_id == "5":
                                                # Resolve Check and Calculation
                                                if not c_used_resolve and c_used_focus:
                                                    if c_universe == "My Hero Academia":  # My Hero Trait
                                                        # fortitude or luck is based on health
                                                        fortitude = 0.0
                                                        low = c_health - (c_health * .75)
                                                        high = c_health - (c_health * .66)
                                                        fortitude = round(random.randint(int(low), int(high)))
                                                        # Resolve Scaling
                                                        c_resolve_health = round(fortitude + (.5 * c_resolve))
                                                        c_resolve_attack = round(
                                                            (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                        c_resolve_defense = round(
                                                            (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                        ccard_lvl_ap_buff = ccard_lvl_ap_buff + 200 + turn_total

                                                        c_stamina = 160
                                                        c_health = c_health + c_resolve_health
                                                        c_attack = round(c_attack + c_resolve_attack)
                                                        c_defense = round(c_defense - c_resolve_defense)
                                                        c_used_resolve = True
                                                        c_pet_used = False
                                                        embedVar = discord.Embed(title=f"{c_card} PLUS ULTRAAA",
                                                                                description=f"**{c_card} says**\n{c_resolve_description}",
                                                                                colour=0xe91e63)
                                                        embedVar.add_field(name=f"Transformation: Plus Ultra",
                                                                        value="You do not lose a turn after you Resolve.")
                                                        #await button_ctx.send(embed=embedVar)
                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: PLUS ULTRA!")
                                                        await button_ctx.defer(ignore=True)
                                                        turn_total = turn_total + 1
                                                        turn = 2

                                                    if c_universe == "One Piece" and (c_card_tier in high_tier_cards):
                                                        # fortitude or luck is based on health
                                                        fortitude = 0.0
                                                        low = c_health - (c_health * .75)
                                                        high = c_health - (c_health * .66)
                                                        fortitude = round(random.randint(int(low), int(high)))
                                                        # Resolve Scaling
                                                        c_resolve_health = round(fortitude + (.5 * c_resolve))
                                                        c_resolve_attack = round(
                                                            (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                        c_resolve_defense = round(
                                                            (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                        
                                                        t_ap_buff = t_ap_buff - 125

                                                        c_stamina = c_stamina + c_resolve
                                                        c_health = c_health + c_resolve_health
                                                        c_attack = round(c_attack + c_resolve_attack)
                                                        c_defense = round(c_defense - c_resolve_defense)
                                                        c_used_resolve = True
                                                        c_pet_used = False

                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Conquerors Haki!")

                                                        turn_total = turn_total + 1
                                                        turn = 2


                                                    elif c_universe == "Demon Slayer": 
                                                        # fortitude or luck is based on health
                                                        fortitude = 0.0
                                                        low = c_health - (c_health * .75)
                                                        high = c_health - (c_health * .66)
                                                        fortitude = round(random.randint(int(low), int(high)))
                                                        # Resolve Scaling
                                                        c_resolve_health = round(fortitude + (.5 * c_resolve))
                                                        c_resolve_attack = round(
                                                            (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                        c_resolve_defense = round(
                                                            (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                        

                                                        c_stamina = c_stamina + c_resolve
                                                        c_health = c_health + c_resolve_health
                                                        c_attack = round(c_attack + c_resolve_attack)
                                                        c_defense = round(c_defense - c_resolve_defense)
                                                        if t_attack > c_attack:
                                                            c_attack = t_attack
                                                        if t_defense > c_defense:
                                                            c_defense = t_defense
                                                        c_used_resolve = True
                                                        c_pet_used = False
                                                        embedVar = discord.Embed(title=f"{c_card} begins Total Concentration Breathing",
                                                                                description=f"**{c_card} says**\n{c_resolve_description}",
                                                                                colour=0xe91e63)
                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Total Concentration Breathing!")
                                                        await button_ctx.defer(ignore=True)
                                                        turn_total = turn_total + 1
                                                        turn = 0

                                                    elif c_universe == "Naruto": 
                                                        # fortitude or luck is based on health
                                                        fortitude = 0.0
                                                        low = c_health - (c_health * .75)
                                                        high = c_health - (c_health * .66)
                                                        fortitude = round(random.randint(int(low), int(high)))
                                                        # Resolve Scaling
                                                        c_resolve_health = round(fortitude + (.5 * c_resolve))
                                                        c_resolve_attack = round(
                                                            (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                        c_resolve_defense = round(
                                                            (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                        

                                                        c_stamina = c_stamina + c_resolve
                                                        c_health = c_health + c_resolve_health
                                                        c_health = c_health + c_naruto_heal_buff
                                                        c_attack = round(c_attack + c_resolve_attack)
                                                        c_defense = round(c_defense - c_resolve_defense)
                                                        c_used_resolve = True
                                                        c_pet_used = False
                                                        embedVar = discord.Embed(title=f"{c_card} Heals from Hashirama Cells",
                                                                                description=f"**{c_card} says**\n{c_resolve_description}",
                                                                                colour=0xe91e63)
                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Hashirama Cells heal you for **{c_naruto_heal_buff}**")
                                                        await button_ctx.defer(ignore=True)
                                                        turn_total = turn_total + 1
                                                        turn = 0



                                                    
                                                    elif c_universe == "Attack On Titan":
                                                        # fortitude or luck is based on health
                                                        fortitude = 0.0
                                                        low = c_health - (c_health * .75)
                                                        high = c_health - (c_health * .66)
                                                        fortitude = round(random.randint(int(low), int(high)))
                                                        # Resolve Scaling
                                                        c_resolve_health = round(fortitude + (.5 * c_resolve))
                                                        c_resolve_attack = round(
                                                            (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                        c_resolve_defense = round(
                                                            (.30 * c_defense) * (c_resolve / (.50 * c_defense)))

                                                        c_stamina = c_stamina + c_resolve
                                                        c_health = c_health + c_resolve_health
                                                        c_attack = round(c_attack + c_resolve_attack)
                                                        c_defense = round(c_defense - c_resolve_defense)
                                                        c_used_resolve = True
                                                        c_pet_used = False
                                                        health_boost = 100 * c_focus_count
                                                        c_health = c_health + health_boost
                                                        embedVar = discord.Embed(title=f"{c_card} Titan Mode",
                                                                                description=f"**{c_card} says**\n{c_resolve_description}",
                                                                                colour=0xe91e63)
                                                        embedVar.add_field(name=f"Transformation Complete",
                                                                        value=f"Health increased by **{health_boost}**!")
                                                        #await button_ctx.send(embed=embedVar)
                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Titan Mode! Health increased by **{health_boost}**!")
                                                        await button_ctx.defer(ignore=True)
                                                        turn_total = turn_total + 1
                                                        turn = 3
                                                    elif c_universe == "Bleach":  # Bleach Trait
                                                        # fortitude or luck is based on health
                                                        fortitude = 0.0
                                                        low = c_health - (c_health * .75)
                                                        high = c_health - (c_health * .66)
                                                        fortitude = round(random.randint(int(low), int(high)))
                                                        # Resolve Scaling
                                                        c_resolve_health = round(fortitude + (.5 * c_resolve))
                                                        c_resolve_attack = round(
                                                            (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                        c_resolve_defense = round(
                                                            (.30 * c_defense) * (c_resolve / (.50 * c_defense)))

                                                        c_stamina = c_stamina + c_resolve
                                                        c_health = c_health + c_resolve_health
                                                        c_attack = round((c_attack + (2 * c_resolve_attack))*2 )
                                                        c_defense = round(c_defense - c_resolve_defense)
                                                        # if c_defense >= 120:
                                                        # c_defense = 120
                                                        c_used_resolve = True
                                                        c_pet_used = False
                                                        embedVar = discord.Embed(
                                                            title=f"{c_card} STRENGTHENED RESOLVE :zap:",
                                                            description=f"**{c_card} says**\n{c_resolve_description}",
                                                            colour=0xe91e63)
                                                        embedVar.add_field(name=f"Transformation: Bankai",
                                                                        value="Gain double Attack on Resolve.")
                                                        #await button_ctx.send(embed=embedVar)
                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Bankai!")
                                                        await button_ctx.defer(ignore=True)
                                                        turn_total = turn_total + 1
                                                        turn = 3
                                                    elif c_universe == "God Of War":  # God Of War Trait
                                                        # fortitude or luck is based on health
                                                        fortitude = 0.0
                                                        low = c_health - (c_health * .75)
                                                        high = c_health - (c_health * .66)
                                                        fortitude = round(random.randint(int(low), int(high)))
                                                        # Resolve Scaling
                                                        c_resolve_health = round(fortitude + (.5 * o_resolve))
                                                        c_resolve_attack = round(
                                                            (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                        c_resolve_defense = round(
                                                            (.30 * c_defense) * (c_resolve / (.50 * c_defense)))

                                                        c_stamina = c_stamina + c_resolve
                                                        c_attack = round(c_attack + c_resolve_attack)
                                                        c_defense = round(c_defense - c_resolve_defense)
                                                        c_used_resolve = True
                                                        c_pet_used = False

                                                        if c_gow_resolve:
                                                            c_health = c_max_health
                                                            previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Ascension!")
                                                        elif not c_gow_resolve:
                                                            c_health = round(c_health + (c_max_health / 2))
                                                            c_used_resolve = False
                                                            c_gow_resolve = True
                                                            
                                                            previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Crushed Blood Orb: Health Refill")
                                                        

                                                        embedVar = discord.Embed(
                                                            title=f"{c_card} STRENGTHENED RESOLVE :zap:",
                                                            description=f"**{c_card} says**\n{c_resolve_description}",
                                                            colour=0xe91e63)
                                                        embedVar.add_field(name=f"Transformation: Ascension",
                                                                        value="On Resolve Refill Health.")
                                                        #await button_ctx.send(embed=embedVar)
                                                        
                                                        await button_ctx.defer(ignore=True)
                                                        turn_total = turn_total + 1
                                                        turn = 3
                                                    elif c_universe == "Fate":  # Fate Trait
                                                        # fortitude or luck is based on health
                                                        fortitude = 0.0
                                                        low = c_health - (c_health * .75)
                                                        high = c_health - (c_health * .66)
                                                        fortitude = round(random.randint(int(low), int(high)))
                                                        # Resolve Scaling
                                                        c_resolve_health = round(fortitude + (.5 * c_resolve))
                                                        c_resolve_attack = round(
                                                            (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                        c_resolve_defense = round(
                                                            (.30 * c_defense) * (c_resolve / (.50 * c_defense)))

                                                        c_stamina = c_stamina + c_resolve
                                                        c_health = c_health + c_resolve_health
                                                        c_attack = round(c_attack + c_resolve_attack)
                                                        c_defense = round(c_defense - c_resolve_defense)

                                                        dmg = damage_cal(mode,c_card_tier, c_talisman_dict, cap3, t_for_c_opponent_affinities, ultimate_attack_name, cmove3_element, c_universe, c_card, c_3, c_attack, c_defense,
                                                                        t_defense, c_stamina, c_enhancer_used, c_health,
                                                                        t_health, t_stamina, c_max_health, t_attack,
                                                                        c_special_move_description, turn_total,
                                                                        ccard_lvl_ap_buff, None)
                                                        t_health = t_health - dmg['DMG']
                                                        embedVar = discord.Embed(
                                                            title=f"{c_card} STRENGTHENED RESOLVE :zap:\n\n{dmg['MESSAGE']}",
                                                            description=f"**{c_card} says**\n{c_resolve_description}",
                                                            colour=0xe91e63)
                                                        embedVar.add_field(name=f"Transformation: Command Seal",
                                                                        value="On Resolve, Strike with Ultimate, then Focus.")
                                                        #await button_ctx.send(embed=embedVar)
                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Command Seal! {dmg['MESSAGE']}")
                                                        await button_ctx.defer(ignore=True)
                                                        # c_stamina = 0
                                                        c_used_resolve = True
                                                        c_pet_used = False
                                                        turn_total = turn_total + 1
                                                        turn = 3
                                                    elif c_universe == "Kanto Region" or c_universe == "Johto Region" or c_universe == "Hoenn Region" or c_universe == "Sinnoh Region" or c_universe == "Kalos Region" or c_universe == "Unova Region" or c_universe == "Alola Region" or c_universe == "Galar Region":  # Pokemon Resolves
                                                        # fortitude or luck is based on health
                                                        fortitude = 0.0
                                                        low = c_health - (c_health * .75)
                                                        high = c_health - (c_health * .66)
                                                        fortitude = round(random.randint(int(low), int(high)))
                                                        # Resolve Scaling
                                                        c_resolve_health = round(fortitude + (.5 * o_resolve))
                                                        c_resolve_attack = round(
                                                            (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                        c_resolve_defense = round(
                                                            (.30 * c_defense) * (c_resolve / (.50 * c_defense)))

                                                        c_stamina = c_stamina + c_resolve
                                                        c_health = c_health + c_resolve_health
                                                        c_attack = round(c_attack + c_resolve_attack)
                                                        c_defense = round(c_defense) * 2
                                                        c_used_resolve = True
                                                        c_pet_used = False
                                                        embedVar = discord.Embed(
                                                            title=f"{c_card} STRENGTHENED RESOLVE :zap:",
                                                            description=f"**{c_card} says**\n{c_resolve_description}",
                                                            colour=0xe91e63)
                                                        embedVar.add_field(name=f"Transformation: Evolution",
                                                                        value="When you Resolve your Defense doubles")
                                                        await button_ctx.defer(ignore=True)
                                                        #await button_ctx.send(embed=embedVar)
                                                        if turn_total >= 50:
                                                            c_max_health = c_max_health + 1000
                                                            c_health = c_health + 1000
                                                            previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Gigantomax Evolution!!! Gained **1000** HP!!!")
                                                        elif turn_total >= 30:
                                                            c_max_health = c_max_health + 500
                                                            c_health = c_health + 500
                                                            previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Mega Evolution!! Gained **500** HP!")
                                                        else:
                                                            previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Evolution!")
                                                        turn_total = turn_total + 1
                                                        turn = 3
                                                    else:  # Standard Resolve
                                                        # fortitude or luck is based on health
                                                        fortitude = 0.0
                                                        low = c_health - (c_health * .75)
                                                        high = c_health - (c_health * .66)
                                                        fortitude = round(random.randint(int(low), int(high)))
                                                        # Resolve Scaling
                                                        c_resolve_health = round(fortitude + (.5 * c_resolve))
                                                        c_resolve_attack = round(
                                                            (.30 * c_defense) * (c_resolve / (.50 * c_defense)))
                                                        c_resolve_defense = round(
                                                            (.30 * c_defense) * (c_resolve / (.50 * c_defense)))

                                                        c_stamina = c_stamina + c_resolve
                                                        c_health = c_health + c_resolve_health
                                                        c_attack = round(c_attack + c_resolve_attack)
                                                        c_defense = round(c_defense - c_resolve_defense)
                                                        c_used_resolve = True
                                                        c_pet_used = False
                                                        if c_universe == "League Of Legends":
                                                            t_health = t_health - (60 * (c_focus_count + t_focus_count))
                                                            embedVar = discord.Embed(title=f"{c_card} PENTA KILL!",
                                                                                    description=f"**{c_card} says**\n{c_resolve_description}",
                                                                                    colour=0xe91e63)
                                                            embedVar.add_field(name=f"Nexus Destroyed",
                                                                            value=f"**{c_card}** dealt **{(60 * (c_focus_count + t_focus_count))}** damage.")
                                                            previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Resolved: Pentakill! Dealing {(60 * (c_focus_count + t_focus_count))} damage.")
                                                            await button_ctx.defer(ignore=True)
                                                        elif c_universe == "Souls":
                                                            previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Phase 2: Enhanced Moveset!")
                                                            await button_ctx.defer(ignore=True)
                                                        else:
                                                            embedVar = discord.Embed(
                                                                title=f"{c_card} STRENGTHENED RESOLVE :zap:",
                                                                description=f"**{c_card} says**\n{c_resolve_description}",
                                                                colour=0xe91e63)
                                                            embedVar.add_field(name=f"Transformation",
                                                                            value="All stats & stamina greatly increased")
                                                            previous_moves.append(f"(**{turn_total}**) ⚡ **{c_card}** Resolved!")
                                                        #await button_ctx.send(embed=embedVar)
                                                        await button_ctx.defer(ignore=True)
                                                        turn_total = turn_total + 1
                                                        turn = 3
                                                else:
                                                    previous_moves.append(f"(**{turn_total}**) {c_card} cannot resolve!")
                                                    await button_ctx.defer(ignore=True)
                                            elif button_ctx.custom_id == "6":
                                                # Resolve Check and Calculation
                                                if c_used_resolve and c_used_focus and not c_pet_used:
                                                    c_enhancer_used = True
                                                    dmg = damage_cal(mode,c_card_tier, c_talisman_dict, cap1, t_for_c_opponent_affinities, basic_attack_name, cmove1_element, c_universe, c_card, cpet_move, c_attack, c_defense,
                                                                    t_defense, c_stamina, c_enhancer_used, c_health,
                                                                    t_health, t_stamina, c_max_health, t_attack,
                                                                    c_special_move_description, turn_total,
                                                                    ccard_lvl_ap_buff, None)
                                                    c_enhancer_used = False
                                                    c_pet_used = True
                                                    cpet_dmg = dmg['DMG']
                                                    cpet_type = dmg['ENHANCED_TYPE']
                                                    if dmg['CAN_USE_MOVE']:
                                                        if cpet_type == 'ATK':
                                                            c_attack = round(c_attack + dmg['DMG'])
                                                        elif cpet_type == 'DEF':
                                                            c_defense = round(c_defense + dmg['DMG'])
                                                        elif cpet_type == 'STAM':
                                                            c_stamina = round(c_stamina + dmg['DMG'])
                                                        elif cpet_type == 'HLT':
                                                            c_health = round(c_health + dmg['DMG'])
                                                        elif cpet_type == 'LIFE':
                                                            c_health = round(c_health + dmg['DMG'])
                                                            t_health = round(t_health - dmg['DMG'])
                                                        elif cpet_type == 'DRAIN':
                                                            c_stamina = round(c_stamina + dmg['DMG'])
                                                            t_stamina = round(t_stamina - dmg['DMG'])
                                                        elif cpet_type == 'FLOG':
                                                            c_attack = round(c_attack + dmg['DMG'])
                                                            t_attack = round(t_attack - dmg['DMG'])
                                                        elif cpet_type == 'WITHER':
                                                            c_defense = round(c_defense + dmg['DMG'])
                                                            t_defense = round(t_defense - dmg['DMG'])
                                                        elif cpet_type == 'RAGE':
                                                            c_defense = round(c_defense - dmg['DMG'])
                                                            c_ap_buff = round(c_ap_buff + dmg['DMG'])
                                                        elif cpet_type == 'BRACE':
                                                            c_ap_buff = round(c_ap_buff + dmg['DMG'])
                                                            c_attack = round(c_attack - dmg['DMG'])
                                                        elif cpet_type == 'BZRK':
                                                            c_health = round(c_health - dmg['DMG'])
                                                            c_attack = round(c_attack + dmg['DMG'])
                                                        elif cpet_type == 'CRYSTAL':
                                                            c_health = round(c_health - dmg['DMG'])
                                                            c_defense = round(c_defense + dmg['DMG'])
                                                        elif cpet_type == 'GROWTH':
                                                            c_max_health = round(c_max_health - (c_max_health * .10))
                                                            c_defense = round(c_defense + dmg['DMG'])
                                                            c_attack = round(c_attack + dmg['DMG'])
                                                            c_ap_buff = round(c_ap_buff + dmg['DMG'])
                                                        elif cpet_type == 'STANCE':
                                                            tempattack = dmg['DMG']
                                                            c_attack = c_defense
                                                            c_defense = tempattack
                                                        elif cpet_type == 'CONFUSE':
                                                            tempattack = dmg['DMG']
                                                            t_attack = t_defense
                                                            t_defense = tempattack
                                                        elif cpet_type == 'BLINK':
                                                            c_stamina = round(c_stamina - dmg['DMG'])
                                                            t_stamina = round(t_stamina + dmg['DMG'])
                                                        elif cpet_type == 'SLOW':
                                                            tempstam = round(t_stamina + dmg['DMG'])
                                                            c_stamina = round(c_stamina - dmg['DMG'])
                                                            t_stamina = c_stamina
                                                            c_stamina = tempstam
                                                        elif cpet_type == 'HASTE':
                                                            tempstam = round(t_stamina - dmg['DMG'])
                                                            c_stamina = round(c_stamina + dmg['DMG'])
                                                            t_stamina = c_stamina
                                                            c_stamina = tempstam
                                                        elif cpet_type == 'SOULCHAIN':
                                                            c_stamina = round(dmg['DMG'])
                                                            t_stamina = c_stamina
                                                        elif cpet_type == 'GAMBLE':
                                                            c_health = round(dmg['DMG'])
                                                            t_health = c_health
                                                        elif cpet_type == 'FEAR':
                                                            if c_universe != "Chainsawman":
                                                                c_max_health = round(c_max_health - (c_max_health * .10))
                                                            t_defense = round(t_defense - dmg['DMG'])
                                                            t_attack= round(t_attack - dmg['DMG'])
                                                            t_ap_buff = round(t_ap_buff - dmg['DMG'])

                                                        elif cpet_type == 'WAVE':
                                                            t_health = round(t_health - dmg['DMG'])
                                                        elif cpet_type == 'BLAST':
                                                            if dmg['DMG'] >= 300:
                                                                dmg['DMG'] = 300
                                                            t_health = round(t_health - dmg['DMG'])
                                                        elif cpet_type == 'CREATION':
                                                            c_max_health = round(c_max_health + dmg['DMG'])
                                                            c_health = round(c_health + dmg['DMG'])
                                                        elif cpet_type == 'DESTRUCTION':
                                                            if dmg['DMG'] >= 300:
                                                                dmg['DMG'] = 300
                                                            t_max_health = round(t_max_health - dmg['DMG'])
                                                            if t_max_health <=1:
                                                                t_max_health = 1

                                                        #c_stamina = c_stamina - int(dmg['STAMINA_USED'])
                                                        if c_universe == "Persona":
                                                            petdmg = damage_cal(mode,c_card_tier, c_talisman_dict, cap1, t_for_c_opponent_affinities, basic_attack_name, cmove1_element, c_universe, c_card, c_1, c_attack,
                                                                                c_defense, t_defense, c_stamina,
                                                                                c_enhancer_used, c_health, t_health,
                                                                                t_stamina, c_max_health, t_attack,
                                                                                c_special_move_description, turn_total,
                                                                                ccard_lvl_ap_buff, None)

                                                            t_health = t_health - petdmg['DMG']

                                                            embedVar = discord.Embed(
                                                                title=f"**PERSONA!**\n{cpet_name} was summoned from {c_card}'s soul dealing **{petdmg['DMG']}** damage!!",
                                                                colour=0xe91e63)
                                                            await battle_msg.delete(delay=None)
                                                            if not operformance:
                                                                csummon_file = showsummon(cpet_image, cpet_name, dmg['MESSAGE'], cpet_lvl, cpet_bond)
                                                                embedVar.set_image(url="attachment://pet.png")
                                                                await asyncio.sleep(2)
                                                                battle_msg = await private_channel.send(embed=embedVar, file=csummon_file)
                                                                await asyncio.sleep(2)
                                                                await battle_msg.delete(delay=None)
                                                            
                                                            #await button_ctx.send(embed=embedVar, file=csummon_file)
                                                            previous_moves.append(f"(**{turn_total}**) **Persona!** 🩸 : **{cpet_name}** was summoned from **{c_card}'s** soul dealing **{petdmg['DMG']}** damage!\n**{t_card}** summon disabled!")
                                                            t_pet_used = True
                                                            await button_ctx.defer(ignore=True)
                                                            
                                                        else:
                                                            embedVar = discord.Embed(
                                                                title=f"{c_card} Summoned 🧬 {cpet_name}",
                                                                colour=0xe91e63)

                                                            #await private_channel.send(embed=embedVar)
                                                            await battle_msg.delete(delay=None)
                                                            if not operformance: #FindMeT
                                                                csummon_file = showsummon(cpet_image, cpet_name, dmg['MESSAGE'], cpet_lvl, cpet_bond)
                                                                embedVar.set_image(url="attachment://pet.png")
                                                                await asyncio.sleep(2)
                                                                battle_msg = await private_channel.send(embed=embedVar, file=csummon_file)
                                                                await asyncio.sleep(2)
                                                                await battle_msg.delete(delay=None)
                                                            previous_moves.append(f"(**{turn_total}**) **{c_card}** Summoned 🧬 **{cpet_name}**: {dmg['MESSAGE']}")
                                                            
                                                            await button_ctx.defer(ignore=True)
                                                            
                                                        turn = 2
                                                    else:
                                                        previous_moves.append(f"(**{turn_total}**) {c_card} Could not summon 🧬 **{cpet_name}**. Needs rest")
                                                        await button_ctx.defer(ignore=True)
                                                        turn = 2
                                                else:
                                                    previous_moves.append(f"(**{turn_total}**) {c_card} Could not summon 🧬 **{cpet_name}**. Needs rest")
                                                    await button_ctx.defer(ignore=True)
                                            elif button_ctx.custom_id == "7":
                                                c_enhancer_used = True
                                                dmg = damage_cal(mode,c_card_tier, c_talisman_dict, cap1, t_for_c_opponent_affinities, basic_attack_name, cmove1_element, c_universe, c_card, c_enhancer, c_attack, c_defense,
                                                                o_defense, c_stamina, c_enhancer_used, c_health, o_health,
                                                                player1_card.stamina, c_max_health, o_attack,
                                                                c_special_move_description, turn_total, ccard_lvl_ap_buff, None)
                                                c_enhancer_used = False
                                                cdmg = dmg['DMG']
                                                cenh_type = dmg['ENHANCED_TYPE']
                                                if dmg['CAN_USE_MOVE']:
                                                    if cenh_type == 'ATK':
                                                        o_attack = round(o_attack + dmg['DMG'])
                                                    elif cenh_type == 'DEF':
                                                        o_defense = round(o_defense + dmg['DMG'])
                                                    elif cenh_type == 'STAM':
                                                        player1_card.stamina = round(player1_card.stamina + dmg['DMG'])
                                                    elif cenh_type == 'HLT':
                                                        o_health = round(o_health + dmg['DMG'])
                                                    elif cenh_type == 'LIFE':
                                                        o_health = round(o_health + dmg['DMG'])
                                                        c_health = round(c_health - dmg['DMG'])
                                                    elif cenh_type == 'DRAIN':
                                                        player1_card.stamina = round(player1_card.stamina + dmg['DMG'])
                                                        c_stamina = round(c_stamina - dmg['DMG'])
                                                    elif cenh_type == 'FLOG':
                                                        o_attack = round(o_attack + dmg['DMG'])
                                                        t_attack = round(t_attack - dmg['DMG'])
                                                    elif cenh_type == 'WITHER':
                                                        o_defense = round(o_defense + dmg['DMG'])
                                                        t_defense = round(t_defense - dmg['DMG'])
                                                    elif cenh_type == 'RAGE':
                                                        o_defense = round(o_defense - dmg['DMG'])
                                                        o_ap_buff = round(o_ap_buff + dmg['DMG'])
                                                    elif cenh_type == 'BRACE':
                                                        o_ap_buff = round(o_ap_buff + dmg['DMG'])
                                                        o_attack = round(o_attack - dmg['DMG'])
                                                    elif cenh_type == 'BZRK':
                                                        o_health = round(o_health - dmg['DMG'])
                                                        o_attack = round(o_attack + dmg['DMG'])
                                                    elif cenh_type == 'CRYSTAL':
                                                        o_health = round(o_health - dmg['DMG'])
                                                        o_defense = round(o_defense + dmg['DMG'])
                                                    elif cenh_type == 'GROWTH':
                                                        o_max_health = round(o_max_health - (o_max_health * .10))
                                                        o_defense = round(o_defense + dmg['DMG'])
                                                        o_attack= round(o_attack + dmg['DMG'])
                                                        o_ap_buff = round(o_ap_buff + dmg['DMG'])
                                                    elif cenh_type == 'STANCE':
                                                        tempattack = dmg['DMG']
                                                        o_attack = o_defense
                                                        o_defense = tempattack
                                                    elif cenh_type == 'CONFUSE':
                                                        tempattack = dmg['DMG']
                                                        c_attack = c_defense
                                                        c_defense = tempattack
                                                    elif cenh_type == 'BLINK':
                                                        player1_card.stamina = round(player1_card.stamina - dmg['DMG'])
                                                        c_stamina = round(c_stamina + dmg['DMG'])
                                                    elif cenh_type == 'SLOW':
                                                        tempstam = round(c_stamina + dmg['DMG'])
                                                        player1_card.stamina = round(player1_card.stamina - dmg['DMG'])
                                                        c_stamina = player1_card.stamina
                                                        player1_card.stamina = tempstam
                                                    elif cenh_type == 'HASTE':
                                                        tempstam = round(c_stamina - dmg['DMG'])
                                                        player1_card.stamina = round(player1_card.stamina + dmg['DMG'])
                                                        c_stamina = player1_card.stamina
                                                        player1_card.stamina = tempstam
                                                    elif cenh_type == 'SOULCHAIN':
                                                        player1_card.stamina = round(dmg['DMG'])
                                                        c_stamina = player1_card.stamina
                                                    elif cenh_type == 'GAMBLE':
                                                        o_health = round(dmg['DMG'])
                                                        c_health = o_health
                                                    elif cenh_type == 'FEAR':
                                                        if o_universe != "Chainsawman":
                                                            o_max_health = round(o_max_health - (o_max_health * .10))
                                                        c_defense = round(c_defense - dmg['DMG'])
                                                        c_attack = round(c_attack - dmg['DMG'])
                                                        c_ap_buff = round(c_ap_buff - dmg['DMG'])
                                                    elif cenh_type == 'WAVE':
                                                        t_health = round(t_health - dmg['DMG'])
                                                    elif cenh_type == 'BLAST':
                                                        if dmg['DMG'] >= 700:
                                                            dmg['DMG'] = 700

                                                        t_health = round(t_health - dmg['DMG'])
                                                    elif cenh_type == 'CREATION':
                                                        o_max_health = round(o_max_health + dmg['DMG'])
                                                        o_health = round(o_health + dmg['DMG'])
                                                    elif enh_type == 'DESTRUCTION':
                                                        t_max_health = round(t_max_health - dmg['DMG'])
                                                        # c_max_health = round(c_max_health - dmg['DMG'])
                                                        if t_max_health <=1:
                                                            t_max_health = 1
                                                        # if c_max_health <=1:
                                                        #     c_max_health = 1
                                                    
                                                    if enh_type in Stamina_Enhancer_Check or enh_type in Time_Enhancer_Check or enh_type in Control_Enhancer_Check:
                                                        c_stamina = c_stamina
                                                    else:
                                                        c_stamina = c_stamina - int(dmg['STAMINA_USED'])

                                                    embedVar = discord.Embed(
                                                        title=f"**{c_card}** ASSISTED **{o_card}** 👥",
                                                        colour=0xe91e63)
                                                    embedVar.add_field(name=f"{c_card} used {cmove_enhanced_text}!",
                                                                    value=f"Enhanced {cenh_type}")
                                                    #await button_ctx.send(embed=embedVar)
                                                    previous_moves.append(f'(**{turn_total}**) **{c_card}** used {cmove_enhanced_text}:👥 Assisting **{o_card}**')
                                                    await button_ctx.defer(ignore=True)
                                                    turn_total = turn_total + 1
                                                    turn = 3
                                                else:
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** not enough Stamina to use this move")
                                                    await button_ctx.defer(ignore=True)
                                                    turn = 2
                                                    await button_ctx.defer(ignore=True)
                                            elif button_ctx.custom_id == "0":
                                                if c_stamina >= 20:
                                                    if c_universe == "Attack On Titan":
                                                        previous_moves.append(f"(**{turn_total}**) **Rally** 🩸 ! **{c_card}** Increased Max Health ❤️")
                                                        c_max_health = round(c_max_health + 100)
                                                        c_health = c_health + 100

                                                    if c_universe == "Bleach":
                                                        dmg = damage_cal(mode,c_card_tier, c_talisman_dict, cap1, t_for_c_opponent_affinities, basic_attack_name, cmove1_element, c_universe, c_card, c_1, c_attack, c_defense, t_defense,
                                                                    c_stamina, c_enhancer_used, c_health, t_health, t_stamina,
                                                                    c_max_health, t_attack, c_special_move_description,
                                                                    turn_total, ccard_lvl_ap_buff, None)
                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}** Exerted their 🩸 Spiritual Pressure - {dmg['MESSAGE']}")
                                                        
                                                        if c_universe == "One Piece" and (c_card_tier in low_tier_cards or c_card_tier in mid_tier_cards or c_card_tier in high_tier_cards):
                                                            if c_focus_count == 0:
                                                                dmg['DMG'] = dmg['DMG'] * .6
                                                        
                                                        if dmg['REPEL']:
                                                            c_health = c_health - dmg['DMG']
                                                        elif dmg['ABSORB']:
                                                            t_health = t_health + dmg['DMG']
                                                        elif dmg['ELEMENT'] == water_element:
                                                            if cmove1_element == water_element:
                                                                c_basic_water_buff = c_basic_water_buff + 40
                                                            if cmove2_element == water_element:
                                                                c_special_water_buff = c_special_water_buff + 40
                                                            if cmove3_element == water_element:
                                                                c_ultimate_water_buff = c_ultimate_water_buff + 40
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == ice_element:
                                                            c_ice_counter = c_ice_counter + 1
                                                            if c_ice_counter == 2:
                                                                c_freeze_enh = True
                                                                c_ice_counter = 0
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == time_element:
                                                            if c_stamina <= 80:
                                                                c_stamina = 0
                                                            player3_card.used_defend = True
                                                            c_defense = round(c_defense * 2)
                                                            previous_moves.append(f"**{c_card}** Blocked 🛡️")
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == bleed_element:
                                                            c_bleed_counter = c_bleed_counter + 1
                                                            if c_bleed_counter == 3:
                                                                c_bleed_hit = True
                                                                c_bleed_counter = 0
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == recoil_element:
                                                            c_health = c_health - (dmg['DMG'] * .60)
                                                            if c_health <= 0:
                                                                c_health = 1
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == earth_element:
                                                            c_defense = c_defense + (dmg['DMG'] * .25)
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == death_element:
                                                            t_max_health = t_max_health - (dmg['DMG'] * .20)
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == light_element:
                                                            c_stamina = round(c_stamina + (dmg['STAMINA_USED'] / 2))
                                                            c_attack = c_attack + (dmg['DMG'] * .20)
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == dark_element:
                                                            t_stamina = t_stamina - 15
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == life_element:
                                                            c_health = c_health + (dmg['DMG'] * .20)
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == psychic_element:
                                                            t_defense = t_defense - (dmg['DMG'] * .15)
                                                            t_attack = t_attack - (dmg['DMG'] * .15)
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == fire_element:
                                                            c_burn_dmg = c_burn_dmg + round(dmg['DMG'] * .25)
                                                            t_health = t_health - dmg['DMG']


                                                        elif dmg['ELEMENT'] == electric_element:
                                                            c_shock_buff = c_shock_buff +  (dmg['DMG'] * .15)
                                                            t_health = t_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == poison_element:
                                                            if c_poison_dmg <= 600:
                                                                c_poison_dmg = c_poison_dmg + 30
                                                            t_health = t_health - dmg['DMG']
                                                            
                                                        elif dmg['ELEMENT'] == gravity_element:
                                                            c_gravity_hit = True
                                                            t_health = t_health - dmg['DMG']
                                                            t_defense = t_defense - (dmg['DMG'] * .25)
                                                            
                                                        else:
                                                            t_health = t_health - dmg['DMG']

                                                    player3_card.used_defend = True
                                                    c_stamina = c_stamina - 20
                                                    c_defense = round(c_defense * 2)
                                                    embedVar = discord.Embed(
                                                        title=f"**{c_card}** Defended 🛡️ {o_card}",
                                                        colour=0xe91e63)

                                                    #await button_ctx.send(embed=embedVar)
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}**: Defended 🛡️ **{o_card}**")
                                                    turn_total = turn_total + 1
                                                    turn = 3
                                                    await button_ctx.defer(ignore=True)
                                                else:
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** is too tired to block.")
                                                    turn = 2
                                                    await button_ctx.defer(ignore=True)

                                            if button_ctx.custom_id != "5" and button_ctx.custom_id != "6" and button_ctx.custom_id != "7" and button_ctx.custom_id != "0" and button_ctx.custom_id != "q" and button_ctx.custom_id in options:
                                                # If you have enough stamina for move, use it

                                                if dmg['CAN_USE_MOVE']:
                                                    if dmg['ENHANCE']:
                                                        enh_type = dmg['ENHANCED_TYPE']

                                                        if enh_type == 'ATK':
                                                            c_attack = round(c_attack + dmg['DMG'])
                                                        elif enh_type == 'DEF':
                                                            c_defense = round(c_defense + dmg['DMG'])
                                                        elif enh_type == 'STAM':
                                                            c_stamina = round(c_stamina + dmg['DMG'])
                                                        elif enh_type == 'HLT':
                                                            c_health = round(c_health + dmg['DMG'])
                                                        elif enh_type == 'LIFE':
                                                            c_health = round(c_health + dmg['DMG'])
                                                            t_health = round(t_health - dmg['DMG'])
                                                        elif enh_type == 'DRAIN':
                                                            c_stamina = round(c_stamina + dmg['DMG'])
                                                            t_stamina = round(t_stamina - dmg['DMG'])
                                                        elif enh_type == 'FLOG':
                                                            c_attack = round(c_attack + dmg['DMG'])
                                                            t_attack = round(t_attack - dmg['DMG'])
                                                        elif enh_type == 'WITHER':
                                                            c_defense = round(c_defense + dmg['DMG'])
                                                            t_defense = round(t_defense - dmg['DMG'])
                                                        elif enh_type == 'RAGE':
                                                            c_defense = round(c_defense - dmg['DMG'])
                                                            c_ap_buff = round(c_ap_buff + dmg['DMG'])
                                                        elif enh_type == 'BRACE':
                                                            c_ap_buff = round(c_ap_buff + dmg['DMG'])
                                                            c_attack = round(c_attack - dmg['DMG'])
                                                        elif enh_type == 'BZRK':
                                                            c_health = round(c_health - dmg['DMG'])
                                                            c_attack = round(c_attack + dmg['DMG'])
                                                        elif enh_type == 'CRYSTAL':
                                                            c_health = round(c_health - dmg['DMG'])
                                                            c_defense = round(c_defense + dmg['DMG'])
                                                        elif enh_type == 'GROWTH':
                                                            c_max_health = round(c_max_health - (c_max_health * .10))
                                                            c_defense = round(c_defense + dmg['DMG'])
                                                            c_attack = round(c_attack + dmg['DMG'])
                                                            c_ap_buff = round(c_ap_buff + dmg['DMG'])
                                                        elif enh_type == 'STANCE':
                                                            tempattack = dmg['DMG']
                                                            c_attack = c_defense
                                                            c_defense = tempattack
                                                        elif enh_type == 'CONFUSE':
                                                            tempattack = dmg['DMG']
                                                            t_attack = t_defense
                                                            t_defense = tempattack
                                                        elif enh_type == 'BLINK':
                                                            c_stamina = round(c_stamina - dmg['DMG'])
                                                            t_stamina = round(t_stamina + dmg['DMG'])
                                                        elif enh_type == 'SLOW':
                                                            tempstam = round(t_stamina + dmg['DMG'])
                                                            c_stamina = round(c_stamina - dmg['DMG'])
                                                            t_stamina = c_stamina
                                                            c_stamina = tempstam
                                                        elif enh_type == 'HASTE':
                                                            tempstam = round(t_stamina - dmg['DMG'])
                                                            c_stamina = round(c_stamina + dmg['DMG'])
                                                            t_stamina = c_stamina
                                                            c_stamina = tempstam
                                                        elif enh_type == 'SOULCHAIN':
                                                            c_stamina = round(dmg['DMG'])
                                                            t_stamina = c_stamina
                                                        elif enh_type == 'GAMBLE':
                                                            if mode in D_modes:
                                                                t_health = round(dmg['DMG']) * 2
                                                                c_health = round(dmg['DMG'])
                                                            elif mode in B_modes:
                                                                t_health = round(dmg['DMG']) * 4
                                                                c_health = round(dmg['DMG'])
                                                            else:
                                                                t_health = round(dmg['DMG'])
                                                                c_health = round(dmg['DMG'])
                                                        elif enh_type == 'FEAR':
                                                            if c_universe != "Chainsawman":
                                                                c_max_health = round(c_max_health - (c_max_health * .10))
                                                            t_defense = round(t_defense - dmg['DMG'])
                                                            t_attack= round(t_attack - dmg['DMG'])
                                                            t_ap_buff = round(t_ap_buff - dmg['DMG'])
                                                        elif enh_type == 'WAVE':
                                                            t_health = round(t_health - dmg['DMG'])
                                                        elif enh_type == 'BLAST':
                                                            if dmg['DMG'] >= 700:
                                                                dmg['DMG'] = 700

                                                            t_health = round(t_health - dmg['DMG'])
                                                        elif enh_type == 'CREATION':
                                                            c_max_health = round(c_max_health + dmg['DMG'])
                                                            c_health = round(c_health + dmg['DMG'])
                                                        elif enh_type == 'DESTRUCTION':
                                                            t_max_health = round(t_max_health - dmg['DMG'])
                                                            # c_max_health = round(c_max_health - dmg['DMG'])
                                                            if t_max_health <=1:
                                                                t_max_health = 1
                                                            # if c_max_health <=1:
                                                            #     c_max_health = 1
                                                        
                                                        if enh_type in Stamina_Enhancer_Check or enh_type in Time_Enhancer_Check or enh_type in Control_Enhancer_Check:
                                                            c_stamina = c_stamina
                                                        else:
                                                            c_stamina = c_stamina - int(dmg['STAMINA_USED'])

                                                        embedVar = discord.Embed(title=f"{dmg['MESSAGE']}",
                                                                                colour=embed_color_c)
                                                        #await button_ctx.send(embed=embedVar)
                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}**: 🦠 {dmg['MESSAGE']}")
                                                        turn_total = turn_total + 1
                                                        turn = 3
                                                        await button_ctx.defer(ignore=True)
                                                    elif dmg['DMG'] == 0:
                                                        c_stamina = c_stamina - int(dmg['STAMINA_USED'])

                                                        embedVar = discord.Embed(title=f"{dmg['MESSAGE']}", colour=embed_color_c)
                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}**: {dmg['MESSAGE']}")
                                                        if carm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                            carm_barrier_active=False
                                                            embedVar.add_field(name=f"{c_card}'s **Barrier** Disabled!", value =f"*Maximize **Barriers** with your Enhancer!*")
                                                            previous_moves.append(f"(**{turn_total}**) **{c_card}**'s 💠 Barrier Disabled!")
                                                        #await button_ctx.send(embed=embedVar)
                                                        turn_total = turn_total + 1
                                                        turn = 3
                                                        await button_ctx.defer(ignore=True)
                                                    else:
                                                        if t_universe == "Naruto" and t_stamina < 10:
                                                            t_stored_damage = round(dmg['DMG'])
                                                            t_naruto_heal_buff = t_naruto_heal_buff + t_stored_damage
                                                            t_health = t_health 
                                                            embedVar = discord.Embed(title=f"{t_card}: Substitution Jutsu", description=f"{c_card} strikes a log", colour=0xe91e63)
                                                            previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸: Substitution Jutsu")
                                                            if not t_used_resolve:
                                                                previous_moves.append(f"(**{turn_total}**) 🩸**{t_stored_damage}** Hasirama Cells stored. 🩸**{t_naruto_heal_buff}** total stored.")
                                                            if carm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                carm_barrier_active=False
                                                                embedVar.add_field(name=f"{c_card}'s **Barrier** Disabled!", value =f"*Maximize **Barriers** with your Enhancer!*")
                                                                previous_moves.append(f"(**{turn_total}**) **{c_card}**'s 💠 Barrier Disabled!")
                                                            #await private_channel.send(embed=embedVar)
                                                            await button_ctx.defer(ignore=True)
                                                        elif tarm_shield_active and dmg['ELEMENT'] != dark_element:
                                                            if dmg['ELEMENT'] == poison_element: #Poison Update
                                                                if c_poison_dmg <= 600:
                                                                    c_poison_dmg = o_poison_dmg + 30
                                                         
                                                            if tshield_value > 0:
                                                                tshield_value = tshield_value -dmg['DMG']
                                                                t_health = t_health 
                                                                if tshield_value <=0:
                                                                    embedVar = discord.Embed(title=f"{t_card}'s' **Shield** Shattered!", description=f"{c_card} breaks the **Shield**!", colour=0xe91e63)
                                                                    previous_moves.append(f"(**{turn_total}**) **{t_card}'s** 🌐 Shield Shattered!")
                                                                    if carm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                        carm_barrier_active=False
                                                                        embedVar.add_field(name=f"{c_card}'s **Barrier** Disabled!", value =f"*Maximize **Barriers** with your Enhancer!*")
                                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}**'s 💠 Barrier Disabled!")
                                                                    #await private_channel.send(embed=embedVar)
                                                                    tarm_shield_active = False
                                                                    await button_ctx.defer(ignore=True)
                                                                else:
                                                                    embedVar = discord.Embed(title=f"{t_card} Activates **Shield** 🌐", description=f"**{c_card}** strikes the Shield 🌐\n**{tshield_value} Shield** Left!", colour=0xe91e63)
                                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** strikes **{t_card}**'s Shield 🌐\n**{tshield_value} Shield** Left!")
                                                                    if carm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                        carm_barrier_active=False
                                                                        embedVar.add_field(name=f"{c_card}'s **Barrier** Disabled!", value =f"*Maximize **Barriers** with your Enhancer!*")
                                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}**'s 💠 Barrier Disabled!")
                                                                    #await private_channel.send(embed=embedVar)
                                                                    await button_ctx.defer(ignore=True)

                                                        elif tarm_barrier_active and dmg['ELEMENT'] != psychic_element :
                                                            if tbarrier_count >1:
                                                                t_health = t_health 
                                                                embedVar = discord.Embed(title=f"{t_card} Activates **Barrier** 💠", description=f"{c_card}'s attack **Nullified**!\n **{tbarrier_count - 1} Barriers** remain!", colour=0xe91e63)
                                                                previous_moves.append(f"(**{turn_total}**) **{t_card}** Activates Barrier 💠  {c_card}'s attack **Nullified**!\n💠 {tbarrier_count - 1} **Barriers** remain!")
                                                                if carm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                    carm_barrier_active=False
                                                                    embedVar.add_field(name=f"{c_card}'s **Barrier** Disabled!", value =f"*Maximize **Barriers** with your Enhancer!*")
                                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}**'s 💠 Barrier Disabled!")
                                                                #await private_channel.send(embed=embedVar)
                                                                # await button_ctx.defer(ignore=True)
                                                                tbarrier_count = tbarrier_count - 1
                                                            elif tbarrier_count==1:
                                                                embedVar = discord.Embed(title=f"{t_card}'s **Barrier** Broken!", description=f"{c_card} destroys the **Barrier**", colour=0xe91e63)
                                                                previous_moves.append(f"(**{turn_total}**) **{t_card}**'s Barrier Broken!")
                                                                tbarrier_count = tbarrier_count - 1
                                                                if carm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                    carm_barrier_active=False
                                                                    embedVar.add_field(name=f"{c_card}'s **Barrier** Disabled!", value =f"*Maximize **Barriers** with your Enhancer!*")
                                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}**'s 💠 Barrier Disabled!")
                                                                #await private_channel.send(embed=embedVar)
                                                                # await button_ctx.defer(ignore=True)
                                                                tarm_barrier_active = False
                                                        elif tarm_parry_active and dmg['ELEMENT'] != earth_element:
                                                            if tparry_count > 1:
                                                                t_health = t_health
                                                                tparry_damage = round(dmg['DMG'])
                                                                t_health = round(t_health - (tparry_damage * .75))
                                                                c_health = round(c_health - (tparry_damage * .40))
                                                                tparry_count = tparry_count - 1
                                                                embedVar = discord.Embed(title=f"{t_card} Activates **Parry** 🔄", description=f"{c_card} takes {round(tparry_damage * .40)}! DMG\n **{tparry_count} Parries** to go!!", colour=0xe91e63)
                                                                previous_moves.append(f"(**{turn_total}**) **{t_card}** Activates Parry 🔄 after **{round(tparry_damage * .75)}** dmg dealt: {c_card} takes {round(tparry_damage * .40)}! DMG\n **{tparry_count}  Parries** to go!!")
                                                                if carm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                    carm_barrier_active=False
                                                                    embedVar.add_field(name=f"{c_card}'s **Barrier** Disabled!", value =f"*Maximize **Barriers** with your Enhancer!*")
                                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}**'s 💠 Barrier Disabled!")
                                                                #await private_channel.send(embed=embedVar)
                                                                # await button_ctx.defer(ignore=True)
                                                                
                                                            elif tparry_count==1:
                                                                t_health = t_health
                                                                tparry_damage = round(dmg['DMG'])
                                                                t_health = round(t_health - (tparry_damage * .75))
                                                                c_health = round(c_health - (tparry_damage * .40))
                                                                embedVar = discord.Embed(title=f"{t_card} **Parry** Penetrated!!", description=f"{c_card} takes {round(tparry_damage * .40)}! DMG and breaks the **Parry**", colour=0xe91e63)
                                                                previous_moves.append(f"(**{turn_total}**) **{t_card}** Parry Penetrated! **{c_card}** takes **{round(tparry_damage * .40)}**! DMG and breaks the **Parry**")
                                                                tparry_count = tparry_count - 1
                                                                if carm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                    carm_barrier_active=False
                                                                    embedVar.add_field(name=f"{c_card}'s **Barrier** Disabled!", value =f"*Maximize **Barriers** with your Enhancer!*")
                                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}**'s 💠 Barrier Disabled!")
                                                                #await private_channel.send(embed=embedVar)
                                                                tarm_parry_active = False
                                                                # await button_ctx.defer(ignore=True)
                                                        else:

                                                            if c_universe == "One Piece" and (c_card_tier in low_tier_cards or c_card_tier in mid_tier_cards or c_card_tier in high_tier_cards):
                                                                if c_focus_count == 0:
                                                                    dmg['DMG'] = dmg['DMG'] * .6


                                                            if dmg['REPEL']:
                                                                c_health = c_health - int(dmg['DMG'])
                                                            elif dmg['ABSORB']:
                                                                t_health = t_health + int(dmg['DMG'])
                                                            elif dmg['ELEMENT'] == water_element:
                                                                if cmove1_element == water_element:
                                                                    c_basic_water_buff = c_basic_water_buff + 40
                                                                if cmove2_element == water_element:
                                                                    c_special_water_buff = c_special_water_buff + 40
                                                                if cmove3_element == water_element:
                                                                    c_ultimate_water_buff = c_ultimate_water_buff + 40
                                                                t_health = t_health - dmg['DMG']

                                                            elif dmg['ELEMENT'] == ice_element:
                                                                c_ice_counter = c_ice_counter + 1
                                                                if c_ice_counter == 2:
                                                                    c_freeze_enh = True
                                                                    c_ice_counter = 0
                                                                t_health = t_health - dmg['DMG']

                                                            elif dmg['ELEMENT'] == time_element:
                                                                if c_stamina <= 80:
                                                                    c_stamina = 0
                                                                player3_card.used_defend = True
                                                                c_defense = round(c_defense * 2)
                                                                previous_moves.append(f"**{c_card}** Blocked 🛡️")

                                                                t_health = t_health - dmg['DMG']

                                                            elif dmg['ELEMENT'] == bleed_element:
                                                                c_bleed_counter = c_bleed_counter + 1
                                                                if c_bleed_counter == 3:
                                                                    c_bleed_hit = True
                                                                    c_bleed_counter = 0
                                                                t_health = t_health - dmg['DMG']

                                                            elif dmg['ELEMENT'] == recoil_element:
                                                                c_health = c_health - (dmg['DMG'] * .60)
                                                                if c_health <= 0:
                                                                    c_health = 1
                                                                t_health = t_health - dmg['DMG']

                                                            elif dmg['ELEMENT'] == earth_element:
                                                                c_defense = c_defense + (dmg['DMG'] * .25)
                                                                t_health = t_health - dmg['DMG']

                                                            elif dmg['ELEMENT'] == death_element:
                                                                t_max_health = t_max_health - (dmg['DMG'] * .20)
                                                                t_health = t_health - dmg['DMG']

                                                            elif dmg['ELEMENT'] == light_element:
                                                                c_stamina = round(c_stamina + (dmg['STAMINA_USED'] / 2))
                                                                c_attack = c_attack + (dmg['DMG'] * .20)
                                                                t_health = t_health - dmg['DMG']

                                                            elif dmg['ELEMENT'] == dark_element:
                                                                t_stamina = t_stamina - 15
                                                                t_health = t_health - dmg['DMG']

                                                            elif dmg['ELEMENT'] == life_element:
                                                                c_health = c_health + (dmg['DMG'] * .20)
                                                                t_health = t_health - dmg['DMG']

                                                            elif dmg['ELEMENT'] == psychic_element:
                                                                t_defense = t_defense - (dmg['DMG'] * .15)
                                                                t_attack = t_attack - (dmg['DMG'] * .15)
                                                                t_health = t_health - dmg['DMG']

                                                            elif dmg['ELEMENT'] == fire_element:
                                                                c_burn_dmg = c_burn_dmg + round(dmg['DMG'] * .25)
                                                                t_health = t_health - dmg['DMG']


                                                            elif dmg['ELEMENT'] == electric_element:
                                                                c_shock_buff = c_shock_buff +  (dmg['DMG'] * .15)
                                                                t_health = t_health - dmg['DMG']

                                                            elif dmg['ELEMENT'] == poison_element:
                                                                if c_poison_dmg <= 600:
                                                                    c_poison_dmg = c_poison_dmg + 30
                                                                t_health = t_health - dmg['DMG']
                                                                
                                                            elif dmg['ELEMENT'] == gravity_element:
                                                                c_gravity_hit = True
                                                                t_health = t_health - dmg['DMG']
                                                                t_defense = t_defense - (dmg['DMG'] * .25)
                                                        
                                                            else:
                                                                t_health = t_health - dmg['DMG']


                                                            embedVar = discord.Embed(title=f"{dmg['MESSAGE']}", colour=0xe91e63)
                                                            previous_moves.append(f"(**{turn_total}**) **{c_card}**: {dmg['MESSAGE']}")
                                                            if carm_siphon_active:
                                                                siphon_damage = (dmg['DMG'] * .15) + csiphon_value
                                                                c_health = round(c_health + siphon_damage)
                                                                if c_health >= c_max_health:
                                                                    c_health = c_max_health
                                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}**: 💉 Siphoned **Full Health!**")
                                                                else:
                                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}**: 💉 Siphoned **{round(siphon_damage)}** Health!")
                                                                await button_ctx.defer(ignore=True)
                                                            if carm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                carm_barrier_active=False
                                                                embedVar.add_field(name=f"{c_card}'s **Barrier** Disabled!", value =f"*Maximize **Barriers** with your Enhancer!*")
                                                                previous_moves.append(f"(**{turn_total}**) **{c_card}**'s 💠 Barrier Disabled!")
                                                            #await private_channel.send(embed=embedVar)
                                                            # await button_ctx.defer(ignore=True)
                                                        if t_health <= 0:
                                                            if t_final_stand==True:
                                                                if t_universe == "Dragon Ball Z":
                                                                    embedVar = discord.Embed(title=f"{t_card}'s LAST STAND", description=f"{t_card} FINDS RESOLVE", colour=0xe91e63)
                                                                    embedVar.add_field(name=f"**{t_card}** Resolved and continues to fight", value="All stats & stamina increased")
                                                                    previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 Transformation: Last Stand!!!")
                                                                    if carm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                        carm_barrier_active=False
                                                                        embedVar.add_field(name=f"{c_card}'s **Barrier** Disabled!", value =f"*Maximize **Barriers** with your Enhancer!*")
                                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}**'s 💠 Barrier Disabled!")
                                                                    #await private_channel.send(embed=embedVar)
                                                                    t_health = int(.75 * (t_attack + t_defense))
                                                                    
                                                                    t_used_resolve = True
                                                                    t_used_focus = True
                                                                    t_final_stand = False
                                                                    c_stamina = c_stamina - dmg['STAMINA_USED']
                                                                    turn_total = turn_total + 1
                                                                    turn = 3
                                                                    # await button_ctx.defer(ignore=True)
                                                            else:
                                                                t_health = 0
                                                                c_stamina = c_stamina - dmg['STAMINA_USED']
                                                                turn_total = turn_total + 1
                                                                #await button_ctx.defer(ignore=True)
                                                        else:
                                                            c_stamina = c_stamina - dmg['STAMINA_USED']
                                                            turn_total = turn_total + 1
                                                            turn = 3
                                                            #await button_ctx.defer(ignore=True)
                                                else:
                                                    emessage = m.NOT_ENOUGH_STAMINA
                                                    embedVar = discord.Embed(title=emessage,
                                                                            description=f"Use abilities to Increase `STAM` or enter `FOCUS STATE`!",
                                                                            colour=0xe91e63)
                                                    #await button_ctx.send(embed=embedVar)
                                                    previous_moves.append(f"(**{turn_total}**) **{c_card}** not enough Stamina to use this move") 
                                                    turn = 2
                                                    # await button_ctx.defer(ignore=True)
                                        except asyncio.TimeoutError:
                                            await battle_msg.delete()
                                            #await battle_msg.edit(components=[])
                                            await save_spot(self, ctx, universe, mode, currentopponent)
                                            await ctx.author.send(f"{ctx.author.mention} your game timed out. Your channel has been closed but your spot in the tales has been saved where you last left off.")
                                            await ctx.send(f"{ctx.author.mention} your game timed out. Your channel has been closed but your spot in the tales has been saved where you last left off.")
                                            # await discord.TextChannel.delete(private_channel, reason=None)
                                            previous_moves.append(f"(**{turn_total}**) 💨 **{c_card}** Fled...")
                                            c_health = 0
                                            o_health = 0
                                        except Exception as ex:
                                            trace = []
                                            tb = ex.__traceback__
                                            while tb is not None:
                                                trace.append({
                                                    "filename": tb.tb_frame.f_code.co_filename,
                                                    "name": tb.tb_frame.f_code.co_name,
                                                    "lineno": tb.tb_lineno
                                                })
                                                tb = tb.tb_next
                                            print(str({
                                                'type': type(ex).__name__,
                                                'message': str(ex),
                                                'trace': trace
                                            }))
                                            guild = self.bot.get_guild(main.guild_id)
                                            channel = guild.get_channel(main.guild_channel)
                                            await channel.send(f"'PLAYER': **{str(ctx.author)}**, 'GUILD': **{str(ctx.author.guild)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")

                            # Opponent Turn Start
                            elif turn == 3:
                                if t_universe == "YuYu Hakusho":
                                    t_attack = t_attack + t_stamina

                                if c_bleed_hit:
                                    c_bleed_hit = False
                                    bleed_dmg = 10 * turn_total
                                    t_health = t_health - bleed_dmg
                                    previous_moves.append(f"🩸 **{t_card}** shredded for **{round(bleed_dmg)}** bleed dmg...")
                                    if t_health <= 0:
                                        continue

                                if c_burn_dmg > 3:
                                    t_health = t_health - c_burn_dmg
                                    previous_moves.append(f"🔥 **{t_card}** burned for **{round(c_burn_dmg)}** dmg...")
                                    if t_health <= 0:
                                        continue

                                if c_freeze_enh:
                                    previous_moves.append(f"❄️ **{t_card}** has been frozen for a turn...")
                                    turn_total = turn_total + 1
                                    turn = 0
                                    continue
                                if c_poison_dmg:
                                    t_health = t_health - c_poison_dmg
                                    previous_moves.append(f"🧪 **{t_card}** poisoned for **{c_poison_dmg}** dmg...")
                                    if t_health <= 0:
                                        continue

                                c_burn_dmg = round(c_burn_dmg / 2)
                                t_freeze_enh = False
                                
                                if o_bleed_hit:
                                    o_bleed_hit = False
                                    bleed_dmg = 10 * turn_total
                                    t_health = t_health - bleed_dmg
                                    previous_moves.append(f"🩸 **{t_card}** shredded for **{round(bleed_dmg)}** bleed dmg...")
                                    if t_health <= 0:
                                        continue

                                if o_burn_dmg > 3:
                                    t_health = t_health - o_burn_dmg
                                    previous_moves.append(f"🔥 **{t_card}** burned for **{round(o_burn_dmg)}** dmg...")
                                    if t_health <= 0:
                                        continue

                                if o_freeze_enh:
                                    previous_moves.append(f"❄️ **{t_card}** has been frozen for a turn...")
                                    turn_total = turn_total + 1
                                    if _battle._is_co_op:
                                        turn = 2
                                        continue
                                    else:
                                        turn = 0
                                        continue
                                if o_poison_dmg:
                                    t_health = t_health - o_poison_dmg
                                    previous_moves.append(f"🧪 **{t_card}** poisoned for **{o_poison_dmg}** dmg...")
                                    if t_health <= 0:
                                        continue

                                if t_gravity_hit:
                                    t_gravity_hit = False
                      
                                o_burn_dmg = round(o_burn_dmg / 2)
                                t_freeze_enh = False


                                if t_title_passive_type:
                                    if t_title_passive_type == "HLT":
                                        if t_max_health > t_health:
                                            t_health = round(t_health + ((t_title_passive_value / 100) * t_health))

                                    if t_title_passive_type == "LIFE":
                                        if t_max_health > t_health:
                                            c_health = c_health - ((t_title_passive_value / 100) * c_health)
                                            t_health = t_health + ((t_title_passive_value / 100) * c_health)
                                    if t_title_passive_type == "ATK":
                                        t_attack = t_attack + t_title_passive_value
                                    if t_title_passive_type == "DEF":
                                        t_defense = t_defense + t_title_passive_value
                                    if t_title_passive_type == "STAM":
                                        if t_stamina > 15:
                                            t_stamina = t_stamina + t_title_passive_value
                                    if t_title_passive_type == "DRAIN":
                                        if t_stamina > 15:
                                            t_stamina = t_stamina + t_title_passive_value
                                            c_stamina = c_stamina - t_title_passive_value
                                    if t_title_passive_type == "FLOG":
                                        t_attack = t_attack + ((t_title_passive_value / 100) * c_attack)
                                        c_attack = c_attack - ((t_title_passive_value / 100) * c_attack)
                                    if t_title_passive_type == "WITHER":
                                        t_defense = t_defense + ((t_title_passive_value / 100) * c_defense)
                                        c_defense = c_defense - ((t_title_passive_value / 100) * c_defense)
                                    if t_title_passive_type == "RAGE":
                                        t_defense = round(t_defense - ((t_title_passive_value / 100) * t_defense))
                                        t_ap_buff = round(t_ap_buff + ((t_title_passive_value / 100) * t_defense))
                                    if t_title_passive_type == "BRACE":
                                        t_ap_buff = round(t_ap_buff + ((t_title_passive_value / 100) * t_attack))
                                        t_attack = round(t_attack - ((t_title_passive_value / 100) * t_attack))
                                    if t_title_passive_type == "BZRK":
                                        t_health = round(t_health - ((t_title_passive_value / 100) * t_health))
                                        t_attack = round(t_attack + ((t_title_passive_value / 100) * t_health))
                                    if t_title_passive_type == "CRYSTAL":
                                        t_health = round(t_health - ((t_title_passive_value / 100) * t_health))
                                        t_defense = round(t_defense + ((t_title_passive_value / 100) * t_health))
                                    if t_title_passive_type == "FEAR":
                                        if t_universe != "Chainsawman":
                                            t_max_health = t_max_health - (t_max_health * .03)
                                        c_defense = c_defense - t_title_passive_value
                                        c_attack = c_attack - t_title_passive_value
                                        c_ap_buff = c_ap_buff - t_title_passive_value
                                    if t_title_passive_type == "GROWTH":
                                        t_max_health = t_max_health - (t_max_health * .03)
                                        t_defense = t_defense + t_title_passive_value
                                        t_attack = t_attack + t_title_passive_value
                                        t_ap_buff = t_ap_buff + t_title_passive_value
                                    if t_title_passive_type == "SLOW":
                                        if turn_total != 0:
                                            turn_total = turn_total - 1
                                    if t_title_passive_type == "HASTE":
                                        turn_total = turn_total + 1
                                    if t_title_passive_type == "STANCE":
                                        tempattack = t_attack + t_title_passive_value
                                        t_attack = t_defense
                                        t_defense = tempattack
                                    if t_title_passive_type == "CONFUSE":
                                        tempattack = c_attack - t_title_passive_value
                                        c_attack = c_defense
                                        c_defense = tempattack
                                    if t_title_passive_type == "BLINK":
                                        if c_stamina >= 10:
                                            c_stamina = c_stamina + t_title_passive_value
                                        t_stamina = t_stamina - t_title_passive_value
                                    if t_title_passive_type == "CREATION":
                                        t_max_health = round(round(t_max_health + ((t_title_passive_value / 100) * t_max_health)))
                                    if t_title_passive_type == "DESTRUCTION":
                                        c_max_health = round(c_max_health - ((t_title_passive_value / 100) * c_max_health))
                                    if t_title_passive_type == "BLAST":
                                        c_health = round(c_health - t_title_passive_value)
                                    if t_title_passive_type == "WAVE":
                                        if turn_total % 10 == 0:
                                            c_health = round(c_health - 100)

                                if t_card_passive_type:
                                    t_value_for_passive = t_card_tier * .5
                                    t_flat_for_passive = 10 * (t_card_tier * .5)
                                    t_stam_for_passive = 5 * (t_card_tier * .5)
                                    if t_card_passive_type == "HLT":
                                        if t_max_health > t_health:
                                            t_health = round(round(t_health + ((t_value_for_passive / 100) * t_health)))
                                    if t_card_passive_type == "CREATION":
                                        t_max_health = round(round(t_max_health + ((t_value_for_passive / 100) * t_max_health)))
                                    if t_card_passive_type == "DESTRUCTION":
                                        c_max_health = round(round(c_max_health - ((t_value_for_passive / 100) * c_max_health)))

                                    if t_card_passive_type == "LIFE":
                                        if t_max_health > t_health:
                                            c_health = round(c_health - ((t_value_for_passive / 100) * c_health))
                                            t_health = round(t_health + ((t_value_for_passive / 100) * c_health))
                                    if t_card_passive_type == "ATK":
                                        t_attack = round(t_attack + ((t_value_for_passive / 100) * t_attack))
                                    if t_card_passive_type == "DEF":
                                        t_defense = round(t_defense + ((t_value_for_passive / 100) * t_defense))
                                    if t_card_passive_type == "STAM":
                                        if t_stamina > 15:
                                            t_stamina = t_stamina + t_stam_for_passive
                                    if t_card_passive_type == "DRAIN":
                                        if t_stamina > 15:
                                            c_stamina = c_stamina - t_stam_for_passive
                                            t_stamina = t_stamina + t_stam_for_passive
                                    if t_card_passive_type == "FLOG":
                                        c_attack = round(c_attack - ((t_value_for_passive / 100) * c_attack))
                                        t_attack = round(t_attack + ((t_value_for_passive / 100) * c_attack))
                                    if t_card_passive_type == "WITHER":
                                        c_defense = round(c_defense - ((t_value_for_passive / 100) * c_defense))
                                        t_defense = round(t_defense + ((t_value_for_passive / 100) * c_defense))
                                    if t_card_passive_type == "RAGE":
                                        t_defense = round(t_defense - ((t_value_for_passive / 100) * t_defense))
                                        c_ap_buff = round(c_ap_buff + ((t_value_for_passive / 100) * t_defense))
                                    if t_card_passive_type == "BRACE":
                                        c_ap_buff = round(c_ap_buff + ((t_value_for_passive / 100) * t_attack))
                                        t_attack = round(t_attack - ((t_value_for_passive / 100) * t_attack))
                                    if t_card_passive_type == "BZRK":
                                        t_health = round(t_health - ((t_value_for_passive / 100) * t_health))
                                        t_attack = round(t_attack + ((t_value_for_passive / 100) * t_health))
                                    if t_card_passive_type == "CRYSTAL":
                                        t_health = round(t_health - ((t_value_for_passive / 100) * t_health))
                                        t_defense = round(t_defense + ((t_value_for_passive / 100) * t_health))
                                    if t_card_passive_type == "FEAR":
                                        if t_universe != "Chainsawman":
                                            t_max_health = t_max_health - (t_max_health * .03)
                                        c_defense = c_defense - t_flat_for_passive
                                        c_attack = c_attack - t_flat_for_passive
                                        c_ap_buff = c_ap_buff - t_flat_for_passive
                                    if t_card_passive_type == "GROWTH":
                                        t_max_health = t_max_health - (t_max_health * .03)
                                        t_defense = t_defense + t_flat_for_passive
                                        t_attack = t_attack + t_flat_for_passive
                                        t_ap_buff = t_ap_buff + t_flat_for_passive
                                    if t_card_passive_type == "SLOW":
                                        if turn_total != 0:
                                            turn_total = turn_total - 1
                                    if t_card_passive_type == "HASTE":
                                        turn_total = turn_total + 1
                                    if t_card_passive_type == "STANCE":
                                        tempattack = t_attack + t_flat_for_passive
                                        t_attack = t_defense
                                        t_defense = tempattack
                                    if t_card_passive_type == "CONFUSE":
                                        tempattack = c_attack - t_flat_for_passive
                                        c_attack = c_defense
                                        c_defense = tempattack
                                    if t_card_passive_type == "BLINK":
                                        t_stamina = t_stamina - t_stam_for_passive
                                        if c_stamina >=10:
                                            c_stamina = c_stamina + t_stam_for_passive
                                    if t_card_passive_type == "BLAST":
                                        c_health = round(c_health - t_value_for_passive)
                                    if t_card_passive_type == "WAVE":
                                        if turn_total % 10 == 0:
                                            c_health = round(c_health - 100)
                        

                                # await asyncio.sleep(2)
                                if t_block_used == True:
                                    t_block_used = False
                                    t_defense = int(t_defense / 2)
                                if t_attack <= 25:
                                    t_attack = 25
                                if t_defense <= 30:
                                    t_defense = 30
                                if t_attack >= 9999:
                                    t_attack = 9999
                                if t_defense >= 9999:
                                    t_defense = 9999
                                if t_health >= t_max_health:
                                    t_health = t_max_health
                                # o_pet_used = True
                                if t_health <= (t_max_health * .25):
                                    embed_color_t = 0xe74c3c
                                    if t_chainsaw == True:
                                        if t_atk_chainsaw == False:
                                            t_atk_chainsaw = True
                                            t_chainsaw = False
                                            t_defense = t_defense * 2
                                            t_attack = t_attack * 2
                                            t_max_health = t_max_health * 2
                                            embedVar = discord.Embed(title=f"{t_card}'s Devilization",
                                                                    description=f"**{t_card}** Doubles Stats",
                                                                    colour=0xe91e63)
                                            previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸's Devilization")

                                elif t_health <= (t_max_health * .50):
                                    embed_color_t = 0xe67e22
                                    if t_chainsaw == True:
                                        if t_atk_chainsaw == False:
                                            t_atk_chainsaw = True
                                            t_chainsaw = False
                                            t_defense = t_defense * 2
                                            t_attack = t_attack * 2
                                            t_max_health = t_max_health * 2
                                            embedVar = discord.Embed(title=f"{t_card}'s Devilization",
                                                                    description=f"**{t_card}** Doubles Stats",
                                                                    colour=0xe91e63)
                                            previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸's Devilization")
                                elif t_health <= (t_max_health * .75):
                                    embed_color_t = 0xf1c40f
                                else:
                                    embed_color_t = 0x2ecc71

                                # Focus
                                if t_stamina < 10:
                                    t_pet_used = False
                                    t_focus_count = t_focus_count + 1
                                    fortitude = round(t_health * .1)
                                    if fortitude <= 50:
                                        fortitude = 50

                                    t_stamina = t_focus
                                    t_healthcalc = round(fortitude)
                                    t_attackcalc = round(fortitude * (t_card_tier / 10))
                                    t_defensecalc = round(fortitude * (t_card_tier / 10))
                                    t_newhealth = 0
                                    healmessage = ""
                                    messagenumber = 0

                                    if t_universe == "One Piece" and (t_card_tier in mid_tier_cards or t_card_tier in high_tier_cards):
                                        t_attackcalc = t_attackcalc + t_attackcalc
                                        t_defensecalc = t_defensecalc + t_defensecalc

                                    if t_title_passive_type:
                                        if t_title_passive_type == "GAMBLE":
                                            t_healthcalc = t_title_passive_value
                                        if t_title_passive_type == "SOULCHAIN":
                                            player1_card.stamina = t_title_passive_value
                                            t_stamina = t_title_passive_value
                                            if _battle._is_co_op:
                                                c_stmina = t_title_passive_value
                                        if t_title_passive_type == "BLAST":
                                            o_health = o_health - (t_title_passive_value * turn_total)
                                            if _battle._is_co_op:
                                                    c_health = c_health - (t_title_passive_value * turn_total)


                                    if o_title_passive_type:
                                        if o_title_passive_type == "GAMBLE":
                                            t_healthcalc = o_title_passive_value
                                    
                                    if _battle._is_co_op:
                                        if c_title_passive_type:
                                            if c_title_passive_type == "GAMBLE":
                                                t_healthcalc = c_title_passive_value


                                    if t_universe == "Crown Rift Madness":
                                        healmessage = "yet inner **Madness** drags on..."
                                        messagenumber = 3
                                    else:
                                        if t_health <= t_max_health:
                                            t_newhealth = t_health + t_healthcalc
                                            if t_newhealth > t_max_health:
                                                healmessage = f"recovered!"
                                                messagenumber = 1
                                                t_health = t_max_health
                                            else:
                                                healmessage = f"stopped the bleeding..."
                                                messagenumber = 2
                                                t_health = t_newhealth
                                        else:
                                            healmessage = f"hasn't been touched..."
                                            messagenumber = 0
                                    if mode in B_modes:
                                        embedVar = discord.Embed(title=f"**{t_card}** Enters Focus State",
                                                                description=f"{t_powerup}", colour=0xe91e63)
                                        embedVar.add_field(name=f"A great aura starts to envelop **{t_card}** ",
                                                        value=f"{t_aura}")
                                        embedVar.set_footer(text=f"{t_card} Says: 'Now, are you ready for a real fight?'")
                                        await ctx.send(embed=embedVar)
                                        previous_moves.append(f"(**{turn_total}**) 🌀 **{t_card}** Focused and Says: 'Now, are you ready for a real fight?'")
                                    else:
                                        previous_moves.append(f"(**{turn_total}**) 🌀 **{t_card}** focused and {healmessage}")
                                    if not t_used_resolve:
                                        t_attack = t_attack + t_attackcalc
                                        t_defense = t_defense + t_defensecalc
                                    t_used_focus = True

                                    if not t_used_resolve and t_used_focus and t_universe == "Digimon":  # Digimon Universal Trait
                                        # fortitude or luck is based on health
                                        fortitude = 0.0
                                        low = t_health - (t_health * .75)
                                        high = t_health - (t_health * .66)
                                        fortitude = round(random.randint(int(low), int(high)))
                                        # Resolve Scaling
                                        t_resolve_health = round(fortitude + (.5 * t_resolve))
                                        t_resolve_attack = round((.30 * t_defense) * (t_resolve / (.50 * t_defense)))
                                        t_resolve_defense = round((.30 * t_defense) * (t_resolve / (.50 * t_defense)))

                                        t_stamina = t_stamina + t_resolve
                                        t_health = t_health + t_resolve_health
                                        t_attack = round(t_attack + t_resolve_attack)
                                        t_defense = round(t_defense - t_resolve_defense)
                                        t_used_resolve = True
                                        t_attack = round(t_attack * 1.5)
                                        t_defense = round(t_defense * 1.5)

                                        embedVar = discord.Embed(title=f"{t_card} STRENGTHENED RESOLVE :zap:",
                                                                description=f"**{t_card} says**\n{t_resolve_description}",
                                                                colour=0xe91e63)
                                        embedVar.add_field(name=f"Transformation: Digivolve", value="On Focus you Resolve.")
                                        #await private_channel.send(embed=embedVar)
                                        if turn_total <=5:
                                            t_attack = round(t_attack * 2)
                                            t_defense = round(t_defense * 2 )
                                            t_health = t_health + 500
                                            t_max_health = t_max_health + 500
                                            previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 Transformation: Mega Digivolution!!!")
                                        else:
                                            previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 Transformation: Digivolve")


                                    elif t_universe == "League Of Legends":
                                        embedVar = discord.Embed(title=f"Turret Shot hits {c_card} for **{60 + turn_total}** Damage 💥",
                                                                colour=0xe91e63)
                                        #await private_channel.send(embed=embedVar)
                                        previous_moves.append(f"(**{turn_total}**) 🩸 Turret Shot hits **{c_card}** for **{60 + turn_total}** Damage 💥")
                                        c_health = round(c_health - (60 + turn_total))

                                    elif t_universe == "Dragon Ball Z":
                                        t_health = t_health + c_stamina
                                        previous_moves.append(f"(**{turn_total}**) 🩸 Saiyan Spirit... You heal for **{c_stamina + turn_total}** ❤️")


                                    elif t_universe == "Solo Leveling":
                                        embedVar = discord.Embed(
                                            title=f"Ruler's Authority... {c_card} loses **{30 + turn_total}** 🛡️ 🔻",
                                            colour=0xe91e63)
                                        #await private_channel.send(embed=embedVar)
                                        previous_moves.append(f"(**{turn_total}**) 🩸 Ruler's Authority... {c_card} loses **{30 + turn_total}** 🛡️ 🔻")
                                        c_defense = round(c_defense - (30 + turn_total))

                                    elif t_universe == "Black Clover":
                                        embedVar = discord.Embed(title=f"Mana Zone! **{t_card}** Increased Stamina 🌀",
                                                                colour=0xe91e63)
                                        #await private_channel.send(embed=embedVar)
                                        previous_moves.append(f"(**{turn_total}**) 🩸 Mana Zone! **{t_card}** Increased AP & Stamina 🌀")
                                        t_stamina = 100
                                        tcard_lvl_ap_buff = tcard_lvl_ap_buff + 30

                                    elif t_universe == "Death Note":
                                        if turn_total >= 100:
                                            embedVar = discord.Embed(title=f"{o_card}'s' Scheduled Death 📓",
                                                                    description=f"**{t_card} says**\n**Delete**",
                                                                    colour=0xe91e63)
                                            embedVar.add_field(name=f"{o_card} had a heart attack and died",
                                                            value=f"Death....")
                                            #await private_channel.send(embed=embedVar)
                                            previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 had a heart attack and died")
                                            c_health = 0

                                    if c_universe == "One Punch Man" and t_universe != "Death Note":
                                        embedVar = discord.Embed(
                                            title=f"Hero Reinforcements! {c_card}  Increased Health & Max Health ❤️",
                                            colour=0xe91e63)
                                        #await private_channel.send(embed=embedVar)
                                        previous_moves.append(f"(**{turn_total}**) 🩸 Hero Reinforcements! **{c_card}**  Increased Health & Max Health ❤️")
                                        c_health = round(c_health + 100)
                                        c_max_health = round(c_max_health + 100)

                                    elif c_universe == "7ds":
                                        embedVar = discord.Embed(
                                            title=f"Power Of Friendship! 🧬 Summon Rested {c_card} Increased Stamina 🌀", colour=0xe91e63)
                                        #await private_channel.send(embed=embedVar)
                                        previous_moves.append(f"(**{turn_total}**) 🩸 Power Of Friendship! 🧬 **{cpet_name}** Rested, **{c_card}** Increased Stamina 🌀")
                                        c_stamina = c_stamina + 60
                                        c_pet_used = False

                                    elif c_universe == "Souls":
                                        embedVar = discord.Embed(
                                            title=f"Combo Recognition! {c_card} Increased Attack by **{60 + turn_total}** 🔺 ",
                                            colour=0xe91e63)
                                        #await private_channel.send(embed=embedVar)
                                        previous_moves.append(f"(**{turn_total}**) 🩸 Combo Recognition! **{c_card}** Increased Attack by **{60 + turn_total}** 🔺")
                                        c_attack = round(c_attack + (60 + turn_total))

                                    else:
                                        turn_total = turn_total + 1
                                        if t_universe != "Crown Rift Madness":
                                            turn = 0
                                        else:
                                            turn = 3
                                    turn_total = turn_total + 1
                                    if t_universe != "Crown Rift Madness":
                                        turn = 0
                                    else:
                                        turn = 3
                                else:
                                    # UNIVERSE CARD
                                    tap1 = list(t_1.values())[0] + tcard_lvl_ap_buff + corruption_ap_buff + t_shock_buff + t_basic_water_buff + t_ap_buff
                                    tap2 = list(t_2.values())[0] + tcard_lvl_ap_buff + corruption_ap_buff + t_shock_buff + t_special_water_buff + t_ap_buff
                                    tap3 = list(t_3.values())[0] + tcard_lvl_ap_buff + tdemon_slayer_buff + corruption_ap_buff + t_shock_buff + t_ultimate_water_buff + t_ap_buff
                                    tenh1 = list(t_enhancer.values())[0]
                                    tenh_name = list(t_enhancer.values())[2]
                                    tpet_enh_name = list(tpet_move.values())[2]
                                    tpet_msg_on_resolve = ""

                                    if tap1 < 150:
                                        tap1 = 150
                                    if tap2 < 150:
                                        tap2 = 150            
                                    if tap3 < 150:
                                        tap3 = 150

                                    # UNIVERSE CARD
                                    if t_universe == "Souls" and t_used_resolve:
                                        player_2_card = showcard("battle", t, tarm,t_max_health, t_health, t_max_stamina, t_stamina,
                                                            t_used_resolve, ttitle, t_used_focus, t_attack, t_defense,
                                                            turn_total, tap2, tap3, tap3, tenh1, tenh_name, tcard_lvl, c_defense)
                                    else:
                                        player_2_card = showcard("battle", t, tarm,t_max_health, t_health, t_max_stamina, t_stamina,
                                                                t_used_resolve, ttitle, t_used_focus, t_attack, t_defense,
                                                                turn_total, tap1, tap2, tap3, tenh1, tenh_name, tcard_lvl, c_defense)
                                                            

                                    if t_universe == "Solo Leveling" and not t_swapped:
                                        if temp_carm_shield_active and not carm_shield_active:
                                            if tarm_shield_active:
                                                tshield_value = tshield_value + temp_cshield_value
                                                previous_moves.append(f"(**{turn_total}**) (**{turn_total}**) **{t_card}** 🩸 **ARISE!** *{carm_name}* is now yours")
                                                t_swapped = True
                                            elif not tarm_shield_active:
                                                tarm_shield_active = True
                                                tshield_value = temp_cshield_value
                                                previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 **ARISE!** *{carm_name}* is now yours")
                                                t_swapped = True
                                        elif temp_carm_barrier_active and not carm_barrier_active:
                                            if tarm_barrier_active:
                                                tbarrier_count = tbarrier_count + temp_cbarrier_count
                                                previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 **ARISE!** *{carm_name}* is now yours")
                                                t_swapped = True
                                            elif not tarm_barrier_active:
                                                tarm_barrier_active = True
                                                tbarrier_count = temp_cbarrier_count
                                                previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 **ARISE!** *{carm_name}* is now yours")
                                                t_swapped = True
                                        elif temp_carm_parry_active and not carm_parry_active:
                                            if tarm_parry_active:
                                                tparry_count = tparry_count + temp_cparry_count
                                                previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 **ARISE!** *{carm_name}* is now yours")
                                                t_swapped = True
                                            elif not tarm_parry_active:
                                                tarm_parry_active = True
                                                tparry_count = temp_cparry_count
                                                previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 **ARISE!** *{carm_name}* is now yours")
                                                t_swapped = True


                                    tembedVar = discord.Embed(title=f"_Turn_ {turn_total}", description=textwrap.dedent(f"""\
                                    {previous_moves_into_embed}
                                    """), color=0xe74c3c)
                                    tembedVar.set_image(url="attachment://image.png")
                                    await battle_msg.delete(delay=None)
                                    # await asyncio.sleep(2)
                                    battle_msg = await private_channel.send(embed=tembedVar, file=player_2_card)
                                    selected_move = 0

                                    if t_used_resolve and not t_pet_used:
                                        selected_move = 6
                                    elif t_enhancer['TYPE'] == "WAVE" and (turn_total % 10 == 0 or turn_total == 0 or turn_total == 1):
                                        if t_stamina >=20:
                                            selected_move =4
                                    elif tarm_barrier_active: #Ai Barrier Checks
                                        if t_stamina >=20: #Stamina Check For Enhancer
                                            selected_move = await ai_enhancer_moves(turn_total,t_used_focus,t_used_resolve,t_pet_used,t_stamina,
                                                                        t_enhancer['TYPE'],t_health,t_max_health,t_attack,
                                                                        t_defense,c_stamina,c_attack,c_defense, c_health)
                                        else:
                                            selected_move = 1
                                    elif c_health <=350: #Killing Blow
                                        if t_enhancer['TYPE'] == "BLAST":
                                            if t_stamina >=20:
                                                selected_move =4
                                            else:
                                                selected_move =1
                                        elif t_enhancer['TYPE'] == "WAVE" and (turn_total % 10 == 0 or turn_total == 0 or turn_total == 1):
                                            if t_stamina >=20:
                                                selected_move =4
                                            else:
                                                selected_move =1
                                        else:
                                            if t_stamina >= 90:
                                                selected_move = 1
                                            elif t_stamina >= 80:
                                                selected_move =3
                                            elif t_stamina >=30:
                                                selected_move=2
                                            else:
                                                selected_move=1
                                    elif c_stamina < 10:
                                        selected_move = 1
                                    elif t_stamina >= 160 and (t_health >= c_health):
                                        selected_move = 3
                                    elif t_stamina >= 160:
                                        selected_move = 3
                                    elif t_stamina >= 150 and (t_health >= c_health):
                                        selected_move = 1
                                    elif t_stamina >= 150:
                                        selected_move = 1
                                    elif t_stamina >= 140 and (t_health >= c_health):
                                        selected_move = 1
                                    elif t_stamina >= 140:
                                        selected_move = 3
                                    elif t_stamina >= 130 and (t_health >= c_health):
                                        selected_move = 1
                                    elif t_stamina >= 130:
                                        selected_move = 3
                                    elif t_stamina >= 120 and (t_health >= c_health):
                                        selected_move = 2
                                    elif t_stamina >= 120:
                                        selected_move = 3
                                    elif t_stamina >= 110 and (t_health >= c_health):
                                        selected_move = 1
                                    elif t_stamina >= 110:
                                        selected_move = 2
                                    elif t_stamina >= 100 and (t_health >= c_health):
                                        selected_move = await ai_enhancer_moves(turn_total,t_used_focus,t_used_resolve,t_pet_used,t_stamina,
                                                                        t_enhancer['TYPE'],t_health,t_max_health,t_attack,
                                                                        t_defense,c_stamina,c_attack,c_defense, c_health)
                                    elif t_stamina >= 100:
                                        selected_move = 1
                                    elif t_stamina >= 90 and (t_health >= c_health):
                                        selected_move = 3
                                    elif t_stamina >= 90:
                                        selected_move = await ai_enhancer_moves(turn_total,t_used_focus,t_used_resolve,t_pet_used,t_stamina,
                                                                        t_enhancer['TYPE'],t_health,t_max_health,t_attack,
                                                                        t_defense,c_stamina,c_attack,c_defense, c_health)
                                    elif t_stamina >= 80 and (t_health >= c_health):
                                        selected_move = 1
                                    elif t_stamina >= 80:
                                        selected_move = 3
                                    elif t_stamina >= 70 and (t_health >= c_health):
                                        selected_move = await ai_enhancer_moves(turn_total,t_used_focus,t_used_resolve,t_pet_used,t_stamina,
                                                                        t_enhancer['TYPE'],t_health,t_max_health,t_attack,
                                                                        t_defense,c_stamina,c_attack,c_defense, c_health)
                                    elif t_stamina >= 70:
                                        selected_move = 1
                                    elif t_stamina >= 60 and (t_health >= c_health):
                                        if t_used_resolve == False and t_used_focus:
                                            selected_move = 5
                                        elif t_used_focus == False:
                                            selected_move = 2
                                        else:
                                            selected_move = 1
                                    elif t_stamina >= 60:
                                        if t_used_resolve == False and t_used_focus:
                                            selected_move = 5
                                        elif t_used_focus == False:
                                            selected_move = 2
                                        else:
                                            selected_move = 1
                                    elif t_stamina >= 50 and (t_health >= c_health):
                                        if t_used_resolve == False and t_used_focus:
                                            selected_move = 5
                                        elif t_used_focus == False:
                                            selected_move = 2
                                        else:
                                            selected_move = 1
                                    elif t_stamina >= 50:
                                        if t_used_resolve == False and t_used_focus:
                                            selected_move = 5
                                        elif t_used_focus == False:
                                            selected_move = 2
                                        else:
                                            selected_move = 1
                                    elif t_stamina >= 40 and (t_health >= c_health):
                                        selected_move = 1
                                    elif t_stamina >= 40:
                                        selected_move = 2
                                    elif t_stamina >= 30 and (t_health >= c_health):
                                        selected_move = await ai_enhancer_moves(turn_total,t_used_focus,t_used_resolve,t_pet_used,t_stamina,
                                                                        t_enhancer['TYPE'],t_health,t_max_health,t_attack,
                                                                        t_defense,c_stamina,c_attack,c_defense, c_health)
                                    elif t_stamina >= 30:
                                        selected_move = 2
                                    elif t_stamina >= 20 and (t_health >= c_health):
                                        selected_move = 1
                                    elif t_stamina >= 20:
                                        selected_move = await ai_enhancer_moves(turn_total,t_used_focus,t_used_resolve,t_pet_used,t_stamina,
                                                                        t_enhancer['TYPE'],t_health,t_max_health,t_attack,
                                                                        t_defense,c_stamina,c_attack,c_defense, c_health)
                                    elif t_stamina >= 10:
                                        selected_move = 1
                                    else:
                                        selected_move = 0

                                    t_special_move_description = ""
                                    if int(selected_move) == 0:
                                        t_health = 0
                                    if int(selected_move) == 1:

                                        if o_defend_used == True:
                                            if t_universe == "Souls" and t_used_resolve:
                                                dmg = damage_cal(mode,t_card_tier, t_talisman_dict, tap2, o_opponent_affinities, special_attack_name, tmove2_element, t_universe, t_card, t_2, t_attack, t_defense, o_defense, t_stamina,
                                                                t_enhancer_used, t_health, o_health, player1_card.stamina, t_max_health,
                                                                o_attack, t_special_move_description, turn_total,
                                                                tcard_lvl_ap_buff, t_1)
                                            else:
                                                dmg = damage_cal(mode,t_card_tier, t_talisman_dict, tap1, o_opponent_affinities, basic_attack_name, tmove1_element, t_universe, t_card, t_1, t_attack, t_defense, o_defense,
                                                                t_stamina, t_enhancer_used, t_health, o_health, player1_card.stamina,
                                                                t_max_health, o_attack, t_special_move_description, turn_total,
                                                                tcard_lvl_ap_buff, None)
                                        else:
                                            if t_universe == "Souls" and t_used_resolve:
                                                dmg = damage_cal(mode,t_card_tier, t_talisman_dict, tap2, c_opponent_affinities, special_attack_name, tmove2_element, t_universe, t_card, t_2, t_attack, t_defense, c_defense, t_stamina,
                                                                t_enhancer_used, t_health, c_health, c_stamina, t_max_health,
                                                                c_attack, t_special_move_description, turn_total,
                                                                tcard_lvl_ap_buff, t_1)
                                            else:
                                                dmg = damage_cal(mode,t_card_tier, t_talisman_dict, tap1, c_opponent_affinities, basic_attack_name, tmove1_element, t_universe, t_card, t_1, t_attack, t_defense, c_defense,
                                                                t_stamina, t_enhancer_used, t_health, c_health, c_stamina,
                                                                t_max_health, c_attack, t_special_move_description, turn_total,
                                                                tcard_lvl_ap_buff, None)
                                    elif int(selected_move) == 2:

                                        if o_defend_used == True:
                                            if t_universe == "Souls" and t_used_resolve:
                                                dmg = damage_cal(mode,t_card_tier, t_talisman_dict, tap3, o_opponent_affinities, ultimate_attack_name, tmove3_element, t_universe, t_card, t_3, t_attack, t_defense, o_defense, t_stamina,
                                                                t_enhancer_used, t_health, o_health, player1_card.stamina, t_max_health,
                                                                o_attack, t_special_move_description, turn_total,
                                                                tcard_lvl_ap_buff, t_2)
                                            else:
                                                dmg = damage_cal(mode,t_card_tier, t_talisman_dict, tap2, o_opponent_affinities, special_attack_name, tmove2_element, t_universe, t_card, t_2, t_attack, t_defense, o_defense,
                                                                t_stamina, t_enhancer_used, t_health, o_health, player1_card.stamina,
                                                                t_max_health, o_attack, t_special_move_description, turn_total,
                                                                tcard_lvl_ap_buff, None)
                                        else:
                                            if t_universe == "Souls" and t_used_resolve:
                                                dmg = damage_cal(mode,t_card_tier, t_talisman_dict, tap3, c_opponent_affinities, ultimate_attack_name, tmove3_element, t_universe, t_card, t_3, t_attack, t_defense, c_defense, t_stamina,
                                                                t_enhancer_used, t_health, c_health, c_stamina, t_max_health,
                                                                c_attack, t_special_move_description, turn_total,
                                                                tcard_lvl_ap_buff, t_2)
                                            else:
                                                dmg = damage_cal(mode,t_card_tier, t_talisman_dict, tap2, c_opponent_affinities, special_attack_name, tmove2_element, t_universe, t_card, t_2, t_attack, t_defense, c_defense,
                                                                t_stamina, t_enhancer_used, t_health, c_health, c_stamina,
                                                                t_max_health, c_attack, t_special_move_description, turn_total,
                                                                tcard_lvl_ap_buff, None)
                                    elif int(selected_move) == 3:

                                        if o_defend_used == True:
                                            dmg = damage_cal(mode,t_card_tier, t_talisman_dict, tap3, o_opponent_affinities, ultimate_attack_name, tmove3_element, t_universe, t_card, t_3, t_attack, t_defense, o_defense,
                                                            t_stamina, t_enhancer_used, t_health, o_health, player1_card.stamina,
                                                            t_max_health, o_attack, t_special_move_description, turn_total,
                                                            tcard_lvl_ap_buff, None)
                                        else:
                                            dmg = damage_cal(mode,t_card_tier, t_talisman_dict, tap3, c_opponent_affinities, ultimate_attack_name, tmove3_element, t_universe, t_card, t_3, t_attack, t_defense, c_defense,
                                                            t_stamina, t_enhancer_used, t_health, c_health, c_stamina,
                                                            t_max_health, c_attack, t_special_move_description, turn_total,
                                                            tcard_lvl_ap_buff, None)
                                        if t_gif != "N/A" and not operformance:
                                            await battle_msg.delete(delay=2)
                                            await asyncio.sleep(2)
                                            battle_msg = await private_channel.send(f"{t_gif}")
                                            await asyncio.sleep(2)
                                    elif int(selected_move) == 4:

                                        t_enhancer_used = True
                                        if o_defend_used == True:
                                            dmg = damage_cal(mode,t_card_tier, t_talisman_dict, tap1, o_opponent_affinities, basic_attack_name, tmove1_element, t_universe, t_card, t_enhancer, t_attack, t_defense, o_defense,
                                                            t_stamina, t_enhancer_used, t_health, o_health, player1_card.stamina,
                                                            t_max_health, o_attack, t_special_move_description, turn_total,
                                                            tcard_lvl_ap_buff, None)
                                        else:
                                            dmg = damage_cal(mode,t_card_tier, t_talisman_dict, tap1, t_for_c_opponent_affinities, basic_attack_name, tmove1_element, t_universe, t_card, t_enhancer, t_attack, t_defense, c_defense,
                                                            t_stamina, t_enhancer_used, t_health, c_health, c_stamina,
                                                            t_max_health, c_attack, t_special_move_description, turn_total,
                                                            tcard_lvl_ap_buff, None)
                                        t_enhancer_used = False
                                    elif int(selected_move) == 5:
                                        if not t_used_resolve and t_used_focus:
                                            if botActive and mode in B_modes:
                                                embedVar = discord.Embed(title=f"**{t_card}** Resolved!",
                                                                        description=f"{t_rmessage}", colour=0xe91e63)
                                                embedVar.set_footer(text=f"{o_card} this will not be easy...")
                                                await ctx.send(embed=embedVar)
                                            if t_universe == "My Hero Academia":  # My hero TRait
                                                # fortitude or luck is based on health
                                                fortitude = 0.0
                                                low = t_health - (t_health * .75)
                                                high = t_health - (t_health * .66)
                                                fortitude = round(random.randint(int(low), int(high)))
                                                # Resolve Scaling
                                                t_resolve_health = round(fortitude + (.5 * t_resolve))
                                                t_resolve_attack = round(
                                                    (.30 * t_defense) * (t_resolve / (.50 * t_defense)))
                                                t_resolve_defense = round(
                                                    (.30 * t_defense) * (t_resolve / (.50 * t_defense)))
                                                tcard_lvl_ap_buff = tcard_lvl_ap_buff + 200 + turn_total

                                                t_stamina = 160
                                                t_health = t_health + t_resolve_health
                                                t_attack = round(t_attack + t_resolve_attack)
                                                t_defense = round(t_defense - t_resolve_defense)
                                                t_used_resolve = True
                                                t_pet_used = False

                                                embedVar = discord.Embed(title=f"{t_card} PLUS ULTRAAA",
                                                                        description=f"**{t_card} says**\n{t_resolve_description}",
                                                                        colour=0xe91e63)
                                                embedVar.add_field(name=f"Transformation: Plus Ultra",
                                                                value="You do not lose a turn after you Resolve.")
                                                previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 Resolved: PLUS ULTRA!")
                                                #await private_channel.send(embed=embedVar)
                                                turn_total = turn_total + 1
                                                turn = 3

                                            elif t_universe == "One Piece" and (t_card_tier in high_tier_cards):
                                                # fortitude or luck is based on health
                                                fortitude = 0.0
                                                low = t_health - (t_health * .75)
                                                high = t_health - (t_health * .66)
                                                fortitude = round(random.randint(int(low), int(high)))
                                                # Resolve Scaling
                                                t_resolve_health = round(fortitude + (.5 * t_resolve))
                                                t_resolve_attack = round(
                                                    (.30 * t_defense) * (t_resolve / (.50 * t_defense)))
                                                t_resolve_defense = round(
                                                    (.30 * t_defense) * (t_resolve / (.50 * t_defense)))
                                                o_ap_buff = o_ap_buff - 125
                                                
                                                t_stamina = t_stamina + t_resolve
                                                t_health = t_health + t_resolve_health
                                                t_attack = round(t_attack + t_resolve_attack)
                                                t_defense = round(t_defense - t_resolve_defense)
                                                t_used_resolve = True
                                                t_pet_used = False

                                                previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 Resolved: Conquerors Haki!")
                                                await button_ctx.defer(ignore=True)
                                                turn_total = turn_total + 1
                                                turn = 3
                                    
                                            elif t_universe == "Demon Slayer": 
                                                # fortitude or luck is based on health
                                                fortitude = 0.0
                                                low = t_health - (t_health * .75)
                                                high = t_health - (t_health * .66)
                                                fortitude = round(random.randint(int(low), int(high)))
                                                # Resolve Scaling
                                                t_resolve_health = round(fortitude + (.5 * t_resolve))
                                                t_resolve_attack = round(
                                                    (.30 * t_defense) * (t_resolve / (.50 * t_defense)))
                                                t_resolve_defense = round(
                                                    (.30 * t_defense) * (t_resolve / (.50 * t_defense)))
                                                

                                                t_stamina = t_stamina + t_resolve
                                                t_health = t_health + t_resolve_health
                                                t_attack = round(t_attack + t_resolve_attack)
                                                t_defense = round(t_defense - t_resolve_defense)
                                                if c_attack > t_attack:
                                                    t_attack = c_attack
                                                if c_defense > t_defense:
                                                    t_defense = c_defense
                                                t_used_resolve = True
                                                t_pet_used = False
                                                embedVar = discord.Embed(title=f"{t_card} begins Total Concentration Breathing",
                                                                        description=f"**{t_card} says**\n{t_resolve_description}",
                                                                        colour=0xe91e63)
                                                previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 Resolved: Total Concentration Breathing!")
                                                
                                                turn_total = turn_total + 1
                                                turn = 0

                                            elif t_universe == "Naruto": 
                                                # fortitude or luck is based on health
                                                fortitude = 0.0
                                                low = t_health - (t_health * .75)
                                                high = t_health - (t_health * .66)
                                                fortitude = round(random.randint(int(low), int(high)))
                                                # Resolve Scaling
                                                t_resolve_health = round(fortitude + (.5 * t_resolve))
                                                t_resolve_attack = round(
                                                    (.30 * t_defense) * (t_resolve / (.50 * t_defense)))
                                                t_resolve_defense = round(
                                                    (.30 * t_defense) * (t_resolve / (.50 * t_defense)))

                                                t_stamina = t_stamina + t_resolve
                                                t_health = t_health + t_resolve_health
                                                t_health = t_health + t_naruto_heal_buff
                                                t_attack = round(t_attack + t_resolve_attack)
                                                t_defense = round(t_defense - t_resolve_defense)
                                                t_used_resolve = True
                                                t_pet_used = False
                                                embedVar = discord.Embed(title=f"{t_card} Heals from Hashirama Cells",
                                                                        description=f"**{t_card} says**\n{t_resolve_description}",
                                                                        colour=0xe91e63)
                                                previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 Resolved: Hashirama Cells heal you for **{t_naruto_heal_buff}**")
                                                turn_total = turn_total + 1
                                                turn = 0


                                            
                                            elif t_universe == "Attack On Titan":
                                                # fortitude or luck is based on health
                                                fortitude = 0.0
                                                low = t_health - (t_health * .75)
                                                high = t_health - (t_health * .66)
                                                fortitude = round(random.randint(int(low), int(high)))
                                                # Resolve Scaling
                                                t_resolve_health = round(fortitude + (.5 * t_resolve))
                                                t_resolve_attack = round(
                                                    (.30 * t_defense) * (t_resolve / (.50 * t_defense)))
                                                t_resolve_defense = round(
                                                    (.30 * t_defense) * (t_resolve / (.50 * t_defense)))
                                                t_stamina = t_stamina + t_resolve
                                                t_health = t_health + t_resolve_health
                                                t_attack = round(t_attack + t_resolve_attack)
                                                t_defense = round(t_defense - t_resolve_defense)
                                                t_used_resolve = True
                                                t_pet_used = False
                                                health_boost = 100 * t_focus_count
                                                t_health = t_health + health_boost

                                                embedVar = discord.Embed(title=f"{t_card} Titan Mode",
                                                                        description=f"**{t_card} says**\n{t_resolve_description}",
                                                                        colour=0xe91e63)
                                                embedVar.add_field(name=f"Transformation Complete",
                                                                value=f"Health increased by **{health_boost}**!")
                                                previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 Resolved: Titan Mode! Health increased by **{health_boost}**!")
                                                #await private_channel.send(embed=embedVar)
                                                turn_total = turn_total + 1
                                                turn = 0

                                            elif t_universe == "Bleach":  # Bleach Trait
                                                # fortitude or luck is based on health
                                                fortitude = 0.0
                                                low = t_health - (t_health * .75)
                                                high = t_health - (t_health * .66)
                                                fortitude = round(random.randint(int(low), int(high)))
                                                # Resolve Scaling
                                                t_resolve_health = round(fortitude + (.5 * t_resolve))
                                                t_resolve_attack = round(
                                                    (.30 * t_defense) * (t_resolve / (.50 * t_defense)))
                                                t_resolve_defense = round(
                                                    (.30 * t_defense) * (t_resolve / (.50 * t_defense)))

                                                t_stamina = t_stamina + t_resolve
                                                t_health = t_health + t_resolve_health
                                                t_attack = round((t_attack + (2 * t_resolve_attack))* 2)
                                                t_defense = round(t_defense - t_resolve_defense)
                                                # if t_defense >= 120:
                                                # t_defense = 120
                                                t_used_resolve = True
                                                t_pet_used = False

                                                embedVar = discord.Embed(title=f"{t_card} STRENGTHENED RESOLVE :zap:",
                                                                        description=f"**{t_card} says**\n{t_resolve_description}",
                                                                        colour=0xe91e63)
                                                embedVar.add_field(name=f"Transformation: Bankai",
                                                                value="Gain double Attack on Resolve.")
                                                previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 Resolved: Bankai!")
                                                #await private_channel.send(embed=embedVar)
                                                turn_total = turn_total + 1
                                                turn = 0
                                            elif t_universe == "God Of War":  # God Of War Trait
                                                # fortitude or luck is based on health
                                                fortitude = 0.0
                                                low = t_health - (t_health * .75)
                                                high = t_health - (t_health * .66)
                                                fortitude = round(random.randint(int(low), int(high)))
                                                # Resolve Scaling
                                                t_resolve_health = round(fortitude + (.5 * t_resolve))
                                                t_resolve_attack = round(
                                                    (.30 * t_defense) * (t_resolve / (.50 * t_defense)))
                                                t_resolve_defense = round(
                                                    (.30 * t_defense) * (t_resolve / (.50 * t_defense)))

                                                t_stamina = t_stamina + t_resolve
                                                t_attack = round(t_attack + t_resolve_attack)
                                                t_defense = round(t_defense - t_resolve_defense)
                                                t_used_resolve = True
                                                t_pet_used = False
                                                if t_gow_resolve:
                                                    t_health = t_max_health
                                                    previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 Resolved: Ascension!")
                                                elif not t_gow_resolve:
                                                    t_health = round(t_health + (t_max_health / 2))
                                                    t_used_resolve = False
                                                    t_gow_resolve = True
                                                    
                                                    previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 Crushed Blood Orb: Health Refill")

                                                turn_total = turn_total + 1
                                                turn = 0
                                            elif t_universe == "Fate":  # Fate Trait
                                                # fortitude or luck is based on health
                                                fortitude = 0.0
                                                low = t_health - (t_health * .75)
                                                high = t_health - (t_health * .66)
                                                fortitude = round(random.randint(int(low), int(high)))
                                                # Resolve Scaling
                                                t_resolve_health = round(fortitude + (.5 * t_resolve))
                                                t_resolve_attack = round(
                                                    (.30 * t_defense) * (t_resolve / (.50 * t_defense)))
                                                t_resolve_defense = round(
                                                    (.30 * t_defense) * (t_resolve / (.50 * t_defense)))

                                                t_stamina = t_stamina + t_resolve
                                                t_health = t_health + t_resolve_health
                                                t_attack = round(t_attack + t_resolve_attack)
                                                t_defense = round(t_defense - t_resolve_defense)
                                                t_used_resolve = True

                                                embedVar = discord.Embed(title=f"{t_card} STRENGTHENED RESOLVE :zap:",
                                                                        description=f"**{t_card} says**\n{t_resolve_description}",
                                                                        colour=0xe91e63)
                                                embedVar.add_field(name=f"Transformation: Command Seal",
                                                                value="On Resolve, Strike with Ultimate, then Focus.")
                                                #await private_channel.send(embed=embedVar)
                                                if o_defend_used == True:
                                                    dmg = damage_cal(mode,t_card_tier, t_talisman_dict, tap3, o_opponent_affinities, ultimate_attack_name, tmove3_element, t_universe, t_card, t_3, t_attack, t_defense,
                                                                    o_defense, t_stamina, t_enhancer_used, t_health,
                                                                    o_health, player1_card.stamina, t_max_health, o_attack,
                                                                    t_special_move_description, turn_total,
                                                                    tcard_lvl_ap_buff, None)
                                                    o_health = o_health - int(dmg['DMG'])
                                                else:
                                                    dmg = damage_cal(mode,t_card_tier, t_talisman_dict, tap3, t_for_c_opponent_affinities, ultimate_attack_name, tmove3_element, t_universe, t_card, t_3, t_attack, t_defense,
                                                                    c_defense, t_stamina, t_enhancer_used, t_health,
                                                                    c_health, c_stamina, t_max_health, c_attack,
                                                                    t_special_move_description, turn_total,
                                                                    tcard_lvl_ap_buff, None)
                                                    c_health = c_health - int(dmg['DMG'])
                                                t_pet_used = False
                                                embedVar = discord.Embed(title=f"{dmg['MESSAGE']}", colour=embed_color_t)
                                                previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 Resolved: Command Seal! {dmg['MESSAGE']}")
                                                #await private_channel.send(embed=embedVar)
                                                # t_stamina = 0
                                                turn_total = turn_total + 1
                                                turn = 0
                                            elif t_universe == "Kanto Region" or t_universe == "Johto Region" or t_universe == "Hoenn Region" or t_universe == "Sinnoh Region" or t_universe == "Kalos Region" or t_universe == "Unova Region" or t_universe == "Alola Region" or t_universe == "Galar Region":  # Pokemon Resolves
                                                # fortitude or luck is based on health
                                                fortitude = 0.0
                                                low = t_health - (t_health * .75)
                                                high = t_health - (t_health * .66)
                                                fortitude = round(random.randint(int(low), int(high)))
                                                # Resolve Scaling
                                                t_resolve_health = round(fortitude + (.5 * t_resolve))
                                                t_resolve_attack = round(
                                                    (.30 * t_defense) * (t_resolve / (.50 * t_defense)))
                                                t_resolve_defense = round(
                                                    (.30 * t_defense) * (t_resolve / (.50 * t_defense)))

                                                t_stamina = t_stamina + t_resolve
                                                t_health = t_health + t_resolve_health
                                                t_attack = round(t_attack + t_resolve_attack)
                                                t_defense = round(t_defense) * 2
                                                t_used_resolve = True
                                                t_pet_used = False

                                                embedVar = discord.Embed(title=f"{t_card} STRENGTHENED RESOLVE :zap:",
                                                                        description=f"**{t_card} says**\n{t_resolve_description}",
                                                                        colour=0xe91e63)
                                                embedVar.add_field(name=f"Transformation: Evolution",
                                                                value="When you Resolve your Defense doubles")
                                                if turn_total >= 50:
                                                    t_max_health = t_max_health + 1000
                                                    t_health = t_health + 1000
                                                    previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 Resolved: Gigantomax Evolution!!! Gained **1000** HP!!!")
                                                elif turn_total >= 30:
                                                    t_max_health = t_max_health + 500
                                                    t_health = t_health + 500
                                                    previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 Resolved: Mega Evolution!! Gained **500** HP!")
                                                else:
                                                    previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 Resolved: Evolution!")
                                                #await private_channel.send(embed=embedVar)
                                                turn_total = turn_total + 1
                                                turn = 0
                                            else:
                                                # fortitude or luck is based on health
                                                fortitude = 0.0
                                                low = t_health - (t_health * .75)
                                                high = t_health - (t_health * .66)
                                                fortitude = round(random.randint(int(low), int(high)))
                                                # Resolve Scaling
                                                t_resolve_health = round(fortitude + (.5 * t_resolve))
                                                t_resolve_attack = round(
                                                    (.30 * t_defense) * (t_resolve / (.50 * t_defense)))
                                                t_resolve_defense = round(
                                                    (.30 * t_defense) * (t_resolve / (.50 * t_defense)))

                                                t_stamina = t_stamina + t_resolve
                                                t_health = t_health + t_resolve_health
                                                t_attack = round(t_attack + t_resolve_attack)
                                                t_defense = round(t_defense - t_resolve_defense)
                                                t_used_resolve = True
                                                t_pet_used = False

                                                if t_universe == "League Of Legends":
                                                    if o_block_used == True:
                                                        o_health = o_health - (60 * (o_focus_count + t_focus_count))
                                                        embedVar = discord.Embed(title=f"{t_card} PENTA KILL!",
                                                                                description=f"**{t_card} says**\n{t_resolve_description}",
                                                                                colour=0xe91e63)
                                                        embedVar.add_field(name=f"Nexus Destroyed",
                                                                        value=f"**{t_card}** dealt **{(60 * (o_focus_count + t_focus_count))}** damage.")
                                                        previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 Resolved: Pentakill! Dealing {(60 * (o_focus_count + t_focus_count))} damage.")
                                                    else:
                                                        c_health = c_health - (60 * (c_focus_count + t_focus_count))
                                                        embedVar = discord.Embed(title=f"{t_card} PENTA KILL!",
                                                                                description=f"**{t_card} says**\n{t_resolve_description}",
                                                                                colour=0xe91e63)
                                                        embedVar.add_field(name=f"Nexus Destroyed",
                                                                        value=f"**{t_card}** dealt **{(60 * (c_focus_count + t_focus_count))}** damage.")
                                                        previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 Resolved: Pentakill! Dealing {(60 * (c_focus_count + t_focus_count))} damage.")
                                                elif t_universe == "Souls":
                                                    previous_moves.append(f"(**{turn_total}**) **{t_card}** 🩸 Phase 2: Enhanced Moveset!")
                                                    
                                                else:
                                                    embedVar = discord.Embed(title=f"{t_card} STRENGTHENED RESOLVE :zap:",
                                                                            description=f"**{t_card} says**\n{t_resolve_description}",
                                                                            colour=0xe91e63)
                                                    embedVar.add_field(name=f"Transformation",
                                                                    value="All stats & stamina greatly increased")
                                                    previous_moves.append(f"(**{turn_total}**) ⚡ **{t_card}** Resolved!")
                                                #await private_channel.send(embed=embedVar)
                                                turn_total = turn_total + 1
                                                turn = 0
                                        else:
                                            previous_moves.append(f"(**{turn_total}**) {t_card} cannot resolve!")
                                            turn = 3
                                    elif int(selected_move) == 6:
                                        # Resolve Check and Calculation
                                        if t_used_resolve and t_used_focus and not t_pet_used:
                                            if o_defend_used == True:
                                                t_enhancer_used = True
                                                dmg = damage_cal(mode,t_card_tier, t_talisman_dict, tap1, o_opponent_affinities, basic_attack_name, tmove1_element, t_universe, t_card, tpet_move, t_attack, t_defense,
                                                                o_defense, t_stamina, t_enhancer_used, t_health, o_health,
                                                                player1_card.stamina, t_max_health, o_attack,
                                                                t_special_move_description, turn_total, tcard_lvl_ap_buff, None)
                                                t_enhancer_used = False
                                                t_pet_used = True
                                                tpet_dmg = dmg['DMG']
                                                tpet_type = dmg['ENHANCED_TYPE']
                                                if dmg['CAN_USE_MOVE']:
                                                    if tpet_type == 'ATK':
                                                        t_attack = round(t_attack + dmg['DMG'])
                                                    elif tpet_type == 'DEF':
                                                        t_defense = round(t_defense + dmg['DMG'])
                                                    elif tpet_type == 'STAM':
                                                        t_stamina = round(t_stamina + dmg['DMG'])
                                                    elif tpet_type == 'HLT':
                                                        t_health = round(t_health + dmg['DMG'])
                                                    elif tpet_type == 'LIFE':
                                                        t_health = round(t_health + dmg['DMG'])
                                                        o_health = round(o_health - dmg['DMG'])
                                                    elif tpet_type == 'DRAIN':
                                                        t_stamina = round(t_stamina + dmg['DMG'])
                                                        player1_card.stamina = round(player1_card.stamina - dmg['DMG'])
                                                    elif tpet_type == 'FLOG':
                                                        t_attack = round(t_attack + dmg['DMG'])
                                                        o_attack = round(o_attack - dmg['DMG'])
                                                    elif tpet_type == 'WITHER':
                                                        t_defense = round(t_defense + dmg['DMG'])
                                                        o_defense = round(o_defense - dmg['DMG'])
                                                    elif tpet_type == 'RAGE':
                                                        t_defense = round(t_defense - dmg['DMG'])
                                                        t_ap_buff = round(t_ap_buff + dmg['DMG'])
                                                    elif tpet_type == 'BRACE':
                                                        t_ap_buff = round(t_ap_buff + dmg['DMG'])
                                                        t_attack = round(t_attack - dmg['DMG'])
                                                    elif tpet_type == 'BZRK':
                                                        t_health = round(t_health - dmg['DMG'])
                                                        t_attack = round(t_attack + dmg['DMG'])
                                                    elif tpet_type == 'CRYSTAL':
                                                        t_health = round(t_health - dmg['DMG'])
                                                        t_defense = round(t_defense + dmg['DMG'])
                                                    elif tpet_type == 'GROWTH':
                                                        t_max_health = round(t_max_health - (t_max_health * .10))
                                                        t_defense = round(t_defense + dmg['DMG'])
                                                        t_attack= round(t_attack + dmg['DMG'])
                                                        t_ap_buff = round(t_ap_buff + dmg['DMG'])
                                                    elif tpet_type == 'STANCE':
                                                        tempattack = dmg['DMG']
                                                        t_attack = t_defense
                                                        t_defense = tempattack
                                                    elif tpet_type == 'CONFUSE':
                                                        tempattack = dmg['DMG']
                                                        o_attack = o_defense
                                                        o_defense = tempattack
                                                    elif tpet_type == 'BLINK':
                                                        t_stamina = round(t_stamina - dmg['DMG'])
                                                        player1_card.stamina = round(player1_card.stamina + dmg['DMG'])
                                                    elif tpet_type == 'SLOW':
                                                        tempstam = round(player1_card.stamina + dmg['DMG'])
                                                        t_stamina = round(t_stamina - dmg['DMG'])
                                                        player1_card.stamina = t_stamina
                                                        t_stamina = tempstam
                                                    elif tpet_type == 'HASTE':
                                                        tempstam = round(player1_card.stamina - dmg['DMG'])
                                                        t_stamina = round(t_stamina + dmg['DMG'])
                                                        player1_card.stamina = t_stamina
                                                        t_stamina = tempstam
                                                    elif tpet_type == 'SOULCHAIN':
                                                        t_stamina = round(dmg['DMG'])
                                                        player1_card.stamina = t_stamina
                                                    elif tpet_type == 'GAMBLE':
                                                        t_health = round(dmg['DMG'])
                                                        o_health = t_health
                                                    elif tpet_type == 'FEAR':
                                                        if t_universe != "Chainsawman":
                                                            t_max_health = round(t_max_health - (t_max_health * .10))
                                                        o_defense = round(o_defense - dmg['DMG'])
                                                        o_attack= round(o_attack - dmg['DMG'])
                                                        o_ap_buff = round(o_ap_buff - dmg['DMG'])
                                                    elif tpet_type == 'WAVE':
                                                        o_health = round(o_health - dmg['DMG'])
                                                    elif tpet_type == 'BLAST':
                                                        if dmg['DMG'] >= 300:
                                                            dmg['DMG'] = 300
                                                        o_health = round(o_health - dmg['DMG'])
                                                    elif tpet_type == 'CREATION':
                                                        t_max_health = round(t_max_health + dmg['DMG'])
                                                        t_health = round(t_health + dmg['DMG'])
                                                    elif tpet_type == 'DESTRUCTION':
                                                        if dmg['DMG'] >= 300:
                                                            dmg['DMG'] = 300
                                                        o_max_health = round(o_max_health - dmg['DMG'])
                                                        if o_max_health <=1:
                                                            o_max_health = 1
                                                    t_stamina = t_stamina - int(dmg['STAMINA_USED'])

                                                    if t_universe == "Persona":
                                                        petdmg = damage_cal(mode,t_card_tier, t_talisman_dict, tap1, t_for_c_opponent_affinities, basic_attack_name, tmove1_element, t_universe, t_card, t_1, t_attack, t_defense,
                                                                            c_defense, t_stamina, t_enhancer_used, t_health,
                                                                            c_health, c_stamina, t_max_health, c_attack,
                                                                            t_special_move_description, turn_total,
                                                                            tcard_lvl_ap_buff, None)

                                                        o_health = o_health - petdmg['DMG']

                                                        embedVar = discord.Embed(
                                                            title=f"**PERSONA!**\n{tpet_name} was summoned from {t_card}'s soul dealing **{petdmg['DMG']}** damage!!",
                                                            colour=0xe91e63)
                                                        await battle_msg.delete(delay=2)
                                                        if not operformance:
                                                            tsummon_file = showsummon(tpet_image, tpet_name, dmg['MESSAGE'], tpet_lvl, tpet_bond)
                                                            await asyncio.sleep(2)
                                                            battle_msg = await private_channel.send(embed=embedVar, file=tsummon_file)
                                                            await asyncio.sleep(2)
                                                            await battle_msg.delete(delay=2)
                                                        
                                                        
                                                        embedVar.set_image(url="attachment://pet.png")
                                                        #await button_ctx.send(embed=embedVar)
                                                        previous_moves.append(f"(**{turn_total}**) **Persona!** 🩸 : **{tpet_name}** was summoned from **{t_card}'s** soul dealing **{petdmg['DMG']}** damage!\n**{c_card}** summon disabled!")
                                                        c_pet_used = True
                                                        
                                                        
                                                    else:
                                                        embedVar = discord.Embed(
                                                            title=f"{t_card} Summoned 🧬 **{tpet_name}**",
                                                            colour=0xe91e63)
                                                        await battle_msg.delete(delay=2)
                                                        if not operformance:
                                                            tsummon_file = showsummon(tpet_image, tpet_name, dmg['MESSAGE'], tpet_lvl, tpet_bond)
                                                            await asyncio.sleep(2)
                                                            battle_msg = await private_channel.send(embed=embedVar, file=tsummon_file)
                                                            await asyncio.sleep(2)
                                                            await battle_msg.delete(delay=2)
                                                        
                                                        
                                                        embedVar.set_image(url="attachment://pet.png")
                                                        #await private_channel.send(embed=embedVar)
                                                        previous_moves.append(f"(**{turn_total}**) **{t_card}** Summoned 🧬 **{tpet_name}**: {dmg['MESSAGE']}")
                                                        
                                                    turn = 3
                                                else:
                                                    previous_moves.append(f"(**{turn_total}**) {t_card} Could not summon 🧬 **{tpet_name}**. Needs rest")
                                                    turn = 3
                                            else:
                                                t_enhancer_used = True
                                                dmg = damage_cal(mode,t_card_tier, t_talisman_dict, tap1, t_for_c_opponent_affinities, basic_attack_name, tmove1_element, t_universe, t_card, tpet_move, t_attack, t_defense,
                                                                c_defense, t_stamina, t_enhancer_used, t_health, c_health,
                                                                c_stamina, t_max_health, c_attack,
                                                                t_special_move_description, turn_total, tcard_lvl_ap_buff, None)
                                                t_enhancer_used = False
                                                t_pet_used = True
                                                tpet_dmg = dmg['DMG']
                                                tpet_type = dmg['ENHANCED_TYPE']
                                                if dmg['CAN_USE_MOVE']:
                                                    if tpet_type == 'ATK':
                                                        t_attack = round(t_attack + dmg['DMG'])
                                                    elif tpet_type == 'DEF':
                                                        t_defense = round(t_defense + dmg['DMG'])
                                                    elif tpet_type == 'STAM':
                                                        t_stamina = round(t_stamina + dmg['DMG'])
                                                    elif tpet_type == 'HLT':
                                                        t_health = round(t_health + dmg['DMG'])
                                                    elif tpet_type == 'LIFE':
                                                        t_health = round(t_health + dmg['DMG'])
                                                        c_health = round(c_health - dmg['DMG'])
                                                    elif tpet_type == 'DRAIN':
                                                        t_stamina = round(t_stamina + dmg['DMG'])
                                                        c_stamina = round(c_stamina - dmg['DMG'])
                                                    elif tpet_type == 'FLOG':
                                                        t_attack = round(t_attack + dmg['DMG'])
                                                        c_attack = round(c_attack - dmg['DMG'])
                                                    elif tpet_type == 'WITHER':
                                                        t_defense = round(t_defense + dmg['DMG'])
                                                        c_defense = round(c_defense - dmg['DMG'])
                                                    elif tpet_type == 'RAGE':
                                                        t_defense = round(t_defense - dmg['DMG'])
                                                        t_ap_buff = round(t_ap_buff + dmg['DMG'])
                                                    elif tpet_type == 'BRACE':
                                                        t_ap_buff = round(t_ap_buff + dmg['DMG'])
                                                        t_attack = round(t_attack - dmg['DMG'])
                                                    elif tpet_type == 'BZRK':
                                                        t_health = round(t_health - dmg['DMG'])
                                                        t_attack = round(t_attack + dmg['DMG'])
                                                    elif tpet_type == 'CRYSTAL':
                                                        t_health = round(t_health - dmg['DMG'])
                                                        t_defense = round(t_defense + dmg['DMG'])
                                                    elif tpet_type == 'GROWTH':
                                                        t_max_health = round(t_max_health - (t_max_health * .10))
                                                        t_defense = round(t_defense + dmg['DMG'])
                                                        t_attack= round(t_attack + dmg['DMG'])
                                                        t_ap_buff = round(t_ap_buff + dmg['DMG'])
                                                    elif tpet_type == 'STANCE':
                                                        tempattack = dmg['DMG']
                                                        t_attack = t_defense
                                                        t_defense = tempattack
                                                    elif tpet_type == 'CONFUSE':
                                                        tempattack = dmg['DMG']
                                                        c_attack = c_defense
                                                        c_defense = tempattack
                                                    elif tpet_type == 'BLINK':
                                                        t_stamina = round(t_stamina - dmg['DMG'])
                                                        c_stamina = round(c_stamina + dmg['DMG'])
                                                    elif tpet_type == 'SLOW':
                                                        tempstam = round(c_stamina + dmg['DMG'])
                                                        t_stamina = round(t_stamina - dmg['DMG'])
                                                        c_stamina = t_stamina
                                                        t_stamina = tempstam
                                                    elif tpet_type == 'HASTE':
                                                        tempstam = round(c_stamina - dmg['DMG'])
                                                        t_stamina = round(t_stamina + dmg['DMG'])
                                                        c_stamina = t_stamina
                                                        t_stamina = tempstam
                                                    elif tpet_type == 'SOULCHAIN':
                                                        t_stamina = round(dmg['DMG'])
                                                        c_stamina = t_stamina
                                                    elif tpet_type == 'GAMBLE':
                                                        t_health = round(dmg['DMG'])
                                                        c_health = t_health
                                                    elif tpet_type == 'FEAR':
                                                        if t_universe != "Chainsawman":
                                                            t_max_health = round(t_max_health - (t_max_health * .10))
                                                        c_attack = round(c_attack - dmg['DMG'])
                                                        c_defense = round(c_defense - dmg['DMG'])
                                                        c_ap_buff = round(c_ap_buff - dmg['DMG'])
                                                    elif tpet_type == 'WAVE':
                                                        c_health = round(c_health - dmg['DMG'])
                                                    elif tpet_type == 'BLAST':
                                                        if dmg['DMG'] >= 300:
                                                            dmg['DMG'] = 300
                                                        c_health = round(c_health - dmg['DMG'])
                                                    elif tpet_type == 'CREATION':
                                                        t_max_health = round(t_max_health + dmg['DMG'])
                                                        t_health = round(t_health + dmg['DMG'])
                                                    elif tpet_type == 'DESTRUCTION':
                                                        if dmg['DMG'] >= 300:
                                                            dmg['DMG'] = 300    
                                                        o_max_health = round(o_max_health - dmg['DMG'])
                                                        if o_max_health <=1:
                                                            o_max_health = 1
                                                    t_stamina = t_stamina - int(dmg['STAMINA_USED'])

                                                    if t_universe == "Persona":
                                                        petdmg = damage_cal(mode,t_card_tier, t_talisman_dict, tap1, t_for_c_opponent_affinities, basic_attack_name, tmove1_element, t_universe, t_card, t_1, t_attack, t_defense,
                                                                            c_defense, t_stamina, t_enhancer_used, t_health,
                                                                            c_health, c_stamina, t_max_health, c_attack,
                                                                            t_special_move_description, turn_total,
                                                                            tcard_lvl_ap_buff, None)

                                                        c_health = c_health - petdmg['DMG']

                                                        embedVar = discord.Embed(
                                                            title=f"**PERSONA!**\n{tpet_name} was summoned from {t_card}'s soul dealing **{petdmg['DMG']}** damage!!",
                                                            colour=0xe91e63)
                                                        await battle_msg.delete(delay=2)
                                                        if not operformance:
                                                            tsummon_file = showsummon(tpet_image, tpet_name, dmg['MESSAGE'], tpet_lvl, tpet_bond)
                                                            embedVar.set_image(url="attachment://pet.png")
                                                            await asyncio.sleep(2)
                                                            battle_msg = await private_channel.send(embed=embedVar, file=tsummon_file)
                                                            await asyncio.sleep(2)
                                                            await battle_msg.delete(delay=2)
                                                        
                                                        
                                                        #embedVar.set_image(url="attachment://pet.png")
                                                        #await button_ctx.send(embed=embedVar)
                                                        previous_moves.append(f"(**{turn_total}**) **Persona!** 🩸 : **{tpet_name}** was summoned from **{t_card}'s** soul dealing **{petdmg['DMG']}** damage!\n**{c_card}** summon disabled!")
                                                        c_pet_used = True
                                                        
                                                    else:
                                                        embedVar = discord.Embed(
                                                            title=f"{t_card} Summoned 🧬 **{tpet_name}**",
                                                            colour=0xe91e63)
                                                        await battle_msg.delete(delay=2)
                                                        if not operformance:
                                                            tsummon_file = showsummon(tpet_image, tpet_name, dmg['MESSAGE'], tpet_lvl, tpet_bond)
                                                            embedVar.set_image(url="attachment://pet.png")
                                                            await asyncio.sleep(2)
                                                            battle_msg = await private_channel.send(embed=embedVar, file=tsummon_file)
                                                            await asyncio.sleep(2)
                                                            await battle_msg.delete(delay=2)
                                                        
                                                        
                                                        
                                                        previous_moves.append(f"(**{turn_total}**) **{t_card}** Summoned 🧬 **{tpet_name}**: {dmg['MESSAGE']}")
                                                        
                                                    turn = 3
                                                else:
                                                    previous_moves.append(f"(**{turn_total}**) {t_card} Could not summon 🧬 **{tpet_name}**. Needs rest")
                                                    turn = 3
                                    elif int(selected_move) == 7:
                                        if t_stamina >= 20:
                                            if t_universe == "Attack On Titan":
                                                previous_moves.append(f"(**{turn_total}**) **Rally** 🩸 ! **{t_card}** Increased Max Health ❤️")
                                                t_max_health = round(t_max_health + 100)
                                                t_health = t_health + 100

                                            if t_universe == "Bleach":
                                                dmg = damage_cal(mode,t_card_tier, t_talisman_dict, tap1, o_opponent_affinities, basic_attack_name, tmove1_element, t_universe, t_card, t_1, t_attack, t_defense, o_defense,
                                                                t_stamina, t_enhancer_used, t_health, o_health, player1_card.stamina,
                                                                t_max_health, o_attack, t_special_move_description, turn_total,
                                                                tcard_lvl_ap_buff, None)
                                                previous_moves.append(f"(**{turn_total}**) **{t_card}** Exerted their 🩸 Spiritual Pressure - {dmg['MESSAGE']}")
                                                if c_universe == "One Piece" and (c_card_tier in low_tier_cards or c_card_tier in mid_tier_cards or c_card_tier in high_tier_cards):
                                                    if c_focus_count == 0:
                                                        dmg['DMG'] = dmg['DMG'] * .6

                                                
                                                if dmg['REPEL']:
                                                    t_health = t_health - dmg['DMG']
                                                elif dmg['ABSORB']:
                                                    c_health = c_health + dmg['DMG']
                                                elif dmg['ELEMENT'] == water_element:
                                                    if tmove1_element == water_element:
                                                        t_basic_water_buff = t_basic_water_buff + 40
                                                    if tmove2_element == water_element:
                                                        t_special_water_buff = t_special_water_buff + 40
                                                    if tmove3_element == water_element:
                                                        t_ultimate_water_buff = t_ultimate_water_buff + 40
                                                    c_health = c_health - dmg['DMG']

                                                elif dmg['ELEMENT'] == ice_element:
                                                    t_ice_counter = t_ice_counter + 1
                                                    if t_ice_counter == 2:
                                                        t_freeze_enh = True
                                                        t_ice_counter = 0
                                                    c_health = c_health - dmg['DMG']

                                                elif dmg['ELEMENT'] == time_element:
                                                    if t_stamina <= 80:
                                                        t_stamina = 0
                                                    t_block_used = True
                                                    t_defense = round(t_defense * 2)
                                                    previous_moves.append(f"**{t_card}** Blocked 🛡️")

                                                    c_health = c_health - dmg['DMG']

                                                elif dmg['ELEMENT'] == bleed_element:
                                                    t_bleed_counter = t_bleed_counter + 1
                                                    if t_bleed_counter == 3:
                                                        t_bleed_hit = True
                                                        t_bleed_counter = 0
                                                    c_health = c_health - dmg['DMG']

                                                elif dmg['ELEMENT'] == recoil_element:
                                                    t_health = t_health - (dmg['DMG'] * .60)
                                                    if t_health <= 0:
                                                        t_health = 1
                                                    c_health = c_health - dmg['DMG']

                                                elif dmg['ELEMENT'] == earth_element:
                                                    t_defense = t_defense + (dmg['DMG'] * .25)
                                                    c_health = c_health - dmg['DMG']

                                                elif dmg['ELEMENT'] == death_element:
                                                    c_max_health = c_max_health - (dmg['DMG'] * .20)
                                                    c_health = c_health - dmg['DMG']

                                                elif dmg['ELEMENT'] == light_element:
                                                    t_stamina = round(t_stamina + (dmg['STAMINA_USED'] / 2))
                                                    t_attack = t_attack + (dmg['DMG'] * .20)
                                                    c_health = c_health - dmg['DMG']

                                                elif dmg['ELEMENT'] == dark_element:
                                                    c_stamina = c_stamina - 15
                                                    c_health = c_health - dmg['DMG']

                                                elif dmg['ELEMENT'] == life_element:
                                                    t_health = t_health + (dmg['DMG'] * .20)
                                                    c_health = c_health - dmg['DMG']

                                                elif dmg['ELEMENT'] == psychic_element:
                                                    c_defense = c_defense - (dmg['DMG'] * .15)
                                                    c_attack = c_attack - (dmg['DMG'] * .15)
                                                    c_health = c_health - dmg['DMG']

                                                elif dmg['ELEMENT'] == fire_element:
                                                    t_burn_dmg = t_burn_dmg + round(dmg['DMG'] * .25)
                                                    c_health = c_health - dmg['DMG']

                                                elif dmg['ELEMENT'] == electric_element:
                                                    t_shock_buff = t_shock_buff +  (dmg['DMG'] * .15)
                                                    c_health = c_health - dmg['DMG']

                                                elif dmg['ELEMENT'] == poison_element:
                                                    if t_poison_dmg <= 600:
                                                        t_poison_dmg = t_poison_dmg + 30
                                                    c_health = c_health - dmg['DMG']
                                                    
                                                elif dmg['ELEMENT'] == gravity_element:
                                                    t_gravity_hit = True
                                                    c_health = c_health - dmg['DMG']
                                                    c_defense = c_defense - (dmg['DMG'] * .25)
                                                
                                                else:
                                                    c_health = c_health - dmg['DMG']

                                            t_stamina = t_stamina - 20
                                            t_block_used = True
                                            t_defense = round(t_defense * 2)
                                            previous_moves.append(f"(**{turn_total}**) **{t_card}:** Blocked 🛡️")
                                            turn_total = turn_total + 1
                                            turn = 0
                                        else:
                                            turn = 2

                                    if int(selected_move) != 5 and int(selected_move) != 6 and int(selected_move) !=7:
                                        # If you have enough stamina for move, use it
                                        # check if o is blocking

                                        if o_defend_used == True:
                                            if dmg['CAN_USE_MOVE']:
                                                if dmg['ENHANCE']:
                                                    enh_type = dmg['ENHANCED_TYPE']
                                                    if enh_type == 'ATK':
                                                        t_attack = round(t_attack + dmg['DMG'])
                                                    elif enh_type == 'DEF':
                                                        t_defense = round(t_defense + dmg['DMG'])
                                                    elif enh_type == 'STAM':
                                                        t_stamina = round(t_stamina + dmg['DMG'])
                                                    elif enh_type == 'HLT':
                                                        t_health = round(t_health + dmg['DMG'])
                                                    elif enh_type == 'LIFE':
                                                        t_health = round(t_health + dmg['DMG'])
                                                        o_health = round(o_health - dmg['DMG'])
                                                    elif enh_type == 'DRAIN':
                                                        t_stamina = round(t_stamina + dmg['DMG'])
                                                        player1_card.stamina = round(player1_card.stamina - dmg['DMG'])
                                                    elif enh_type == 'FLOG':
                                                        t_attack = round(t_attack + dmg['DMG'])
                                                        o_attack = round(o_attack - dmg['DMG'])
                                                    elif enh_type == 'WITHER':
                                                        t_defense = round(t_defense + dmg['DMG'])
                                                        o_defense = round(o_defense - dmg['DMG'])
                                                    elif enh_type == 'RAGE':
                                                        t_defense = round(t_defense - dmg['DMG'])
                                                        t_ap_buff = round(t_ap_buff + dmg['DMG'])
                                                    elif enh_type == 'BRACE':
                                                        t_ap_buff = round(t_ap_buff + dmg['DMG'])
                                                        t_attack = round(t_attack - dmg['DMG'])
                                                    elif enh_type == 'BZRK':
                                                        t_health = round(t_health - dmg['DMG'])
                                                        t_attack = round(t_attack + (dmg['DMG']))
                                                    elif enh_type == 'CRYSTAL':
                                                        t_health = round(t_health - dmg['DMG'])
                                                        t_defense = round(t_defense + dmg['DMG'])
                                                    elif enh_type == 'GROWTH':
                                                        t_max_health = round(t_max_health - (t_max_health * .10))
                                                        t_defense = round(t_defense + dmg['DMG'])
                                                        t_attack= round(t_attack + dmg['DMG'])
                                                        t_ap_buff = round(t_ap_buff + dmg['DMG'])
                                                    elif enh_type == 'STANCE':
                                                        tempattack = dmg['DMG']
                                                        t_attack = t_defense
                                                        t_defense = tempattack
                                                    elif enh_type == 'CONFUSE':
                                                        tempattack = dmg['DMG']
                                                        o_attack = o_defense
                                                        o_defense = tempattack
                                                    elif enh_type == 'BLINK':
                                                        t_stamina = round(t_stamina - dmg['DMG'])
                                                        player1_card.stamina = round(player1_card.stamina + dmg['DMG'])
                                                    elif enh_type == 'SLOW':
                                                        tempstam = round(player1_card.stamina + dmg['DMG'])
                                                        t_stamina = round(t_stamina - dmg['DMG'])
                                                        player1_card.stamina = t_stamina
                                                        t_stamina = tempstam
                                                    elif enh_type == 'HASTE':
                                                        tempstam = round(player1_card.stamina - dmg['DMG'])
                                                        t_stamina = round(t_stamina + dmg['DMG'])
                                                        player1_card.stamina = t_stamina
                                                        t_stamina = tempstam
                                                    elif enh_type == 'SOULCHAIN':
                                                        t_stamina = round(dmg['DMG'])
                                                        player1_card.stamina = player1_card.stamina
                                                    elif enh_type == 'GAMBLE':
                                                        if mode in D_modes:
                                                            t_health = round(dmg['DMG']) * 3
                                                            o_health = round(dmg['DMG'])
                                                        elif mode in B_modes:
                                                            t_health = round(dmg['DMG']) * 4
                                                            o_health = round(dmg['DMG'])
                                                        else:
                                                            t_health = round(dmg['DMG']) * 2
                                                            o_health = round(dmg['DMG'])
                                                    elif enh_type == 'FEAR':
                                                        if t_universe != "Chainsawman":
                                                            t_max_health = round(t_max_health - (t_max_health * .10))
                                                        o_defense = round(o_defense - dmg['DMG'])
                                                        o_attack= round(o_attack - dmg['DMG'])
                                                        o_ap_buff = round(o_ap_buff - dmg['DMG'])
                                                    elif enh_type == 'WAVE':
                                                        o_health = round(o_health - dmg['DMG'])
                                                    elif enh_type == 'BLAST':
                                                        if dmg['DMG'] >= 700:
                                                            dmg['DMG'] = 700

                                                        o_health = round(o_health - dmg['DMG'])
                                                    elif enh_type == 'CREATION':
                                                        t_max_health = round(t_max_health + dmg['DMG'])
                                                        t_health = round(t_health + dmg['DMG'])
                                                    elif enh_type == 'DESTRUCTION':
                                                        # t_max_health = round(t_max_health - dmg['DMG'])
                                                        o_max_health = round(o_max_health - dmg['DMG'])
                                                        # if t_max_health <=1:
                                                        #     t_max_health = 1
                                                        if o_max_health <=1:
                                                            o_max_health = 1
                                                    
                                                    if enh_type in Stamina_Enhancer_Check or enh_type in Time_Enhancer_Check or enh_type in Control_Enhancer_Check:
                                                        t_stamina = t_stamina
                                                    else:
                                                        t_stamina = t_stamina - int(dmg['STAMINA_USED'])
                                                    embedVar = discord.Embed(title=f"{dmg['MESSAGE']}",
                                                                            colour=embed_color_t)
                                                    #await private_channel.send(embed=embedVar)
                                                    previous_moves.append(f"(**{turn_total}**) **{t_card}**: 🦠 {dmg['MESSAGE']}")
                                                    turn_total = turn_total + 1
                                                    turn = 0
                                                elif dmg['DMG'] == 0:
                                                    t_stamina = t_stamina - int(dmg['STAMINA_USED'])
                                                    embedVar = discord.Embed(title=f"{dmg['MESSAGE']}", colour=embed_color_t)
                                                    previous_moves.append(f"(**{turn_total}**) **{t_card}**: {dmg['MESSAGE']}")
                                                    if tarm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                        tarm_barrier_active=False
                                                        
                                                        previous_moves.append(f"(**{turn_total}**) **{t_card}**'s 💠 Barrier Disabled!")
                                                    #await private_channel.send(embed=embedVar)
                                                    turn_total = turn_total + 1
                                                    turn = 0
                                                else:
                                                    if o_universe == "Naruto" and player1_card.stamina < 10:
                                                        o_stored_damage = round(dmg['DMG'])
                                                        o_naruto_heal_buff = o_naruto_heal_buff + o_stored_damage
                                                        o_health = o_health 
                                                        embedVar = discord.Embed(title=f"{o_card}: Substitution Jutsu", description=f"{t_card} strikes a log", colour=0xe91e63)
                                                        previous_moves.append(f"(**{turn_total}**) **{o_card}** 🩸: Substitution Jutsu")
                                                        if not o_used_resolve:
                                                            previous_moves.append(f"(**{turn_total}**) 🩸**{o_stored_damage}** Hasirama Cells stored. 🩸**{o_naruto_heal_buff}** total stored.")
                                                        if tarm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                            tarm_barrier_active=False
                                                            
                                                            previous_moves.append(f"(**{turn_total}**) **{t_card}**'s 💠 Barrier Disabled!")
                                                        #await private_channel.send(embed=embedVar)
                                                    elif oarm_shield_active and dmg['ELEMENT'] != dark_element:
                                                        if dmg['ELEMENT'] == poison_element: #Poison Update
                                                            if t_poison_dmg <= 600:
                                                                t_poison_dmg = o_poison_dmg + 30
                                                   
                                                        if oshield_value > 0:
                                                            oshield_value = oshield_value -dmg['DMG']
                                                            o_health = o_health 
                                                            if oshield_value <=0:
                                                                embedVar = discord.Embed(title=f"{o_card}'s' **Shield** Shattered!", description=f"{t_card} breaks the **Shield**!", colour=0xe91e63)
                                                                previous_moves.append(f"(**{turn_total}**) **{o_card}'s** 🌐 Shield Shattered!")
                                                                if tarm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                    tarm_barrier_active=False
                                                                    
                                                                    previous_moves.append(f"(**{turn_total}**) **{t_card}**'s 💠 Barrier Disabled!")
                                                                #await private_channel.send(embed=embedVar)
                                                                oarm_shield_active = False
                                                            else:
                                                                embedVar = discord.Embed(title=f"{o_card} Activates **Shield** 🌐", description=f"**{t_card}** strikes the Shield 🌐\n**{oshield_value} Shield** Left!", colour=0xe91e63)
                                                                previous_moves.append(f"(**{turn_total}**) **{t_card}** strikes **{o_card}**'s Shield 🌐\n**{oshield_value} Shield** Left!")
                                                                if tarm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                    tarm_barrier_active=False
                                                                    
                                                                    previous_moves.append(f"(**{turn_total}**) **{t_card}**'s 💠 Barrier Disabled!")
                                                                #await private_channel.send(embed=embedVar)

                                                    elif oarm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                        if obarrier_count >1:
                                                            o_health = o_health 
                                                            embedVar = discord.Embed(title=f"{o_card} Activates **Barrier** 💠", description=f"{t_card}'s attack **Nullified**!\n💠 {obarrier_count - 1} **Barriers** remain!", colour=0xe91e63)
                                                            previous_moves.append(f"(**{turn_total}**) /**{o_card}** Activates Barrier 💠  {t_card}'s attack **Nullified**!\n💠 {obarrier_count - 1} **Barriers** remain!")
                                                            if tarm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                tarm_barrier_active=False
                                                                
                                                                previous_moves.append(f"(**{turn_total}**) **{t_card}**'s 💠 Barrier Disabled!")
                                                            #await private_channel.send(embed=embedVar)
                                                            obarrier_count = obarrier_count - 1
                                                        elif obarrier_count==1:
                                                            embedVar = discord.Embed(title=f"{o_card}'s **Barrier** Broken!", description=f"{t_card} destroys the **Barrier**", colour=0xe91e63)
                                                            previous_moves.append(f"(**{turn_total}**) **{o_card}**'s Barrier Broken!")
                                                            obarrier_count = obarrier_count - 1
                                                            if tarm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                tarm_barrier_active=False
                                                                
                                                                previous_moves.append(f"(**{turn_total}**) **{t_card}**'s 💠 Barrier Disabled!")
                                                            #await private_channel.send(embed=embedVar)
                                                            oarm_barrier_active = False
                                                    elif oarm_parry_active and dmg['ELEMENT'] != earth_element:
                                                        if oparry_count > 1:
                                                            oparry_damage = round(dmg['DMG'])
                                                            o_health = round(o_health - (oparry_damage * .75))
                                                            t_health = round(t_health - (oparry_damage * .40))
                                                            oparry_count = oparry_count - 1
                                                            embedVar = discord.Embed(title=f"{o_card} Activates **Parry** 🔄", description=f"{t_card} takes {round(oparry_damage * .40)}! DMG\n **{oparry_count} Parries** to go!!", colour=0xe91e63)
                                                            previous_moves.append(f"(**{turn_total}**) **{o_card}** Activates Parry 🔄 after **{round(oparry_damage * .75)}** dmg dealt: {t_card} takes {round(oparry_damage * .40)}! DMG\n **{oparry_count}  Parries** to go!!")
                                                            if tarm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                tarm_barrier_active=False
                                                                
                                                                previous_moves.append(f"(**{turn_total}**) **{t_card}**'s 💠 Barrier Disabled!")
                                                            #await private_channel.send(embed=embedVar)
                                                            
                                                        elif oparry_count==1:
                                                            oparry_damage = round(dmg['DMG'])
                                                            o_health = round(o_health - (oparry_damage * .75))
                                                            t_health = round(t_health - (oparry_damage * .40))
                                                            embedVar = discord.Embed(title=f"{o_card} **Parry** Penetrated!!", description=f"{t_card} takes {round(oparry_damage * .40)}! DMG and breaks the **Parry**", colour=0xe91e63)
                                                            previous_moves.append(f"(**{turn_total}**) **{o_card}** Parry Penetrated! **{t_card}** takes **{round(oparry_damage * .40)}**! DMG and breaks the **Parry**")
                                                            oparry_count = oparry_count - 1
                                                            if tarm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                tarm_barrier_active=False
                                                                
                                                                previous_moves.append(f"(**{turn_total}**) **{t_card}**'s 💠 Barrier Disabled!")
                                                            #await private_channel.send(embed=embedVar)
                                                            oarm_parry_active = False
                                                    else:
                                                        if t_universe == "One Piece" and (t_card_tier in low_tier_cards or t_card_tier in mid_tier_cards or t_card_tier in high_tier_cards):
                                                            if t_focus_count == 0:
                                                                dmg['DMG'] = dmg['DMG'] * .6

                                                        if dmg['REPEL']:
                                                            t_health = t_health - int(dmg['DMG'])
                                                        elif dmg['ABSORB']:
                                                            o_health = o_health + int(dmg['DMG'])
                                                        elif dmg['ELEMENT'] == water_element:
                                                            if tmove1_element == water_element:
                                                                t_basic_water_buff = t_basic_water_buff + 40
                                                            if tmove2_element == water_element:
                                                                t_special_water_buff = t_special_water_buff + 40
                                                            if tmove3_element == water_element:
                                                                t_ultimate_water_buff = t_ultimate_water_buff + 40
                                                            o_health = o_health - (dmg['DMG'] + t_water_buff)

                                                        elif dmg['ELEMENT'] == earth_element:
                                                            t_defense = t_defense + (dmg['DMG'] * .25)
                                                            o_health = o_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == recoil_element:
                                                            t_health = t_health - (dmg['DMG'] * .60)
                                                            if t_health <= 0:
                                                                t_health = 1
                                                            o_health = o_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == time_element:
                                                            if t_stamina <= 80:
                                                                t_stamina = 0
                                                            t_block_used = True
                                                            t_defense = round(t_defense * 2)
                                                            previous_moves.append(f"**{t_card}** Blocked 🛡️")

                                                            o_health = o_health - dmg['DMG']


                                                        elif dmg['ELEMENT'] == death_element:
                                                            o_max_health = o_max_health - (dmg['DMG'] * .20)
                                                            o_health = o_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == light_element:
                                                            t_stamina = round(t_stamina + (dmg['STAMINA_USED'] / 2))
                                                            t_attack = t_attack + (dmg['DMG'] * .20)
                                                            o_health = o_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == dark_element:
                                                            player1_card.stamina = player1_card.stamina - 15
                                                            o_health = o_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == life_element:
                                                            t_health = t_health + (dmg['DMG'] * .20)
                                                            o_health = o_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == psychic_element:
                                                            o_defense = o_defense - (dmg['DMG'] * .15)
                                                            o_attack = o_attack - (dmg['DMG'] * .15)
                                                            o_health = o_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == fire_element:
                                                            t_burn_dmg = t_burn_dmg + round(dmg['DMG'] * .25)
                                                            o_health = o_health - dmg['DMG']


                                                        elif dmg['ELEMENT'] == electric_element:
                                                            t_shock_buff = t_shock_buff +  (dmg['DMG'] * .15)
                                                            o_health = o_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == poison_element:
                                                            if t_poison_dmg <= 600:
                                                                t_poison_dmg = t_poison_dmg + 30
                                                            o_health = o_health - dmg['DMG']
    
                                                        elif dmg['ELEMENT'] == ice_element:
                                                            t_ice_counter = t_ice_counter + 1
                                                            if t_ice_counter == 2:
                                                                t_freeze_enh = True
                                                                t_ice_counter = 0
                                                            o_health = o_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == bleed_element:
                                                            t_bleed_counter = t_bleed_counter + 1
                                                            if t_bleed_counter == 3:
                                                                t_bleed_hit = True
                                                                t_bleed_counter = 0
                                                            o_health = o_health - dmg['DMG']
                                                            
                                                        elif dmg['ELEMENT'] == gravity_element:
                                                            t_gravity_hit = True
                                                            o_health = o_health - dmg['DMG']
                                                            o_defense = o_defense - (dmg['DMG'] * .25)
                                                        
                                                        else:
                                                            o_health = o_health - dmg['DMG']


                                                        embedVar = discord.Embed(title=f"{dmg['MESSAGE']}", colour=embed_color_t)
                                                        previous_moves.append(f"(**{turn_total}**) **{t_card}**: {dmg['MESSAGE']}")
                                                        if tarm_siphon_active:
                                                            siphon_damage = (dmg['DMG'] * .15) + tsiphon_value
                                                            t_health = round(t_health + siphon_damage)
                                                            if t_health >= t_max_health:
                                                                t_health = t_max_health
                                                                previous_moves.append(f"(**{turn_total}**) **{t_card}**: 💉 Siphoned **Full Health!**")
                                                            else:
                                                                previous_moves.append(f"(**{turn_total}**) **{t_card}**: 💉 Siphoned **{round(siphon_damage)}** Health!")
                                                        if tarm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                            tarm_barrier_active=False
                                                            
                                                            previous_moves.append(f"(**{turn_total}**) **{t_card}**'s 💠 Barrier Disabled!")
                                                        #await private_channel.send(embed=embedVar)
                                                    if o_health <= 0:
                                                        if o_final_stand==True:
                                                            if o_universe == "Dragon Ball Z":
                                                                embedVar = discord.Embed(title=f"{o_card}'s LAST STAND", description=f"{o_card} FINDS RESOLVE", colour=0xe91e63)
                                                                embedVar.add_field(name=f"**{o_card}** Resolved and continues to fight", value="All stats & stamina increased")
                                                                previous_moves.append(f"(**{turn_total}**) **{o_card}** 🩸 Transformation: Last Stand!!!")
                                                                if tarm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                    tarm_barrier_active=False
                                                                    
                                                                    previous_moves.append(f"(**{turn_total}**) **{t_card}**'s 💠 Barrier Disabled!")
                                                                #await private_channel.send(embed=embedVar)
                                                                o_health = int(.75 * (o_attack + o_defense))
                                                                
                                                                player1_card.stamina = 100
                                                                o_used_resolve = True
                                                                o_final_stand = False
                                                                o_used_focus = True
                                                                t_stamina = t_stamina - int(dmg['STAMINA_USED'])
                                                                turn_total = turn_total + 1
                                                                turn = 0
                                                        else:
                                                            o_health = 0
                                                            t_stamina = t_stamina - int(dmg['STAMINA_USED'])
                                                            turn_total = turn_total + 1
                                                    else:
                                                        t_stamina = t_stamina - int(dmg['STAMINA_USED'])
                                                        turn_total = turn_total + 1
                                                        turn = 0
                                            else:
                                                previous_moves.append(f"(**{turn_total}**) **{t_card}** not enough Stamina to use this move") 
                                                turn = 3
                                        else:
                                            if dmg['CAN_USE_MOVE']:
                                                if dmg['ENHANCE']:
                                                    enh_type = dmg['ENHANCED_TYPE']
                                                    if enh_type == 'ATK':
                                                        t_attack = round(t_attack + dmg['DMG'])
                                                    elif enh_type == 'DEF':
                                                        t_defense = round(t_defense + dmg['DMG'])
                                                    elif enh_type == 'STAM':
                                                        t_stamina = round(t_stamina + dmg['DMG'])
                                                    elif enh_type == 'HLT':
                                                        t_health = round(t_health + dmg['DMG'])
                                                    elif enh_type == 'LIFE':
                                                        t_health = round(t_health + dmg['DMG'])
                                                        c_health = round(c_health - dmg['DMG'])
                                                    elif enh_type == 'DRAIN':
                                                        t_stamina = round(t_stamina + dmg['DMG'])
                                                        c_stamina = round(c_stamina - dmg['DMG'])
                                                    elif enh_type == 'FLOG':
                                                        t_attack = round(t_attack + dmg['DMG'])
                                                        c_attack = round(c_attack - dmg['DMG'])
                                                    elif enh_type == 'WITHER':
                                                        t_defense = round(t_defense + dmg['DMG'])
                                                        c_defense = round(t_defense - dmg['DMG'])
                                                    elif enh_type == 'RAGE':
                                                        t_defense = round(t_defense - dmg['DMG'])
                                                        t_ap_buff = round(t_ap_buff + dmg['DMG'])
                                                    elif enh_type == 'BRACE':
                                                        t_ap_buff = round(t_ap_buff + dmg['DMG'])
                                                        t_attack = round(t_attack - dmg['DMG'])
                                                    elif enh_type == 'BZRK':
                                                        t_health = round(t_health - dmg['DMG'])
                                                        t_attack = round(t_attack + (dmg['DMG']))
                                                    elif enh_type == 'CRYSTAL':
                                                        t_health = round(t_health - dmg['DMG'])
                                                        t_defense = round(t_defense + dmg['DMG'])
                                                    elif enh_type == 'GROWTH':
                                                        t_max_health = round(t_max_health - (t_max_health * .10))
                                                        t_defense = round(t_defense + dmg['DMG'])
                                                        t_attack= round(t_attack + dmg['DMG'])
                                                        t_ap_buff = round(t_ap_buff + dmg['DMG'])
                                                    elif enh_type == 'STANCE':
                                                        tempattack = dmg['DMG']
                                                        t_attack = t_defense
                                                        t_defense = tempattack
                                                    elif enh_type == 'CONFUSE':
                                                        tempattack = dmg['DMG']
                                                        c_attack = c_defense
                                                        c_defense = tempattack
                                                    elif enh_type == 'BLINK':
                                                        t_stamina = round(t_stamina - dmg['DMG'])
                                                        c_stamina = round(c_stamina + dmg['DMG'])
                                                    elif enh_type == 'SLOW':
                                                        tempstam = round(c_stamina + dmg['DMG'])
                                                        t_stamina = round(t_stamina - dmg['DMG'])
                                                        c_stamina = t_stamina
                                                        t_stamina = tempstam
                                                    elif enh_type == 'HASTE':
                                                        tempstam = round(c_stamina - dmg['DMG'])
                                                        t_stamina = round(t_stamina + dmg['DMG'])
                                                        c_stamina = t_stamina
                                                        t_stamina = tempstam
                                                    elif enh_type == 'SOULCHAIN':
                                                        t_stamina = round(dmg['DMG'])
                                                        c_stamina = t_stamina
                                                    elif enh_type == 'GAMBLE':
                                                        if mode in D_modes:
                                                            t_health = round(dmg['DMG']) * 3
                                                            c_health = round(dmg['DMG'])
                                                        elif mode in B_modes:
                                                            t_health = round(dmg['DMG']) * 4
                                                            c_health = round(dmg['DMG'])
                                                        else:
                                                            t_health = round(dmg['DMG']) * 2
                                                            c_health = round(dmg['DMG'])
                                                    elif enh_type == 'FEAR':
                                                        if t_universe != "Chainsawman":
                                                            t_max_health = round(t_max_health - (t_max_health * .10))
                                                        c_attack = round(c_attack - dmg['DMG'])
                                                        c_defense = round(c_defense - dmg['DMG'])
                                                        c_ap_buff = round(c_ap_buff - dmg['DMG'])
                                                    elif enh_type == 'WAVE':
                                                        c_health = round(c_health - dmg['DMG'])
                                                    elif enh_type == 'BLAST':
                                                        if dmg['DMG'] >= 700:
                                                            dmg['DMG'] = 700

                                                        c_health = round(c_health - dmg['DMG'])
                                                    elif enh_type == 'CREATION':
                                                        t_max_health = round(t_max_health + dmg['DMG'])
                                                        t_health = round(t_health + dmg['DMG'])
                                                    elif enh_type == 'DESTRUCTION':
                                                        # t_max_health = round(t_max_health - dmg['DMG'])
                                                        c_max_health = round(c_max_health - dmg['DMG'])
                                                        # if t_max_health <=1:
                                                        #     t_max_health = 1
                                                        if c_max_health <=1:
                                                            c_max_health = 1
                                                    if enh_type in Stamina_Enhancer_Check or enh_type in Time_Enhancer_Check or enh_type in Control_Enhancer_Check:
                                                        t_stamina = t_stamina
                                                    else:
                                                        t_stamina = t_stamina - int(dmg['STAMINA_USED'])
                                                    embedVar = discord.Embed(title=f"{dmg['MESSAGE']}",
                                                                            colour=embed_color_t)
                                                    #await private_channel.send(embed=embedVar)
                                                    previous_moves.append(f"(**{turn_total}**) **{t_card}**: 🦠 {dmg['MESSAGE']}")
                                                    turn_total = turn_total + 1
                                                    turn = 0
                                                elif dmg['DMG'] == 0:
                                                    t_stamina = t_stamina - int(dmg['STAMINA_USED'])
                                                    embedVar = discord.Embed(title=f"{dmg['MESSAGE']}", colour=embed_color_t)
                                                    previous_moves.append(f"(**{turn_total}**) **{t_card}**: {dmg['MESSAGE']}")
                                                    if tarm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                        tarm_barrier_active=False
                                                        
                                                        previous_moves.append(f"(**{turn_total}**) **{t_card}**'s 💠 Barrier Disabled!")
                                                    #await private_channel.send(embed=embedVar)
                                                    turn_total = turn_total + 1
                                                    turn = 0
                                                else:
                                                    if c_universe == "Naruto" and c_stamina < 10:
                                                        c_stored_damage = round(dmg['DMG'])
                                                        c_naruto_heal_buff = c_naruto_heal_buff + c_stored_damage
                                                        c_health = c_health 
                                                        embedVar = discord.Embed(title=f"{c_card}: Substitution Jutsu", description=f"{t_card} strikes a log", colour=0xe91e63)
                                                        previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸: Substitution Jutsu")
                                                        if not c_used_resolve:
                                                            previous_moves.append(f"(**{turn_total}**) 🩸**{c_stored_damage}** Hasirama Cells stored. 🩸**{c_naruto_heal_buff}** total stored.")
                                                        if tarm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                            tarm_barrier_active=False
                                                            
                                                            previous_moves.append(f"(**{turn_total}**) **{t_card}**'s 💠 Barrier Disabled!")
                                                        #await private_channel.send(embed=embedVar)
                                                    elif carm_shield_active and dmg['ELEMENT'] != dark_element:
                                                        if dmg['ELEMENT'] == poison_element: #Poison Update
                                                            if t_poison_dmg <= 600:
                                                                t_poison_dmg = o_poison_dmg + 30
                                                            c_health = c_health - dmg['DMG']
                                                        if cshield_value > 0:
                                                            cshield_value = cshield_value -dmg['DMG']
                                                            c_health = c_health 
                                                            if cshield_value <=0:
                                                                embedVar = discord.Embed(title=f"{c_card}'s' **Shield** Shattered!", description=f"{t_card} breaks the **Shield**!", colour=0xe91e63)
                                                                previous_moves.append(f"(**{turn_total}**) **{c_card}'s** 🌐 Shield Shattered!")
                                                                if tarm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                    tarm_barrier_active=False
                                                                    
                                                                    previous_moves.append(f"(**{turn_total}**) **{t_card}**'s 💠 Barrier Disabled!")
                                                                #await private_channel.send(embed=embedVar)
                                                                carm_shield_active = False
                                                            else:
                                                                embedVar = discord.Embed(title=f"{c_card} Activates **Shield** 🌐", description=f"**{t_card}** strikes the Shield 🌐\n**{cshield_value} Shield** Left!", colour=0xe91e63)
                                                                previous_moves.append(f"(**{turn_total}**) **{t_card}** strikes **{c_card}**'s Shield 🌐\n**{cshield_value} Shield** Left!")
                                                                if tarm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                    tarm_barrier_active=False
                                                                    
                                                                    previous_moves.append(f"(**{turn_total}**) **{t_card}**'s 💠 Barrier Disabled!")
                                                                #await private_channel.send(embed=embedVar)

                                                    elif carm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                        if cbarrier_count >1:
                                                            c_health = c_health 
                                                            embedVar = discord.Embed(title=f"{c_card} Activates **Barrier** 💠", description=f"{t_card}'s attack **Nullified**!\n 💠{cbarrier_count - 1} **Barriers** remain!", colour=0xe91e63)
                                                            previous_moves.append(f"(**{turn_total}**) **{c_card}** Activates Barrier 💠 {t_card}'s attack **Nullified**!\n💠 {cbarrier_count - 1} **Barriers** remain!")
                                                            if tarm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                tarm_barrier_active=False
                                                                
                                                                previous_moves.append(f"(**{turn_total}**) **{t_card}**'s 💠 Barrier Disabled!")
                                                            #await private_channel.send(embed=embedVar)
                                                            cbarrier_count = cbarrier_count - 1
                                                        elif cbarrier_count==1:
                                                            embedVar = discord.Embed(title=f"{c_card}'s **Barrier** Broken!", description=f"{t_card} destroys the **Barrier**", colour=0xe91e63)
                                                            previous_moves.append(f"(**{turn_total}**) **{c_card}**'s Barrier Broken!")
                                                            cbarrier_count = cbarrier_count - 1
                                                            if tarm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                tarm_barrier_active=False
                                                                
                                                                previous_moves.append(f"(**{turn_total}**) **{t_card}**'s 💠 Barrier Disabled!")
                                                            #await private_channel.send(embed=embedVar)
                                                            carm_barrier_active = False
                                                    elif carm_parry_active and dmg['ELEMENT'] != earth_element:
                                                        if cparry_count > 1:
                                                            c_health = c_health
                                                            cparry_damage = round(dmg['DMG'])
                                                            c_health = round(c_health - (cparry_damage * .75))
                                                            t_health = round(t_health - (cparry_damage * .40))
                                                            cparry_count = cparry_count - 1
                                                            
                                                            previous_moves.append(f"(**{turn_total}**) **{c_card}** Activates Parry 🔄 after **{round(cparry_damage * .75)}** dmg dealt: {t_card} takes {round(cparry_damage * .40)}! DMG\n **{cparry_count}  Parries** to go!!")
                                                            if tarm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                tarm_barrier_active=False
                                                                embedVar.add_field(name=f"{t_card}'s **Barrier** Disabled!", value =f"*Maximize **Barriers** with your Enhancer!**")
                                                                previous_moves.append(f"(**{turn_total}**) **{t_card}**'s 💠 Barrier Disabled!")
                                                            #await private_channel.send(embed=embedVar)
                                                            
                                                        elif cparry_count==1:
                                                            c_health = c_health
                                                            cparry_damage = round(dmg['DMG'])
                                                            c_health = round(c_health - (cparry_damage * .75))
                                                            t_health = round(t_health - (cparry_damage * .40))
                                                            embedVar = discord.Embed(title=f"{c_card} **Parry** Penetrated!!", description=f"{t_card} takes {round(cparry_damage * .40)}! DMG and breaks the **Parry**", colour=0xe91e63)
                                                            previous_moves.append(f"(**{turn_total}**) **{c_card}** Parry Penetrated! **{t_card}** takes **{round(cparry_damage * .40)}**! DMG and breaks the **Parry**")
                                                            cparry_count = cparry_count - 1
                                                            if tarm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                tarm_barrier_active=False
                                                                
                                                                previous_moves.append(f"(**{turn_total}**) **{t_card}**'s 💠 Barrier Disabled!")
                                                            #await private_channel.send(embed=embedVar)
                                                            carm_parry_active = False
                                                    else:
                                                        if t_universe == "One Piece" and (t_card_tier in low_tier_cards or t_card_tier in mid_tier_cards or t_card_tier in high_tier_cards):
                                                            if t_focus_count == 0:
                                                                dmg['DMG'] = dmg['DMG'] * .6

                                                        if dmg['REPEL']:
                                                            t_health = t_health - int(dmg['DMG'])
                                                        elif dmg['ABSORB']:
                                                            c_health = c_health + int(dmg['DMG'])
                                                        elif dmg['ELEMENT'] == water_element:
                                                            if tmove1_element == water_element:
                                                                t_basic_water_buff = t_basic_water_buff + 40
                                                            if tmove2_element == water_element:
                                                                t_special_water_buff = t_special_water_buff + 40
                                                            if tmove3_element == water_element:
                                                                t_ultimate_water_buff = t_ultimate_water_buff + 40
                                                            c_health = c_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == ice_element:
                                                            t_ice_counter = t_ice_counter + 1
                                                            if t_ice_counter == 2:
                                                                t_freeze_enh = True
                                                                t_ice_counter = 0
                                                            c_health = c_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == time_element:
                                                            if t_stamina <= 80:
                                                                t_stamina = 0
                                                            t_block_used = True
                                                            t_defense = round(t_defense * 2)
                                                            previous_moves.append(f"**{t_card}** Blocked 🛡️")
                                                            c_health = c_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == bleed_element:
                                                            t_bleed_counter = t_bleed_counter + 1
                                                            if t_bleed_counter == 3:
                                                                t_bleed_hit = True
                                                                t_bleed_counter = 0
                                                            c_health = c_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == recoil_element:
                                                            t_health = t_health - (dmg['DMG'] * .60)
                                                            if t_health <= 0:
                                                                t_health = 1
                                                            c_health = c_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == earth_element:
                                                            t_defense = t_defense + (dmg['DMG'] * .25)
                                                            c_health = c_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == death_element:
                                                            c_max_health = c_max_health - (dmg['DMG'] * .20)
                                                            c_health = c_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == light_element:
                                                            t_stamina = round(t_stamina + (dmg['STAMINA_USED'] / 2))
                                                            t_attack = t_attack + (dmg['DMG'] * .20)
                                                            c_health = c_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == dark_element:
                                                            c_stamina = c_stamina - 15
                                                            c_health = c_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == life_element:
                                                            t_health = t_health + (dmg['DMG'] * .20)
                                                            c_health = c_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == psychic_element:
                                                            c_defense = c_defense - (dmg['DMG'] * .15)
                                                            c_attack = c_attack - (dmg['DMG'] * .15)
                                                            c_health = c_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == fire_element:
                                                            t_burn_dmg = t_burn_dmg + round(dmg['DMG'] * .25)
                                                            c_health = c_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == electric_element:
                                                            t_shock_buff = t_shock_buff +  (dmg['DMG'] * .15)
                                                            c_health = c_health - dmg['DMG']

                                                        elif dmg['ELEMENT'] == poison_element:
                                                            if t_poison_dmg <= 600:
                                                                t_poison_dmg = t_poison_dmg + 30
                                                            c_health = c_health - dmg['DMG']
                                                            
                                                        elif dmg['ELEMENT'] == gravity_element:
                                                            t_gravity_hit = True
                                                            c_health = c_health - dmg['DMG']
                                                            c_defense = c_defense - (dmg['DMG'] * .25)
                                                        
                                                        else:
                                                            c_health = c_health - dmg['DMG']



                                                        embedVar = discord.Embed(title=f"{dmg['MESSAGE']}", colour=embed_color_t)
                                                        previous_moves.append(f"(**{turn_total}**) **{t_card}**: {dmg['MESSAGE']}")
                                                        if tarm_siphon_active:
                                                            siphon_damage = (dmg['DMG'] * .15) + tsiphon_value
                                                            t_health = round(t_health + siphon_damage)
                                                            if t_health >= t_max_health:
                                                                t_health = t_max_health
                                                                previous_moves.append(f"(**{turn_total}**) **{t_card}**: 💉 Siphoned **Full Health!**")
                                                            else:
                                                                previous_moves.append(f"(**{turn_total}**) **{t_card}**: 💉 Siphoned **{round(siphon_damage)}** Health!")
                                                        if tarm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                            tarm_barrier_active=False
                                                            
                                                            previous_moves.append(f"(**{turn_total}**) **{t_card}**'s 💠 Barrier Disabled!")
                                                        #await private_channel.send(embed=embedVar)
                                                    if c_health <= 0:
                                                        if c_final_stand==True:
                                                            if c_universe == "Dragon Ball Z":
                                                                embedVar = discord.Embed(title=f"{c_card}'s LAST STAND", description=f"{c_card} FINDS RESOLVE", colour=0xe91e63)
                                                                embedVar.add_field(name=f"{c_card} resolved and continues to fight", value="All stats & stamina increased")
                                                                previous_moves.append(f"(**{turn_total}**) **{c_card}** 🩸 Transformation: Last Stand!!!")
                                                                if tarm_barrier_active and dmg['ELEMENT'] != psychic_element:
                                                                    tarm_barrier_active=False
                                                                    
                                                                    previous_moves.append(f"(**{turn_total}**) **{t_card}**'s 💠 Barrier Disabled!")
                                                                #await private_channel.send(embed=embedVar)
                                                                c_health = int(.75 * (c_attack + c_defense))
                                                                
                                                                c_used_resolve = True
                                                                c_used_focus = True
                                                                c_final_stand = False
                                                                t_stamina = t_stamina - int(dmg['STAMINA_USED'])
                                                                turn_total = turn_total + 1
                                                                turn = 2
                                                        else:
                                                            c_health = 0
                                                            t_stamina = t_stamina - int(dmg['STAMINA_USED'])
                                                            turn_total = turn_total + 1
                                                    else:
                                                        t_stamina = t_stamina - int(dmg['STAMINA_USED'])
                                                        turn_total = turn_total + 1
                                                        turn = 0
                                            else:
                                                #await private_channel.send(m.NOT_ENOUGH_STAMINA)
                                                previous_moves.append(f"(**{turn_total}**) **{t_card}** not enough Stamina to use this move")
                                                turn = 3

                        # End the match
                    if (((o_health <= 0 or c_health <= 0) and _battle._is_co_op) or (
                            o_max_health <= 0 or c_max_health <= 0) and _battle._is_co_op) or (
                            (o_health <= 0 or o_max_health <= 0) and mode not in co_op_modes):
                        mode = original_mode
                        if previous_moves:
                            if previous_moves_len ==0:
                                previous_moves_into_embed = "\n\n".join(previous_moves)
                                #previous_moves_into_embed = f"You got One Shot! Try Again..."  
                            elif previous_moves_len >= 6:
                                previous_moves = previous_moves[-5:]
                                previous_moves_into_embed = "\n\n".join(previous_moves)
                            else:
                                previous_moves_into_embed = "\n\n".join(previous_moves)
                            

                        if mode in PVP_MODES or mode =="RAID":
                            try:
                                # await ctx.send(f":zap: {user2.mention} you win the match!")
                                uid = t_DID
                                ouid = sowner['DID']
                                tuser = await self.bot.fetch_user(uid)
                                ouser = await self.bot.fetch_user(ouid)
                                wintime = time.asctime()
                                h_playtime = int(wintime[11:13])
                                m_playtime = int(wintime[14:16])
                                s_playtime = int(wintime[17:19])
                                gameClock = getTime(int(h_gametime), int(m_gametime), int(s_gametime), h_playtime, m_playtime,
                                                    s_playtime)
                                match = await savematch(str(tuser), str(t_card), str(t_card_path), str(ttitle['TITLE']),
                                                        str(tarm['ARM']), "N/A", "PVP", o['EXCLUSIVE'])
                                
                                sownerctx = await self.bot.fetch_user(ouid)
                                if mode == "RAID":
                                    guild_query = {'FDID': oguild['FDID']}
                                    guild_info = db.queryGuild(guild_query)
                                    fee = universe['FEE']
                                    guildwin = db.updateGuild(guild_query, {'$inc': {'BOUNTY': fee, 'STREAK': 1}})
                                    bounty = oguild['BOUNTY']
                                    bonus = oguild['STREAK']
                                    total_bounty = (bounty + ((bonus / 100) * bounty))
                                    wage = .50 * total_bounty
                                # response = await score(sownerctx, tuser)
                                await crown_utilities.curse(30, str(ctx.author.id))
                                await crown_utilities.bless(80, tuser.id)
                                loss_value = {"$inc": {"PVP_LOSS" : 1}}#MATCH UPDATE
                                oquery = {'DID': str(o_DID)}
                                loss_update = db.updateUserNoFilter(oquery, loss_value)
                                win_value = {"$inc": {"PVP_WINS" : 1}}
                                tquery = {'DID': str(t_DID)}
                                win_update = db.updateUserNoFilter(tquery, win_value)
                                if tguild:
                                    await crown_utilities.bless(15, str(tuser.id))
                                    await crown_utilities.blessteam(25, cteam)
                                    await teamwin(cteam)
                                    await crown_utilities.blessguild(60, tguild)
                                    if oguild:
                                        await crown_utilities.curse(7, str(tuser.id))
                                        await crown_utilities.curseteam(15, oteam)
                                        await teamloss(oteam)
                                        await crown_utilities.curseguild(30, oguild)

                                if arena_flag and arena_type == "SINGLES":
                                    arena = db.queryArena({"OWNER": str(arena_owner), "ACTIVE": True})
                                    guild1_lost = False
                                    for member in arena['GUILD1_MEMBERS']:
                                        if member['NAME'] == sowner['DISNAME'] and member['STRIKES'] == 1:
                                            guild1_lost = True
                                    guild2_lost = False
                                    for member in arena['GUILD2_MEMBERS']:
                                        if member['NAME'] == opponent['DISNAME'] and member['STRIKES'] == 1:
                                            guild2_lost = True
                                    if guild1_lost:
                                        query = {'OWNER': sowner['DISNAME'], "ACTIVE": True}
                                        update_query = {
                                            '$inc': {'GUILD1_MEMBERS.$[type].' + 'STRIKES': 1},
                                            '$set': {'ACTIVE': False, "WINNER": str(opponent['DISNAME']), "LOSER": str(sowner['DISNAME'])}
                                            }
                                        filter_query = [{'type.' + "NAME": str(sowner['DISNAME'])}]
                                        res = db.updateArena(query, update_query, filter_query)
                                        await crown_utilities.bless(10000, str(tuser.id))
                                        # await ctx.send(f"{ouser.mention} has won the 1v1, earning :coin: 10,000!")
                                        await battle_msg.delete(delay=2)
                                        await asyncio.sleep(2)
                                        battle_msg = await private_channel.send(content=f"{ouser.mention} has won the 1v1, earning :coin: 10,000!")

                                    else:
                                        query = {'OWNER': sowner['DISNAME'], "ACTIVE": True}
                                        update_query = {
                                            '$inc': {'GUILD1_MEMBERS.$[type].' + 'STRIKES': 1}
                                            }
                                        filter_query = [{'type.' + "NAME": str(sowner['DISNAME'])}]
                                        res = db.updateArena(query, update_query, filter_query)
                                        # print("This oneee")
                                        # await ctx.send(f"{tuser.mention} ❌")
                                        await battle_msg.delete(delay=2)
                                        await asyncio.sleep(2)
                                        battle_msg = await private_channel.send(content=f"{tuser.mention} ❌")
                                if mode == "RAID":
                                    embedVar = discord.Embed(title=f"🛡️ **{t_card}** defended the {oguild['GNAME']}\nMatch concluded in {turn_total} turns",
                                        description=textwrap.dedent(f"""
                                                                    {previous_moves_into_embed}
                                                                    """),
                                        colour=0x1abc9c)
                                    embedVar.set_author(name=f"{o_card} says:\n{o_lose_description}")
                                    if int(gameClock[0]) == 0 and int(gameClock[1]) == 0:
                                        embedVar.set_footer(text=f"Battle Time: {gameClock[2]} Seconds.")
                                    elif int(gameClock[0]) == 0:
                                        embedVar.set_footer(text=f"Battle Time: {gameClock[1]} Minutes and {gameClock[2]} Seconds.")
                                    else:
                                        embedVar.set_footer(
                                            text=f"Battle Time: {gameClock[0]} Hours {gameClock[1]} Minutes and {gameClock[2]} Seconds.")
                                    embedVar.add_field(name="🔢 Focus Count",
                                                    value=f"**{o_card}**: {o_focus_count}\n**{t_card}**: {t_focus_count}")
                                    if o_focus_count >= t_focus_count:
                                        embedVar.add_field(name="🌀 Most Focused", value=f"**{o_card}**")
                                    else:
                                        embedVar.add_field(name="🌀 Most Focused", value=f"**{t_card}**")
                                        await battle_msg.delete(delay=2)
                                    battle_msg = await private_channel.send(embed=embedVar)
                                    continued =False
                                    return
                                else:
                                    victory_message = f":zap: {t_card} VICTORY"
                                    victory_description = f"Match concluded in {turn_total} turns."
                                    if botActive:
                                        victory_message = f":zap: TRY AGAIN"
                                        victory_description = f"Remember to equip **Talismans**, **Titles** and **Arms** to apply **Enhancers** in battle!\nMatch concluded in {turn_total} turns."
                                    embedVar = discord.Embed(title=f"{victory_message}",
                                                            description=f"{victory_description}\n{previous_moves_into_embed}",
                                                            colour=0x1abc9c)
                                    embedVar.set_author(name=f"{o_card} says:\n{o_lose_description}")
                                    if int(gameClock[0]) == 0 and int(gameClock[1]) == 0:
                                        embedVar.set_footer(text=f"Battle Time: {gameClock[2]} Seconds.")
                                    elif int(gameClock[0]) == 0:
                                        embedVar.set_footer(text=f"Battle Time: {gameClock[1]} Minutes and {gameClock[2]} Seconds.")
                                    else:
                                        embedVar.set_footer(
                                            text=f"Battle Time: {gameClock[0]} Hours {gameClock[1]} Minutes and {gameClock[2]} Seconds.")
                                    embedVar.add_field(name="🔢 Focus Count",
                                                    value=f"**{o_card}**: {o_focus_count}\n**{t_card}**: {t_focus_count}")
                                    if o_focus_count >= t_focus_count:
                                        embedVar.add_field(name="🌀 Most Focused", value=f"**{o_card}**")
                                    else:
                                        embedVar.add_field(name="🌀 Most Focused", value=f"**{t_card}**")
                                    # await ctx.send(embed=embedVar)
                                    await battle_msg.delete(delay=2)
                                    await asyncio.sleep(2)
                                    battle_msg = await private_channel.send(embed=embedVar)
                                    continued = False
                                    return
                            except Exception as ex:
                                trace = []
                                tb = ex.__traceback__
                                while tb is not None:
                                    trace.append({
                                        "filename": tb.tb_frame.f_code.co_filename,
                                        "name": tb.tb_frame.f_code.co_name,
                                        "lineno": tb.tb_lineno
                                    })
                                    tb = tb.tb_next
                                print(str({
                                    'type': type(ex).__name__,
                                    'message': str(ex),
                                    'trace': trace
                                }))
                                guild = self.bot.get_guild(main.guild_id)
                                channel = guild.get_channel(main.guild_channel)
                                await channel.send(f"'PLAYER': **{str(ctx.author)}**, 'GUILD': **{str(ctx.author.guild)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")
                            continued = False
                            return
                        else:
                            # await private_channel.send(f":zap: {user2.mention} you win the match!")
                            wintime = time.asctime()
                            h_playtime = int(wintime[11:13])
                            m_playtime = int(wintime[14:16])
                            s_playtime = int(wintime[17:19])
                            gameClock = getTime(int(h_gametime), int(m_gametime), int(s_gametime), h_playtime, m_playtime,
                                                s_playtime)
                            if o_user['RIFT'] == 1:
                                response = db.updateUserNoFilter({'DISNAME': str(o_user['DISNAME'])}, {'$set': {'RIFT': 0}})
                            
                            if randomized_battle:
                                embedVar = discord.Embed(title=f":zap: **{t_card}** wins the match!\nThe game lasted {turn_total} rounds.", description=textwrap.dedent(f"""
                                {previous_moves_into_embed}
                                
                                """),colour=0x1abc9c)
                                embedVar.set_author(name=f"{o_card}")
                                if int(gameClock[0]) == 0 and int(gameClock[1]) == 0:
                                    embedVar.set_footer(text=f"Battle Time: {gameClock[2]} Seconds.")
                                elif int(gameClock[0]) == 0:
                                    embedVar.set_footer(text=f"Battle Time: {gameClock[1]} Minutes and {gameClock[2]} Seconds.")
                                else:
                                    embedVar.set_footer(
                                        text=f"Battle Time: {gameClock[0]} Hours {gameClock[1]} Minutes and {gameClock[2]} Seconds.")

                                await battle_msg.delete(delay=2)
                                await asyncio.sleep(2)
                                battle_msg = await private_channel.send(embed=embedVar)
                                # await discord.TextChannel.delete(private_channel, reason=None)
                                return
                            # BOSS LOSS
                            if mode in B_modes:
                                embedVar = discord.Embed(title=f":zap: **{t_card}** Wins...\nMatch concluded in {turn_total} turns!\n{t_wins}", description=textwrap.dedent(f"""
                                {previous_moves_into_embed}
                                
                                """),colour=0x1abc9c)
                                embedVar.set_author(name=f"{o_card} says:\n{o_lose_description}",
                                                    icon_url="https://res.cloudinary.com/dkcmq8o15/image/upload/v1620236432/PCG%20LOGOS%20AND%20RESOURCES/PCGBot_1.png")
                                if int(gameClock[0]) == 0 and int(gameClock[1]) == 0:
                                    embedVar.set_footer(text=f"Battle Time: {gameClock[2]} Seconds.")
                                elif int(gameClock[0]) == 0:
                                    embedVar.set_footer(text=f"Battle Time: {gameClock[1]} Minutes and {gameClock[2]} Seconds.")
                                else:
                                    embedVar.set_footer(
                                        text=f"Battle Time: {gameClock[0]} Hours {gameClock[1]} Minutes and {gameClock[2]} Seconds.")
                                await battle_msg.delete(delay=2)
                                await asyncio.sleep(2)
                                #battle_msg = await private_channel.send(embed=embedVar)
                                # await discord.TextChannel.delete(private_channel, reason=None)

                            # Play Again Buttons
                            play_again_buttons = [
                                manage_components.create_button(
                                    style=ButtonStyle.blue,
                                    label="Start Over",
                                    custom_id="Yes"
                                ),
                                manage_components.create_button(
                                    style=ButtonStyle.red,
                                    label="End",
                                    custom_id="No"
                                )
                            ]
                            o_user = db.queryUser({'DID': o_user['DID']})
                            o_team = o_user['TEAM']
                            rematch_buff = False
                            if o_team != 'PCG':
                                team_info = db.queryTeam({'TEAM_NAME': str(o_team.lower())})
                                guild_buff_info = team_info['ACTIVE_GUILD_BUFF']
                                if guild_buff_info == 'Rematch':
                                    rematch_buff =True
                            if rematch_buff: #rematch update
                                play_again_buttons.append(
                                    manage_components.create_button(
                                        style=ButtonStyle.green,
                                        label=f"Guild Rematches Available!",
                                        custom_id="grematch"
                                    )
                                )        
                            elif o_user['RETRIES'] >= 1:
                                play_again_buttons.append(
                                    manage_components.create_button(
                                        style=ButtonStyle.green,
                                        label=f"{o_user['RETRIES']} Rematches Available!",
                                        custom_id="rematch"
                                    )
                                )
                            else:
                                rematch_buff = False
                            play_again_buttons_action_row = manage_components.create_actionrow(*play_again_buttons)
                            if mode not in B_modes and mode not in co_op_modes:
                                embedVar = discord.Embed(title=f":zap: **{t_card}** wins the match!\nThe game lasted {turn_total} rounds.", description=textwrap.dedent(f"""
                                {previous_moves_into_embed}
                                
                                """),colour=0x1abc9c)
                            if _battle._is_co_op and mode not in ai_co_op_modes:
                                teammates = False
                                fam_members =False
                                stat_bonus = 0
                                hlt_bonus = 0 
                                if o_user['TEAM'] == c_user['TEAM'] and o_user['TEAM'] != 'PCG':
                                    teammates=True
                                    stat_bonus=50
                                if o_user['FAMILY'] == c_user['FAMILY'] and o_user['FAMILY'] != 'PCG':
                                    fam_members=True
                                    hlt_bonus=100
                                
                                if teammates==True:
                                    bonus_message = f"Guild **{o_user['TEAM']}:** 🗡️**+{stat_bonus}** 🛡️**+{stat_bonus}**"
                                    if fam_members==True:
                                        bonus_message = f"Family **{o_user['FAMILY']}:** ❤️**+{hlt_bonus}**\nGuild **{o_user['TEAM']}:** 🗡️**+{stat_bonus}**\🛡️**+{stat_bonus}**"
                                elif fam_members==True:
                                        bonus_message = f"Family **{o_user['FAMILY']}:** ❤️**+{hlt_bonus}**"
                                else:
                                    bonus_message = f"Join a Guild or Create a Family for Coop Bonuses!"
                                    
                                embedVar = discord.Embed(title=f":zap: **{t_card}** wins the match!\n\n**{o_user['NAME']}** and **{c_user['NAME']}** will you play again?\nThe game lasted {turn_total} rounds.", description=textwrap.dedent(f"""
                                {previous_moves_into_embed}
                                
                                """),colour=0x1abc9c)
                                embedVar.add_field(name="**Co-Op Bonus**",
                                                value=f"{bonus_message}")
                            elif _battle._is_co_op and mode in ai_co_op_modes:
                                embedVar = discord.Embed(title=f":zap: **{t_card}** wins the match!\n\n**{o_user['NAME']}** and **{c_card}** will you play again?\nThe game lasted {turn_total} rounds.", description=textwrap.dedent(f"""
                                {previous_moves_into_embed}
                                
                                """),colour=0x1abc9c)
                                embedVar.add_field(name="**Duo Tips**",
                                                value=f"Create Duos that compliment each others Weaknesses")
                            # if int(gameClock[0]) == 0 and int(gameClock[1]) == 0:
                            #     embedVar.set_footer(text=f"Battle Time: {gameClock[2]} Seconds.")
                            # elif int(gameClock[0]) == 0:
                            #     embedVar.set_footer(text=f"Battle Time: {gameClock[1]} Minutes and {gameClock[2]} Seconds.")
                            # else:
                            #     embedVar.set_footer(
                            #         text=f"Battle Time: {gameClock[0]} Hours {gameClock[1]} Minutes and {gameClock[2]} Seconds.")
                            msg = await private_channel.send(embed=embedVar, components=[play_again_buttons_action_row])

                            if mode not in co_op_modes and mode != "Abyss":
                                play_again_selector = ctx.author
                            elif _battle._is_co_op and mode not in ai_co_op_modes:
                                play_again_selector = ctx.author
                            else:
                                play_again_selector = ctx.author

                            def check(button_ctx):
                                return button_ctx.author == play_again_selector

                            try:
                                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[
                                    play_again_buttons_action_row], timeout=300, check=check)

                                if button_ctx.custom_id == "No":
                                    await msg.edit(components=[])
                                    await button_ctx.defer(ignore=True)
                                    return

                                if button_ctx.custom_id == "Yes":
                                    currentopponent = 0
                                    continued = True
                                    
                                if button_ctx.custom_id == "rematch":
                                    new_info = await crown_utilities.updateRetry(button_ctx.author.id, "U","DEC")
                                    continued = True
                                if button_ctx.custom_id == "grematch":
                                    new_info = await crown_utilities.guild_buff_update_function(str(o_team.lower()))
                                    update_team_response = db.updateTeam(new_info['QUERY'], new_info['UPDATE_QUERY'])
                                    continued = True
                            except asyncio.TimeoutError:
                                continued = False
                                # await discord.TextChannel.delete(private_channel, reason=None)

                    elif t_health <= 0 or t_max_health <= 0:
                        mode = original_mode
                        if previous_moves:
                            if previous_moves_len ==0:
                                previous_moves_into_embed = "\n\n".join(previous_moves)
                                #previous_moves_into_embed = f"**{t_card}** GOT DROPPED! **{o_card}** ONE SHOT THEM!"  
                            elif previous_moves_len >= 6:
                                previous_moves = previous_moves[-6:]
                                previous_moves_into_embed = "\n\n".join(previous_moves)
                            else:
                                previous_moves_into_embed = "\n\n".join(previous_moves)
                        # print(previous_moves_into_embed)
                        if mode in PVP_MODES or mode == "RAID":
                            try:
                                uid = o_DID
                                tuid = t_DID
                                ouser = await self.bot.fetch_user(uid)
                                tuser = await self.bot.fetch_user(tuid)
                                wintime = time.asctime()
                                h_playtime = int(wintime[11:13])
                                m_playtime = int(wintime[14:16])
                                s_playtime = int(wintime[17:19])
                                gameClock = getTime(int(h_gametime), int(m_gametime), int(s_gametime), h_playtime, m_playtime,
                                                    s_playtime)
                                ouid = sowner['DID']
                                sownerctx = await self.bot.fetch_user(ouid)
                                if mode == "RAID":
                                    guild_query = {'FDID': oguild['FDID']}
                                    bounty = oguild['BOUNTY']
                                    bonus = oguild['STREAK']
                                    total_bounty = (bounty + ((bonus / 100) * bounty))
                                    winbonus = int(((bonus / 100) * bounty))
                                    if winbonus == 0:
                                        winbonus = bounty
                                    wage = int(total_bounty)
                                    endmessage = f":yen: SHIELD BOUNTY CLAIMED :coin: {'{:,}'.format(winbonus)}"
                                    hall_info = db.queryHall({"HALL":oguild['HALL']})
                                    fee = hall_info['FEE']
                                    if title_match_active:
                                        if shield_test_active:
                                            endmessage = f":flags: {oguild['GNAME']} DEFENSE TEST OVER!"
                                        elif shield_training_active:
                                            endmessage = f":flags: {oguild['GNAME']} TRAINING COMPLETE!"
                                        else:
                                            newshield = db.updateGuild(guild_query, {'$set': {'SHIELD': str(ctx.author)}})
                                            newshieldid = db.updateGuild(guild_query, {'$set': {'SDID': str(ctx.author.id)}})
                                            guildwin = db.updateGuild(guild_query, {'$set': {'BOUNTY': winbonus, 'STREAK': 1}})
                                            endmessage = f":flags: {oguild['GNAME']} SHIELD CLAIMED!"
                                            prev_team_update = {'$set': {'SHIELDING': False}}
                                            remove_shield = db.updateTeam({'TEAM_NAME': str(tteam)}, prev_team_update)
                                            update_shielding = {'$set': {'SHIELDING': True}}
                                            add_shield = db.updateTeam({'TEAM_NAME': str(oteam)}, update_shielding)
                                    else:
                                        guildloss = db.updateGuild(guild_query, {'$set': {'BOUNTY': fee, 'STREAK': 0}})
                                
                                talisman_response = crown_utilities.inc_talisman(ouid, o_talisman)
                                # response = await score(sownerctx, ouser)
                                await crown_utilities.bless(10000, str(ctx.author.id))
                                # await crown_utilities.curse(3000, str(tuser.id))
                                win_value = {"$inc": {"PVP_WINS" : 1}}#MATCH UPDATE
                                oquery = {'DID': str(o_DID)}
                                win_update = db.updateUserNoFilter(oquery, win_value)
                                loss_value = {"$inc": {"PVP_LOSS" : 1}}
                                tquery = {'DID': str(t_DID)}
                                loss_update = db.updateUserNoFilter(tquery, loss_value)
                                if oguild:
                                    await crown_utilities.bless(15, str(ctx.author.id))
                                    await crown_utilities.blessteam(25, oteam)
                                    await teamwin(oteam)
                                    await crown_utilities.blessguild(60, oguild)
                                    if tguild:
                                        await crown_utilities.curse(7, str(tuser.id))
                                        await crown_utilities.curseteam(15, tteam)
                                        await teamloss(tteam)
                                        await crown_utilities.curseguild(30, tguild)


                                if arena_flag and arena_type == "SINGLES":
                                    arena = db.queryArena({"OWNER": str(arena_owner), "ACTIVE": True})
                                    guild1_lost = False
                                    for member in arena['GUILD1_MEMBERS']:
                                        if member['NAME'] == sowner['DISNAME'] and member['STRIKES'] == 1:
                                            guild1_lost = True
                                    guild2_lost = False
                                    for member in arena['GUILD2_MEMBERS']:
                                        if member['NAME'] == opponent['DISNAME'] and member['STRIKES'] == 1:
                                            guild2_lost = True
                                    if guild2_lost:
                                        query = {'OWNER': sowner['DISNAME'], 'ACTIVE': True}
                                        update_query = {
                                            '$inc': {'GUILD2_MEMBERS.$[type].' + 'STRIKES': 1},
                                            '$set': {'ACTIVE': False, "WINNER": str(sowner['DISNAME']), "LOSER": str(opponent['DISNAME'])}
                                            }
                                        filter_query = [{'type.' + "NAME": str(opponent['DISNAME'])}]
                                        res = db.updateArena(query, update_query, filter_query)
                                        await crown_utilities.bless(10000, str(ouser.id))
                                        # await ctx.send(f"{tuser.mention} has won the 1v1, earning :coin: 10,000!")
                                        await battle_msg.delete(delay=2)
                                        await asyncio.sleep(2)
                                        battle_msg = await private_channel.send(f"{tuser.mention} has won the 1v1, earning :coin: 10,000!")

                                    else:
                                        query = {'OWNER': sowner['DISNAME'], 'ACTIVE': True}
                                        update_query = {
                                            '$inc': {'GUILD2_MEMBERS.$[type].' + 'STRIKES': 1}
                                            }
                                        filter_query = [{'type.' + "NAME": str(opponent['DISNAME'])}]
                                        res = db.updateArena(query, update_query, filter_query)
                                        
                                        # await ctx.send(f"{ouser.mention} ❌")
                                        await battle_msg.delete(delay=2)
                                        await asyncio.sleep(2)
                                        battle_msg = await private_channel.send(f"{ouser.mention} ❌")


                                match = await savematch(str(ouser), str(o_card), str(o_card_path), str(otitle['TITLE']),
                                                        str(oarm['ARM']), "N/A", "PVP", o['EXCLUSIVE'])
                                
                                if mode == "RAID":
                                    embedVar = discord.Embed(
                                        title=f"{endmessage}\n\n You have defeated the {tguild} SHIELD!\nMatch concluded in {turn_total} turns",
                                        description=textwrap.dedent(f"""
                                                                    {previous_moves_into_embed}
                                                                    
                                                                    """), colour=0xe91e63)
                                    # embedVar.set_author(name=f"{t_card} says\n{t_lose_description}")
                                    if int(gameClock[0]) == 0 and int(gameClock[1]) == 0:
                                        embedVar.set_footer(text=f"Battle Time: {gameClock[2]} Seconds.")
                                    elif int(gameClock[0]) == 0:
                                        embedVar.set_footer(text=f"Battle Time: {gameClock[1]} Minutes and {gameClock[2]} Seconds.")
                                    else:
                                        embedVar.set_footer(
                                            text=f"Battle Time: {gameClock[0]} Hours {gameClock[1]} Minutes and {gameClock[2]} Seconds.")
                                    embedVar.add_field(name="🔢 Focus Count",
                                                    value=f"**{o_card}**: {o_focus_count}\n**{t_card}**: {t_focus_count}")
                                    if o_focus_count >= t_focus_count:
                                        embedVar.add_field(name="🌀 Most Focused", value=f"**{o_card}**")
                                    else:
                                        embedVar.add_field(name="🌀 Most Focused", value=f"**{t_card}**")
                                    battle_msg = await private_channel.send(embed=embedVar)
                                    continued = False
                                    return
                                else:
                                    victory_message = f":zap: {o_card} VICTORY"
                                    victory_description = f"Match concluded in {turn_total} turns."
                                    if botActive:
                                        victory_message = f":zap: TUTORIAL VICTORY"
                                        victory_description = f"GG! Try the other **/solo** games modes!\nSelect **🌑 The Abyss** to unlock new features or choose **⚔️ Tales/Scenarios** to grind Universes!\nnMatch concluded in {turn_total} turns."
                                    
                                    embedVar = discord.Embed(title=f"{victory_message}\n{victory_description}", description=textwrap.dedent(f"""
                                    {previous_moves_into_embed}
                                    
                                    """),colour=0xe91e63)
                                    # embedVar.set_author(name=f"{t_card} says\n{t_lose_description}")
                                    if int(gameClock[0]) == 0 and int(gameClock[1]) == 0:
                                        print(gameClock[2])
                                        embedVar.set_footer(text=f"Battle Time: {gameClock[2]} Seconds.")
                                    elif int(gameClock[0]) == 0:
                                        embedVar.set_footer(text=f"Battle Time: {gameClock[1]} Minutes and {gameClock[2]} Seconds.")
                                    else:
                                        embedVar.set_footer(
                                            text=f"Battle Time: {gameClock[0]} Hours {gameClock[1]} Minutes and {gameClock[2]} Seconds.")
                                    embedVar.add_field(name="🔢 Focus Count",
                                                    value=f"**{o_card}**: {o_focus_count}\n**{t_card}**: {t_focus_count}")
                                    if o_focus_count >= t_focus_count:
                                        embedVar.add_field(name="🌀 Most Focused", value=f"**{o_card}**")
                                    else:
                                        embedVar.add_field(name="🌀 Most Focused", value=f"**{t_card}**")
                                    # await ctx.send(embed=embedVar)
                                    await battle_msg.delete(delay=2)
                                    await asyncio.sleep(2)
                                    battle_msg = await private_channel.send(embed=embedVar)


                                    continued = False
                                    return
                            except Exception as ex:
                                trace = []
                                tb = ex.__traceback__
                                while tb is not None:
                                    trace.append({
                                        "filename": tb.tb_frame.f_code.co_filename,
                                        "name": tb.tb_frame.f_code.co_name,
                                        "lineno": tb.tb_lineno
                                    })
                                    tb = tb.tb_next
                                print(str({
                                    'type': type(ex).__name__,
                                    'message': str(ex),
                                    'trace': trace
                                }))
                                guild = self.bot.get_guild(main.guild_id)
                                channel = guild.get_channel(main.guild_channel)
                                await channel.send(f"'PLAYER': **{str(ctx.author)}**, 'GUILD': **{str(ctx.author.guild)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")

                        else:
                            talisman_response = crown_utilities.inc_talisman(str(o_user['DID']), o_talisman)
                            corrupted_message = ""
                            if mode != "ABYSS" and mode != "SCENARIO" and mode not in RAID_MODES and mode not in PVP_MODES and difficulty != "EASY":
                                if universe['CORRUPTED']:
                                    corrupted_message = await crown_utilities.corrupted_universe_handler(ctx, selected_universe, difficulty)
                                    if not corrupted_message:
                                        corrupted_message = "You must dismantle a card from this universe to enable crafting."

                            tale_or_dungeon_only = ""
                            if mode in U_modes:
                                tale_or_dungeon_only = "Tales"
                            if mode in D_modes:
                                tale_or_dungeon_only = "Dungeon"
                            

                            if randomized_battle:
                                bounty = abyss_scaling
                                if explore_type == "glory":
                                    drop_response = await specific_drops(self,str(o_user['DID']), t_card, t_universe, explore_type)
                                await crown_utilities.bless(bounty, str(o_user['DID']))
                                embedVar = discord.Embed(title=f"VICTORY\n:coin: {bounty} Bounty Received!\nThe game lasted {turn_total} rounds.\n\n{drop_response}",description=textwrap.dedent(f"""
                                {previous_moves_into_embed}
                                
                                """),colour=0x1abc9c)
                                embedVar.set_author(name=f"{t_card} lost!")
                                # await ctx.send(embed=embedVar)
                                await battle_msg.delete(delay=2)
                                await asyncio.sleep(2)
                                battle_msg = await private_channel.send(embed=embedVar)

                                # await discord.TextChannel.delete(private_channel, reason=None)
                                return

                            if mode in B_modes:
                                uid = o_DID
                                ouser = await self.bot.fetch_user(uid)
                                wintime = time.asctime()
                                h_playtime = int(wintime[11:13])
                                m_playtime = int(wintime[14:16])
                                s_playtime = int(wintime[17:19])
                                gameClock = getTime(int(h_gametime), int(m_gametime), int(s_gametime), h_playtime, m_playtime,
                                                    s_playtime)
                                drop_response = await bossdrops(self,ctx.author, t_universe)
                                db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_FOUGHT': True}})
                                match = await savematch(str(ouser), str(o_card), str(o_card_path), str(otitle['TITLE']),
                                                        str(oarm['ARM']), "N/A", "Boss", o['EXCLUSIVE'])
                                bank_amount = 100000
                                fam_amount = 50000
                                if difficulty == "HARD":
                                    bank_amount = 1500000
                                    fam_amount = 1000000


                                if mode == "CBoss":
                                    # cmatch = await savematch(str(user2), str(c_card), str(c_card_path), str(ctitle['TITLE']),
                                    #                         str(carm['ARM']), "N/A", "Boss", c['EXCLUSIVE'])
                                    cfambank = await crown_utilities.blessfamily(bank_amount, cfam)
                                    cteambank = await crown_utilities.blessteam(bank_amount, cteam)
                                    cpetlogger = await summonlevel(cpet_name, user2)
                                    uc = await main.bot.fetch_user(user2.id)
                                    ccardlogger = await crown_utilities.cardlevel(uc, c_card, user2.id, "Dungeon", selected_universe)
                                    await crown_utilities.bless(50000, str(user2.id))
                                    teammates = False
                                    fam_members =False
                                    stat_bonus = 0
                                    hlt_bonus = 0 
                                    if o_user['TEAM'] == c_user['TEAM'] and o_user['TEAM'] != 'PCG':
                                        teammates=True
                                        stat_bonus=50
                                    if o_user['FAMILY'] == c_user['FAMILY'] and o_user['FAMILY'] != 'PCG':
                                        fam_members=True
                                        hlt_bonus=100
                                    
                                    if teammates==True:
                                        bonus_message = f":checkered_flag:**{o_user['TEAM']}:** 🗡️**+{stat_bonus}** 🛡️**+{stat_bonus}**"
                                        if fam_members==True:
                                            bonus_message = f":family_mwgb:**{o_user['FAMILY']}:** ❤️**+{hlt_bonus}**\n:checkered_flag:**{o_user['TEAM']}:**🗡️**+{stat_bonus}** 🛡️**+{stat_bonus}**"
                                    elif fam_members==True:
                                            bonus_message = f":family_mwgb:**{o_user['FAMILY']}:** ❤️**+{hlt_bonus}**"
                                    else:
                                        bonus_message = f"Join a Guild or Create a Family for Coop Bonuses!"
                                    embedVar = discord.Embed(title=f":zap: **{o_card}** and **{c_card}** defeated the {t_universe} Boss {t_card}!\nMatch concluded in {turn_total} turns!\n\n{drop_response} + :coin: 15,000!\n\n{c_user['NAME']} got :coin: 10,000!", description=textwrap.dedent(f"""
                                    {previous_moves_into_embed}
                                    
                                    """),colour=0x1abc9c)
                                    embedVar.set_author(name=f"**{t_card}** Says: {t_concede}")
                                    embedVar.add_field(name="**Co-Op Bonus**",
                                                value=f"{bonus_message}")
                                else:
                                    embedVar = discord.Embed(title=f":zap: **{o_card}** defeated the {t_universe} Boss {t_card}!\nMatch concluded in {turn_total} turns!\n\n{drop_response} + :coin: 25,000!\n{corrupted_message}",description=textwrap.dedent(f"""
                                    {previous_moves_into_embed}
                                    
                                    """),colour=0x1abc9c)
                                await crown_utilities.bless(25000, str(ctx.author.id))
                                ofambank = await crown_utilities.blessfamily(fam_amount, ofam)
                                oteambank = await crown_utilities.blessteam(bank_amount, oteam)
                                petlogger = await summonlevel(opet_name, ouser)
                                u = await main.bot.fetch_user(ouser.id)
                                cardlogger = await crown_utilities.cardlevel(u, o_card, ouser.id, "Dungeon", selected_universe)

                                if crestsearch:
                                    await crown_utilities.blessguild(25000, oguild['GNAME'])
                                    teambank = await crown_utilities.blessteam(5000, oteam)
                                    await movecrest(selected_universe, oguild['GNAME'])
                                    embedVar.add_field(name=f"**{selected_universe} Crest Claimed**!",
                                                    value=f":flags:**{oguild['GNAME']}** earned the {selected_universe} **Crest**")
                                embedVar.set_author(name=f"{t_card} lost",
                                                    icon_url="https://res.cloudinary.com/dkcmq8o15/image/upload/v1620236432/PCG%20LOGOS%20AND%20RESOURCES/PCGBot_1.png")
                                if int(gameClock[0]) == 0 and int(gameClock[1]) == 0:
                                    embedVar.set_footer(text=f"Battle Time: {gameClock[2]} Seconds.")
                                elif int(gameClock[0]) == 0:
                                    embedVar.set_footer(text=f"Battle Time: {gameClock[1]} Minutes and {gameClock[2]} Seconds.")
                                else:
                                    embedVar.set_footer(
                                        text=f"Battle Time: {gameClock[0]} Hours {gameClock[1]} Minutes and {gameClock[2]} Seconds.")
                                # await ctx.send(embed=embedVar)
                                await battle_msg.delete(delay=2)
                                await asyncio.sleep(2)
                                battle_msg = await private_channel.send(embed=embedVar)

                                if t_card not in sowner['BOSS_WINS']:
                                    if difficulty == "HARD":
                                        await crown_utilities.bless(5000000, str(ctx.author.id))
                                    else:
                                        await crown_utilities.bless(15000000, str(ctx.author.id))
                                    if mode == "CBoss":
                                        if difficulty == "HARD":
                                            await crown_utilities.bless(5000000, str(user2.id))
                                        else:
                                            await crown_utilities.bless(15000000, str(user2.id))

                                    query = {'DISNAME': sowner['DISNAME']}
                                    new_query = {'$addToSet': {'BOSS_WINS': t_card}}
                                    resp = db.updateUserNoFilter(query, new_query)

                                # await discord.TextChannel.delete(private_channel, reason=None)
                                continued = False
                            
                            if mode == "ABYSS":
                                if currentopponent != (total_legends):
                                    embedVar = discord.Embed(title=f"VICTORY\nThe game lasted {turn_total} rounds.",description=textwrap.dedent(f"""
                                    {previous_moves_into_embed}
                                    
                                    """),colour=0x1abc9c)

                                    embedVar.set_author(name=f"{t_card} lost!")
                                    

                                    await battle_msg.delete(delay=2)
                                    await asyncio.sleep(2)
                                    battle_msg = await private_channel.send(embed=embedVar)
                                    currentopponent = currentopponent + 1
                                    continued = True
                                if currentopponent == (total_legends):
                                    uid = o_DID
                                    ouser = await self.bot.fetch_user(uid)
                                    floor = universe['FLOOR']
                                    new_level = floor + 1
                                    response = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'LEVEL': new_level}})
                                    abyss_message = await abyss_level_up_message(str(ctx.author.id), floor, t_card, t_title, tarm_name)
                                    cardlogger = await crown_utilities.cardlevel(ouser, o_card, ctx.author.id, "Purchase", "n/a")
                                    abyss_drop_message = "\n".join(abyss_message['DROP_MESSAGE'])
                                    bless_amount = 100000 + (10000 * floor)
                                    await crown_utilities.bless(bless_amount, ctx.author.id)
                                    embedVar = discord.Embed(title=f"🌑 Floor **{floor}** Cleared\nThe game lasted {turn_total} rounds.",description=textwrap.dedent(f"""
                                    Counquer the **Abyss** to unlock **Abyssal Rewards** and **New Game Modes.**
                                    
                                    🎊**Abyss Floor Unlocks**
                                    **3** - *PvP and Guilds*
                                    **10** - *Trading*
                                    **15** - *Associations and Raids*
                                    **20** - *Gifting*
                                    **25** - *Explore Mode*
                                    **30** - *Marriage*
                                    **40** - *Dungeons*
                                    **60** - *Bosses*
                                    **100** - *Boss Soul Exchange*
                                    """),colour=0xe91e63)

                                    embedVar.set_author(name=f"{t_card} lost!")
                                    embedVar.set_footer(text=f"Traverse the **Abyss** in /solo to unlock new game modes and features!")
                                    floor_list = [0,2,3,6,7,8,9,10,20,25,40,60,100]
                                    if floor in floor_list:
                                        embedVar.add_field(
                                        name=f"Abyssal Unlock",
                                        value=f"{abyss_message['MESSAGE']}")
                                    embedVar.add_field(
                                    name=f"Abyssal Rewards",
                                    value=f"{abyss_drop_message}")
 
                                    battle_msg = await private_channel.send(embed=embedVar)

                                    continued = False

                            if mode == "SCENARIO":
                                if currentopponent != (total_legends):
                                    uid = o_DID
                                    ouser = await self.bot.fetch_user(uid)
                                    cardlogger = await crown_utilities.cardlevel(ouser, o_card, ouser.id, "Tales", universe['UNIVERSE'])

                                    embedVar = discord.Embed(title=f"VICTORY\nThe game lasted {turn_total} rounds.",description=textwrap.dedent(f"""
                                    {previous_moves_into_embed}
                                    
                                    """),colour=0x1abc9c)

                                    embedVar.set_author(name=f"{t_card} lost!")
                                    

                                    await battle_msg.delete(delay=2)
                                    await asyncio.sleep(2)
                                    battle_msg = await private_channel.send(embed=embedVar)
                                    currentopponent = currentopponent + 1
                                    continued = True
                                if currentopponent == (total_legends):
                                    uid = o_DID
                                    ouser = await self.bot.fetch_user(uid)
                                    response = await scenario_drop(self, ctx, universe, difficulty)
                                    bless_amount = 50000
                                    await crown_utilities.bless(bless_amount, ctx.author.id)
                                    embedVar = discord.Embed(title=f"Scenario Battle Cleared!\nThe game lasted {turn_total} rounds.",description=textwrap.dedent(f"""
                                    Good luck on your next adventure!
                                    """),colour=0xe91e63)

                                    embedVar.set_author(name=f"{t_card} lost!")
                                    embedVar.add_field(
                                    name=f"Scenario Reward",
                                    value=f"{response}")
 
                                    battle_msg = await private_channel.send(embed=embedVar)

                                    continued = False

                            elif mode not in B_modes and mode != "ABYSS":
                                uid = o_DID
                                ouser = await self.bot.fetch_user(uid)
                                wintime = time.asctime()
                                h_playtime = int(wintime[11:13])
                                m_playtime = int(wintime[14:16])
                                s_playtime = int(wintime[17:19])
                                gameClock = getTime(int(h_gametime), int(m_gametime), int(s_gametime), h_playtime, m_playtime,
                                                    s_playtime)

                                bank_amount = 5000
                                fam_amount = 2000
                                if mode in D_modes:
                                    bank_amount = 20000
                                    fam_amount = 5000

                                if difficulty == "HARD":
                                    bank_amount = 100000
                                    fam_amount = 50000
                                    

                                if difficulty == "EASY":
                                    bank_amount = 500
                                    fam_amount = 100

                                if mode in D_modes:
                                    teambank = await crown_utilities.blessteam(bank_amount, oteam)
                                else:
                                    teambank = await crown_utilities.blessteam(bank_amount, oteam)
                                if o_user['RIFT'] == 1:
                                    response = db.updateUserNoFilter({'DISNAME': str(o_user['DISNAME'])}, {'$set': {'RIFT': 0}})

                                if mode in D_modes:
                                    drop_response = await dungeondrops(self, ouser, selected_universe, currentopponent)
                                elif mode in U_modes:
                                    drop_response = await drops(self, ouser, selected_universe, currentopponent)
                                if mode in D_modes:
                                    ofambank = await crown_utilities.blessfamily(fam_amount, ofam)
                                else:
                                    ofambank = await crown_utilities.blessfamily(fam_amount, ofam)
                                match = await savematch(str(ouser), str(o_card), str(o_card_path), str(otitle['TITLE']),
                                                        str(oarm['ARM']), str(selected_universe), tale_or_dungeon_only,
                                                        o['EXCLUSIVE'])
                                ran_element = crown_utilities.select_random_element(difficulty, mode)
                                essence = crown_utilities.inc_essence(ouser.id, ran_element["ELEMENT"], ran_element["ESSENCE"])

                                if difficulty != "EASY":
                                    questlogger = await quest(ouser, t_card, tale_or_dungeon_only)
                                    destinylogger = await destiny(ouser, t_card, tale_or_dungeon_only)
                                    petlogger = await summonlevel(opet_name, ouser)
                                    cardlogger = await crown_utilities.cardlevel(ouser, o_card, ouser.id, tale_or_dungeon_only, selected_universe)
                                    # if questlogger:
                                    #     await private_channel.send(questlogger)
                                    # if destinylogger:
                                    #     await private_channel.send(destinylogger)
                                
                                if _battle._is_co_op and mode not in ai_co_op_modes:
                                    teammates = False
                                    fam_members =False
                                    stat_bonus = 0
                                    hlt_bonus = 0 
                                    if o_user['TEAM'] == c_user['TEAM'] and o_user['TEAM'] != 'PCG':
                                        teammates=True
                                        stat_bonus=50
                                    if o_user['FAMILY'] == c_user['FAMILY'] and o_user['FAMILY'] != 'PCG':
                                        fam_members=True
                                        hlt_bonus=100
                                    
                                    if teammates==True:
                                        bonus_message = f":checkered_flag:**{o_user['TEAM']}:** 🗡️**+{stat_bonus}** 🛡️**+{stat_bonus}**"
                                        if fam_members==True:
                                            bonus_message = f":family_mwgb:**{o_user['FAMILY']}:** ❤️**+{hlt_bonus}**\n:checkered_flag:**{o_user['TEAM']}:**🗡️**+{stat_bonus}** 🛡️**+{stat_bonus}**"
                                    elif fam_members==True:
                                            bonus_message = f":family_mwgb:**{o_user['FAMILY']}:** ❤️**+{hlt_bonus}**"
                                    else:
                                        bonus_message = f"Join a Guild or Create a Family for Coop Bonuses!"
                                    cuid = c_DID
                                    talisman_response = crown_utilities.inc_talisman(str(cuid), c_talisman)
                                    cuser = await self.bot.fetch_user(cuid)
                                    if mode in D_modes:
                                        teambank = await crown_utilities.blessteam(bank_amount, oteam)
                                        cteambank = await crown_utilities.blessteam(bank_amount, oteam)
                                    else:
                                        teambank = await crown_utilities.blessteam(bank_amount, oteam)
                                        cteambank = await crown_utilities.blessteam(bank_amount, oteam)
                                    if mode in D_modes:
                                        cdrop_response = await dungeondrops(self,user2, selected_universe, currentopponent)
                                    elif mode in U_modes:
                                        cdrop_response = await drops(self,user2, selected_universe, currentopponent)
                                    if mode in D_modes:
                                        cfambank = await crown_utilities.blessfamily(fam_amount, cfam)
                                        ofambank = await crown_utilities.blessfamily(fam_amount, ofam)
                                    else:
                                        cfambank = await crown_utilities.blessfamily(fam_amount, cfam)
                                        ofambank = await crown_utilities.blessfamily(fam_amount, ofam)
                                    # cmatch = await savematch(str(user2), str(c_card), str(c_card_path), str(ctitle['TITLE']),
                                    #                         str(carm['ARM']), str(selected_universe), tale_or_dungeon_only, c['EXCLUSIVE'])
                                    cfambank = await crown_utilities.blessfamily(fam_amount, cfam)
                                    cteambank = await crown_utilities.blessteam(bank_amount, cteam)
                                    cpetlogger = await summonlevel(cpet_name, user2)
                                    ucc = await main.bot.fetch_user(user2.id)
                                    ccardlogger = await crown_utilities.cardlevel(ucc, c_card, user2.id, tale_or_dungeon_only, selected_universe)
                                    await crown_utilities.bless(5000, str(user2.id))
                                    cessence = crown_utilities.inc_essence(cuser.id, ran_element["ELEMENT"], ran_element["ESSENCE"])
                                if currentopponent != (total_legends):
                                    if mode not in co_op_modes:
                                        embedVar = discord.Embed(title=f"🎊 VICTORY\nThe game lasted {turn_total} rounds.\n\n{drop_response}\nEarned {essence} {ran_element['ESSENCE']} Essence\n{corrupted_message}",description=textwrap.dedent(f"""
                                        {previous_moves_into_embed}
                                        
                                        """),colour=0x1abc9c)
                                        if difficulty != "EASY":
                                            if questlogger:
                                                embedVar.add_field(name="**Quest Progress**",
                                                    value=f"{questlogger}")
                                            if destinylogger:
                                                embedVar.add_field(name="**Destiny Progress**",
                                                    value=f"{destinylogger}")
                                    elif _battle._is_co_op and mode not in ai_co_op_modes:
                                        embedVar = discord.Embed(title=f"👥 CO-OP VICTORY\nThe game lasted {turn_total} rounds.\n\n👤**{o_user['NAME']}:** {drop_response}\nEarned {essence} {ran_element['ESSENCE']} Essence\n👥**{c_user['NAME']}:** {cdrop_response}\nEarned {cessence} {ran_element['ESSENCE']} Essence",description=textwrap.dedent(f"""
                                        {previous_moves_into_embed}
                                        
                                        """),colour=0x1abc9c)
                                        embedVar.add_field(name="**Co-Op Bonus**",
                                                value=f"{bonus_message}")
                                        if questlogger:
                                            embedVar.add_field(name="**Quest Progress**",
                                                value=f"{questlogger}")
                                        if destinylogger:
                                            embedVar.add_field(name="**Destiny Progress**",
                                                value=f"{destinylogger}")
                                    elif mode in ai_co_op_modes:
                                        embedVar = discord.Embed(title=f"🎊 DUO VICTORY\nThe game lasted {turn_total} rounds.\n\n{drop_response}\n{corrupted_message}",description=textwrap.dedent(f"""
                                        {previous_moves_into_embed}
                                        
                                        """),colour=0x1abc9c)
                                    if mode in D_modes:
                                        if crestsearch:
                                            await crown_utilities.blessguild(10000, oguild['GNAME'])
                                            embedVar.add_field(name=f"**{selected_universe} Crest Search!**",
                                                            value=f":flags:**{oguild['GNAME']}** earned **100,000** :coin:")
                                    embedVar.set_author(name=f"{t_card} lost!")
                                    
                                    await battle_msg.delete(delay=2)
                                    await asyncio.sleep(2)
                                    battle_msg = await private_channel.send(embed=embedVar)

                                    currentopponent = currentopponent + 1
                                    continued = True

                                if currentopponent == (total_legends):
                                    if mode in D_modes:
                                        embedVar = discord.Embed(title=f":fire: DUNGEON CONQUERED",
                                                                description=f"**{selected_universe} Dungeon** has been conquered\n\n{drop_response}\n{corrupted_message}",
                                                                colour=0xe91e63)
                                        embedVar.set_author(name=f"{selected_universe} Boss has been unlocked!")
                                        if crestsearch:
                                            await crown_utilities.blessguild(100000, oguild['GNAME'])
                                            teambank = await crown_utilities.blessteam(100000, oteam)
                                            await movecrest(selected_universe, oguild['GNAME'])
                                            embedVar.add_field(name=f"**{selected_universe}** CREST CLAIMED!",
                                                            value=f"**{oguild['GNAME']}** earned the {selected_universe} **Crest**")
                                        if questlogger:
                                            embedVar.add_field(name="**Quest Progress**",
                                                value=f"{questlogger}")
                                        if destinylogger:
                                            embedVar.add_field(name="**Destiny Progress**",
                                                value=f"{destinylogger}")
                                        embedVar.set_footer(text="Visit the /shop for a huge discount!")
                                        if difficulty != "EASY":
                                            upload_query = {'DID': str(ctx.author.id)}
                                            new_upload_query = {'$addToSet': {'DUNGEONS': selected_universe}}
                                            r = db.updateUserNoFilter(upload_query, new_upload_query)
                                        if selected_universe in o_user['DUNGEONS']:
                                            await crown_utilities.bless(300000, ctx.author.id)
                                            teambank = await crown_utilities.blessteam(bank_amount, oteam)
                                            # await crown_utilities.bless(125, user2)
                                            # await ctx.send(embed=embedVar)
                                            await battle_msg.delete(delay=2)
                                            await asyncio.sleep(2)
                                            embedVar.add_field(name="Minor Reward",
                                                        value=f"You were awarded :coin: 300,000 for completing the {selected_universe} Dungeon again!")
                                            #battle_msg = await private_channel.send(embed=embedVar)
                                        else:
                                            await crown_utilities.bless(6000000, ctx.author.id)
                                            teambank = await crown_utilities.blessteam(1500000, oteam)
                                            # await ctx.send(embed=embedVar)
                                            await battle_msg.delete(delay=2)
                                            await asyncio.sleep(2)
                                            embedVar.add_field(name="Dungeon Reward",
                                                        value=f"You were awarded :coin: 6,000,000 for completing the {selected_universe} Dungeon!")
                                            #battle_msg = await private_channel.send(embed=embedVar)
                                        if _battle._is_co_op and mode not in ai_co_op_modes:
                                            cuid = c_DID
                                            cuser = await self.bot.fetch_user(cuid)
                                            await crown_utilities.bless(500000, user2.id)
                                            teambank = await crown_utilities.blessteam(200000, cteam)
                                            # await crown_utilities.bless(125, user2)
                                            # await ctx.send(embed=embedVar)
                                            await asyncio.sleep(2)
                                            
                                            await ctx.send(
                                                f"{user2.mention} You were awarded :coin: 500,000 for  assisting in the {selected_universe} Dungeon!")
                                        battle_msg = await private_channel.send(embed=embedVar)
                                        continued = False
                                        # await discord.TextChannel.delete(private_channel, reason=None)
                                    elif mode in U_modes:
                                        embedVar = discord.Embed(title=f"🎊 UNIVERSE CONQUERED",
                                                                description=f"**{selected_universe}** has been conquered\n\n{drop_response}\n{corrupted_message}",
                                                                colour=0xe91e63)
                                        if questlogger:
                                            embedVar.add_field(name="**Quest Progress**",
                                                value=f"{questlogger}")
                                        if destinylogger:
                                            embedVar.add_field(name="**Destiny Progress**",
                                                value=f"{destinylogger}")
                                        embedVar.set_footer(text=f"You can now /craft {selected_universe} cards")
                                        if difficulty != "EASY":
                                            embedVar.set_author(name=f"{selected_universe} Dungeon has been unlocked!")
                                            upload_query = {'DID': str(ctx.author.id)}
                                            new_upload_query = {'$addToSet': {'CROWN_TALES': selected_universe}}
                                            r = db.updateUserNoFilter(upload_query, new_upload_query)
                                        if selected_universe in o_user['CROWN_TALES']:
                                            await crown_utilities.bless(100000, ctx.author.id)
                                            teambank = await crown_utilities.blessteam(25000, oteam)
                                            # await ctx.send(embed=embedVar)
                                            await battle_msg.delete(delay=2)
                                            await asyncio.sleep(2)
                                            embedVar.add_field(name="Minor Reward",
                                                        value=f"You were awarded :coin: 100,000 for completing the {selected_universe} Tale again!")
                                        else:
                                            await crown_utilities.bless(2000000, ctx.author.id)
                                            teambank = await crown_utilities.blessteam(500000, oteam)
                                            # await ctx.send(embed=embedVar)
                                            await battle_msg.delete(delay=2)
                                            await asyncio.sleep(2)
                                            
                                            embedVar.add_field(name="Conquerors Reward",
                                                        value=f"You were awarded :coin: 2,000,000 for completing the {selected_universe} Tale!")
                                            #battle_msg = await private_channel.send(embed=embedVar)
                                        if _battle._is_co_op and mode not in ai_co_op_modes:
                                            cuid = c_DID
                                            cuser = await self.bot.fetch_user(cuid)
                                            await crown_utilities.bless(250000, user2.id)
                                            teambank = await crown_utilities.blessteam(80000, cteam)
                                            # await crown_utilities.bless(125, user2)
                                            # await ctx.send(embed=embedVar)
                                            await asyncio.sleep(2)
                                            embedVar.add_field(name="Companion Reward",
                                                        value=f"{user2.mention} You were awarded :coin: 250,000 for assisting in the {selected_universe} Tale!")
                                            
                                        battle_msg = await private_channel.send(embed=embedVar)
                                        continued = False

            except asyncio.TimeoutError:
                await battle_msg.edit(components=[])
                if mode != "ABYSS" and mode != "SCENARIO":
                    #await msg.edit(components=[])
                    if not tutorial:
                        if mode in PVP_MODES: #pvp check
                            await ctx.send(f"{ctx.author.mention} your game timed out. Your channel has been closed.")
                        else:
                            await save_spot(self, ctx, universe, mode, currentopponent)
                            await ctx.author.send(f"{ctx.author.mention} your game timed out. Your channel has been closed but your spot in the tales has been saved where you last left off.")
                            await ctx.send(f"{ctx.author.mention} your game timed out. Your channel has been closed but your spot in the tales has been saved where you last left off.")
                    else:
                        await ctx.author.send(f"{ctx.author.mention} your game timed out. Your channel has been closed, restart the tutorial with **/solo**.")
                        await ctx.send(f"{ctx.author.mention} your game timed out. Your channel has been closed , restart the tutorial with **/solo**.")
                else:
                    await ctx.author.send(f"{ctx.author.mention} your game timed out. Your channel has been closed and your Abyss Floor was Reset.") #Findme
                    await ctx.send(f"{ctx.author.mention} your game timed out. Your channel has been closed and your Abyss Floor was Reset.")
                return
            except Exception as ex:
                trace = []
                tb = ex.__traceback__
                while tb is not None:
                    trace.append({
                        "filename": tb.tb_frame.f_code.co_filename,
                        "name": tb.tb_frame.f_code.co_name,
                        "lineno": tb.tb_lineno
                    })
                    tb = tb.tb_next
                print(str({
                    'PLAYER': str(ctx.author),
                    'type': type(ex).__name__,
                    'message': str(ex),
                    'trace': trace
                }))
                # if mode not in ai_co_op_modes:
                #     await battle_ping_message.delete()
                await battle_msg.delete()
                guild = self.bot.get_guild(main.guild_id)
                channel = guild.get_channel(main.guild_channel)
                await channel.send(f"'PLAYER': **{str(ctx.author)}**, 'GUILD': **{str(ctx.author.guild)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")
                return

    except asyncio.TimeoutError:
        await battle_msg.edit(components=[])
        if mode != "ABYSS" and mode != "SCENARIO":
            if not tutorial:
                if mode in PVP_MODES: #pvp check
                    await ctx.send(f"{ctx.author.mention} your game timed out. Your channel has been closed.")
                else:
                    await save_spot(self, ctx, universe, mode, currentopponent)
                    await ctx.author.send(f"{ctx.author.mention} your game timed out. Your channel has been closed but your spot in the tales has been saved where you last left off.")
                    await ctx.send(f"{ctx.author.mention} your game timed out. Your channel has been closed but your spot in the tales has been saved where you last left off.")
            else:
                await ctx.author.send(f"{ctx.author.mention} your game timed out. Your channel has been closed, restart the tutorial with **/solo**.")
                await ctx.send(f"{ctx.author.mention} your game timed out. Your channel has been closed , restart the tutorial with **/solo**.")
        else:
            await ctx.author.send(f"{ctx.author.mention} your game timed out. Your channel has been closed and your Abyss Floor was Reset.") #Findme
            await ctx.send(f"{ctx.author.mention} your game timed out. Your channel has been closed and your Abyss Floor was Reset.")
    
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'PLAYER': str(ctx.author),
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        guild = self.bot.get_guild(main.guild_id)
        channel = guild.get_channel(main.guild_channel)
        await channel.send(f"'PLAYER': **{str(ctx.author)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")
        return


async def save_spot(self, ctx, universe, mode, currentopponent):
    try:
        user = {"DID": str(ctx.author.id)}
        query = {"$addToSet": {"SAVE_SPOT": {"UNIVERSE": str(universe['TITLE']), "MODE": str(mode), "CURRENTOPPONENT": currentopponent}}}
        response = db.updateUserNoFilter(user, query)
        return
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'PLAYER': str(ctx.author),
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        guild = self.bot.get_guild(main.guild_id)
        channel = guild.get_channel(main.guild_channel)
        await channel.send(f"'PLAYER': **{str(ctx.author)}**, 'GUILD': **{str(ctx.author.guild)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")
        return

        

def update_arm_durability(self, vault, arm, arm_universe, arm_price, card):
    try:
        player_info = db.queryUser({'DID': str(vault['DID'])})
        if player_info['DIFFICULTY'] == "EASY":
            return
        pokemon_universes = ['Kanto Region', 'Johto Region','Hoenn Region','Sinnon Region','Kalos Region','Alola Region','Galar Region']
        if card['UNIVERSE'] == 'Crown Rift Slayers':
            arm_universe = card['UNIVERSE']
            
        if arm_universe in pokemon_universes:
            arm_universe = card['UNIVERSE']

        decrease_value = -1
        break_value = 1
        if arm_universe != card['UNIVERSE'] and arm_universe != "Unbound":
            decrease_value = -5
            break_value = 5

        for a in vault['ARMS']:
            if a['ARM'] == str(arm['ARM']):
                current_durability = a['DUR']
                if current_durability <= 0:
                    selected_arm = arm['ARM']
                    arm_name = arm['ARM']
                    selected_universe = arm_universe
                    dismantle_amount = 5000
                    current_gems = []
                    for gems in vault['GEMS']:
                        current_gems.append(gems['UNIVERSE'])

                    if selected_universe in current_gems:
                        query = {'DID': str(vault['DID'])}
                        update_query = {'$inc': {'GEMS.$[type].' + "GEMS": dismantle_amount}}
                        filter_query = [{'type.' + "UNIVERSE": selected_universe}]
                        response = db.updateVault(query, update_query, filter_query)
                    else:
                        response = db.updateVaultNoFilter({'DID': str(vault['DID'])},{'$addToSet':{'GEMS': {'UNIVERSE': selected_universe, 'GEMS': dismantle_amount, 'UNIVERSE_HEART': False, 'UNIVERSE_SOUL': False}}})


                    query = {'DID': str(vault['DID'])}
                    update_query = {'$pull': {'ARMS': {'ARM': str(arm['ARM'])}}}
                    resp = db.updateVaultNoFilter(query, update_query)

                    user_query = {'DID': str(vault['DID'])}
                    user_update_query = {'$set': {'ARM': 'Stock'}}
                    user_resp = db.updateUserNoFilter(user_query, user_update_query)
                    return {"MESSAGE": f"**{arm['ARM']}** has been dismantled after losing all ⚒️ durability, you earn 💎 {str(dismantle_amount)}. Your arm will be **Stock** after your next match."}
                else:                   
                    query = {'DID': str(vault['DID'])}
                    update_query = {'$inc': {'ARMS.$[type].' + 'DUR': decrease_value}}
                    filter_query = [{'type.' + "ARM": str(arm['ARM'])}]
                    resp = db.updateVault(query, update_query, filter_query)
                    if current_durability >= 15:
                        return {"MESSAGE": False}
                    else:
                        return {"MESSAGE": f"**{arm['ARM']}** will lose all ⚒️ durability soon! Use **/blacksmith** to repair!"}
        return {"MESSAGE": False}
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        return
        


def update_save_spot(self, ctx, saved_spots, selected_universe, modes):
    try:
        currentopponent = 0
        if saved_spots:
            for save in saved_spots:
                if save['UNIVERSE'] == selected_universe and save['MODE'] in modes:
                    currentopponent = save['CURRENTOPPONENT']
                    query = {'DID': str(ctx.author.id)}
                    update_query = {'$pull': {'SAVE_SPOT': {"UNIVERSE": selected_universe}}}
                    resp = db.updateUserNoFilter(query, update_query)
        return currentopponent
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'PLAYER': str(ctx.author),
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        return



def health_and_stamina_bars(health, stamina, max_health, max_stamina, resolved):
    health_response = ""
    stamina_response = ""

    if health >= max_health:
        health_response = f"❤️❤️❤️❤️❤️"
    if health >= (max_health * .80) and health < max_health:
        health_response = f"❤️❤️❤️❤️💔"
    if health >= (max_health * .60) and health < (max_health * .80):
        health_response = f"❤️❤️❤️💔💔"
    if health >= (max_health * .40) and health < (max_health * .60):
        health_response = f"❤️❤️💔💔💔"
    if health >= (max_health * .20) and health < (max_health * .40):
        health_response = f"❤️💔💔💔💔"
    if health >= 0 and health <= (max_health * .20):
        health_response = f"💔💔💔💔💔"
    if resolved:
        if stamina >= max_stamina:
            stamina_response = f"⚡⚡⚡⚡⚡"
        if stamina >= (max_stamina * .80) and stamina < max_stamina:
            stamina_response = f"⚡⚡⚡⚡💫"
        if stamina >= (max_stamina * .60) and stamina < (max_stamina * .80):
            stamina_response = f"⚡⚡⚡💫💫"
        if stamina >= (max_stamina * .40) and stamina < (max_stamina * .60):
            stamina_response = f"⚡⚡💫💫💫"
        if stamina >= (max_stamina * .10) and stamina < (max_stamina * .40):
            stamina_response = f"⚡💫💫💫💫"
        if stamina >= 0 and stamina <= (max_stamina * .10):
            stamina_response = f"💫💫💫💫💫"
    else:
        if stamina >= max_stamina:
            stamina_response = f"🌀🌀🌀🌀🌀"
        if stamina >= (max_stamina * .80) and stamina < max_stamina:
            stamina_response = f"🌀🌀🌀🌀⚫"
        if stamina >= (max_stamina * .60) and stamina < (max_stamina * .80):
            stamina_response = f"🌀🌀🌀⚫⚫"
        if stamina >= (max_stamina * .40) and stamina < (max_stamina * .60):
            stamina_response = f"🌀🌀⚫⚫⚫"
        if stamina >= (max_stamina * .10) and stamina < (max_stamina * .40):
            stamina_response = f"🌀⚫⚫⚫⚫"
        if stamina >= 0 and stamina <= (max_stamina * .10):
            stamina_response = f"⚫⚫⚫⚫⚫"

    return {"HEALTH": health_response, "STAMINA": stamina_response}


def getTime(hgame, mgame, sgame, hnow, mnow, snow):
    hoursPassed = hnow - hgame
    minutesPassed = mnow - mgame
    secondsPassed = snow - sgame
    if hoursPassed > 0:
        minutesPassed = mnow
        if minutesPassed > 0:
            secondsPassed = snow
        else:
            secondsPassed = snow - sgame
    else:
        minutesPassed = mnow - mgame
        if minutesPassed > 0:
            secondsPassed = snow
        else:
            secondsPassed = snow - sgame
    gameTime = str(hoursPassed) + str(minutesPassed) + str(secondsPassed)
    return gameTime


async def blessteam(amount, team):
    blessAmount = amount
    posBlessAmount = 0 + abs(int(blessAmount))
    query = {'TEAM_NAME': str(team.lower())}
    team_data = db.queryTeam(query)
    if team_data:
        guild_mult = 1.0
        if team_data['GUILD'] != 'PCG':
            guild_query = {'GNAME': str(team_data['GUILD'])}
            guild_info = db.queryGuildAlt(guild_query)
            guild_hall = guild_info['HALL']
            hall_query = {'HALL': str(guild_hall)}
            hall_info = db.queryHall(hall_query)
            guild_mult = hall_info['SPLIT']
            blessAmount = amount * guild_mult
            posBlessAmount = 0 + abs(int(blessAmount))
        total_members = team_data['MEMBERS']
        headcount_bonus = 0
        bonus_percentage = 0.0
        for m in total_members:
            headcount_bonus= headcount_bonus + 1
        bonus_percentage= (headcount_bonus/25)
        if bonus_percentage >= 1:
            bonus_percentage = 1.5
        posBlessAmount = int((posBlessAmount + (bonus_percentage * posBlessAmount)))
        update_query = {"$inc": {'BANK': posBlessAmount}}
        db.updateTeam(query, update_query)



async def teamwin(team):
    query = {'TEAM_NAME': str(team.lower())}
    team_data = db.queryTeam(query)
    if team_data:
        update_query = {"$inc": {'SCRIM_WINS': 1}}
        db.updateTeam(query, update_query)
    else:
        print("Cannot find Guild")


async def teamloss(team):
    query = {'TEAM_NAME': str(team.lower())}
    team_data = db.queryTeam(query)
    if team_data:
        update_query = {"$inc": {'SCRIM_LOSSES': 1}}
        db.updateTeam(query, update_query)
    else:
        print("Cannot find Guild")


async def movecrest(universe, guild):
    guild_name = guild
    universe_name = universe
    guild_query = {'GNAME': guild_name}
    guild_info = db.queryGuildAlt(guild_query)
    if guild_info:
        alt_query = {'FDID': guild_info['FDID']}
        crest_list = guild_info['CREST']
        pull_query = {'$pull': {'CREST': universe_name}}
        pull = db.updateManyGuild(pull_query)
        update_query = {'$push': {'CREST': universe_name}}
        update = db.updateGuild(alt_query, update_query)
        universe_guild = db.updateUniverse({'TITLE': universe_name}, {'$set': {'GUILD': guild_name}})
    else:
        print("Association not found: Crest")


async def scenario_drop(self, ctx, scenario, difficulty):
    try:
        vault_query = {'DID': str(ctx.author.id)}
        vault = db.queryVault(vault_query)
        scenario_level = scenario["ENEMY_LEVEL"]
        scenario_gold = crown_utilities.scenario_gold_drop(scenario_level)
        # player_info = db.queryUser({'DID': str(vault['DID'])})
        
        owned_destinies = []
        for destiny in vault['DESTINY']:
            owned_destinies.append(destiny['NAME'])


        owned_arms = []
        for arm in vault['ARMS']:
            owned_arms.append(arm['ARM'])

        easy = "EASY_DROPS"
        normal = "NORMAL_DROPS"
        hard = "HARD_DROPS"
        rewards = []
        rewarded = ""
        mode = ""

        if difficulty == "EASY":
            rewards = scenario[easy]
            mode = "TALES"
            scenario_gold = round(scenario_gold / 3)
        if difficulty == "NORMAL":
            rewards = scenario[normal]
            mode = "TALES"
        if difficulty == "HARD":
            rewards = scenario[hard]
            mode = "DUNGEON"
            scenario_gold = round(scenario_gold * 3)
        if len(rewards) > 1:
            num_of_potential_rewards = len(rewards)
            selection = round(random.randint(0, num_of_potential_rewards))
            rewarded = rewards[selection]
        else:
            rewarded = rewards[0]
        
        await crown_utilities.bless(scenario_gold, ctx.author.id)
        # Add Card Check
        arm = db.queryArm({"ARM": rewarded})
        if arm:
            arm_name = arm['ARM']
            element_emoji = crown_utilities.set_emoji(arm['ELEMENT'])
            arm_passive = arm['ABILITIES'][0]
            arm_passive_type = list(arm_passive.keys())[0]
            arm_passive_value = list(arm_passive.values())[0]
            reward = f"{element_emoji} {arm_passive_type.title()} **{arm_name}** Attack: **{arm_passive_value}** dmg"

            if len(vault['ARMS']) >= 25:
                return f"You're maxed out on Arms! You earned :coin:**{'{:,}'.format(scenario_gold)}** instead!"
            elif rewarded in owned_arms:
                return f"You already own {reward}! You earn :coin: **{'{:,}'.format(scenario_gold)}**."
            else:
                response = db.updateVaultNoFilter(vault_query, {'$addToSet': {'ARMS': {'ARM': rewarded, 'DUR': 100}}})
                return f"You earned _Arm:_ {reward} with ⚒️**{str(100)} Durability** and :coin: **{'{:,}'.format(scenario_gold)}**!"
        else:
            card = db.queryCard({"NAME": rewarded})
            u = await main.bot.fetch_user(str(ctx.author.id))
            response = await crown_utilities.store_drop_card(u, str(ctx.author.id), card["NAME"], card["UNIVERSE"], vault, owned_destinies, 3000, 1000, mode, False, 0, "cards")
            response = f"{response}\nYou earned :coin: **{'{:,}'.format(scenario_gold)}**!"
            if not response:
                bless_amount = (5000 + (2500 * matchcount)) * (1 + rebirth)
                await crown_utilities.bless(bless_amount, str(ctx.author.id))
                return f"You earned :coin: **{'{:,}'.format(scenario_gold)}**!"
            return response

    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))

    

    


async def drops(self,player, universe, matchcount):
    all_available_drop_cards = db.queryDropCards(universe)
    all_available_drop_titles = db.queryDropTitles(universe)
    all_available_drop_arms = db.queryDropArms(universe)
    all_available_drop_pets = db.queryDropPets(universe)
    vault_query = {'DID': str(player.id)}
    vault = db.queryVault(vault_query)
    player_info = db.queryUser({'DID': str(vault['DID'])})

    difficulty = player_info['DIFFICULTY']

    if difficulty == "EASY":
        bless_amount = 100
        await crown_utilities.bless(bless_amount, player.id)
        return f"You earned :coin: **{bless_amount}**!"

    owned_arms = []
    for arm in vault['ARMS']:
        owned_arms.append(arm['ARM'])
        
    owned_titles = []
    owned_titles = vault['TITLES']

    user_query = {'DID': str(player.id)}
    user = db.queryUser(user_query)
    rebirth = user['REBIRTH']
    owned_destinies = []
    for destiny in vault['DESTINY']:
        owned_destinies.append(destiny['NAME'])

    cards = []
    titles = []
    arms = []
    pets = []

    # if matchcount <= 2:
    #     bless_amount = (500 + (1000 * matchcount)) * (1 + rebirth)
    #     if difficulty == "HARD":
    #         bless_amount = (5000 + (2500 * matchcount)) * (1 + rebirth)
    #     await crown_utilities.bless(bless_amount, player.id)
    #     return f"You earned :coin: **{bless_amount}**!"



    if all_available_drop_cards:
        for card in all_available_drop_cards:
            cards.append(card['NAME'])

    if all_available_drop_titles:
        for title in all_available_drop_titles:
            titles.append(title['TITLE'])

    if all_available_drop_arms:
        for arm in all_available_drop_arms:
            arms.append(arm['ARM'])
        
    if all_available_drop_pets:
        for pet in all_available_drop_pets:
            pets.append(pet['PET'])
         
    
    if len(cards)==0:
        rand_card = 0
    else:
        c = len(cards) - 1
        rand_card = random.randint(0, c)

    if len(titles)==0:
        rand_title= 0
    else:
        t = len(titles) - 1
        rand_title = random.randint(0, t)

    if len(arms)==0:
        rand_arm = 0
    else:
        a = len(arms) - 1
        rand_arm = random.randint(0, a)

    
    if len(pets)==0:
        rand_pet = 0
    else:
        p = len(pets) - 1
        rand_pet = random.randint(0, p)

    gold_drop = 125  # 125
    rift_rate = 150  # 150
    rematch_rate = 175 #175
    title_drop = 190  # 190
    arm_drop = 195  # 195
    pet_drop = 198  # 198
    card_drop = 200  # 200
    drop_rate = random.randint((0 + (rebirth * rebirth) * (1 + rebirth)), 200)
    durability = random.randint(1, 45)
    if difficulty == "HARD":
        mode = "Purchase"
        gold_drop = 30
        rift_rate = 55
        rematch_rate = 70
        title_drop = 75  
        arm_drop = 100  
        pet_drop = 180  
        card_drop = 200 
        drop_rate = random.randint((0 + (rebirth * rebirth) * (1 + rebirth)), 200)
        durability = random.randint(35, 50)
        
    try:
        if drop_rate <= gold_drop:
            bless_amount = (10000 + (1000 * matchcount)) * (1 + rebirth)
            if difficulty == "HARD":
                bless_amount = (30000 + (2500 * matchcount)) * (1 + rebirth)
            await crown_utilities.bless(bless_amount, player.id)
            return f"You earned :coin: **{bless_amount}**!"
        elif drop_rate <= rift_rate and drop_rate > gold_drop:
            response = db.updateUserNoFilter(user_query, {'$set': {'RIFT': 1}})
            bless_amount = (20000 + (1000 * matchcount)) * (1 + rebirth)
            await crown_utilities.bless(bless_amount, player.id)
            return f"A RIFT HAS OPENED! You have earned :coin: **{bless_amount}**!"
        elif drop_rate <= rematch_rate and drop_rate > rift_rate:
            response = db.updateUserNoFilter(user_query, {'$inc': {'RETRIES': 1}})
            bless_amount = (25000 + (1000 * matchcount)) * (1 + rebirth)
            await crown_utilities.bless(bless_amount, player.id)
            return f"🆚  You have earned 1 Rematch and  :coin: **{bless_amount}**!"
        elif drop_rate <= title_drop and drop_rate > rematch_rate:
            if all_available_drop_titles:
                # if len(vault['TITLES']) >= 25:
                #     await crown_utilities.bless(300, player.id)
                #     return f"You're maxed out on Titles! You earned :coin: 300 instead!"
                # if str(titles[rand_title]) in owned_titles:
                #     await crown_utilities.bless(150, player.id)
                #     return f"You already own **{titles[rand_title]}**! You earn :coin: **150**."
                # response = db.updateVaultNoFilter(vault_query, {'$addToSet': {'TITLES': str(titles[rand_title])}})
                # return f"You earned _Title:_ **{titles[rand_title]}**!"
                u = await main.bot.fetch_user(player.id)
                response = await crown_utilities.store_drop_card(u, player.id, titles[rand_title], universe, vault, owned_destinies, 150, 150, "mode", False, 0, "titles")
                return response
            else:
                await crown_utilities.bless(150, player.id)
                return f"You earned :coin: **150**!"
        elif drop_rate <= arm_drop and drop_rate > title_drop:
            if all_available_drop_arms:
                # if len(vault['ARMS']) >= 25:
                #     await crown_utilities.bless(300, player.id)
                #     return f"You're maxed out on Arms! You earned :coin: 300 instead!"
                # if str(arms[rand_arm]) in owned_arms:
                #     await crown_utilities.bless(150, player.id)
                #     return f"You already own **{arms[rand_arm]}**! You earn :coin: **150**."
                # else:
                #     response = db.updateVaultNoFilter(vault_query, {'$addToSet': {'ARMS': {'ARM': str(arms[rand_arm]), 'DUR': durability}}})
                #     return f"You earned _Arm:_ **{arms[rand_arm]}** with ⚒️**{str(durability)}**!"
                u = await main.bot.fetch_user(player.id)
                response = await crown_utilities.store_drop_card(u, player.id, arms[rand_arm], universe, vault, durability, 2000, 2000, "mode", False, 0, "arms")
            else:
                await crown_utilities.bless(150, player.id)
                return f"You earned :coin: **150**!"
        elif drop_rate <= pet_drop and drop_rate > arm_drop:
            if all_available_drop_pets:
                if len(vault['PETS']) >= 25:
                    await crown_utilities.bless(300, player.id)
                    return f"You're maxed out on Summons! You earned :coin: 300 instead!"

                pet_owned = False
                for p in vault['PETS']:
                    if p['NAME'] == pets[rand_pet]:
                        pet_owned = True

                if pet_owned:

                    await crown_utilities.bless(150, player.id)
                    return f"You own _Summon:_ **{pets[rand_pet]}**! Received extra + :coin: 150!"
                else:

                    selected_pet = db.queryPet({'PET': pets[rand_pet]})
                    pet_ability_name = list(selected_pet['ABILITIES'][0].keys())[0]
                    pet_ability_power = list(selected_pet['ABILITIES'][0].values())[0]
                    pet_ability_type = list(selected_pet['ABILITIES'][0].values())[1]

                    response = db.updateVaultNoFilter(vault_query, {'$addToSet': {
                        'PETS': {'NAME': selected_pet['PET'], 'LVL': 0, 'EXP': 0, pet_ability_name: int(pet_ability_power),
                                'TYPE': pet_ability_type, 'BOND': 0, 'BONDEXP': 0, 'PATH': selected_pet['PATH']}}})
                    await crown_utilities.bless(50, player.id)
                    return f"You earned _Summon:_ **{pets[rand_pet]}** + :coin: 50!"
            else:
                await crown_utilities.bless(150, player.id)
                return f"You earned :coin: **150**!"
        elif drop_rate <= card_drop and drop_rate > pet_drop:
            if all_available_drop_cards:
                u = await main.bot.fetch_user(player.id)
                response = await crown_utilities.store_drop_card(u, player.id, cards[rand_card], universe, vault, owned_destinies, 3000, 1000, "mode", False, 0, "cards")
                if not response:
                    bless_amount = (5000 + (2500 * matchcount)) * (1 + rebirth)
                    await crown_utilities.bless(bless_amount, player.id)
                    return f"You earned :coin: **{bless_amount}**!"
                return response
            else:
                await crown_utilities.bless(5000, player.id)
                return f"You earned :coin: **5000**!"
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'player': str(player),
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        await crown_utilities.bless(5000, player.id)
        guild = self.bot.get_guild(main.guild_id)
        channel = guild.get_channel(main.guild_channel)
        await channel.send(f"'PLAYER': **{str(player)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")

        return f"You earned :coin: **5000**!"


async def specific_drops(self,player, card, universe):
    vault_query = {'DID': str(player)}
    vault = db.queryVault(vault_query)
    user_query = {'DID': str(player)}
    user = db.queryUser(user_query)

    if user['DIFFICULTY'] == "EASY":
        bless_amount = 100
        await crown_utilities.bless(100, player)
        return f"You earned :coin: **{bless_amount}**!"

    rebirth = user['REBIRTH']
    owned_destinies = []
    for destiny in vault['DESTINY']:
        owned_destinies.append(destiny['NAME'])

    try:
        u = await main.bot.fetch_user(player)
        response = await crown_utilities.store_drop_card(u, player, card, universe, vault, owned_destinies, 3000, 1000, "Purchase", False, 0, "cards")
        return response
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'player': str(player),
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        await crown_utilities.bless(5000, player.id)
        guild = self.bot.get_guild(main.guild_id)
        channel = guild.get_channel(main.guild_channel)
        await channel.send(f"'PLAYER': **{str(player)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")

        return f"You earned :coin: **5000**!"


async def dungeondrops(self, player, universe, matchcount):
    all_available_drop_cards = db.queryExclusiveDropCards(universe)
    all_available_drop_titles = db.queryExclusiveDropTitles(universe)
    all_available_drop_arms = db.queryExclusiveDropArms(universe)
    all_available_drop_pets = db.queryExclusiveDropPets(universe)
    vault_query = {'DID': str(player.id)}
    vault = db.queryVault(vault_query)
    owned_arms = []
    for arm in vault['ARMS']:
        owned_arms.append(arm['ARM'])
    owned_titles = vault['TITLES']

    user_query = {'DID': str(player.id)}
    user = db.queryUser(user_query)

    player_info = db.queryUser({'DID': str(vault['DID'])})
    difficulty = player_info['DIFFICULTY']
    if difficulty == "EASY":
        bless_amount = 100
        await crown_utilities.bless(bless_amount, player.id)
        return f"You earned :coin: **{bless_amount}**!"




    rebirth = user['REBIRTH']
    owned_destinies = []
    for destiny in vault['DESTINY']:
        owned_destinies.append(destiny['NAME'])

    cards = []
    titles = []
    arms = []
    pets = []

    if matchcount <= 3:
        bless_amount = (20000 + (2000 * matchcount)) * (1 + rebirth)
        if difficulty == "HARD":
            bless_amount = (50000 + (20000 * matchcount)) * (1 + rebirth)
        await crown_utilities.bless(bless_amount, player.id)
        return f"You earned :coin: **{bless_amount}**!"


    for card in all_available_drop_cards:
        cards.append(card['NAME'])

    for title in all_available_drop_titles:
        titles.append(title['TITLE'])

    for arm in all_available_drop_arms:
        arms.append(arm['ARM'])

    for pet in all_available_drop_pets:
        pets.append(pet['PET'])
    
    if len(cards)==0:
        rand_card = 0
    else:
        c = len(cards) - 1
        rand_card = random.randint(0, c)

    if len(titles)==0:
        rand_title= 0
    else:
        t = len(titles) - 1
        rand_title = random.randint(0, t)

    if len(arms)==0:
        rand_arm = 0
    else:
        a = len(arms) - 1
        rand_arm = random.randint(0, a)

    
    if len(pets)==0:
        rand_pet = 0
    else:
        p = len(pets) - 1
        rand_pet = random.randint(0, p)


    gold_drop = 250  #
    rift_rate = 300  #
    rematch_rate = 350
    title_drop = 380  #
    arm_drop = 390  #
    pet_drop = 396  #
    card_drop = 400  #
    drop_rate = random.randint((0 + (rebirth * rebirth) * (1 + rebirth)), 400)
    durability = random.randint(10, 75)
    mode="Dungeon"
    if difficulty == "HARD":
        gold_drop = 30  
        rift_rate = 55
        rematch_rate = 70
        title_drop = 75  
        arm_drop = 100  
        pet_drop = 250  
        card_drop = 300 
        drop_rate = random.randint((0 + (rebirth * rebirth) * (1 + rebirth)), 300)
        durability = 100
        mode="Purchase"

    try:
        if drop_rate <= gold_drop:
            bless_amount = (30000 + (2000 * matchcount)) * (1 + rebirth)
            if difficulty == "HARD":
                bless_amount = (60000 + (5000 * matchcount)) * (1 + rebirth)
            await crown_utilities.bless(bless_amount, player.id)
            return f"You earned :coin: **{bless_amount}**!"
        elif drop_rate <= rift_rate and drop_rate > gold_drop:
            response = db.updateUserNoFilter(user_query, {'$set': {'RIFT': 1}})
            bless_amount = (35000 + (5000 * matchcount)) * (1 + rebirth)
            await crown_utilities.bless(bless_amount, player.id)
            return f"A RIFT HAS OPENED! You have earned :coin: **{bless_amount}**!"
        elif drop_rate <= rematch_rate and drop_rate > rift_rate:
            response = db.updateUserNoFilter(user_query, {'$inc': {'RETRIES': 3}})
            bless_amount = (40000 + (5000 * matchcount)) * (1 + rebirth)
            await crown_utilities.bless(bless_amount, player.id)
            return f"🆚  You have earned 3 Rematches and  :coin: **{bless_amount}**!"
        elif drop_rate <= title_drop and drop_rate > rematch_rate:
            # if len(vault['TITLES']) >= 25:
            #     await crown_utilities.bless(2500, player.id)
            #     return f"You're maxed out on Titles! You earned :coin: 2500 instead!"
            # if str(titles[rand_title]) in owned_titles:
            #         await crown_utilities.bless(2000, player.id)
            #         return f"You already own **{titles[rand_title]}**! You earn :coin: **2000**."
            # response = db.updateVaultNoFilter(vault_query, {'$addToSet': {'TITLES': str(titles[rand_title])}})
            # return f"You earned _Title:_ **{titles[rand_title]}**!"
            u = await main.bot.fetch_user(player.id)
            response = await crown_utilities.store_drop_card(u, player.id, titles[rand_title], universe, vault, owned_destinies, 30000, 30000,"mode", False, 0, "titles")
            return response
        elif drop_rate <= arm_drop and drop_rate > title_drop:
            # if len(vault['ARMS']) >= 25:
            #     await crown_utilities.bless(3000, player.id)
            #     return f"You're maxed out on Arms! You earned :coin: 3000 instead!"
            # if str(arms[rand_arm]) in owned_arms:
            #     await crown_utilities.bless(2500, player.id)
            #     return f"You already own **{arms[rand_arm]}**! You earn :coin: **2500**."
            # else:
            #     response = db.updateVaultNoFilter(vault_query, {'$addToSet': {'ARMS': {'ARM': str(arms[rand_arm]), 'DUR': durability}}})
            #     return f"You earned _Arm:_ **{arms[rand_arm]}** with ⚒️**{str(durability)}**!"
            u = await main.bot.fetch_user(player.id)
            response = await crown_utilities.store_drop_card(u, player.id, arms[rand_arm], universe, vault, durability, 3000, 3000,"mode", False, 0, "arms")
            return response
        elif drop_rate <= pet_drop and drop_rate > arm_drop:
            if len(vault['PETS']) >= 25:
                await crown_utilities.bless(4000, player.id)
                return f"You're maxed out on Summons! You earned :coin: 4000 instead!"
            pet_owned = False
            for p in vault['PETS']:
                if p['NAME'] == pets[rand_pet]:
                    pet_owned = True

            if pet_owned:
                await crown_utilities.bless(5000, player.id)
                return f"You own _Summon:_ **{pets[rand_pet]}**! Received extra + :coin: 5000!"
            else:
                selected_pet = db.queryPet({'PET': pets[rand_pet]})
                pet_ability_name = list(selected_pet['ABILITIES'][0].keys())[0]
                pet_ability_power = list(selected_pet['ABILITIES'][0].values())[0]
                pet_ability_type = list(selected_pet['ABILITIES'][0].values())[1]

                response = db.updateVaultNoFilter(vault_query, {'$addToSet': {
                    'PETS': {'NAME': selected_pet['PET'], 'LVL': 0, 'EXP': 0, pet_ability_name: int(pet_ability_power),
                             'TYPE': pet_ability_type, 'BOND': 0, 'BONDEXP': 0, 'PATH': selected_pet['PATH']}}})
                await crown_utilities.bless(10000, player.id)
                return f"You earned _Summon:_ **{pets[rand_pet]}** + :coin: 10000!"
        elif drop_rate <= card_drop and drop_rate > pet_drop:
            u = await main.bot.fetch_user(player.id)
            response = await crown_utilities.store_drop_card(u, player.id, cards[rand_card], universe, vault, owned_destinies, 5000, 2500,"mode", False, 0, "cards")
            return response
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'player': str(player),
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        await crown_utilities.bless(5000, player.id)
        guild = self.bot.get_guild(main.guild_id)
        channel = guild.get_channel(main.guild_channel)
        await channel.send(f"'PLAYER': **{str(player)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")

        return f"You earned :coin: **5000**!"


async def bossdrops(self,player, universe):
    all_available_drop_cards = db.queryExclusiveDropCards(universe)
    all_available_drop_titles = db.queryExclusiveDropTitles(universe)
    all_available_drop_arms = db.queryExclusiveDropArms(universe)
    all_available_drop_pets = db.queryExclusiveDropPets(universe)
    boss = db.queryBoss({'UNIVERSE': universe})
    vault_query = {'DID': str(player.id)}
    vault = db.queryVault(vault_query)
    owned_arms = []
    for arm in vault['ARMS']:
        owned_arms.append(arm['ARM'])
    owned_titles = vault['TITLES']

    user_query = {'DID': str(player.id)}
    user = db.queryUser(user_query)
    difficulty = user['DIFFICULTY']
    rebirth = user['REBIRTH']

    owned_destinies = []
    for destiny in vault['DESTINY']:
        owned_destinies.append(destiny['NAME'])

    cards = []
    titles = []
    arms = []
    pets = []
    boss_title = boss['TITLE']
    boss_arm = boss['ARM']
    boss_pet = boss['PET']
    boss_card = boss['CARD']

    for card in all_available_drop_cards:
        cards.append(card['NAME'])

    for title in all_available_drop_titles:
        titles.append(title['TITLE'])

    for arm in all_available_drop_arms:
        arms.append(arm['ARM'])

    for pet in all_available_drop_pets:
        pets.append(pet['PET'])

    if len(cards)==0:
        rand_card = 0
    else:
        c = len(cards) - 1
        rand_card = random.randint(0, c)

    if len(titles)==0:
        rand_title= 0
    else:
        t = len(titles) - 1
        rand_title = random.randint(0, t)

    if len(arms)==0:
        rand_arm = 0
    else:
        a = len(arms) - 1
        rand_arm = random.randint(0, a)

    
    if len(pets)==0:
        rand_pet = 0
    else:
        p = len(pets) - 1
        rand_pet = random.randint(0, p)


    gold_drop = 300  #
    rematch_drop = 330 #330
    title_drop = 340  #
    arm_drop = 370  #
    pet_drop = 390  #
    card_drop = 400  #
    boss_title_drop = 450  #
    boss_arm_drop = 480  #
    boss_pet_drop = 495  #
    boss_card_drop = 500  #

    drop_rate = random.randint((0 + (rebirth * rebirth) * (1 + rebirth)), 500)
    durability = random.randint(100, 150)

    try:
        if drop_rate <= gold_drop:
            bless_amount = 1000000 * (1 + rebirth)
            if difficulty == "HARD":
                bless_amount = 5000000 * (1 + rebirth)
            await crown_utilities.bless(bless_amount, player.id)
            return f"You earned :coin: {bless_amount}!"
        elif drop_rate <= rematch_drop and drop_rate > gold_drop:
            response = db.updateUserNoFilter(user_query, {'$inc': {'RETRIES': 10}})
            bless_amount = (1000000  * (1 + rebirth))
            await crown_utilities.bless(bless_amount, player.id)
            return f"🆚  You have earned 10 Rematches and  :coin: **{bless_amount}**!"
        elif drop_rate <= title_drop and drop_rate > gold_drop:
            # if len(vault['TITLES']) >= 25:
            #     await crown_utilities.bless(500000, player.id)
            #     return f"You're maxed out on Titles! You earned :coin: **500000** instead!"
            # if str(titles[rand_title]) in owned_titles:
            #         await crown_utilities.bless(30000, player.id)
            #         return f"You already own **{titles[rand_title]}**! You earn :coin: **30000**."
            # response = db.updateVaultNoFilter(vault_query, {'$addToSet': {'TITLES': str(titles[rand_title])}})
            # return f"You earned {titles[rand_title]}!"
            u = await main.bot.fetch_user(player.id)
            response = await crown_utilities.store_drop_card(u, player.id, titles[rand_title], universe, vault, owned_destinies, 30000, 30000, "Dungeon", False, 0, "titles")
            return response
        elif drop_rate <= arm_drop and drop_rate > title_drop:
            # if len(vault['ARMS']) >= 25:
            #     await crown_utilities.bless(40000, player.id)
            #     return f"You're maxed out on Arms! You earned :coin: **40000** instead!"
            # if str(arms[rand_arm]) in owned_arms:
            #     await crown_utilities.bless(40000, player.id)
            #     return f"You already own **{arms[rand_arm]}**! You earn :coin: **40000**."
            # else:
            #     response = db.updateVaultNoFilter(vault_query, {'$addToSet': {'ARMS': {'ARM': str(arms[rand_arm]), 'DUR': durability}}})
            #     return f"You earned _Arm:_ **{arms[rand_arm]}** with ⚒️**{str(durability)}**!"
            u = await main.bot.fetch_user(player.id)
            response = await crown_utilities.store_drop_card(u, player.id, arms[rand_arm], universe, vault, durability, 40000, 40000, "Dungeon", False, 0, "arms")
            return response
        elif drop_rate <= pet_drop and drop_rate > arm_drop:
            if len(vault['PETS']) >= 25:
                await crown_utilities.bless(8000, player.id)
                return f"You're maxed out on Summons! You earned :coin: 8000 instead!"
            selected_pet = db.queryPet({'PET': pets[rand_pet]})
            pet_ability_name = list(selected_pet['ABILITIES'][0].keys())[0]
            pet_ability_power = list(selected_pet['ABILITIES'][0].values())[0]
            pet_ability_type = list(selected_pet['ABILITIES'][0].values())[1]

            response = db.updateVaultNoFilter(vault_query, {'$addToSet': {
                'PETS': {'NAME': selected_pet['PET'], 'LVL': 0, 'EXP': 0, pet_ability_name: int(pet_ability_power),
                         'TYPE': pet_ability_type, 'BOND': 0, 'BONDEXP': 0, 'PATH': selected_pet['PATH']}}})
            await crown_utilities.bless(750000, player.id)
            return f"You earned {pets[rand_pet]} + :coin: 750000!"
        elif drop_rate <= card_drop and drop_rate > pet_drop:
            u = await main.bot.fetch_user(player.id)
            response = await crown_utilities.store_drop_card(u, player.id, cards[rand_card], universe, vault, owned_destinies, 500000, 500000, "Dungeon", False, 0, "cards")
            return response
        elif drop_rate <= boss_title_drop and drop_rate > card_drop:
            # if len(vault['TITLES']) >= 25:
            #     await crown_utilities.bless(10000000, player.id)
            #     return f"You're maxed out on Titles! You earned :coin: **10,000,000** instead!"
            # response = db.updateVaultNoFilter(vault_query, {'$addToSet': {'TITLES': str(boss_title)}})
            # return f"You earned the Exclusive Boss Title: {boss_title}!"
            u = await main.bot.fetch_user(player.id)
            response = await crown_utilities.store_drop_card(u, player.id, boss_title, universe, vault, owned_destinies, 50000, 50000, "Boss", False, 0, "titles")
            return response
        elif drop_rate <= boss_arm_drop and drop_rate > boss_title_drop:
            # if len(vault['ARMS']) >= 25:
            #     await crown_utilities.bless(10000000, player.id)
            #     return f"You're maxed out on Arms! You earned :coin: **10,000,000** instead!"
            # if str(boss_arm) in owned_arms:
            #     await crown_utilities.bless(9000000, player.id)
            #     return f"You already own **{arms[rand_arm]}**! You earn :coin: **9,000,000**."
            # else:
            #     response = db.updateVaultNoFilter(vault_query, {'$addToSet': {'ARMS': {'ARM': str(boss_arm), 'DUR': durability}}})
            #     return f"You earned the Exclusive Boss Arm: **{str(boss_arm)}** with ⚒️**{str(durability)}**!"
            u = await main.bot.fetch_user(player.id)
            response = await crown_utilities.store_drop_card(u, player.id, boss_arm, universe, vault, durability, 9000000, 9000000, "Boss", False, 0, "arms")
            return response
        elif drop_rate <= boss_pet_drop and drop_rate > boss_arm_drop:
            if len(vault['PETS']) >= 25:
                await crown_utilities.bless(1500000, player.id)
                return f"You're maxed out on Summons! You earned :coin: **15,000,000** instead!"
            selected_pet = db.queryPet({'PET': boss['PET']})
            pet_ability_name = list(selected_pet['ABILITIES'][0].keys())[0]
            pet_ability_power = list(selected_pet['ABILITIES'][0].values())[0]
            pet_ability_type = list(selected_pet['ABILITIES'][0].values())[1]

            response = db.updateVaultNoFilter(vault_query, {'$addToSet': {
                'PETS': {'NAME': selected_pet['PET'], 'LVL': 0, 'EXP': 0, pet_ability_name: int(pet_ability_power),
                         'TYPE': pet_ability_type, 'BOND': 0, 'BONDEXP': 0, 'PATH': selected_pet['PATH']}}})
            await crown_utilities.bless(10000000, player.id)
            return f"You earned the Exclusive Boss Summon:  {boss['PET']} + :coin: **10,000,000**!"
        elif drop_rate <= boss_card_drop and drop_rate > boss_pet_drop:
            u = await main.bot.fetch_user(player.id)
            response = await crown_utilities.store_drop_card(u, player.id, boss_card, universe, vault, owned_destinies, 30000, 10000, "Boss", False, 0, "cards")
            return response
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'player': str(player),
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        await crown_utilities.bless(5000, player.id)
        guild = self.bot.get_guild(main.guild_id)
        channel = guild.get_channel(main.guild_channel)
        await channel.send(f"'PLAYER': **{str(player)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")

        return f"You earned :coin: **5000**!"


enhancer_mapping = {'ATK': 'Increase Attack %',
'DEF': 'Increase Defense %',
'STAM': 'Increase Stamina',
'HLT': 'Heal yourself or companion',
'LIFE': 'Steal Health from Opponent',
'DRAIN': 'Drain Stamina from Opponent',
'FLOG': 'Steal Attack from Opponent',
'WITHER': 'Steal Defense from Opponent',
'RAGE': 'Lose Defense, Increase AP',
'BRACE': 'Lose Attack, Increase AP',
'BZRK': 'Lose Health, Increase Attack',
'CRYSTAL': 'Lose Health, Increase Defense',
'GROWTH': 'Lose 10% Max Health, Increase Attack, Defense and AP',
'STANCE': 'Swap your Attack & Defense, Increase Defense',
'CONFUSE': 'Swap Opponent Attack & Defense, Decrease Opponent Defense',
'BLINK': 'Decrease your  Stamina, Increase Target Stamina',
'SLOW': 'Increase Opponent Stamina, Decrease Your Stamina then Swap Stamina with Opponent',
'HASTE': 'Increase your Stamina, Decrease Opponent Stamina then Swap Stamina with Opponent',
'FEAR': 'Lose 10% Max Health, Decrease Opponent Attack, Defense and AP',
'SOULCHAIN': 'You and Your Opponent Stamina Link',
'GAMBLE': 'You and Your Opponent Health Link',
'WAVE': 'Deal Damage, Decreases over time',
'CREATION': 'Heals you, Decreases over time',
'BLAST': 'Deals Damage, Increases over time based on card tier',
'DESTRUCTION': 'Decreases Your Opponent Max Health, Increases over time based on card tier',
'BASIC': 'Increase Basic Attack AP',
'SPECIAL': 'Increase Special Attack AP',
'ULTIMATE': 'Increase Ultimate Attack AP',
'ULTIMAX': 'Increase All AP Values',
'MANA': 'Increase Enchancer AP',
'SHIELD': 'Blocks Incoming DMG, until broken',
'BARRIER': 'Nullifies Incoming Attacks, until broken',
'PARRY': 'Returns 25% Damage, until broken',
'SIPHON': 'Heal for 10% DMG inflicted + AP'
}
title_enhancer_mapping = {'ATK': 'Increase Attack',
'DEF': 'Increase Defense',
'STAM': 'Increase Stamina',
'HLT': 'Heal for AP',
'LIFE': 'Steal AP Health',
'DRAIN': 'Drain Stamina from Opponent',
'FLOG': 'Steal Attack from Opponent',
'WITHER': 'Steal Defense from Opponent',
'RAGE': 'Lose Defense, Increase AP',
'BRACE': 'Lose Attack, Increase AP',
'BZRK': 'Lose Health, Increase Attack',
'CRYSTAL': 'Lose Health, Increase Defense',
'GROWTH': 'Lose 5% Max Health, Increase Attack, Defense and AP',
'STANCE': 'Swap your Attack & Defense, Increase Defense',
'CONFUSE': 'Swap Opponent Attack & Defense, Decrease Opponent Defense',
'BLINK': 'Decrease your Stamina, Increase Target Stamina',
'SLOW': 'Decrease Turn Count by 1',
'HASTE': 'Increase Turn Count By 1',
'FEAR': 'Lose 5% MAx Health, Decrease Opponent Attack, Defense and AP',
'SOULCHAIN': 'Both players stamina regen equals AP',
'GAMBLE': 'Focusing players health regen equals to AP',
'WAVE': 'Deal Damage, Decreases over time',
'CREATION': 'Heals you, Decreases over time',
'BLAST': 'Deals Damage on your turn based on card tier',
'DESTRUCTION': 'Decreases Your Opponent Max Health, Increases over time based on card tier',
'BASIC': 'Increase Basic Attack AP',
'SPECIAL': 'Increase Special Attack AP',
'ULTIMATE': 'Increase Ultimate Attack AP',
'ULTIMAX': 'Increase All AP Values',
'MANA': 'Increase Enchancer AP',
'SHIELD': 'Blocks Incoming DMG, until broken',
'BARRIER': 'Nullifies Incoming Attacks, until broken',
'PARRY': 'Returns 25% Damage, until broken',
'SIPHON': 'Heal for 10% DMG inflicted + AP'
}

element_mapping = {'PHYSICAL': 'If ST(stamina) greater than 80, Deals double Damage',
'FIRE': 'Does 25% damage of previous attack over the next opponent turns, stacks',
'ICE': 'After 2 uses opponent freezes and loses 1 turn',
'WATER': 'Increases all water attack dmg by 40 Flat',
'EARTH': 'Cannot be Parried. Increases Def by 25% AP',
'ELECTRIC': 'Add 15% to Shock damage, added to each attack',
'WIND': 'Cannot Miss, boost all wind damage by 15% DMG',
'PSYCHIC': 'Penetrates Barriers. Reduce opponent ATK & DEF by 15% AP',
'DEATH': 'Adds 20% opponent max health as damage',
'LIFE': 'Heal for 20% AP',
'LIGHT': 'Regain 50% Stamina Cost, Increase ATK by 20% DMG',
'DARK': 'Penetrates shields & decrease opponent stamina by 15',
'POISON': 'Penetrates shields, Opponent takes additional 30 damage each turn stacking up to 600',
'RANGED': 'If ST(Stamina) > 30 deals 1.7x Damage',
'SPIRIT': 'Has higher chance of Crit',
'RECOIL': 'Deals 60% damage back to you, if damage would kill you reduce health to 1',
'TIME': 'IF ST(Stamina) < 80 you Focus after attacking, You Block during your Focus',
'BLEED': 'After 3 Attacks deal 10x turn count damage to opponent',
'GRAVITY': 'Disables Opponent Block and Reduce opponent DEF by 25% AP'
}

passive_enhancer_suffix_mapping = {'ATK': ' %',
'DEF': ' %',
'STAM': ' Flat',
'HLT': ' %',
'LIFE': '%',
'DRAIN': ' Flat',
'FLOG': '%',
'WITHER': '%',
'RAGE': '%',
'BRACE': '%',
'BZRK': '%',
'CRYSTAL': '%',
'GROWTH': ' Flat',
'STANCE': ' Flat',
'CONFUSE': ' Flat',
'BLINK': ' Flat',
'SLOW': ' Flat',
'HASTE': ' Flat',
'FEAR': ' Flat',
'SOULCHAIN': ' Flat',
'GAMBLE': ' Flat',
'WAVE': ' Flat',
'CREATION': '%',
'BLAST': ' Flat',
'DESTRUCTION': '%',
'BASIC': ' Flat',
'SPECIAL': ' Flat',
'ULTIMATE': ' Flat',
'ULTIMAX': ' Flat',
'MANA': ' %',
'SHIELD': ' DMG 🌐',
'BARRIER': ' Blocks 💠',
'PARRY': ' Counters 🔄',
'SIPHON': ' Healing 💉'
}


enhancer_suffix_mapping = {'ATK': '%',
'DEF': '%',
'STAM': ' Flat',
'HLT': '%',
'LIFE': '%',
'DRAIN': ' Flat',
'FLOG': '%',
'WITHER': '%',
'RAGE': '%',
'BRACE': '%',
'BZRK': '%',
'CRYSTAL': '%',
'GROWTH': ' Flat',
'STANCE': ' Flat',
'CONFUSE': ' Flat',
'BLINK': ' Flat',
'SLOW': ' Flat',
'HASTE': ' Flat',
'FEAR': ' Flat',
'SOULCHAIN': ' Flat',
'GAMBLE': ' Flat',
'WAVE': ' Flat',
'CREATION': ' Flat',
'BLAST': ' Flat',
'DESTRUCTION': ' Flat',
'BASIC': ' Flat',
'SPECIAL': ' Flat',
'ULTIMATE': ' Flat',
'ULTIMAX': ' Flat',
'MANA': ' %',
'SHIELD': ' DMG 🌐',
'BARRIER': ' Blocks 💠',
'PARRY': ' Counters 🔄',
'SIPHON': ' Healing 💉'
}
title_enhancer_suffix_mapping = {'ATK': ' Flat',
'DEF': ' Flat',
'STAM': ' Flat',
'HLT': ' %',
'LIFE': '%',
'DRAIN': ' Flat',
'FLOG': '%',
'WITHER': '%',
'RAGE': '%',
'BRACE': '%',
'BZRK': '%',
'CRYSTAL': '%',
'GROWTH': ' Flat',
'STANCE': ' Flat',
'CONFUSE': ' Flat',
'BLINK': ' Flat',
'SLOW': ' Turn',
'HASTE': ' Turn',
'FEAR': ' Flat',
'SOULCHAIN': ' Flat',
'GAMBLE': ' Flat',
'WAVE': ' Flat',
'CREATION': '%',
'BLAST': ' Flat',
'DESTRUCTION': '%',
'BASIC': ' Flat',
'SPECIAL': ' Flat',
'ULTIMATE': ' Flat',
'ULTIMAX': ' Flat',
'MANA': ' %',
'SHIELD': ' DMG 🌐',
'BARRIER': ' Blocks 💠',
'PARRY': ' Counters 🔄',
'SIPHON': ' Healing 💉'
}

abyss_floor_reward_list = [10,20,30,40,50,60,70,80,90,100]

crown_rift_universe_mappings = {'Crown Rift Awakening': 3, 'Crown Rift Slayers': 2, 'Crown Rift Madness': 5}
Healer_Enhancer_Check = ['HLT', 'LIFE']
DPS_Enhancer_Check = ['FLOG', 'WITHER']
INC_Enhancer_Check = ['ATK', 'DEF']
TRADE_Enhancer_Check = ['RAGE', 'BRACE']
Gamble_Enhancer_Check = ['GAMBLE', 'SOULCHAIN']
SWITCH_Enhancer_Check = ['STANCE', 'CONFUSE']
Time_Enhancer_Check = ['HASTE', 'SLOW','BLINK']
Support_Enhancer_Check = ['DEF', 'ATK', 'WITHER', 'FLOG']
Sacrifice_Enhancer_Check = ['BZRK', 'CRYSTAL']
FORT_Enhancer_Check = ['GROWTH', 'FEAR']
Stamina_Enhancer_Check = ['STAM', 'DRAIN']
Control_Enhancer_Check = ['SOULCHAIN']
Damage_Enhancer_Check = ['DESTRUCTION', 'BLAST']
Turn_Enhancer_Check = ['WAVE', 'CREATION']
take_chances_messages = ['You lost immediately.', 'You got smoked!', 'You fainted before the fight even started.',
                         'That... was just sad. You got dropped with ease.', 'Too bad, so sad. You took the L.',
                         'Annnd another L. You lost.', 'Annnnnnnnnnnd another L! You lost.',
                         'How many Ls you gonna take today?', 'That was worse than the last time. You got dropped.']

pokemon_universes= ['Kanto Region', 'Johnto Region', 'Hoenn Region', 'Sinnoh Region', 'Kalos Region', 'Galar Region', 'Alola Region', 'Unova Region']