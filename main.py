import nextcord
import random
import time
import json
import asyncio
import os
import aiofiles
import datetime
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw, ImageFilter
from nextcord.utils import get
from nextcord.ext import commands, tasks
from itertools import cycle

bot_name = "Kámo"
wedry_server_id = 736006656101449821
intents = nextcord.Intents().all()
client = commands.Bot(command_prefix="$", intents=intents)
client.remove_command("help")
client.warnings = {}
bot_id = 691636597439070268
level = ["Věrný následovník", "No Lifer z wishe", "No Lifer", "Ultimátní No Lifer"]
levelnum = [5, 15, 30, 50]

@tasks.loop(seconds=20)
async def status_swap():
	await client.change_presence(activity=nextcord.Game(next(status)))

status = cycle([
	'Sleduj Wedryho!',
	'$help'
])
  
@client.event
async def on_ready():
	print('Přihlásili jsme se jako {0.user}'.format(client))
	status_swap.start()
	client.add_view(RoleView())
	client.add_view(PronounsView())
	for guild in client.guilds:
		client.warnings[guild.id] = {}
        
		async with aiofiles.open(f"{guild.id}.txt", mode="a") as temp:
			pass

		async with aiofiles.open(f"{guild.id}.txt", mode="r") as file:
			lines = await file.readlines()

			for line in lines:
				data = line.split(" ")
				member_id = int(data[0])
				admin_id = int(data[1])
				warn_id = int(data[2])
				reason = " ".join(data[3:]).strip("\n")

				try:
					client.warnings[guild.id][member_id][0] += 1
					client.warnings[guild.id][member_id][1].append((admin_id, warn_id, reason))
					
				except KeyError:
					client.warnings[guild.id][member_id] = [1, [(admin_id, warn_id, reason)]]

@client.event
async def on_guild_join(guild):
    client.warnings[guild.id] = {}
    
@client.event
async def on_member_join(member):
	with open('users.json', 'r') as f:
		users = json.load(f)
        
	await update_data(users, member)
    
	with open('users.json', 'w') as f:
		json.dump(users, f, indent=4)
        
@client.event
async def on_message(message):
	if message.author.bot == False:
		with open('users.json', 'r') as f:
			users = json.load(f)
            
		user = message.author
		await update_data(users, user)
		await add_experience(users, user, random.randint(10, 20))
		await level_up(users, user, message)
        
		with open('users.json', 'w') as f:
			json.dump(users, f, indent=4)
            
	await client.process_commands(message)

@client.event
async def on_member_join(member):
	responses = [f"Vítej {member.mention}!", f"Připojil se k nám {member.mention} a nese se sebou nohu domorodce!", f"Užij si to tady {member.mention}", f"Naše armáda otroků se každým dnem rozrůstá! Dnes se do ní připojil/a {member.mention}", f"Doufám, že neseš jídlo {member.mention}..."]
	await client.get_channel(857306749471555594).send(random.choice(responses))
	try:
		embed=nextcord.Embed(title="Vítej na Wedryho serveru!", description=f"Zde je pár věcí, co by jsi měl udělat jako první.", color=nextcord.Color.purple())
		embed.set_footer(text='Napiš $help v kanálu pro příkazy, aby jsi zjistil ještě víc.')
		embed.add_field(name='1. Pár nejdůležitějších věcí', value="V <#736008766364844092> jsou pravidla, vysvětlení rolí, atd.", inline=False)
		embed.add_field(name='2. Dej subscribe Wedrymu', value='To nikdy neuškodí! **[Wedryho kanál](https://www.youtube.com/user/WedryLP "Na co ještě čekáš?")**')
		embed.add_field(name='3. Přidej si pár rolí', value="V <#736021059005841530> jich pár najdeš.", inline=False)
		embed.add_field(name='4. Podívej se na boty', value="V <#838418809337282582> je vysvětlení jednotlivých botů.", inline=False)
		embed.add_field(name='A hlavně si to tu užij!', value="Až na občasnou vyjímku tu jsou samí zajímaví lidé :grin:", inline=False)
		embed.set_image(url='https://cdn.discordapp.com/attachments/807343811281944659/860423666432213022/welcome.png')
		await member.send(embed=embed)
	except nextcord.HTTPException:
		return
    
@client.event
async def on_member_remove(member):
	responses = [f"**{member.name}** opustil/a server", f"**{member.name}** se rozpadl/a", f"**{member.name}** už není nolifer", f"A naše armáda je zas o něco menší... **{member.name}**", f"**{member.name}** byl/a stejně sus", f"Spain bez S... **{member.name}**", f"Je nám líto, že se s tebou musíme loučit **{member.name}**", f"Naše počty klesají **{member.name}**", f"**{member.name}** šel pro mlíko"]
	await client.get_channel(857306749471555594).send(random.choice(responses))
    
class PronounsDropdown(nextcord.ui.Select):
	def __init__(self):
		options = [
			nextcord.SelectOption(label="Nic", description="Nechci uvádět", default=True),
			nextcord.SelectOption(label="She/her", value=889219844166254623, description="Oslovování v ženském rodě"),
			nextcord.SelectOption(label="He/him", value=889220638030569554, description="Oslovování v mužském rodě"),
			nextcord.SelectOption(label="They/them", value=889220669093597204, description="Oslovování v množném rodě"),
			nextcord.SelectOption(label="They/she", value=889220803424579624, description="Oslovování v množném a ženském rodě"),
			nextcord.SelectOption(label="She/they", value=889220717554573323, description="Oslovování v ženském a množném rodě"),
			nextcord.SelectOption(label="They/he", value=889220918176538744, description="Oslovování v množném a mužském rodě"),
			nextcord.SelectOption(label="He/they", value=889220969388965969, description="Oslovování v mužském a množném rodě"),
			nextcord.SelectOption(label="She/he", value=889221030537732106, description="Oslovování v ženském a mužském rodě"),
			nextcord.SelectOption(label="He/she", value=889221035042410578, description="Oslovování v mužském a ženském rodě"),
			nextcord.SelectOption(label="She/they/he", value=889221040482435142, description="Oslovování v ženském, množném i mužském rodě"),
			nextcord.SelectOption(label="Xe/xem", value=889221044878061670, description="Oslovování v neutrálním rodě"),
			nextcord.SelectOption(label="Neopronouns", value=889221048921391104, description="Vlastní oslovování"),
		]
		super().__init__(custom_id=f"{bot_name}:{wedry_server_id}:PronounsDropdown", min_values=1, max_values=1, options=options, row=0)
        
	async def callback(self, interaction: nextcord.Interaction):
		PronounsIDs = [889219844166254623, 889220638030569554, 889220669093597204, 889220803424579624, 889220717554573323, 889220918176538744, 889220969388965969, 889221030537732106, 889221035042410578, 889221040482435142, 889221044878061670, 889221048921391104]
		user_roles = interaction.user.roles
		if self.values[0] == "Nic":
			for role in user_roles:
					if role.id in PronounsIDs:
						await interaction.user.remove_roles(role)
			await interaction.response.send_message("Všechny pronouns role, pokud jsi nějaké měl, byly odebrány.", ephemeral=True)
		else:
			PronounsID = int(self.values[0])
			PronounsRole = interaction.guild.get_role(PronounsID)
			assert isinstance(PronounsRole, nextcord.Role)
			if PronounsRole in user_roles:
				pass
			else:
				await interaction.user.add_roles(PronounsRole)
				await interaction.response.send_message(f"Pronoun {PronounsRole.name} byl/a/y přidán/a/y", ephemeral=True)
				for role in user_roles:
					if role.id in PronounsIDs and role.id != PronounsID:
						await interaction.user.remove_roles(role)
                        
