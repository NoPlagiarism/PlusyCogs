from .ext import RYDCog

__red_end_user_data_statement__ = "RYD stores preferences about turning off links scanner"


def setup(bot):
    bot.add_cog(RYDCog(bot))
