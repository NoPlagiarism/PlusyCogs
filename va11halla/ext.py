import discord
from .config import Settings
from redbot.core import commands, data_manager, Config
from redbot.core.utils import AsyncIter
from redbot.vendored.discord.ext import menus
from .reader import Va11HallaJSON, Va11DataManager, Va11ReaderException
import json
from math import ceil
import random
from typing import Optional


with open(Settings.ICONS_PATH, encoding="utf-8", mode="r") as f:
    ICONS = json.load(f)["char_icons"]


def progress_bar(value, max_value, size=10):
    """Просто прогресс бар"""
    progress_string = '▇'
    empty_string = '—'

    progress = round((value / max_value) * size)
    empty = size - progress

    bar = "[" + progress_string * progress + empty_string * empty + "]"
    return bar, progress


class DialEmbed(discord.Embed):
    def __init__(self, dial=None, character_uri=None, data=None):
        super(DialEmbed, self).__init__(colour=Settings.EMBED_COLOR)
        self.dial, self.character_uri = dial, character_uri
        self.data = data
        if dial is not None and character_uri is not None:
            self.update_embed(dial, character_uri)

    def update_embed(self, dial=None, character_uri=None, _clear=True):
        if _clear:
            self.clear_fields()
        if dial is not None and character_uri is not None:
            self.dial, self.character_uri = dial, character_uri
        if str(self.dial) == "":
            self.dial.text = "..."
        self.add_field(name=self.dial.character, value=str(self.dial), inline=False)
        progress_bar_str, percent = progress_bar(dial.line, dial.script.lines)
        self.set_footer(text=f"{repr(dial.script)} {progress_bar_str} {dial.line}/{dial.script.lines}")
        self.set_thumbnail(url=character_uri)

    @property
    def line(self) -> int:
        return self.dial.line

    @property
    def lang(self) -> str:
        return self.dial.lang

    def is_next_line_available(self):
        return self.dial.line != self.dial.script.lines

    def is_prev_line_available(self):
        return self.dial.line != 1

    def random(self):
        dial = self.data.random_from_scripts()
        self.update_embed(dial, ICONS[self.data.names[dial.character]])

    def go_to_prev(self, next_=False):
        if not next_:
            line = self.line - 1
        else:
            line = self.line + 1
        dial = self.data.get_script_line(line, meta=self.dial.script)
        self.update_embed(dial, ICONS[self.data.names[dial.character]])


class Va11HallaMenu(menus.Menu):
    async def send_initial_message(self, ctx, channel):
        return await ctx.send(embed=self.va11_embed)

    def __init__(self, embed: DialEmbed):
        self.va11_embed = embed

        super(Va11HallaMenu, self).__init__(timeout=Settings.REACTIONS_TIMEOUT,
                                            clear_reactions_after=True)
        self.add_all_buttons()

    def add_all_buttons(self):
        for emoji in (Settings.ReactionsEmojis.PREV, Settings.ReactionsEmojis.RANDOM, Settings.ReactionsEmojis.NEXT):
            self.add_button(menus.Button(emoji, self.handle_buttons))

    async def handle_buttons(self, payload: discord.RawReactionActionEvent):
        if str(payload.emoji) == Settings.ReactionsEmojis.RANDOM:
            self.va11_embed.random()
        elif str(payload.emoji) == Settings.ReactionsEmojis.PREV and self.va11_embed.is_prev_line_available():
            self.va11_embed.go_to_prev()
        elif str(payload.emoji) == Settings.ReactionsEmojis.NEXT and self.va11_embed.is_next_line_available():
            self.va11_embed.go_to_prev(True)
        else:
            return
        return await self.message.edit(embed=self.va11_embed)