class PronounsView(nextcord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.add_item(PronounsDropdown())
    
class RoleView(nextcord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
        
	announcement_role = 887001695106768946
	youtube_notif_role = 887001862597935154
	view_name = "RoleView"
	async def role_add(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
		role_id = int(button.custom_id.split("-")[-1])
		role = interaction.guild.get_role(role_id)
		assert isinstance(role, nextcord.Role)
		if role in interaction.user.roles:
			await interaction.user.remove_roles(role)
			await interaction.response.send_message(f"Role {role.name} byla odebrána", ephemeral=True)
		else:
			await interaction.user.add_roles(role)
			await interaction.response.send_message(f"Dostal jsi roli {role.name}", ephemeral=True)
    
	@nextcord.ui.button(label='Oznámení', emoji="📢", style=nextcord.ButtonStyle.primary, custom_id=f"{bot_name}{view_name}-{announcement_role}")
	async def announcement_button(self, button, interaction):
		await self.role_add(button, interaction)
        
	@nextcord.ui.button(label='Youtube oznámení', emoji="❗", style=nextcord.ButtonStyle.primary, custom_id=f"{bot_name}{view_name}-{youtube_notif_role}")
	async def yt_notif_button(self, button, interaction):
		await self.role_add(button, interaction)
        
@client.command()
async def pronouns(ctx):
	await ctx.channel.purge(limit=1)
	if (not ctx.author.guild_permissions.administrator):
		return await ctx.send('Kámo, na tohle nemáš povolení.')
    
	embed=nextcord.Embed(title="Pronouns", description=f"Vyber si svoje pronouns", color=nextcord.Color.dark_blue())
	await ctx.channel.send(embed=embed, view=PronounsView())
    
@client.command()
async def roles(ctx):
	await ctx.channel.purge(limit=1)
	if (not ctx.author.guild_permissions.administrator):
		return await ctx.send('Kámo, na tohle nemáš povolení.')
    
	embed=nextcord.Embed(title="Oznámení", description=f"Klikni na tlačítko, aby jsi přidal nebo odebral oznamující roli", color=nextcord.Color.dark_blue())
	await ctx.channel.send(embed=embed, view=RoleView())

@client.command(aliases=['8ball', '8b'])
async def eightball(ctx, *, question):
	responses = ["Kááámo.", "Ano kámo.", "Kámo... Ne.", "Zeptej se později.", "Nevím, možná to ví Wedry.", "Radši dej subscribe Wedrymu.", "Zdá se, že ano.", "To ti radši neřeknu.", "Stopy značí, že ne.", "To nemůžu vědět kámo.", "Nevím, jsem líný, jdi pryč.", "Nepočítej s tím.", "Si to vygoogli ne?", "Rozhodně ano.", "možná ano, možná ne, kdo ví?", "*visible confusion*", "Já... já... nevím", "Wtf kámo, ne"]
	embed=nextcord.Embed(title=":8ball: Čas na otázky :bangbang:", description=f"Otázka: {question}", color=nextcord.Color.purple())
	embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/807343811281944659/857306206291886170/question-mark-2123967_1920.jpg')
	embed.set_footer(text='Odpovědět, či neodpovědět, to je, oč tu běží')
	embed.add_field(name='Odpověď:', value=random.choice(responses), inline=False)
	await ctx.channel.send(embed=embed)

def calculator(exp):
	o = exp.replace('×', '*')
	o = o.replace('÷', '/')
	result = ''
	try:
		result=str(eval(o))
	except:
		result='Nastal error'
	return result

@client.command(aliases=['Calc', 'Calculator', 'calculator'])
async def calc(ctx):
	buttons = [
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='1', disabled=False, row=0),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='2', disabled=False, row=0),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='3', disabled=False, row=0),
			nextcord.ui.Button(style=nextcord.ButtonStyle.blurple, label='×', disabled=False, row=0),
			nextcord.ui.Button(style=nextcord.ButtonStyle.red, label='Exit', disabled=False, row=0),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='4', disabled=False, row=1),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='5', disabled=False, row=1),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='6', disabled=False, row=1),
			nextcord.ui.Button(style=nextcord.ButtonStyle.blurple, label='÷', disabled=False, row=1),
			nextcord.ui.Button(style=nextcord.ButtonStyle.red, label='←', disabled=False, row=1),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='7', disabled=False, row=2),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='8', disabled=False, row=2),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='9', disabled=False, row=2),
			nextcord.ui.Button(style=nextcord.ButtonStyle.blurple, label='+', disabled=False, row=2),
			nextcord.ui.Button(style=nextcord.ButtonStyle.red, label='Clear', disabled=False, row=2),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='000', disabled=False, row=3),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='0', disabled=False, row=3),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='.', disabled=False, row=3),
			nextcord.ui.Button(style=nextcord.ButtonStyle.blurple, label='-', disabled=False, row=3),
			nextcord.ui.Button(style=nextcord.ButtonStyle.green, label='=', disabled=False, row=3)
	]
	DisButtons = [
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='1', disabled=True, row=0),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='2', disabled=True, row=0),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='3', disabled=True, row=0),
			nextcord.ui.Button(style=nextcord.ButtonStyle.blurple, label='×', disabled=True, row=0),
			nextcord.ui.Button(style=nextcord.ButtonStyle.red, label='Exit', disabled=True, row=0),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='4', disabled=True, row=1),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='5', disabled=True, row=1),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='6', disabled=True, row=1),
			nextcord.ui.Button(style=nextcord.ButtonStyle.blurple, label='÷', disabled=True, row=1),
			nextcord.ui.Button(style=nextcord.ButtonStyle.red, label='←', disabled=True, row=1),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='7', disabled=True, row=2),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='8', disabled=True, row=2),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='9', disabled=True, row=2),
			nextcord.ui.Button(style=nextcord.ButtonStyle.blurple, label='+', disabled=True, row=2),
			nextcord.ui.Button(style=nextcord.ButtonStyle.red, label='Clear', disabled=True, row=2),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='000', disabled=True, row=3),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='0', disabled=True, row=3),
			nextcord.ui.Button(style=nextcord.ButtonStyle.grey, label='.', disabled=True, row=3),
			nextcord.ui.Button(style=nextcord.ButtonStyle.blurple, label='-', disabled=True, row=3),
			nextcord.ui.Button(style=nextcord.ButtonStyle.green, label='=', disabled=True, row=3)
	]
	m = await ctx.send(content = 'Načítání Kalkulačky')
	expression = 'None'
	time = datetime.datetime.utcnow()
	view = nextcord.ui.View(timeout=None)
	view.add_item(buttons)
	delta = datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
	e = nextcord.Embed(title=f'Kalkulačka {ctx.author.name} | {ctx.author.id}', description = expression)
	e.set_footer(text='Začni svoji vlastní napsáním $calc do chatu.')
	await m.edit(embed=e, view=view)
	while time < delta:
		time = datetime.datetime.utcnow()
		res = await client.wait_for("button_click")
		if res.author.id == int(res.message.embeds[0].title.split('|')[1]):
			expression = res.message.embeds[0].description
			if expression == 'None' or expression == 'Nastal error':
				expression = ''
			if res.component.label == 'Exit':
				return await res.respond(content='Kalkulačka byla uzavřena', type=7)
			elif res.component.label == '←':
				expression = expression[:-1]
			elif res.component.label == 'Clear':
				expression = None
			elif res.component.label == '=':
				expression = calculator(expression)
			else:
				expression += res.component.label
			f=nextcord.Embed(title=f'Kalkulačka {res.author.name} | {res.author.id}', description=expression)
			f.set_footer(text='Začni svoji vlastní napsáním $calc do chatu!')
			await res.respond(content='', embed=f, component=buttons, type=7)
			delta = datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
		else:
			res.respond(content="Tohle není tvoje kalkulačka, můžeš si zapnout svoji použitím '$calc'")
	if time >= delta:
		return await ctx.send("Kalkulačka byla pro neaktivitu uzavřena.")
    
