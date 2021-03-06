# client.py
import time
import os
from dotenv import load_dotenv
import json
import discord
from discord import Colour, Embed
from discord.commands import Option
from discord.ui import Button, View
import matplotlib.pyplot as plt
import numpy as np

# .env
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')

# Allow reason changes to be modified globally
class DataHolder:
    def __init__(self, data):
        self.data = data

# reasons.json
f = open('reasons.json')
data_holder = DataHolder(json.load(f))
f.close()

# Reloading reasons
def load_reasons():
    f = open('reasons.json')
    data_holder.data = json.load(f)
    f.close()

bot = discord.Bot()

@bot.event
async def on_ready():
    print("The Jar is ready! :D")

def format_currency(value: float):
    return '${:,.2f}'.format(value)

class ReportView(View):
    def __init__(self, author: discord.Member, victim: discord.Member):
        super().__init__()
        for reason in data_holder.data['reasons']:
            entry = data_holder.data['reason'][reason]
            if (entry['active']): # Only import active jar reasons
                self.add_item(ReportButton(author, reason, entry['title'], entry['value'], entry['emoji'], victim))

class ReportButton(Button):
    def __init__(self, author: discord.Member, id: str, title: str, value: float, emoji, victim: discord.Member):
        super().__init__(label=title, style=self.style(value), emoji=emoji)
        self.author = author
        self.id = id
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
        # Record the violation to CSV file
        record_violation(self.victim, self.id)
        violations = get_violations_list()

        # Calculate the jar and user totals
        total = get_money_total(violations)
        user_total = get_money_user_total(violations, self.victim)
        percentage = '%.1f' % (user_total / total * 100)

        report_final_desc = 'nice.' if (total >= 69 and total < 70) else 'The Jar grows by the day.'

        embed = Embed(title='Thanks!', description=f'{report_final_desc}', colour=Colour.brand_red())
        embed.set_author(name=self.author.name, icon_url=self.author.avatar.url)
        embed.set_thumbnail(url='https://raw.githubusercontent.com/jstnf/the-jar/main/assets/pikafacepalm.png')
        embed.add_field(name='THE ACCUSED', value=self.victim.mention, inline=False)
        embed.add_field(name='THE CRIME', value=f'{self.emoji} **{self.title}**', inline=True)
        embed.add_field(name='Added Amount', value=f'**{format_currency(self.value)}**', inline=True)
        embed.add_field(name=f'{self.victim.name}\'s Total', value=f'**{format_currency(user_total)}** ({percentage}% of total) `{len(get_user_violations(violations, self.victim))}x`', inline=True)
        embed.add_field(name='Jar Total', value=f'**{format_currency(total)}** <:TheJar:947107045188976681>', inline=True)

        await interaction.response.edit_message(embed=embed, view=None)

class Violation:
    def __init__(self, time: str, victim_id: str, reason_id: str):
        self.time = time
        self.victim_id = victim_id
        self.reason_id = reason_id

def record_violation(victim: discord.Member, reason_id: str):
    current_time = round(time.time() * 1000)
    with open('data.csv', 'a') as data_file:
        data_file.write(f'{current_time},{victim.id},{reason_id}\n')

def get_violations_list():
    violations = []
    with open('data.csv', 'r') as data_file:
        lines = data_file.readlines()
        for line in lines:
            parts = line.split(',')
            if len(parts) != 3:
                continue
            violations.append(Violation(parts[0], parts[1], parts[2][:-1]))
    return violations

def get_user_violations(violations, victim: discord.Member):
    user_violations = []
    for v in violations:
        if str(victim.id) == v.victim_id:
            user_violations.append(v)
    return user_violations

def get_money_total(violations):
    total = 0.0
    for v in violations:
        total += float(data_holder.data['reason'][v.reason_id]['value'])
    return total

def get_money_user_total(violations, victim: discord.Member):
    total = 0.0
    for v in violations:
        if v.victim_id == f'{victim.id}':
            total += float(data_holder.data['reason'][v.reason_id]['value'])
    return total

class LeaderboardEntry(object):
    def __init__(self, id: str, amount: float, num_violations: int):
        self.id = id
        self.amount = amount
        self.num_violations = num_violations
    def __eq__(self, other):
        return self.amount == other.amount
    def __ne__(self, other):
        return self.amount != other.amount
    def __lt__(self, other):
        return self.amount < other.amount
    def __gt__(self, other):
        return self.amount > other.amount
    def __le__(self, other):
        return self.amount <= other.amount
    def __ge__(self, other):
        return self.amount >= other.amount

