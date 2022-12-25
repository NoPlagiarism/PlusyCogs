from .ext import Exists

__red_end_user_data_statement__ = """\"Exists\" cog does not collect any info about users or server"""


def setup(bot):
    bot.add_cog(Exists(bot))