@client.command(aliases=['Show'])
async def show(ctx, member:nextcord.Member = None):
	await ctx.channel.purge(limit=1)
	await ctx.send("Počkej chvilku...")
	if member == None:
		member = ctx.author

	show = Image.open("Show.jpg")
	draw = ImageDraw.Draw(show)
	data = BytesIO(await member.avatar.read())
	profile = Image.open(data)

	profile = profile.resize ((125, 125))

	show.paste(profile, (43, 437))

	show.save("show.png")
    
	await ctx.channel.purge(limit=1)
	await ctx.send(file = nextcord.File("show.png"))

	os.remove("show.png") 

@client.command(aliases=["Panakin"])
async def panakin(ctx, member:nextcord.Member=None):
	await ctx.channel.purge(limit=1)
	await ctx.send("Počkej chvilku...")
    
	if member == None:
		member = ctx.author
        
	data = BytesIO(await member.avatar.read())
	f5 = Image.open(data)

	f5.thumbnail((9, 8))
	f5.save("pfp1.png")

	f5 = Image.open("pfp1.png").convert("RGB")

	mask = Image.new("L", f5.size, 0)
	draw = ImageDraw.Draw(mask)
	draw.ellipse((0, 0, f5.size[0], f5.size[1]), fill=255)
	mask = mask.filter(ImageFilter.GaussianBlur(0))

	result = f5.copy()
	result.putalpha(mask)

	result.save('pfp1.png')

	f5 = Image.open("pfp1.png")

	data = BytesIO(await member.avatar.read())
	f2 = Image.open(data)
	f1 = Image.open("Panakin.png")
	f2.thumbnail((54, 52))
	f2.save("pfp.png")

	f2 = Image.open("pfp.png").convert("RGB")

	mask = Image.new("L", f2.size, 0)
	draw = ImageDraw.Draw(mask)
	draw.ellipse((0, 0, f2.size[0], f2.size[1]), fill=255)
	mask = mask.filter(ImageFilter.GaussianBlur(0))

	result = f2.copy()
	result.putalpha(mask)

	result.save('pfp.png')

	f2 = Image.open("pfp.png")

	f3 = f1.copy()
	f3.paste(f2, (214, 414), f2)
	f3.paste(f2, (533, 409), f2)
	f3.paste(f5, (478, 133), f5)
	f3.paste(f5, (617, 131), f5)
	f3.save("panakin.png")
    
	await ctx.channel.purge(limit=1)
	await ctx.send(file = nextcord.File("panakin.png"))

	os.remove("pfp.png")
	os.remove("pfp1.png")
	os.remove("panakin.png")  
    
@client.command(aliases=["Snap", "fake", "Fake"])
async def snap(ctx, member:nextcord.Member=None, *, message="Bruh, who ghost pinged me?"):
	await ctx.channel.purge(limit=1)
	await ctx.send("Počkej chvilku...")
	colour = {
		"time": (114, 118, 125),
		"content": (220, 221, 222)
	}

	size = {
		"title": 35,
		"time": 25
	}

	if member == None:
		member = ctx.author

	img = Image.new('RGB', (1000, 230), color = (54,57,63))
	titlefnt = ImageFont.truetype("discord.otf", size["title"])
	timefnt = ImageFont.truetype("discord.otf", size["time"])
	d = ImageDraw.Draw(img)
	if member.nick is None:
		txt = member.name
	else:
		txt = member.nick
	color = member.color.to_rgb()
	if color == (0, 0, 0):
		color = (255,255,255)
	d.text((180, 40), txt, font=titlefnt, fill=color)
	h, w = d.textsize(txt, font=titlefnt)
	time = datetime.datetime.utcnow().strftime("Today at %I:%M %p")
	d.text((180+h+20, 48), time, font=timefnt, fill=colour["time"])
	d.text((180, 60+w), message, font=titlefnt, fill=colour["content"])

	img.save('img.png')
	data = BytesIO(await member.avatar.read())
	f2 = Image.open(data)
	f1 = Image.open("img.png")
	f2.thumbnail((100, 110))
	f2.save("pfp.png")

	f2 = Image.open("pfp.png").convert("RGB")

	mask = Image.new("L", f2.size, 0)
	draw = ImageDraw.Draw(mask)
	draw.ellipse((0, 0, f2.size[0], f2.size[1]), fill=255)
	mask = mask.filter(ImageFilter.GaussianBlur(0))

	result = f2.copy()
	result.putalpha(mask)

	result.save('pfp.png')

	f2 = Image.open("pfp.png")

	f3 = f1.copy()
	f3.paste(f2, (40, 40), f2)
	f3.save("img.png")

	file = nextcord.File("img.png")
	await ctx.channel.purge(limit=1)
	await ctx.send(file=file)

	try:
		os.remove("pfp.gif")    
		os.remove("img.png")  
		await ctx.message.delete()
	except:
		os.remove("pfp.png")
		os.remove("img.png")  
		await ctx.message.delete()
        
