import aiohttp
import discord
from discord.ext import commands
from discord import app_commands
import requests

class Processor(commands.Cog):
    def __init__(self, bot):
        self.session = aiohttp.ClientSession()
        self.bot = bot
        self.group = "" # Change to your own Group ID
        self.cookie = ""
        self.ranks = {}  # Do not touch

    async def gettoken(self): # Gets Roblox CRF Token
        url = "https://auth.roblox.com/v2/logout"
        headers = {
            "Cookie": ".ROBLOSECURITY={}".format(self.cookie),
            "X-CSRF-TOKEN": "fetch"
        }
        async with self.session.post(url, headers=headers) as response:
            return response.headers.get("X-CSRF-TOKEN")

    async def getranks(self): # Gets ranks/roleids within roblox group, this is not "1-255", it is unique.
        url = "https://groups.roblox.com/v1/groups/{}/roles".format(self.group)
        headers = {
            "Cookie": ".ROBLOSECURITY={}".format(self.cookie)
        }
        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                roles = await response.json()
                self.ranks = {role['name']: role['id'] for role in roles.get('roles', [])}
            else:
                print("[Error]:", response.status, await response.text())

    async def search(self, username: str): # Searches Players username on Roblox and returns ID
        url = "https://users.roblox.com/v1/usernames/users"
        payload = {"usernames": [username], "excludeBannedUsers": True}
        async with self.session.post(url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data['data'][0].get("id")
            else:
                return None

    def error(self, text): # Error Embed / Modify as you wish
        return discord.Embed(title="[Error]", description="An error has occurred when processing this request: {}".format(text), color=discord.Color.red())

    def success(self, user, role): # Success Embed / Modify as you wish
        return discord.Embed(title="[Success]", description="{} has been successfully updated to the role {}.".format(user, role), color=discord.Color.green())

    @app_commands.command(name="update", description="Updates user's role in the given group") # Uses Slash command to update user within group
    async def update(self, ctx: discord.Interaction, username: str, rank: str):
        userid = await self.search(username)
        if userid is None:
            await ctx.response.send_message(embed=self.error("User not found."))
            return

        token = await self.gettoken()
        if token is None:
            await ctx.response.send_message(embed=self.error("Failed to retrieve CSRF token."))
            return

        await self.getranks()
        if rank not in self.ranks:
            await ctx.response.send_message(embed=self.error("The rank '{}' does not exist.".format(rank)))
            return

        roleid = self.ranks[rank]

        url = "https://groups.roblox.com/v1/groups/{}/users/{}".format(self.group, userid)
        headers = {
            "Content-Type": "application/json",
            "Cookie": ".ROBLOSECURITY={}".format(self.cookie),
            "X-CSRF-TOKEN": token
        }
        payload = {
            "roleId": roleid
        }

        async with self.session.patch(url, headers=headers, json=payload) as response:
            if response.status == 200:
                await ctx.response.send_message(embed=self.success(username, rank))
            else:
                error = await response.text()
                await ctx.response.send_message(embed=self.error("Failed to update role: {}".format(error)))


    # Example usage of the command above includes /rank (username) (Rank Name e.g Member, Admin etc)