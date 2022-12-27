import discord
from .config import Settings
from redbot.core import commands, data_manager
from .reader import Va11HallaJSON, Va11DataManager, Va11ReaderException
import json
from math import ceil
import random
from typing import Optional


def progress_bar(value, max_value, size=10):
    """Просто прогресс бар"""
    progress_string = '▇'
    empty_string = '—'

    progress = round((value / max_value) * size)
    empty = size - progress

    bar = "[" + progress_string * progress + empty_string * empty + "]"
    return bar, progress


class DialEmbed(discord.Embed):
    def __init__(self, dial=None, character_uri=None):
        super(DialEmbed, self).__init__(colour=Settings.EMBED_COLOR)
        self.dial, self.character_uri = dial, character_uri
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


class Va11Halla(commands.Cog):
    def __init__(self, bot, validate_download=True):
        self.bot = bot
        path = data_manager.cog_data_path(cog_instance=self)
        self._manager = Va11DataManager(path)
        if validate_download:
            self._manager.validate_and_download()
            self.readers = self._manager.get_all_readers()
        with open(Settings.ICONS_PATH, encoding="utf-8", mode="r") as f:
            self.icons = json.load(f)["char_icons"]

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        original = getattr(error, "original", None)
        if original:
            if isinstance(original, Va11ReaderException):
                return ctx.reply(str(original))
        return await ctx.bot.on_command_error(ctx, error, unhandled_by_cog=True)

    def get_random_icon(self):
        return random.choice(tuple(self.icons.values()))

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
        return tuple(self.readers.keys()), self.get_random_icon(), 1

    def get_lang_from_ctx(self, ctx):
        return Settings.DEF_LANG  # TODO: obvi

    def get_reader_from_ctx(self, ctx):
        return self.readers[self.get_lang_from_ctx(ctx)]

    @commands.command(aliases=("va11", "valhalla"))
    async def va11halla(self, ctx, *args):
        data = self.get_reader_from_ctx(ctx)
        lang = None
        script = None
        line = None
        character = None
        for arg in args:
            if arg in self.readers.keys():
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

        embed = DialEmbed(dial, self.icons[data.names[dial.character]])
        return await ctx.send(embed=embed)

    @commands.command(name="va11halla-list", aliases=("va11-list", "valhalla-list", "va11list", "va11hallalist"))
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