@client.command(aliases=['Pat'])
async def pat(ctx, member:nextcord.Member = None):
	await ctx.channel.purge(limit=1)
	await ctx.send("Počkej chvilku...")
	member2 = ctx.author

	if member == None:
		member = ctx.author
		member2 = ctx.guild.get_member(bot_id)
  
	pat = Image.open("Pat.jpg")
   
	draw = ImageDraw.Draw(pat)
	data = BytesIO(await member.avatar.read())
	profile = Image.open(data)
    
	profile = profile.resize((132, 132))
    
	pat.paste(profile, (655, 379))
    
	asset2 = member2.avatar.url_as(size = 128)
	data2 = BytesIO(await asset2.read())
	profile2 = Image.open(data2)

	profile2 = profile2.resize((173, 173))
   
	pat.paste(profile2, (303, 14))
   
	pat.save("pat.png")
   
	await ctx.channel.purge(limit=1)
	await ctx.send(file = nextcord.File("pat.png"))
	os.remove("pat.png")
    
@client.command(aliases=['Wanted'])
async def wanted(ctx, member:nextcord.Member = None, *, wanted_for=None):
	await ctx.channel.purge(limit=1)
	await ctx.send("Počkej chvilku...")
	if member == None:
		member = ctx.author

	if wanted_for == None:
		wanted = Image.open("WantedEmpty.jpg")
		draw = ImageDraw.Draw(wanted)
		data = BytesIO(await member.avatar.read())
		profile = Image.open(data)

		profile = profile.resize ((400, 400))

		wanted.paste(profile, (150, 271))

		wanted.save("wantedpic.png")

		await ctx.channel.purge(limit=1)
		await ctx.send(file = nextcord.File("wantedpic.png"))

		os.remove("wantedpic.png")
		return

	wanted = Image.open("Wanted.jpg")
	font = ImageFont.truetype("Wanted font.ttf", 26)
   
	draw = ImageDraw.Draw(wanted)
	data = BytesIO(await member.avatar.read())
	profile = Image.open(data)

	profile = profile.resize((400, 400))
   
	wanted.paste(profile, (150, 271))
	draw.text((144, 737), wanted_for, (0, 0, 0), font=font)
   
	wanted.save("wantedpic.png")
   
	await ctx.channel.purge(limit=1)
	await ctx.send(file = nextcord.File("wantedpic.png"))
   
	os.remove("wantedpic.png")
    
@client.command(aliases=['Slowmode', 'Slow', 'slowmode'])
async def slow(ctx, *, time):
	if (not ctx.author.guild_permissions.manage_channels):
		await ctx.send('Kámo, na tohle nemáš povolení.')
		return
	await ctx.channel.purge(limit=1)
	try:
		time = int(time)
		if time == 0:
			embed=nextcord.Embed(description=f'Byl zrušen pomalý režim u {ctx.channel.mention}', color=nextcord.Color.from_rgb(255, 0, 255))
			await ctx.channel.send(embed=embed)
			await ctx.channel.edit(slowmode_delay = 0)
		elif time > 21600:
			embed=nextcord.Embed(description='Nemůžeš nastavit pomalý režim na víc jak __6__ hodin (21600 vteřin)', color=nextcord.Color.from_rgb(255, 0, 0))
			return await ctx.channel.send(embed=embed)
		else:
			await ctx.channel.edit(slowmode_delay = time)
			embed=nextcord.Embed(description=f'Pomalý režim byl nastaven u {ctx.channel.mention} na {time} vteřin.', color=nextcord.Color.from_rgb(255, 0, 255))
			await ctx.channel.send(embed=embed)
	except:
		embed=nextcord.Embed(title='Error', description="Něco se pokazilo, správné použití příkazu je __$slowmode (čas)__, přičemž čas je ve vteřinách.", color=nextcord.Color.from_rgb(255, 0, 0))
		await ctx.channel.send(embed=embed)

@client.command(aliases=['k', 'Yeet', 'yeet'])
async def kick(ctx, member:nextcord.Member, *, reason="Důvod nebyl uveden"):
	if (not ctx.author.guild_permissions.kick_members):
		await ctx.send('Kámo, na tohle nemáš povolení.')
		return
	await ctx.channel.purge(limit=1)
	embed=nextcord.Embed(title=f'{member.name} byl vyhozen!', description=f'**Důvod:** ' + reason, color=nextcord.Color.from_rgb(255, 0, 255))
	embed.set_thumbnail(url=member.avatar.url)
	await ctx.channel.send(embed=embed)
	try:
		await member.send(f"Byl jsi vyhozen z **{guild.name}** z důvodu: __{reason}__")
	except nextcord.HTTPException:
		await ctx.send(f'Nebyl jsem schopen kontaktovat {member.name} v DMs.')
	await member.kick(reason=reason)
    
@client.command(aliases=['Infractions', 'bonked', 'Bonked'])
async def infractions(ctx, member:nextcord.Member=None):
	if (not ctx.author.guild_permissions.ban_members):
		return await ctx.send('Kámo, na tohle nemáš povolení.')
	await ctx.channel.purge(limit=1)
	
	if member is None:
		member = ctx.author

	try:
		count = client.warnings[ctx.guild.id][member.id][0]
		embed=nextcord.Embed(title=f"{member.name} má {count} varování", description="", color=nextcord.Color.from_rgb(255, 0, 255))
		i = 1
		for admin_id, warn_id, reason in client.warnings[ctx.guild.id][member.id][1]:
			admin = ctx.guild.get_member(admin_id)
			embed.description += f"**Varování {i}** dané: {admin.mention} z důvodu: *'{reason}'*.\n"
			i += 1

		await ctx.send(embed=embed)

	except:
		await ctx.send(f"{member.mention} nemá žádné varování.")
        
@client.command(aliases=['bonk', 'Bonk', 'Warn'])
async def warn(ctx, member:nextcord.Member, *, reason="Důvod nebyl uveden"):
	if (not ctx.author.guild_permissions.ban_members):
		return await ctx.send('Kámo, na tohle nemáš povolení.')
	await ctx.channel.purge(limit=1)
	try:
		first_warning = False
		for admin_id, warn_id, reason in client.warnings[ctx.guild.id][member.id][1]:
			warn_id += 1
		client.warnings[ctx.guild.id][member.id][0] += 1
		client.warnings[ctx.guild.id][member.id][1].append((ctx.author.id, warn_id, reason))
        
	except KeyError:
		first_warning = True
		warn_id = 1
		client.warnings[ctx.guild.id][member.id] = [1, [(ctx.author.id, warn_id, reason)]]

	count = client.warnings[ctx.guild.id][member.id][0]

	async with aiofiles.open(f"{ctx.guild.id}.txt", mode="a") as file:
		await file.write(f"{member.id} {ctx.author.id} {warn_id} {reason}\n")

	embed=nextcord.Embed(description=f"{member.mention} byl varován, celkem má __{count}__ varování", color=nextcord.Color.from_rgb(255, 0, 255))
	embed.add_field(name='Z důvodu:', value=reason, inline=False)
	embed.set_footer(text="BONK!")
	await ctx.channel.send(embed=embed)
	try:
		await member.send(f"Byl jsi varován z důvodu: __{reason}__, nyní máš {count} varování, nezapomeň, že za 3 a víc je ban!")
	except:
		return

