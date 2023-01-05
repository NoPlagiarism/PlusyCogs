from .ext import Va11Halla

__red_end_user_data_statement__ = "\"va11halla-quotes\" collect preferences from users like main language of dialogues"


def setup(bot):
    cog = Va11Halla(bot)
    bot.add_cog(cog)
