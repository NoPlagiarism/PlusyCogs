import discord
from redbot.core import commands, Config
from .config import Settings
from .api import OneImageGenerator, SeedGenerator, CityGenerator
from aiohttp import ClientError
import functools
from redbot.core.i18n import Translator, cog_i18n

_ = Translator("Exists", __file__)


class NSFWCheckFailed(Exception):
    def __str__(self):
        return _("NO HORNY!!!")


async def command_check_blacklist(ctx):
    command_name = ctx.command.name
    cog = ctx.command.cog
    if command_name not in Settings.ALIASES.keys():
        return
    blacklist = await cog.config.guild(ctx.guild).blacklist()
    if command_name in blacklist:
        await ctx.reply(_("Generator has been disabled on this server"))
        return False
    return True


@cog_i18n(_)
class Exists(commands.Cog):
    """This x does not 'Exists' cog"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=141012082000)  # Она утонула.
        default_guild = {
            "blacklist": list(),
            "nsfw": False
        }
        self.config.register_guild(**default_guild)
        super(Exists, self).__init__()

    @commands.group(name="exists-config")
    async def exists_conf(self, ctx):
        pass

    @commands.guild_only()
    @commands.admin()
    @exists_conf.group(name="guild")
    async def conf_guild(self, ctx):
        pass

    @conf_guild.command(name="blacklist", aliases=("del", "rem"))
    async def exists_blacklist(self, ctx, remove: str):
        if remove == "clear":
            await self.config.guild(ctx.guild).blacklist.set(list())
            return await ctx.reply(_("Blacklist cleared"))
        if remove not in Settings.ALIASES:
            return await ctx.reply(_("Wrong generator"))
        blacklist = await self.config.guild(ctx.guild).blacklist()
        if remove not in blacklist:
            blacklist.append(remove)
            msg = _("Generator added to blacklist")
        else:
            blacklist.remove(remove)
            msg = _("Generator removed from blacklist")
        await self.config.guild(ctx.guild).blacklist.set(blacklist)
        return await ctx.reply(msg)

    @conf_guild.command(name="nsfw")
    async def toggle_exists_nsfw(self, ctx):
        old_value = await self.config.guild(ctx.guild).nsfw()
        new_value = not old_value
        await self.config.guild(ctx.guild).nsfw.set(new_value)
        return await ctx.reply(_("NSFW is {} in this guild").format({True: "enabled", False: "disabled"}[new_value]))

    @conf_guild.command(name="show")
    async def guild_show(self, ctx):
        blacklist = ", ".join(await self.config.guild(ctx.guild).blacklist()) if len(await self.config.guild(ctx.guild).blacklist()) > 0 else _("Disabled")
        nsfw = {True: _("Enabled"), False: _("Disabled")}[await self.config.guild(ctx.guild).nsfw()]
        return await ctx.send(
            _("Exists Guild Settings\nBlacklist: {blacklist}\nNSFW is {nsfw}").format(blacklist=blacklist, nsfw=nsfw)
        )

    async def can_post_nsfw(self, ctx):
        if not ctx.channel.is_nsfw() and not isinstance(ctx.channel, discord.DMChannel):
            return False
        nsfw_guild = await self.config.guild(ctx.guild).nsfw()
        if not nsfw_guild:
            return True
        return False

    async def red_delete_data_for_user(self, **kwargs):
        return None

    async def red_get_data_for_user(self, **kwargs):
        return dict()

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        original = getattr(error, "original", None)
        if original:
            if isinstance(original, ClientError):
                return ctx.reply(_("Unexpected {} occurred. Try again").format(str(type(original))))
            elif isinstance(original, NSFWCheckFailed):
                return ctx.reply(str(original))
        return await ctx.bot.on_command_error(ctx, error, unhandled_by_cog=True)

    async def one_image_generator(self, ctx, generator_eval):
        generator = eval(generator_eval)
        if generator.nsfw:
            if not await self.can_post_nsfw(ctx):
                raise NSFWCheckFailed()
        return await ctx.send(embed=await generator.get_embed(), file=await generator.get_image())

    async def seed_generator(self, ctx, seed, meta):
        if seed is not None:
            if not (meta.MIN_SEED <= seed <= meta.SET_SIZE):
                return await ctx.reply(
                    _("Send a number in range from {min_seed} to {set_size}").format(min_seed=meta.MIN_SEED, set_size=meta.SET_SIZE)
                )
        generator = SeedGenerator(meta)
        if generator.nsfw:
            if not await self.can_post_nsfw(ctx):
                raise NSFWCheckFailed()
        return await ctx.send(embed=generator.get_embed(seed))

    @commands.check(command_check_blacklist)
    @commands.group(aliases=Settings.ALIASES['exists'])
    async def exists(self, ctx):
        """Compilation of generators like thisxdoesnotexists"""
        pass

    # @commands.check(command_check_blacklist)
    # @exists.command(name="cat", aliases=Settings.ALIASES['cat'])
    # async def cat(self, ctx):
    #     """Cat generator from https://thiscatdoesnotexist.com"""
    #     return await self.one_image_generator(ctx, Settings.CAT)

    @commands.check(command_check_blacklist)
    @exists.command(name="person", aliases=Settings.ALIASES['person'])
    async def person(self, ctx):
        """Human face generator from https://thispersondoesnotexist.com"""
        return await self.one_image_generator(ctx, Settings.PERSON)

    @commands.check(command_check_blacklist)
    @exists.command(name="fursona", aliases=Settings.ALIASES['fursona'])
    async def fursona(self, ctx,  seed: int = None):
        """Furry generator from https://thisfursonadoesnotexist.com"""
        return await self.seed_generator(ctx, seed, Settings.Fursona)

    @commands.check(command_check_blacklist)
    @exists.command(name="pony", aliases=Settings.ALIASES['pony'])
    async def pony(self, ctx,  seed: int = None):
        """Pony generator from https://thisponydoesnotexist.net"""
        return await self.seed_generator(ctx, seed, Settings.Pony)

    @commands.check(command_check_blacklist)
    @exists.command(name="nightsky", aliases=Settings.ALIASES['nightsky'])
    async def night_sky(self, ctx, seed: int = None):
        """Night sky generator from https://arthurfindelair.com/thisnightskydoesnotexist"""
        return await self.seed_generator(ctx, seed, Settings.NightSky)

    @commands.check(command_check_blacklist)
    @exists.command(name="map", aliases=Settings.ALIASES['map'])
    async def map(self, ctx, seed: int = None):
        """Map generator from https://thismapdoesnotexist.com"""
        return await self.seed_generator(ctx, seed, Settings.Map)

    @commands.check(command_check_blacklist)
    @exists.command(name="waifu", aliases=Settings.ALIASES['waifu'])
    async def waifu(self, ctx, seed: int = None):
        """Anime waifu generator from https://thiswaifudoesnotexist.net"""
        return await self.seed_generator(ctx, seed, Settings.Waifu)

    @commands.check(command_check_blacklist)
    @exists.command(name="beach", aliases=Settings.ALIASES['beach'])
    async def beach(self, ctx, seed: int = None):
        """Beach generator from https://thisbeachdoesnotexist.com"""
        return await self.seed_generator(ctx, seed, Settings.Beach)

    @commands.check(command_check_blacklist)
    @exists.command(name="pepe", aliases=Settings.ALIASES['pepe'])
    async def pepe(self, ctx, seed: int = None):
        """Pepe generator from https://www.thispepedoesnotexist.co.uk"""
        return await self.seed_generator(ctx, seed, Settings.Pepe)

    @commands.check(command_check_blacklist)
    @exists.command(name="city", aliases=Settings.ALIASES['city'])
    async def city(self, ctx):
        """Satellite city shot generator from https://thiscitydoesnotexist.com"""
        return await ctx.send(embed=await CityGenerator().get_embed())

    if not Settings.ONLY_COMMAND_GROUP:
        # @commands.check(command_check_blacklist)
        # @commands.command(name="cat", aliases=Settings.ALIASES['cat'])
        # async def ex_cat(self, ctx):
        #     """Cat generator from https://thiscatdoesnotexist.com"""
        #     return await self.one_image_generator(ctx, Settings.CAT)

        @commands.check(command_check_blacklist)
        @commands.command(name="person", aliases=Settings.ALIASES['person'])
        async def ex_person(self, ctx):
            """Human face generator from https://thispersondoesnotexist.com"""
            return await self.one_image_generator(ctx, Settings.PERSON)

        @commands.check(command_check_blacklist)
        @commands.command(name="fursona", aliases=Settings.ALIASES['fursona'])
        async def ex_fursona(self, ctx, seed: int = None):
            """Furry generator from https://thisfursonadoesnotexist.com"""
            return await self.seed_generator(ctx, seed, Settings.Fursona)

        @commands.check(command_check_blacklist)
        @commands.command(name="pony", aliases=Settings.ALIASES['pony'])
        async def ex_pony(self, ctx, seed: int = None):
            """Pony generator from https://thisponydoesnotexist.net"""
            return await self.seed_generator(ctx, seed, Settings.Pony)

        @commands.check(command_check_blacklist)
        @commands.command(name="nightsky", aliases=Settings.ALIASES['nightsky'])
        async def ex_night_sky(self, ctx, seed: int = None):
            """Night sky generator from https://arthurfindelair.com/thisnightskydoesnotexist"""
            return await self.seed_generator(ctx, seed, Settings.NightSky)

        @commands.check(command_check_blacklist)
        @commands.command(name="map", aliases=Settings.ALIASES['map'])
        async def ex_map(self, ctx, seed: int = None):
            """Map generator from https://thismapdoesnotexist.com"""
            return await self.seed_generator(ctx, seed, Settings.Map)

        @commands.check(command_check_blacklist)
        @commands.command(name="waifu", aliases=Settings.ALIASES['waifu'])
        async def ex_waifu(self, ctx, seed: int = None):
            """Anime waifu generator from https://thiswaifudoesnotexist.net"""
            return await self.seed_generator(ctx, seed, Settings.Waifu)

        @commands.check(command_check_blacklist)
        @commands.command(name="beach", aliases=Settings.ALIASES['beach'])
        async def ex_beach(self, ctx, seed: int = None):
            """Beach generator from https://thisbeachdoesnotexist.com"""
            return await self.seed_generator(ctx, seed, Settings.Beach)

        @commands.check(command_check_blacklist)
        @commands.command(name="pepe", aliases=Settings.ALIASES['pepe'])
        async def ex_pepe(self, ctx, seed: int = None):
            """Pepe generator from https://www.thispepedoesnotexist.co.uk"""
            return await self.seed_generator(ctx, seed, Settings.Pepe)

        @commands.check(command_check_blacklist)
        @commands.command(name="city", aliases=Settings.ALIASES['city'])
        async def ex_city(self, ctx):
            """Satellite city shot generator from https://thiscitydoesnotexist.com"""
            return await ctx.send(embed=await CityGenerator().get_embed())