@client.command(aliases=['hammer', 'Hammer', 'Ban'])
async def ban(ctx, member:nextcord.Member, *, reason="Důvod nebyl uveden"):
	if (not ctx.author.guild_permissions.ban_members):
		await ctx.send('Kámo, na tohle nemáš povolení.')
		return
	await ctx.channel.purge(limit=1)
	embed=nextcord.Embed(title=f'{member.name} byl zabanován!', description=f'**__Důvod:__** ' + reason, color=nextcord.Color.from_rgb(255, 0, 255))
	embed.set_footer(icon_url=ctx.author.avatar.url, text=f"{ctx.author.name} použil/a Ban Hammer")
	embed.set_thumbnail(url=member.avatar.url)
	await ctx.channel.send(embed=embed)
	try:
		await member.send(f"Byl jsi zabanován z **{guild.name}** z důvodu: __{reason}__")
	except nextcord.HTTPException:
		await ctx.send(f'Nebyl jsem schopen kontaktovat {member.name} v DMs.')
	await member.ban(reason=reason)

@client.command(aliases=['forgive', 'Forgive', 'Unban'])
async def unban(ctx, *, member):
	if (not ctx.author.guild_permissions.ban_members):
		await ctx.send('Kámo, na tohle nemáš povolení.')
		return
	banned_users = await ctx.guild.bans()
	member_name, member_discriminator = member.split('#')

	for ban_entry in banned_users:
		user = ban_entry.user

	if(user.name, user.discriminator) == (member_name, member_discriminator):
		await ctx.channel.purge(limit=1)
		await ctx.guild.unban(user)
		embed=nextcord.Embed(title=f'Unban proběhl ůspěšně :ok_hand:!', color=nextcord.Color.from_rgb(255, 0, 255))
		await ctx.channel.send(embed=embed)
		return

@client.command(aliases=['clear', 'Clear', 'Delete', 'purge', 'Purge', 'del', 'Del'])
async def delete(ctx, amount=5):
	if (not ctx.author.guild_permissions.manage_messages):
		await ctx.send('Kámo, na tohle nemáš povolení.')
		return
	embed_amount = amount
	amount = amount+1
	if amount > 301:
		await ctx.send('Držme se pod 300 zprávami ok?')
	else:
		await ctx.channel.purge(limit=amount)
		em=nextcord.Embed(title=f'Zprávy byly vymazány.', color=nextcord.Color.from_rgb(255, 0, 255))
		em.set_footer(icon_url=ctx.author.avatar.url, text=f"{ctx.author.name} vymazal {embed_amount} zpráv/y z existence.")
		await ctx.channel.send(embed=em)
        
@client.command(aliases=['Shut', 'shut', 'Mute'])
async def mute(ctx, member:nextcord.Member, *, reason="Důvod nebyl uveden"):
	if (not ctx.author.guild_permissions.manage_roles):
		await ctx.send('Kámo, na tohle nemáš povolení.')
		return
	guild = ctx.guild
	muteRole = nextcord.utils.get(guild.roles, name="Muted")
	await ctx.channel.purge(limit=1)
    
	if not muteRole:
		await ctx.send("Nenašel jsem Muted roli, tak vám jednu vytvořím.")
		muteRole = await guild.create_role(name="Muted")
        
		for channel in guild.channels:
			await channel.set_permissions(muteRole, speak=False, send_messages=False)
	await member.add_roles(muteRole, reason=reason)
	embed=nextcord.Embed(title=f'**Uživatel byl ztlumen.**', description= f'{member} byl umlčen z důvodu: ' + reason, color=nextcord.Color.from_rgb(255, 0, 255))
	embed.set_thumbnail(url=member.avatar.url)
	await ctx.channel.send(embed=embed)
	try:
		await member.send(f"Byl jsi ztlumen v **{guild.name}** z důvodu: __{reason}__")
	except nextcord.HTTPException:
		await ctx.send(f'Nebyl jsem schopen kontaktovat {member.name} v DMs.')

@client.command(aliases=['Unshut', 'unshut', 'Unmute'])
async def unmute(ctx, member:nextcord.Member, *, reason=None):
	if (not ctx.author.guild_permissions.manage_roles):
		await ctx.send('Kámo, na tohle nemáš povolení.')
		return
	guild = ctx.guild
	muteRole = nextcord.utils.get(guild.roles, name="Muted")
    
	if not muteRole:
		await ctx.send("Nebyla nalezena Muted role!")
		return
    
@client.command(aliases=['Tempshut', 'tempshut', 'Tempmute', 'tmute', 'Tmute'])
async def tempmute(ctx, member:nextcord.Member, time = None, *, reason="Důvod nebyl uveden"):
	if (not ctx.author.guild_permissions.manage_roles):
		await ctx.send('Kámo, na tohle nemáš povolení.')
		return
	if time == None:
		return await ctx.send("Na jak dlouho ho mám ztlumit? Správné použití je __$tempmute (člen) (čas) (důvod)__!")
	guild = ctx.guild
	muteRole = nextcord.utils.get(guild.roles, name="Muted")
	time_convert = {"s":1, "m":60, "h":3600, "d": 86400}
	mutetime = int(time[0]) * time_convert[time[-1]]
	await ctx.channel.purge(limit=1)
    
	if not muteRole:
		await ctx.send("Nenašel jsem Muted roli, tak vám jednu vytvořím.")
		muteRole = await guild.create_role(name="Muted")
        
		for channel in guild.channels:
			await channel.set_permissions(muteRole, speak=False, send_messages=False)
	await member.add_roles(muteRole, reason=reason)
	embed=nextcord.Embed(title=f'**Uživatel byl dočasně ztlumen.**', description= f'{member} byl umlčen na {time} z důvodu: ' + reason, color=nextcord.Color.from_rgb(255, 0, 255))
	embed.set_thumbnail(url=member.avatar.url)
	await ctx.channel.send(embed=embed)
	try:
		await member.send(f"Byl jsi dočasně ztlumen v **{guild.name}** z důvodu: __{reason}__")
	except nextcord.HTTPException:
		await ctx.send(f'Nebyl jsem schopen kontaktovat {member.name} v DMs.')
	await asyncio.sleep(mutetime)

	await member.remove_roles(muteRole, reason=reason)
	embed=nextcord.Embed(title=f'**Uživatel byl unmutován.**', color=nextcord.Color.from_rgb(255, 0, 255))
	embed.set_thumbnail(url=member.avatar.url)
	await ctx.channel.send(embed=embed)
	try:
		await member.send(f"Můžeš zase mluvit v **{guild.name}**.")
	except nextcord.HTTPException:
		await ctx.send(f'Nebyl jsem schopen kontaktovat {member.name} v DMs.')

	await ctx.channel.purge(limit=1)
	await member.remove_roles(muteRole, reason=reason)
	embed=nextcord.Embed(title=f'**Uživatel byl unmutován.**', color=nextcord.Color.from_rgb(255, 0, 255))
	embed.set_thumbnail(url=member.avatar.url)
	await ctx.channel.send(embed=embed)
	try:
		await member.send(f"Můžeš zase mluvit v **{guild.name}**.")
	except nextcord.HTTPException:
		await ctx.send(f'Nebyl jsem schopen kontaktovat {member.name} v DMs.')
        
