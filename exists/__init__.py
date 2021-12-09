from .ext import Exists


def setup(bot):
    bot.add_cog(Exists(bot))
