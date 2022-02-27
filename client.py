# client.py
import os
from dotenv import load_dotenv
import json
import discord
from discord import Colour, Embed
from discord.commands import Option
from discord.ui import Button, View

# .env
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')

# reasons.json
f = open('reasons.json')
data = json.load(f)
f.close()

bot = discord.Bot()

@bot.event
async def on_ready():
    print("The Jar is ready! :D")

def formatCurrency(value: float):
    return '${:,.2f}'.format(value)

class ReportView(View):
    def __init__(self, author: discord.Member, victim: discord.Member):
        super().__init__()
        for reason in data['reasons']:
            entry = data['reason'][reason]
            self.add_item(ReportButton(author, entry['title'], entry['value'], entry['emoji'], victim))

class ReportButton(Button):
    def __init__(self, author: discord.Member, title: str, value: float, emoji, victim: discord.Member):
        super().__init__(label=title, style=self.style(value), emoji=emoji)
        self.author = author
        self.title = title
        self.value = value
        self.emoji = emoji
        self.victim = victim

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
        embed = Embed(title='Thanks!', description='The Jar grows by the day.', colour=Colour.brand_red())
        embed.set_author(name=self.author.name, icon_url=self.author.avatar.url)
        embed.set_thumbnail(url='https://raw.githubusercontent.com/jstnf/the-jar/main/assets/pikafacepalm.png')
        embed.add_field(name='THE ACCUSED', value=self.victim.mention, inline=False)
        embed.add_field(name='THE CRIME', value=f'{self.emoji} **{self.title}**', inline=True)
        embed.add_field(name='Added Amount', value=f'{formatCurrency(self.value)}', inline=True)
        embed.add_field(name='Total Amount', value=f'$WIP <:TheJar:947107045188976681>', inline=False)
        await interaction.response.edit_message(embed=embed, view=None)

@bot.slash_command(name='getthejar', guild_ids=[GUILD_ID, '947088843637661696'], description='I can\'t believe you\'ve done this...')
async def _getthejar(
    ctx: discord.ApplicationContext,
    victim: Option(discord.Member, 'Who did the thing?')
):
    report_view = ReportView(ctx.author, victim)
    embed = Embed(title='Ok... who did the thing?', description='The Jar has been summoned.', colour=Colour.brand_red())
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    embed.set_thumbnail(url='https://raw.githubusercontent.com/jstnf/the-jar/main/assets/pikafacepalm.png')
    embed.add_field(name='THE ACCUSED', value=victim.mention)
    await ctx.respond(embed=embed, view=report_view)

bot.run(TOKEN)