@client.command(aliases=['g', 'G', 'Giveaway'])
@commands.cooldown(1, 3600, commands.cooldowns.BucketType.user)
async def giveaway(ctx, time=None, *, prize=None):
	if (not ctx.author.guild_permissions.ban_members):
		await ctx.send('Kámo, na tohle nemáš povolení.')
		return
	if time == None:
		return await ctx.send("Jak dlouho má trvat? Správné použití je __$giveaway (čas) (cena)__")
	elif prize == None:
		return await ctx.send("Co se vyhrává? Správné použití je __$giveaway (čas) (cena)__")
	await ctx.channel.purge(limit=1)
	embed=nextcord.Embed(title=f'**Nová giveaway!**', description=f'Vítěz získane: **{prize}**', color=nextcord.Color.from_rgb(255, 0, 255))
	embed.set_footer(text=f'Giveaway končí za {time}')
	time_convert = {"s":1, "m":60, "h":3600, "d": 86400}
	gawtime = int(time[0]) * time_convert[time[-1]]
	gaw_msg = await ctx.send(embed=embed)

	await gaw_msg.add_reaction("🔥")
	await asyncio.sleep(gawtime)

	new_gaw_msg = await ctx.channel.fetch_message(gaw_msg.id)
    
	users = await new_gaw_msg.reactions[0].users().flatten()
	users.pop(users.index(client.user))
    
	winner = random.choice(users)
    
	await ctx.send(f':partying_face: {winner.mention} vyhrál __{prize}__ :tada:!!!')

@client.command(aliases=['Say'])
async def say(ctx, *, saymsg=None):
	if (not ctx.author.guild_permissions.administrator):
		await ctx.send('Kámo, na tohle nemáš povolení.')
		return
	if saymsg == None:
		return await ctx.send('Ale co mám říct? lol')
	await ctx.send(saymsg)

@client.command(aliases=['Embed', 'e', 'E'])
async def embed(ctx, color = None, *, text):

	if (not ctx.author.guild_permissions.manage_messages):
		return await ctx.send('Kámo, na tohle nemáš povolení.')

	if text == None:
		return await ctx.send('Nemám co říct (doslova)')
	
	if color == "pink":
		try:
			titul, popisek = text.split(';')

			embed=nextcord.Embed(title=titul, description=popisek, color=nextcord.Color.from_rgb(255, 0, 255))

		except:
			embed=nextcord.Embed(description=text, color=nextcord.Color.from_rgb(255, 0, 255))

	elif color == "red":
		try:
			titul, popisek = text.split(';')

			embed=nextcord.Embed(title=titul, description=popisek, color=nextcord.Color.from_rgb(255, 0, 0))

		except:
			embed=nextcord.Embed(description=text, color=nextcord.Color.from_rgb(255, 0, 0))

	elif color == "orange":
		try:
			titul, popisek = text.split(';')

			embed=nextcord.Embed(title=titul, description=popisek, color=nextcord.Color.from_rgb(255, 150, 0))

		except:
			embed=nextcord.Embed(description=text, color=nextcord.Color.from_rgb(255, 150, 0))

	elif color == "white":
		try:
			titul, popisek = text.split(';')

			embed=nextcord.Embed(title=titul, description=popisek, color=nextcord.Color.from_rgb(255, 255, 255))

		except:
			embed=nextcord.Embed(description=text, color=nextcord.Color.from_rgb(255, 255, 255))

	elif color == "green":
		try:
			titul, popisek = text.split(';')

			embed=nextcord.Embed(title=titul, description=popisek, color=nextcord.Color.from_rgb(0, 175, 0))

		except:
			embed=nextcord.Embed(description=text, color=nextcord.Color.from_rgb(0, 175, 0))

	elif color == "blue":
		try:
			titul, popisek = text.split(';')

			embed=nextcord.Embed(title=titul, description=popisek, color=nextcord.Color.from_rgb(0, 0, 255))

		except:
			embed=nextcord.Embed(description=text, color=nextcord.Color.from_rgb(0, 0, 255))

	elif color == "yellow":
		try:
			titul, popisek = text.split(';')

			embed=nextcord.Embed(title=titul, description=popisek, color=nextcord.Color.from_rgb(255, 255, 0))

		except:
			embed=nextcord.Embed(description=text, color=nextcord.Color.from_rgb(255, 0, 255))

	elif color == "purple":
		try:
			titul, popisek = text.split(';')

			embed=nextcord.Embed(title=titul, description=popisek, color=nextcord.Color.from_rgb(199, 0, 222))

		except:
			embed=nextcord.Embed(description=text, color=nextcord.Color.from_rgb(199, 0, 222))

	elif color == "black":
		try:
			titul, popisek = text.split(';')

			embed=nextcord.Embed(title=titul, description=popisek, color=nextcord.Color.from_rgb(0, 0, 0))

		except:
			embed=nextcord.Embed(description=text, color=nextcord.Color.from_rgb(0, 0, 0))

	elif color == "brown":
		try:
			titul, popisek = text.split(';')

			embed=nextcord.Embed(title=titul, description=popisek, color=nextcord.Color.from_rgb(159, 96, 0))

		except:
			embed=nextcord.Embed(description=text, color=nextcord.Color.from_rgb(159, 96, 0))

	elif color == "gray":
		try:
			titul, popisek = text.split(';')

			embed=nextcord.Embed(title=titul, description=popisek, color=nextcord.Color.from_rgb(135, 135, 135))

		except:
			embed=nextcord.Embed(description=text, color=nextcord.Color.from_rgb(135, 135, 135))

	else:
		try:
			titul, popisek = text.split(';')

			embed=nextcord.Embed(title=titul, description=popisek)

		except:
			embed=nextcord.Embed(description=text)

	await ctx.channel.send(embed=embed)

@client.command(aliases=['Otázka', 'otázka', 'Ask'])
async def ask(ctx, *, message=None): 
	if message == None:
		return await ctx.send("A na co se wedryho ptáš huh?")
	await ctx.channel.purge(limit=1)
	await ctx.channel.send("Otázka poslána!")
	embed=nextcord.Embed(title=f'{ctx.author.name} se ptá:', description=f'{message}', color=nextcord.Color.purple())
	ask_msg = await client.get_channel(860505719656022046).send(embed=embed)
	await ask_msg.add_reaction("👍")
	await ask_msg.add_reaction("👎")
    