class Va11Halla(commands.Cog):
    def __init__(self, bot, validate_download=True):
        self.bot = bot
        super(Va11Halla, self).__init__()
        path = data_manager.cog_data_path(cog_instance=self)
        self._manager = Va11DataManager(path)
        if validate_download:
            self._manager.validate_and_download()
            self.readers = self._manager.get_all_readers()

        self.config = Config.get_conf(self, identifier=198403112199)  # FCKPTN
        default_guild = {
            "default_lang": Settings.DEF_LANG,
            "whitelist": None,  # if None => ALL
            "reactions": True
        }
        default_member = {
            "default_lang": Settings.DEF_LANG,
            "reactions": True
        }
        self.config.register_guild(**default_guild)
        self.config.register_member(**default_member)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        original = getattr(error, "original", None)
        if original:
            if isinstance(original, Va11ReaderException):
                return ctx.reply(str(original))
        return await ctx.bot.on_command_error(ctx, error, unhandled_by_cog=True)

    async def red_delete_data_for_user(self, *, requester, user_id):
        """Tnx for bobloy from Fox-V3
        (https://github.com/bobloy/Fox-V3/blob/db3ce301220604d537ea68a7fee10a20f4d50230/lseen/lseen.py)"""
        all_members = await self.config.all_members()
        async for guild_id, guild_data in AsyncIter(all_members.items(), steps=100):
            if user_id in guild_data:
                await self.config.member_from_ids(guild_id, user_id).clear()

    def get_random_icon(self):
        return random.choice(tuple(ICONS.values()))

    def _list_characters(self, page=None, lang=None):  # TODO: Support dogs filter
        if lang is None:
            lang = Settings.DEF_LANG
        data = self.readers[lang]
        per_page = Settings.CHARACTERS_PER_PAGE
        pages_len = ceil(len(data.characters) / per_page)
        if page is None or not (0 <= page <= pages_len - 1):
            page = 0
        characters_slice = data.characters[per_page * page:per_page * (page + 1)]
        icon = self.get_random_icon()
        return characters_slice, icon, pages_len

    def _list_scripts(self, page=None):
        scripts = self.readers[Settings.DEF_LANG].scripts
        pages_len = ceil(len(scripts) / Settings.SCRIPTS_PER_PAGE)
        if page is None or not (0 <= page <= pages_len - 1):
            page = 0
        scripts_slice = scripts[
                        Settings.SCRIPTS_PER_PAGE * page:Settings.SCRIPTS_PER_PAGE * (page + 1)]
        icon = self.get_random_icon()
        return scripts_slice, icon, pages_len

    def _list_langs(self, *args):
        return tuple(self.readers.keys()), self.get_random_icon(), 1  # TODO: Add only available languages in guild

    async def get_lang_from_ctx(self, ctx):
        whitelist_guild = await self.config.guild(ctx.guild).whitelist()
        member_def = await self.config.member(ctx.author).default_lang()
        if whitelist_guild is None:
            return member_def
        elif member_def in whitelist_guild:
            return member_def
        else:
            return await self.config.guild(ctx.guild).default_lang()

    async def get_available_langs_from_ctx(self, ctx):
        if (whitelist := await self.config.guild(ctx.guild).whitelist()) is not None:
            return whitelist
        else:
            return self.readers.keys()

    async def get_reader_from_ctx(self, ctx):
        return self.readers[await self.get_lang_from_ctx(ctx)]

    async def should_use_reactions(self, ctx):
        # Settings, channel permissions, guild config, member config
        if not Settings.USE_REACTIONS:
            return False
        permissions = ctx.channel.permissions_for(ctx.guild.me)
        if not permissions.add_reactions:
            return False
        if ctx.channel.guild is not None:
            guild_conf = await self.config.guild(ctx.channel.guild).reactions()
            if guild_conf:
                return True
        member_conf = await self.config.member(ctx.author).reactions()
        if member_conf:
            return True
        return False

    @commands.command(aliases=("va11", "valhalla"))
    async def va11halla(self, ctx, *args):
        data = await self.get_reader_from_ctx(ctx)
        lang = None
        script = None
        line = None
        character = None
        for arg in args:
            if arg in self.readers.keys():
                if arg not in (whitelist := await self.get_available_langs_from_ctx(ctx)):
                    return await ctx.reply("Choose languages from here: " + ", ".join(whitelist))
                lang = arg
                data = self.readers[lang]
            elif arg in data.scripts:
                script = arg
            elif arg in data.characters:
                character = arg
            else:
                try:
                    line = int(arg)
                except ValueError:
                    return await ctx.reply("Wrong command usage")

        if character and line:
            return await ctx.reply("Do not search character and line")
        elif line and not script:
            return await ctx.reply("Enter script firstly")

        if script and line:
            dial = data.get_script_line(line_num=line, script_name=script)
        elif script and character:
            dial = data.random_from_scripts(script_name=script, character=character)
        elif script:
            dial = data.random_from_scripts(script_name=script)
        elif character:
            dial = data.random_from_characters(character)
        else:
            dial = data.random_from_scripts()

        embed = DialEmbed(dial, ICONS[data.names[dial.character]], data=data)
        if await self.should_use_reactions(ctx):
            menu = Va11HallaMenu(embed)
            return await menu.start(ctx)
        else:
            return await ctx.send(embed=embed)

    @commands.command(name="va11-list", aliases=("va11halla-list", "valhalla-list", "va11list", "va11hallalist"))
    async def va11halla_list(self, ctx, list_type: Optional[str] = None, page: Optional[int] = None):
        if list_type is None:
            return await ctx.reply("Use as argument: scripts, characters, langs")
        if page is None:
            page = 0
        else:
            page -= 1
        try:
            func = {"characters": self._list_characters,
                    "scripts": self._list_scripts,
                    "langs": self._list_langs}[list_type]
        except KeyError:
            return await ctx.reply("Use as argument: scripts, characters, langs")
        if list_type == "langs":
            list_type = "languages"
        list_slice, icon, total_pages = func(page)
        if page > total_pages:
            page = 0
        embed = discord.Embed(colour=Settings.EMBED_COLOR, title="list of " + list_type)
        embed.add_field(name=f"Page {page + 1}", value='\n'.join(list_slice), inline=False)
        embed.set_footer(text=f"{page + 1}/{total_pages}", icon_url=icon)
        return await ctx.send(embed=embed)

    @commands.group(name="va11-config", aliases=("valhalla-config", "va11config", "va11hallaconfig", "va11halla-config"))
    async def va11halla_conf(self, ctx):
        pass

    @va11halla_conf.group(name="me")
    async def conf_local(self, ctx):
        pass

    @conf_local.command(name="lang")
    async def local_lang(self, ctx, lang: str):
        if lang not in (langs := await self.get_available_langs_from_ctx(ctx)):
            return await ctx.reply("Choose from those: " + ", ".join(langs))
        await self.config.member(ctx.author).default_lang.set(lang)
        return await ctx.reply("Default language changed")

    @conf_local.command(name="reactions")
    async def toggle_member_reactions(self, ctx):
        old_value = await self.config.member(ctx.author).reactions()
        new_value = not old_value
        await self.config.member(ctx.author).reactions.set(new_value)
        return await ctx.reply(" ".join("Reactions are" + {True: "Enabled", False: "Disabled"}[new_value] + "now"))

    @va11halla_conf.group(name="guild")
    @commands.admin()
    @commands.guild_only()
    async def conf_guild(self, ctx):
        pass

    @conf_guild.command(name="lang")
    async def guild_lang(self, ctx, lang: str):
        if lang not in self.readers.keys():
            return await ctx.reply("Choose from those: " + ", ".join(self.readers.keys()))
        await self.config.guild(ctx.guild).default_lang.set(lang)
        return await ctx.reply("Default language changed")

    @conf_guild.command(name="whitelist")
    async def guild_whitelist(self, ctx, lang: str):
        if lang == "clear":
            await self.config.guild(ctx.guild).whitelist.set(None)
            return await ctx.reply("Whitelist cleared")
        if lang not in self.readers.keys():
            return await ctx.reply("Choose from those: " + ", ".join(self.readers.keys()))
        old_whitelist = await self.config.guild(ctx.guild).whitelist()
        if old_whitelist is None:
            await self.config.guild(ctx.guild).whitelist.set([lang])
            return await ctx.reply("Language added to whitelist")
        if lang not in old_whitelist:
            old_whitelist.append(lang)
            await self.config.guild(ctx.guild).whitelist.set(old_whitelist)
            return await ctx.reply("Language added to whitelist")
        else:
            old_whitelist.remove(lang)
            await self.config.guild(ctx.guild).whitelist.set(old_whitelist)
            return await ctx.reply("Language removed from whitelist")

    @conf_guild.command(name="reactions")
    async def toggle_guild_reactions(self, ctx):
        old_value = await self.config.guild(ctx.guild).reactions()
        new_value = not old_value
        await self.config.guild(ctx.guild).reactions.set(new_value)
        return await ctx.reply(" ".join("Reactions are" + {True: "Enabled", False: "Disabled"}[new_value] + "now"))

    @conf_guild.command(name="show")
    async def guild_show(self, ctx):
        whitelist = ", ".join(await self.config.guild(ctx.guild).whitelist()) if await self.config.guild(ctx.guild).whitelist() is not None else "Disabled"
        guild_default = await self.config.guild(ctx.guild).default_lang()
        reactions = "Enabled" if await self.config.guild(ctx.guild).reactions() else "Disabled"

        return await ctx.send(
            "VA-11 HALL-A's Guild Settings\n"
            f"Whitelist: {whitelist}\n"
            f"Guild Default Language: {guild_default}\n"
            f"Reactions are {reactions}"
        )

