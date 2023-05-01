from __future__ import annotations
import discord
from discord.ext import commands

import json

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import Bot

    _Permissions = dict[str, bool]
    """
    To be more precise, you could turn this into a TypedDict
    but I'm not sure if that's needed here.

    from typing import (
        TypedDict,
    )
    class _Permissions(TypedDict):
        administrator: bool
        ...
    """


with open('permissions.json', 'r') as file:
    permissions: _Permissions = json.load(file)


class Inviter(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.command()
    async def invite(self, ctx: commands.Context) -> None:
        url = discord.utils.oauth_url(
            client_id=self.bot.user.id,
            permissions=discord.Permissions(**permissions),
        )
        await ctx.send(embed=discord.Embed(description=f'Invite me to your server with [this link]({url} "Click Me!")!'))


async def setup(bot: Bot) -> None:
    await bot.add_cog(Inviter(bot))