@client.command(aliases=['Suggestion', 's', 'S', 'Návrh', 'návrh'])
@commands.cooldown(1, 3600, commands.cooldowns.BucketType.user)
async def suggestion(ctx, *, message=None): 
	if message == None:
		return await ctx.send("A ten návrh? Prázdné to tam poslat nemůžu lol")
	await ctx.channel.purge(limit=1)
	await ctx.channel.send("Návrh poslán!")
	embed=nextcord.Embed(title=f'Nový návrh!', description=f'{ctx.author.mention} navrhuje: **{message}**', color=nextcord.Color.purple())
	ask_msg = await client.get_channel(860505660319858699).send(embed=embed)
	await ask_msg.add_reaction("👍")
	await ask_msg.add_reaction("👎")
    
@client.command(aliases=['Rank', 'level', 'Level'])
async def rank(ctx, user:nextcord.Member = None):
	if user == None:
		user = ctx.author
	with open('users.json', 'r') as f:
		users = json.load(f)

	try:
		xp = users[f'{user.id}']['experience']
		lvl = users[f'{user.id}']['level']
		lvl_end = users[f'{user.id}']['lvl_end']
		remain = lvl_end - xp
		check = lvl_end / 20
		if xp <= (1/2)*check:
			boxes = 0
		elif xp > (1/2)*check and xp < 2*check:
			boxes = 1
		elif xp >= 2*check and xp < 3*check:
			boxes = 2
		elif xp >= 3*check and xp < 4*check:
			boxes = 3
		elif xp >= 4*check and xp < 5*check:
			boxes = 4
		elif xp >= 5*check and xp < 6*check:
			boxes = 5
		elif xp >= 6*check and xp < 7*check:
			boxes = 6
		elif xp >= 7*check and xp < 8*check:
			boxes = 7
		elif xp >= 8*check and xp < 9*check:
			boxes = 8
		elif xp >= 9*check and xp < 10*check:
			boxes = 9
		elif xp >= 10*check and xp < 11*check:
			boxes = 10
		elif xp >= 11*check and xp < 12*check:
			boxes = 11
		elif xp >= 12*check and xp < 13*check:
			boxes = 12
		elif xp >= 13*check and xp < 14*check:
			boxes = 13
		elif xp >= 14*check and xp < 15*check:
			boxes = 14
		elif xp >= 15*check and xp < 16*check:
			boxes = 15
		elif xp >= 16*check and xp < 17*check:
			boxes = 16
		elif xp >= 17*check and xp < 18*check:
			boxes = 17
		elif xp >= 18*check and xp < 19*check:
			boxes = 18
		elif xp >= 19*check and xp < (19+(1/2))*check:
			boxes = 19
		elif xp >= (19+(1/2))*check:
			boxes = 20
		embed = nextcord.Embed(title=f"{user.name} statistiky úrovně", color=nextcord.Color.blue())
		embed.add_field(name="Level", value=f"{lvl}", inline=True)
		embed.add_field(name="Xp", value=f"{xp}", inline=True)
		embed.add_field(name="Do dalšího levelu zbývá", value=f"{int(remain)} xp", inline=True)
		embed.add_field(name=f"Průběh", value=boxes * ":purple_square:" + (20-boxes) * ":white_large_square:", inline=False)
		embed.set_thumbnail(url=user.avatar.url)
		await ctx.channel.send(embed=embed)
	except KeyError:
		embed=nextcord.Embed(description=f"{user.name} ještě neposlal žádnou zprávu.", color=nextcord.Color.blue())
		await ctx.channel.send(embed=embed)
	with open('users.json', 'w') as f:
		json.dump(users, f, indent=4)
        
@client.command(aliases=['sinfo', 'Sinfo', 'Server', 'serverinfo', 'ServerInfo', 'Serverinfo', 'serverInfo'])
async def server(ctx):
	role_count = len(ctx.guild.roles)
	list_of_bots = [bot.mention for bot in ctx.guild.bots]
    
	embed=nextcord.Embed(timestamp=ctx.message.created_at, color=nextcord.Color.blue())
	embed.add_field(name="Jméno", value=f"{ctx.guild.name}", inline=True)
	embed.add_field(name="ID", value=f"{ctx.guild.id}", inline=True)
	embed.add_field(name="Majitel", value=f"{ctx.guild.owner.mention}", inline=True)
	embed.add_field(name="Pravidla", value=f"{ctx.guild.rules_channel.mention}", inline=True)
	embed.add_field(name="Vytvořen dne", value=f"{ctx.guild.created_at}", inline=True)
	embed.add_field(name="Počet členů", value=f"{ctx.guild.member_count}", inline=True)
	embed.add_field(name="Úroveň ověření", value=f"{ctx.guild.verification_level}", inline=True)
	embed.add_field(name="Nejvyšší role", value=f"{ctx.guild.roles[-2]}", inline=True)
	embed.add_field(name="Počet rolí", value=str(role_count), inline=True)
	embed.add_field(name="Boti", value=', '.join(list_of_bots), inline=True)
	embed.add_field(name="Emoji", value=f", ".join(ctx.guild.emojis), inline=True)
	embed.set_thumbnail(url=ctx.guild.icon.url)
	embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
    
	ctx.channel.send(embed=embed)
    
@client.command(aliases=['uinfo', 'Uinfo', 'User', 'userinfo', 'UserInfo', 'Userinfo', 'userInfo'])
async def user(ctx, member: nextcord.Member = None):
	if member == None:
		member = ctx.author
        
	role_count = len(member.roles)
	messages = 0
	async for message in channel.history(limit=100):
    	if message.author == member:
    	    messages += 1
	bot = member.bot
	if bot == True:
		bot = "Ano"
	else:
		bot = "Ne"
	nick = member.nick
	if nick == None:
		nick = "-"
    
	embed=nextcord.Embed(timestamp=ctx.message.created_at, color=nextcord.Color.blue())
	embed.add_field(name="Jméno", value=f"{member.name}{member.discriminator} {member.public_flags}", inline=True)
	embed.add_field(name="Zmínka", value=f"{member.mention}", inline=True)
	embed.add_field(name="Nejvyšší role", value=f"{member.top_role.mention}", inline=True)
	embed.add_field(name="Počet rolí", value=str(role_count), inline=True)
	embed.add_field(name=f"Počet zpráv (z posledních 100 v {ctx.channel.mention})", value=str(messages), inline=True)
	embed.add_field(name="Připojil se na discord", value=f"{member.created_at}", inline=True)
	embed.add_field(name=f"Připojil se na {ctx.guild.name}", value=f"{member.joined_at}", inline=True)
	embed.add_field(name="ID", value=f"{member.id}", inline=True)
	embed.add_field(name="Je bot", value=f"{bot}", inline=True)
	embed.set_thumbnail(url=ctx.member.avatar.url)
	embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
    
	ctx.channel.send(embed=embed)
        
@eightball.error
async def eightball_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		embed=nextcord.Embed(title="**VOLE...**", description=f"Na co mám asi tak odpovídat?", color=nextcord.Color.from_rgb(255, 0, 0))
		embed.set_thumbnail(url="https://cdn.nextcordapp.com/attachments/807343811281944659/860147182672674832/143120null.png")
		await ctx.channel.send(embed=embed)
        
