
import os
import discord
from discord.ext import commands
from discord.ui import Button, View
from flask import Flask
from threading import Thread

# Flask webserver to keep bot alive
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"
def run():
    app.run(host="0.0.0.0", port=8080)
def keep_alive():
    Thread(target=run).start()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
TOKEN = os.environ["TOKEN"]

structure = {
    "Arrival Zone": ["📖｜lore-of-arcania", "🎫｜enter-the-arcadia", "📢｜announcements", "📺｜anex-uploads", "🧭｜guide-to-ascend"],
    "Commons": ["💬｜arcane-chat", "🌑｜shadows-hall", "🎶｜aether-beats", "📦｜nexus-vault"],
    "Guild Halls": ["🧩｜matchmaking-pit", "🎞️｜clip-scroll", "🧱｜rank-totems", "⚙️｜loadout-lab"],
    "Vibe Sanctum": ["🌌｜inner-sanctum", "🖼️｜mythscrolls-gallery", "🎭｜the-loophole"],
    "Quests & Legends": ["🗓️｜event-scrolls", "🏅｜hall-of-heroes", "📈｜level-scrolls"],
    "🎶｜Sonic Sanctum": ["🎧｜neon-vibes", "🎼｜echo-hall", "💿｜jukebox-requests"],
    "🕹️｜Digital Realms": ["🪖｜valor-core", "🚗｜nightdrive-gta", "🔫｜strike-zone-pubg", "🌐｜upload-your-quest"],
    "🎲｜Arcane Bot Quests": ["🐸｜dank-den", "🦉｜owo-grove", "🎒｜poke-lab", "🧩｜epic-tavern", "🥚｜karuta-sanctum"],
    "🗣️｜Arcadian Voice Links": ["👥｜duo-link", "👨‍👩‍👧｜trio-link", "🎯｜squad-link", "🌀｜multi-party-hall", "🗣️｜open-echo-hall"]
}

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user.name}")
    guild = bot.guilds[0]
    verified_role = discord.utils.get(guild.roles, name="Verified Initiates")
    awaiting_role = discord.utils.get(guild.roles, name="Awaiting Initiation")

    for category_name, channels in structure.items():
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            verified_role: discord.PermissionOverwrite(view_channel=True),
            awaiting_role: discord.PermissionOverwrite(view_channel=False)
        }

        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            category = await guild.create_category(category_name, overwrites=overwrites)

        for ch in channels:
            if any(word in ch for word in ["link", "hall", "party"]):
                if not discord.utils.get(guild.voice_channels, name=ch):
                    await guild.create_voice_channel(ch, category=category)
            else:
                if not discord.utils.get(guild.text_channels, name=ch):
                    await guild.create_text_channel(ch, category=category)

    print("✅ Server structure complete!")

@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="Awaiting Initiation")
    if role:
        await member.add_roles(role)

    welcome_channel = discord.utils.get(member.guild.text_channels, name="enter-the-arcadia")
    if welcome_channel:
        embed = discord.Embed(
            title="✨ Welcome to Anex Arcadia ✨",
            description=(
                f"🌐 {member.mention}, welcome to the **Cyber-Fantasy Realm**!

"
                "🧾 Start your journey by reading `📜｜guide-to-ascend`
"
                "🧱 Then choose your path in `🧱｜rank-totems`

"
                "✅ To unlock the entire realm, click the **Verify Me** button below!"
            ),
            color=discord.Color.from_rgb(127, 0, 255)
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text="Anex Arcadia • Powered by your custom bot ⚡")

        await welcome_channel.send(embed=embed)

@bot.command()
async def sendverify(ctx):
    button = Button(label="✅ Verify Me", style=discord.ButtonStyle.success)

    async def button_callback(interaction):
        role = discord.utils.get(interaction.guild.roles, name="Verified Initiates")
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ You are now verified and have access to the full server!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Verification role not found.", ephemeral=True)

    button.callback = button_callback
    view = View()
    view.add_item(button)

    await ctx.send("Click the button below to verify and enter Anex Arcadia!", view=view)

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong! Your custom bot is active.")

keep_alive()
bot.run(TOKEN)
