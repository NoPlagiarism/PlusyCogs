from .ext import Va11Halla
from .reader import Va11DataManager
from redbot.core import data_manager

__red_end_user_data_statement__ = "\"va11halla-quotes\" collect preferences from users like main language of dialogues"


async def setup(bot):
    manager = Va11DataManager(path=data_manager.cog_data_path(raw_name=Va11Halla.__name__))
    await manager.async_validate_and_download()
    cog = Va11Halla(bot, manager=manager, validate_download=False)
    await bot.add_cog(cog)