@kick.error
async def kick_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		embed=nextcord.Embed(title="**Vyhodit mám asi tebe že?**", description=f"Nebo radši příště někoho zmiň :wink:", color=nextcord.Color.from_rgb(255, 0, 0))
		await ctx.channel.send(embed=embed)
	elif isinstance(error, commands.MemberNotFound):
		embed=nextcord.Embed(title="*Hold up*", description=f"Na serveru nikdo takový není.", color=nextcord.Color.from_rgb(255, 0, 0))
		embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/807343811281944659/860154377347792946/PngItem_1564426.png")
		await ctx.channel.send(embed=embed)
        
@ban.error
async def ban_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		embed=nextcord.Embed(title="Kámo...", description=f"Příště někoho zmiň ok?", color=nextcord.Color.from_rgb(255, 0, 0))
		await ctx.channel.send(embed=embed)
	elif isinstance(error, commands.MemberNotFound):
		embed=nextcord.Embed(title="*Hold up*", description=f"Na serveru nikdo takový není.", color=nextcord.Color.from_rgb(255, 0, 0))
		embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/807343811281944659/860154377347792946/PngItem_1564426.png")
		await ctx.channel.send(embed=embed)
        
@mute.error
async def mute_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		embed=nextcord.Embed(title="Kámo...", description=f"Příště někoho zmiň ok?", color=nextcord.Color.from_rgb(255, 0, 0))
		await ctx.channel.send(embed=embed)
	elif isinstance(error, commands.MemberNotFound):
		embed=nextcord.Embed(title="*Hold up*", description=f"Na serveru nikdo takový není.", color=nextcord.Color.from_rgb(255, 0, 0))
		embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/807343811281944659/860154377347792946/PngItem_1564426.png")
		await ctx.channel.send(embed=embed)
    
@unmute.error
async def unmute_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		embed=nextcord.Embed(title="Kámo...", description="Příště někoho zmiň ok?", color=nextcord.Color.from_rgb(255, 0, 0))
		await ctx.channel.send(embed=embed)
	elif isinstance(error, commands.MemberNotFound):
		embed=nextcord.Embed(title="*Hold up*", description="Na serveru nikdo takový není.", color=nextcord.Color.from_rgb(255, 0, 0))
		embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/807343811281944659/860154377347792946/PngItem_1564426.png")
		await ctx.channel.send(embed=embed)
    
@unban.error
async def unban_error(ctx, error):
	if isinstance(error, commands.CommandInvokeError):
		embed=nextcord.Embed(title="Kdo?", description="Napiš zabanovaného člena, nebo napiš i tag toho člena, co chceš unbanovat.", color=nextcord.Color.from_rgb(255, 0, 0))
		await ctx.channel.send(embed=embed)
	if isinstance(error, commands.MissingRequiredArgument):
		embed=nextcord.Embed(title="Kámo...", description="Příště někoho napiš ok?", color=nextcord.Color.from_rgb(255, 0, 0))
		await ctx.channel.send(embed=embed)
        
@tempmute.error
async def tmute_error(ctx, error):
	if isinstance(error, commands.CommandInvokeError):
		await ctx.channel.purge(limit=1)
		embed=nextcord.Embed(title="Špatné použití příkazu", description="Správné použití je __$tempmute (člen) (čas) (důvod)__! z toho za čas musíš doplnit písmeno (s, m, h, d) *bez mezery*", color=nextcord.Color.from_rgb(255, 0, 0))
		await ctx.channel.send(embed=embed)
        
@snap.error
async def snap_error(ctx, error):
	if isinstance(error, commands.MemberNotFound):
		embed=nextcord.Embed(title="Špatné použití příkazu", description="Správné použití je __$snap (člen) (text)__!", color=nextcord.Color.from_rgb(255, 0, 0))
		await ctx.channel.send(embed=embed)
        
@suggestion.error
async def cooldown_error(ctx, error):
	if isinstance(error, commands.CommandOnCooldown):
		embed=nextcord.Embed(title="Jen klid!", description='Tento příkaz můžeš použít znovu až za {:.0f}s'.format(error.retry_after), color=nextcord.Color.from_rgb(255, 0, 0))
		await ctx.channel.send(embed=embed)
        
@giveaway.error
async def cooldown_error(ctx, error):
	if isinstance(error, commands.CommandOnCooldown):
		embed=nextcord.Embed(title="Jen klid!", description='Tento příkaz můžeš použít znovu až za {:.0f}s'.format(error.retry_after), color=nextcord.Color.from_rgb(255, 0, 0))
		await ctx.channel.send(embed=embed)
              
async def update_data(users, user):
	if not f'{user.id}' in users:
		users[f'{user.id}'] = {}
		users[f'{user.id}']['experience'] = 0
		users[f'{user.id}']['level'] = 0
		users[f'{user.id}']['lvl_end'] = 100
        
async def add_experience(users, user, xp):
	users[f'{user.id}']['experience'] += xp
    
async def level_up(users, user, message):
	with open('levels.json', 'r') as g:
		levels = json.load(g)
	experience = users[f'{user.id}']['experience']
	lvl = users[f'{user.id}']['level']
	lvl_end = users[f'{user.id}']['lvl_end']
	if experience >= lvl_end:
		lvl += 1
		if lvl_end <= 300:
			next_lvl = lvl_end / 2
		elif lvl_end > 300 and lvl_end <= 600:
			next_lvl = lvl_end / 3
		elif lvl_end > 600 and lvl_end <= 1000:
			next_lvl = lvl_end / 4
		elif lvl_end > 1000 and lvl_end <= 3200:
			next_lvl = lvl_end / 5
		elif lvl_end > 3200 and lvl_end <= 4000:
			next_lvl = lvl_end / 6
		elif lvl_end > 4000 and lvl_end <= 5000:
			next_lvl = lvl_end / 7
		elif lvl_end > 5000 and lvl_end <= 7000:
			next_lvl = lvl_end / 8
		elif lvl_end > 7000 and lvl_end <= 10000:
			next_lvl = lvl_end / 9
		elif lvl_end > 10000:
			next_lvl = lvl_end / 10
		embed=nextcord.Embed(description=f"Gratuluji {user.mention} - Zvýšil se ti level a to znamená že jsi blíž k Ultimátnímu No Liferovi! Nynější level - **__{lvl}__**", color=nextcord.Color.from_rgb(255, 0, 255))
		embed.set_image(url=user.avatar.url)
		await client.get_channel(856894861793689610).send(embed=embed)
		users[f'{user.id}']['lvl_end'] = lvl_end + int(next_lvl)
		users[f'{user.id}']['level'] = lvl
		users[f'{user.id}']['experience'] = 0
		for i in range(len(level)):
			if lvl == levelnum[i]:
				await user.add_roles(nextcord.utils.get(user.guild.roles, name=level[i]))
				try:
					await user.remove_roles(nextcord.utils.get(user.guild.roles, name=level[i-1]))
				except:
					pass
    
client.run("")
