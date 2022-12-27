from .ext import Va11Halla


def setup(bot):
    cog = Va11Halla(bot)
    bot.add_cog(cog)