def get_leaderboard(violations):
    entries = []
    for v in violations:
        found = False
        for ent in entries:
            if ent.id == v.victim_id:
                ent.amount += data_holder.data['reason'][v.reason_id]['value']
                ent.num_violations = ent.num_violations + 1
                found = True
                break
        if not found:
            entries.append(LeaderboardEntry(v.victim_id, float(data_holder.data['reason'][v.reason_id]['value']), 1))
    entries.sort()
    return entries

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

@bot.slash_command(name='jarleaderboard', guild_ids=[GUILD_ID, '947088843637661696'], description='View the top contributors to The Jar!')
async def _jarleaderboard(
    ctx: discord.ApplicationContext
):
    violations = get_violations_list()
    total = get_money_total(violations)
    users_content = ''
    amounts_content = ''
    entries = get_leaderboard(violations)
    count = 1
    nums = []
    pie_labels = []
    for e in entries[::-1]:
        percentage = '%.1f' % (e.amount / total * 100)
        try:
            member = await ctx.guild.fetch_member(int(e.id))
            users_content += f'**{count}.** {member.mention}\n'
            pie_labels.append(f'{member.name}')
        except:
            users_content += f'**{count}.** <@{e.id}>\n'
            pie_labels.append('???')
        amounts_content += f'**{format_currency(e.amount)}** ({percentage}%) `{e.num_violations}x`\n'
        nums.append(e.amount)
        count += 1

    y = np.array(nums)

    plt.figure().set_facecolor('#36393E')
    plt.pie(y, labels=pie_labels, startangle=90, textprops={'color': 'white'})
    plt.savefig('graph.png')

    img_file = discord.File('graph.png')
    embed=Embed(title='The Jar Leaderboard', description='Here\'s the top contributors to The Jar! <:TheJar:947107045188976681>', colour=Colour.brand_red())
    embed.set_thumbnail(url='https://raw.githubusercontent.com/jstnf/the-jar/main/assets/pikafacepalm.png')
    embed.add_field(name='Rankings', value=users_content, inline=True)
    embed.add_field(name='Amount', value=amounts_content, inline=True)
    embed.add_field(name='Total Amount', value=f'**{format_currency(total)}**', inline=False)
    embed.set_image(url='attachment://graph.png')
    await ctx.respond(file=img_file, embed=embed)

@bot.slash_command(name='jarrules', guild_ids=[GUILD_ID, '947088843637661696'], description='List the rules from The Jar.')
async def _jarrules(
    ctx: discord.ApplicationContext
):
    rules_content = ['', '', '', '']
    for reason in data_holder.data['reasons']:
        entry = data_holder.data['reason'][reason]
        entry_value = float(entry['value'])
        category = 0
        if entry_value == 0.25:
            category = 1
        elif entry_value == 0.5:
            category = 2
        elif entry_value == 1:
            category = 3

        rules_content[category] += f"{entry['emoji']} {entry['title']}\n"

    embed=Embed(title='The Jar Rules', description='Below are the rules of The Jar and their values.', colour=Colour.brand_red())
    embed.set_thumbnail(url='https://raw.githubusercontent.com/jstnf/the-jar/main/assets/pikafacepalm.png')
    embed.add_field(name='$0.10', value=f'{rules_content[0]}', inline=False)
    embed.add_field(name='$0.25', value=f'{rules_content[1]}', inline=False)
    embed.add_field(name='$0.50', value=f'{rules_content[2]}', inline=False)
    embed.add_field(name='$1.00', value=f'{rules_content[3]}', inline=False)
    await ctx.respond(embed=embed)

@bot.slash_command(name='jarreload', guild_ids=[GUILD_ID, '947088843637661696'], description='Reload the rules from The Jar.')
async def _jarreload(
    ctx: discord.ApplicationContext
):
    load_reasons()
    await ctx.respond(f"Loaded {len(data_holder.data['reasons'])} rules.")

@bot.slash_command(name='jarstats', guild_ids=[GUILD_ID, '947088843637661696'], description='View some neat stats for The Jar.')
async def _jarstats(
    ctx: discord.ApplicationContext
):
    violations = get_violations_list()
    total_time = 1
    if (len(violations) > 0):
        total_time = round(time.time() * 1000) - float(violations[0].time)
    total_amount = get_money_total(violations)
    days = total_time / 1000 / 60 / 60 / 24 # Conversion from milliseconds to days
    
    embed=Embed(title='The Jar Stats', description='<a:Emotional_Damage:948883666363383848>', colour=Colour.brand_red())
    embed.set_thumbnail(url='https://raw.githubusercontent.com/jstnf/the-jar/main/assets/pikafacepalm.png')
    embed.add_field(name='Daily Average', value=f'{format_currency(total_amount / days)}', inline=False)
    await ctx.respond(embed=embed)

bot.run(TOKEN)