import asyncio

from Cogs import Group
async def load(bot):
    cogs = [Group.Processor]

    tasks = []
    for Cog in cogs:
        tasks.append(bot.add_cog(Cog(bot)))

    await asyncio.gather(*tasks)
    await bot.tree.sync()
