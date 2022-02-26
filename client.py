# client.py
import os
from dotenv import load_dotenv
import json
import discord
from discord import Embed
from discord.commands import Option
from discord.ui import Button, View

# .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
GUILD_ID = os.getenv('GUILD_ID')

# reasons.json
f = open('reasons.json')
data = json.load(f)
print(data['reasons'])
f.close()

bot = discord.Bot()

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if 'hello jar' in message.content.lower():
        await message.channel.send('hello')

def formatCurrency(value: float):
    return '${:,.2f}'.format(value)

class ReportView(View):
    def __init__(self, victim: discord.Member):
        super().__init__()
        for reason in data['reasons']:
            entry = data['reason'][reason]
            self.add_item(ReportButton(entry['title'], entry['value'], entry['emoji'], victim))

class ReportButton(Button):
    def __init__(self, title: str, value: float, emoji, victim: discord.Member):
        super().__init__(label=title, style=self.style(value), emoji=emoji)
        self.victim = victim
        self.title = title
        self.value = value
        self.emoji = emoji

    def style(self, value: float):
        if value == 0.1:
            return discord.ButtonStyle.secondary
        elif value == 0.25:
            return discord.ButtonStyle.success
        elif value == 0.5:
            return discord.ButtonStyle.primary
        else:
            return discord.ButtonStyle.danger

    async def callback(self, interaction):
        await interaction.response.edit_message(content=f'Put {self.victim.mention} in The Jar for {self.emoji} **{self.title}**. You can do better, c\'mon...', view=None)
        await interaction.followup.send(f'<:TheJar:947107045188976681> +{formatCurrency(self.value)}!')

@bot.slash_command(name='getthejar', guild_ids=[GUILD_ID, '947088843637661696'], description='I can\'t believe you\'ve done this...')
async def _getthejar(
    ctx: discord.ApplicationContext,
    victim: Option(discord.Member, 'Who did the thing?')
):
    await ctx.send('<:pikafacepalm:947104337912541184>')
    report_view = ReportView(victim)
    await ctx.respond(f'ok... what did {victim.mention} do this time D:', view=report_view)

@bot.slash_command(name='embedtest', guild_ids=[GUILD_ID, '947088843637661696'], description='Testing embeds!')
async def _embedtest(
    ctx: discord.ApplicationContext
):
    test_embed = Embed(title='The title!', description='A description goes here.')
    await ctx.respond(embed=test_embed)
bot.run(TOKEN)