from redbot.core import commands
from .config import Settings
from .api import OneImageGenerator, SeedGenerator, CityGenerator, EyeGenerator


class Exists(commands.Cog):
    """This x does not Exists cog"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super(Exists, self).__init__()

    async def red_delete_data_for_user(self, **kwargs):
        return None

    async def red_get_data_for_user(self, **kwargs):
        return dict()

    async def one_image_generator(self, ctx, generator_eval):
        generator = eval(generator_eval)
        return await ctx.send(embed=await generator.get_embed(), file=await generator.get_image())

    async def seed_generator(self, ctx, seed, meta):
        if seed is not None:
            if not (meta.MIN_SEED <= seed <= meta.SET_SIZE):
                return await ctx.reply("Send a number in range from {} to {}".format(meta.MIN_SEED, meta.SET_SIZE))
        generator = SeedGenerator(meta)
        return await ctx.send(embed=generator.get_embed(seed))

    @commands.group(aliases=Settings.ALIASES['exists'])
    async def exists(self, ctx):
        """Compilation of generators like thisxdoesnotexists"""
        pass

    @exists.command(name="cat", aliases=Settings.ALIASES['cat'])
    async def cat(self, ctx):
        """Cat generator from https://thiscatdoesnotexist.com"""
        return await self.one_image_generator(ctx, Settings.CAT)

    @exists.command(name="horse", aliases=Settings.ALIASES['horse'])
    async def horse(self, ctx):
        """Horse generator from https://thishorsedoesnotexist.com"""
        return await self.one_image_generator(ctx, Settings.HORSE)

    @exists.command(name="art", aliases=Settings.ALIASES['art'])
    async def art(self, ctx):
        """Art generator from https://thisartworkdoesnotexist.com"""
        return await self.one_image_generator(ctx, Settings.ART)

    @exists.command(name="person", aliases=Settings.ALIASES['person'])
    async def person(self, ctx):
        """Human face generator from https://thispersondoesnotexist.com"""
        return await self.one_image_generator(ctx, Settings.PERSON)

    @exists.command(name="fursona", aliases=Settings.ALIASES['fursona'])
    async def fursona(self, ctx,  seed: int = None):
        """Furry generator from https://thisfursonadoesnotexist.com"""
        return await self.seed_generator(ctx, seed, Settings.Fursona)

    @exists.command(name="pony", aliases=Settings.ALIASES['pony'])
    async def pony(self, ctx,  seed: int = None):
        """Pony generator from https://thisponydoesnotexist.net"""
        return await self.seed_generator(ctx, seed, Settings.Pony)

    @exists.command(name="nightsky", aliases=Settings.ALIASES['nightsky'])
    async def night_sky(self, ctx, seed: int = None):
        """Night sky generator from https://arthurfindelair.com/thisnightskydoesnotexist"""
        return await self.seed_generator(ctx, seed, Settings.NightSky)

    @exists.command(name="map", aliases=Settings.ALIASES['map'])
    async def map(self, ctx, seed: int = None):
        """Map generator from http://thismapdoesnotexist.com"""
        return await self.seed_generator(ctx, seed, Settings.Map)

    @exists.command(name="waifu", aliases=Settings.ALIASES['waifu'])
    async def waifu(self, ctx, seed: int = None):
        """Anime waifu generator from https://thiswaifudoesnotexist.net"""
        return await self.seed_generator(ctx, seed, Settings.Waifu)

    @exists.command(name="beach", aliases=Settings.ALIASES['beach'])
    async def beach(self, ctx, seed: int = None):
        """Beach generator from https://thisbeachdoesnotexist.com"""
        return await self.seed_generator(ctx, seed, Settings.Beach)

    @exists.command(name="sneaker", aliases=Settings.ALIASES['sneaker'])
    async def sneaker(self, ctx, seed: int = None):
        """Sneaker generator from https://thissneakerdoesnotexist.com"""
        return await self.seed_generator(ctx, seed, Settings.Sneaker)

    @exists.command(name="pepe", aliases=Settings.ALIASES['pepe'])
    async def pepe(self, ctx, seed: int = None):
        """Pepe generator from https://www.thispepedoesnotexist.co.uk"""
        return await self.seed_generator(ctx, seed, Settings.Pepe)

    @exists.command(name="city", aliases=Settings.ALIASES['city'])
    async def city(self, ctx):
        """Satellite city shot generator from http://thiscitydoesnotexist.com"""
        return await ctx.send(embed=await CityGenerator().get_embed())

    @exists.command(aliases=("thiseyedoesnotexist", ))
    async def eye(self, ctx):
        """Eye generator from https://thiseyedoesnotexist.com/"""
        return await ctx.send(embed=await EyeGenerator().get_embed())

    if not Settings.ONLY_COMMAND_GROUP:
        @commands.command(name="cat", aliases=Settings.ALIASES['cat'])
        async def cat(self, ctx):
            """Cat generator from https://thiscatdoesnotexist.com"""
            return await self.one_image_generator(ctx, Settings.CAT)

        @commands.command(name="horse", aliases=Settings.ALIASES['horse'])
        async def horse(self, ctx):
            """Horse generator from https://thishorsedoesnotexist.com"""
            return await self.one_image_generator(ctx, Settings.HORSE)

        @commands.command(name="art", aliases=Settings.ALIASES['art'])
        async def art(self, ctx):
            """Art generator from https://thisartworkdoesnotexist.com"""
            return await self.one_image_generator(ctx, Settings.ART)

        @commands.command(name="person", aliases=Settings.ALIASES['person'])
        async def person(self, ctx):
            """Human face generator from https://thispersondoesnotexist.com"""
            return await self.one_image_generator(ctx, Settings.PERSON)

        @commands.command(name="fursona", aliases=Settings.ALIASES['fursona'])
        async def fursona(self, ctx, seed: int = None):
            """Furry generator from https://thisfursonadoesnotexist.com"""
            return await self.seed_generator(ctx, seed, Settings.Fursona)

        @commands.command(name="pony", aliases=Settings.ALIASES['pony'])
        async def pony(self, ctx, seed: int = None):
            """Pony generator from https://thisponydoesnotexist.net"""
            return await self.seed_generator(ctx, seed, Settings.Pony)

        @commands.command(name="nightsky", aliases=Settings.ALIASES['nightsky'])
        async def night_sky(self, ctx, seed: int = None):
            """Night sky generator from https://arthurfindelair.com/thisnightskydoesnotexist"""
            return await self.seed_generator(ctx, seed, Settings.NightSky)

        @commands.command(name="map", aliases=Settings.ALIASES['map'])
        async def map(self, ctx, seed: int = None):
            """Map generator from http://thismapdoesnotexist.com"""
            return await self.seed_generator(ctx, seed, Settings.Map)

        @commands.command(name="waifu", aliases=Settings.ALIASES['waifu'])
        async def waifu(self, ctx, seed: int = None):
            """Anime waifu generator from https://thiswaifudoesnotexist.net"""
            return await self.seed_generator(ctx, seed, Settings.Waifu)

        @commands.command(name="beach", aliases=Settings.ALIASES['beach'])
        async def beach(self, ctx, seed: int = None):
            """Beach generator from https://thisbeachdoesnotexist.com"""
            return await self.seed_generator(ctx, seed, Settings.Beach)

        @commands.command(name="sneaker", aliases=Settings.ALIASES['sneaker'])
        async def sneaker(self, ctx, seed: int = None):
            """Sneaker generator from https://thissneakerdoesnotexist.com"""
            return await self.seed_generator(ctx, seed, Settings.Sneaker)

        @commands.command(name="pepe", aliases=Settings.ALIASES['pepe'])
        async def pepe(self, ctx, seed: int = None):
            """Pepe generator from https://www.thispepedoesnotexist.co.uk"""
            return await self.seed_generator(ctx, seed, Settings.Pepe)

        @commands.command(name="city", aliases=Settings.ALIASES['city'])
        async def city(self, ctx):
            """Satellite city shot generator from http://thiscitydoesnotexist.com"""
            return await ctx.send(embed=await CityGenerator().get_embed())

        @commands.command(aliases=("thiseyedoesnotexist",))
        async def eye(self, ctx):
            """Eye generator from https://thiseyedoesnotexist.com/"""
            return await ctx.send(embed=await EyeGenerator().get_embed())
