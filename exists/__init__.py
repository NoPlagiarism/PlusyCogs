from .ext import Exists

__red_end_user_data_statement__ = """\"Exists\" cog does not collect any info about users.
But collects guild's blacklist and NSFW preference"""


async def setup(bot):
    await bot.add_cog(Exists(bot))
