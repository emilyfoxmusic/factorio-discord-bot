from discord.ext import commands


class Healthcheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Check if the bot is alive')
    async def heartbeat(self, ctx):
        await ctx.send('Hi! :heart: :heart: :heart: \n Are you ready for some ' +
                       'Factoriooo?! :construction_site:')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if 'penguin' in message.content:
            await message.channel.send(':penguin:')

        if 'train' in message.content:
            await message.channel.send("Let's build a TRAAIINN :train2:")

        if 'science' in message.content:
            await message.channel.send(":man_scientist: Let's do some SCIENCE :woman_scientist:")
