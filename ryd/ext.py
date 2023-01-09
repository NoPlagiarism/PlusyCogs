from redbot.core import commands, Config
from .config import Settings
import re
import aiohttp
from collections import namedtuple
from typing import Optional
import discord
from enum import Enum

votes_tuple = namedtuple("Votes", ['video_id', 'likes', 'dislikes'])


class ChannelScan(Enum):
    DISABLED = 0
    ENABLED = 1
    WHITELISTED = 2


class RYDCog(commands.Cog):
    """'Return YouTube Dislikes' cog"""
    def __init__(self, bot):
        self.bot = bot
        super(RYDCog, self).__init__()
        self.config = Config.get_conf(self, identifier=1984027022015)  # RIP Nemtsov, Fuck Kadyrov
        default_global = {
            "enabled_scan": True,
            "ignore_max": Settings.IGNORE_MAX_REACHED  # True by default
        }
        default_guild = {
            "enabled_scan": True,
            "whitelist_mode": False
        }
        default_member = {
            "enabled_scan": True
        }
        default_channel = {
            "enabled_scan": ChannelScan.ENABLED
        }
        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)
        self.config.register_member(**default_member)
        self.config.register_channel(**default_channel)

    @staticmethod
    def find_video_ids(text):
        res_ids = list()
        for match in re.finditer(Settings.YT_ID_REGEX_TEXT, text):
            if (video_id := match.groupdict().get("videoId")) is not None:
                res_ids.append(video_id)
        return res_ids

    @staticmethod
    async def get_votes(video_id) -> Optional[votes_tuple]:
        async with aiohttp.ClientSession(headers=Settings.REQUEST_HEADERS) as session:
            async with session.get(Settings.VOTES_URL, params={"videoId": video_id}) as response:
                if response.status in (404, 400):
                    return None
                json_resp = await response.json()
        return votes_tuple(json_resp['id'], json_resp['likes'], json_resp['dislikes'])

    @staticmethod
    def get_readable_votes_pbar(votes: votes_tuple, per_ratio=None,
                                ratio_full=None, ratio_empty=None,
                                display_like=None, display_dislike=None):
        if per_ratio is None:
            per_ratio = Settings.DISPLAY_PER_RATIO
        if ratio_full is None:
            ratio_full = Settings.DISPLAY_RATIO_FULL
        if ratio_empty is None:
            ratio_empty = Settings.DISPLAY_RATIO_EMPTY
        if display_like is None:
            display_like = Settings.DISPLAY_LIKE
        if display_dislike is None:
            display_dislike = Settings.DISPLAY_DISLIKE
        result = "{like} {likes} `{ratio}` {dislikes} {dislike}"
        size = per_ratio * 2
        ratio_full_len = round((votes.likes / (votes.likes + votes.dislikes)) * size)
        ratio = ratio_full * ratio_full_len + ratio_empty * (size - ratio_full_len)
        result = result.format(like=display_like, dislike=display_dislike,
                               ratio=ratio,
                               likes=votes.likes, dislikes=votes.dislikes)
        return result

    async def get_readable_line_votes_by_ctx(self, ctx, votes: votes_tuple):
        return self.get_readable_votes_pbar(votes)

    @commands.command(aliases=("returnyoutubedislike", "ytdislikes"))
    async def ryd(self, ctx, url):
        """Insert YouTube video url or id as argument to get dislikes count"""
        if not (video_id := self.find_video_ids(url)):
            video_id = [url]
        try:
            votes = await self.get_votes(video_id[0])
        except IndexError:
            votes = None
        if votes is None:
            return None
        msg = await self.get_readable_line_votes_by_ctx(ctx, votes)
        return await ctx.reply(msg)

    async def should_ignore(self, message: discord.Message, *, edit: bool = False) -> bool:
        if edit:
            return True
        if not await self.config.enabled_scan():
            return True
        guild = message.guild
        if guild is None or message.author.bot:
            return True
        if await self.bot.cog_disabled_in_guild(self, guild):
            return True
        if not await self.config.guild(guild).enabled_scan():
            return True
        if not await self.config.channel(message.channel).enabled_scan():
            return True
        if not await self.config.member(message.author).enabled_scan():
            return True
        return False

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message, *, edit: bool = False) -> None:
        if await self.should_ignore(message, edit=edit):
            return
        if not (video_ids := self.find_video_ids(message.content)):
            return
        if len(video_ids) > Settings.MAX_DISPLAYED:
            if await self.config.ignore_max():
                return
            video_ids = video_ids[:Settings.MAX_DISPLAYED]
        lines = list()
        for video_id in video_ids:
            votes = await self.get_votes(video_id)
            lines.append(await self.get_readable_line_votes_by_ctx(await self.bot.get_context(message), votes))
        return await message.reply("\n".join(lines))

    @commands.group(name="ryd-config")
    async def ryd_config(self, ctx):
        """Change settings of RYD Cog"""
        pass

    @ryd_config.group(name="global")
    @commands.is_owner()
    async def config_global(self, ctx):
        pass

    @config_global.command(name="disable")
    async def global_disable_toggle(self, ctx):
        """Disable/Enable message scanning for the bot"""
        old_value = await self.config.enabled_scan()
        new_value = not old_value
        await self.config.enabled_scan.set(new_value)
        return await ctx.reply(" ".join(("Message scanning is", {True: "Enabled", False: "Disabled"}[new_value], "now")))

    @ryd_config.group(name="me")
    @commands.guild_only()
    async def config_member(self, ctx):
        pass

    @config_member.command(name="disable")
    async def member_disable_toggle(self, ctx):
        """Disable/Enable message scanning for the specific person"""
        old_value = await self.config.member(ctx.author).enabled_scan()
        new_value = not old_value
        await self.config.member(ctx.author).enabled_scan.set(new_value)
        return await ctx.reply(" ".join(("Message scanning is", {True: "Enabled", False: "Disabled"}[new_value], "now")))

    @ryd_config.group("guild")
    @commands.admin()
    @commands.guild_only()
    async def config_guild(self, ctx):
        pass

    @config_guild.command(name="disable")
    async def guild_disable_toggle(self, ctx):
        """Disable/Enable message scanning for guild"""
        old_value = await self.config.guild(ctx.guild).enabled_scan()
        new_value = not old_value
        await self.config.guild(ctx.guild).enabled_scan.set(new_value)
        return await ctx.reply(" ".join(("Message scanning is", {True: "Enabled", False: "Disabled"}[new_value], "now")))

    @config_guild.command(name="channel")
    async def channel_disable_toggle(self, ctx, channel: discord.TextChannel = None):
        """Disable/Enable message scanning for channel"""
        if channel is None:
            channel = ctx.channel
        old_value = await self.config.channel(channel).enabled_scan()
        new_value = not old_value
        await self.config.channel(channel).enabled_scan.set(new_value)
        return await ctx.reply(" ".join(("Message scanning is", {True: "Enabled", False: "Disabled"}[new_value], "now")))
