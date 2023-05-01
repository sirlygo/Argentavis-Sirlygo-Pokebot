from __future__ import annotations
import discord
from discord.ext import commands

import time

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import Bot


class Spins(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    def format_time_delta(self, seconds: float) -> str:
        epoch = int(time.time() + seconds)
        return f'<t:{epoch}:R>'

    @commands.command()
    @commands.cooldown(rate=1, per=60.0*60.0, type=commands.BucketType.user)
    async def hourly(self, ctx: commands.Context) -> None:
        await ctx.send("Spinning...")

    @hourly.error
    async def on_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'Slow down! Try again {self.format_time_delta(error.retry_after)}')
            return
        raise error


async def setup(bot: Bot) -> None:
    await bot.add_cog(Spins(bot))
