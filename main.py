import discord
from discord.ext import commands
import random
import asyncio
import re
from io import BytesIO
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask
import os

# =========================================================
# KONFIGURACJA
# =========================================================

# WAŻNE: po ujawnieniu tokenu wygeneruj NOWY w Discord Developer Portal.
# Wczytaj plik .env znajdujący się obok skryptu.
# Jeśli go tam nie ma, spróbuj również w katalogu roboczym PyCharm.
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent / ".env"
if ENV_PATH.is_file():
    load_dotenv(dotenv_path=ENV_PATH, override=True)
else:
    load_dotenv(override=True)

TOKEN = os.getenv("DISCORD_TOKEN")

VERIFICATION_CHANNEL_ID = 1557481508548382900
LOBBY_CHANNEL_ID = 1557481450922840114
SCREEN_CHANNEL_ID = 1557774434469945416

VERIFIED_ROLE_NAME = "Zweryfikowany"
SCREEN_APPROVED_ROLE_ID = 1557841521124970567

VERIFICATION_EMOJI_ID = 1550784136774426716
VERIFICATION_EMOJI_NAME = "weryfikacja"

MEMBER_EMOJI = "<:czlonek:1557772365725827218>"
ARROW_EMOJI = "<a:strzalka:1557767589411688631>"
RULES_EMOJI = "<:regulamin:1557782271346475018>"
YES_EMOJI = "<:tak:1557787871102894200>"
NO_EMOJI = "<:nie:1557787790132117634>"
STAR_EMOJI = "<:gwiazdka:1557829650737135656>"
TIME_EMOJI = "<:czas:1557829573821993121>"
WARNING_EMOJI = "<:ostrzezenie:1557829272373043370>"

SERVER_NAME = "LineCode"

LOBBY_BANNER_URL = (
    "https://cdn.discordapp.com/attachments/"
    "1472578698074001471/1557796438233321522/"
    "file_000000002da882108382f88003491568.png"
    "?ex=6ac91a7d&is=6ac7c8fd"
    "&hm=9d49d45cd449ac2f81d98f834a825157ca33b91c9caae83b86782e86973c7a55"
)

VERIFICATION_BANNER_URL = (
    "https://cdn.discordapp.com/attachments/"
    "1549797312975347833/1557487722548170793/"
    "lv_0_20261007221959.jpg"
    "?backend=b2&ex=6ac7faf9&is=6ac6a979"
    "&hm=b4e974bbf5f0ec252cdd49a711911bc266530c95eed37b627d833de4dffcf033"
)

# Osobny banner wyłącznie dla panelu ticketów — nie korzysta z bannera lobby.
TICKET_BANNER_URL = (
    "https://cdn.discordapp.com/attachments/1472578698074001471/1558122022402269255/ticket.png"
    "?ex=6aca49b6&is=6ac8f836&hm=df387751c56190734ac153a6c9dc5bf742e88b7ce7fdd393429cb1188dac7202"
)

# =========================================================
# SYSTEM TICKETÓW — UZUPEŁNIJ TE ID
# =========================================================

# Kanał, w którym ma być wysłany panel wyboru ticketu.
TICKET_PANEL_CHANNEL_ID = 1557774175253430282  # Kanał panelu ticketów

# ID kategorii Discord, pod którymi bot będzie tworzył kanały ticketów.
# Utwórz 5 kategorii na serwerze i wpisz ich ID.
TICKET_CATEGORY_IDS = {
    "pomoc": 1558152767464411136,  # kategoria Discord dla ticketów „Pomoc z pluginem”
    "konfiguracja": 1558153112777261076,  # kategoria Discord dla ticketów „Konfiguracja”
    "blad": 1558153188115222578,  # kategoria Discord dla ticketów „Zgłoś błąd”
    "pytanie": 1558153245182918687,  # kategoria Discord dla ticketów „Pytanie”
    "wspolpraca": 1558153305077846066,  # kategoria Discord dla ticketów „Współpraca”
}

# ID roli administracji/supportu, która ma widzieć tickety.
# Zostaw 0, jeśli nie chcesz dodawać dodatkowej roli supportu.
TICKET_STAFF_ROLE_ID = 0

TICKET_COLOR = discord.Color.from_rgb(35, 200, 80)

TICKET_TYPES = {
    "pomoc": {
        "label": "Pomoc z pluginem",
        "emoji": "<:plugin:1558136283639849102>",
        "description": "Masz problem z pluginem? Otwórz ticket.",
        "channel_prefix": "pomoc",
        "questions": [
            ("plugin", " Jaki plugin?", "Podaj nazwę pluginu", True),
            ("autor", " Autor pluginu", "Podaj autora pluginu", True),
            ("opis", " Opisz swój problem", "Dokładnie opisz problem", True),
        ],
    },
    "konfiguracja": {
        "label": "Konfiguracja",
        "emoji": "<:gwiazdka:1557829650737135656>",
        "description": "Potrzebujesz pomocy w konfiguracji pluginu?",
        "channel_prefix": "konfiguracja",
        "questions": [
            ("plugin", "Jaki plugin?", "Podaj nazwę pluginu", True),
            ("autor", "Autor pluginu", "Podaj autora pluginu", True),
            ("opis", "Opis ticketu", "Opisz, co chcesz skonfigurować", True),
        ],
    },
    "blad": {
        "label": "Zgłoś błąd",
        "emoji": "<:ostrzezenie:1557829272373043370>",
        "description": "Znalazłeś błąd w pluginie? Zgłoś go tutaj.",
        "channel_prefix": "blad",
        "questions": [
            ("plugin", "jaki plugin?", "Podaj nazwę pluginu", True),
            ("autor", "Autor pluginu", "Podaj autora pluginu", True),
            ("opis", "Opis błędu", "Opisz błąd i jak go odtworzyć", True),
        ],
    },
    "pytanie": {
        "label": "Pytanie",
        "emoji": "<:zastanowienie:1558136483733446686>",
        "description": "Zadaj pytanie dotyczące jakiegos tematu.",
        "channel_prefix": "pytanie",
        "questions": [
            ("temat", "Czego dotyczy pytanie?", "Podaj temat pytania", True),
            ("opis", "Opis pytania", "Opisz dokładnie swoje pytanie", True),
        ],
    },
    "wspolpraca": {
        "label": "Współpraca",
        "emoji": "<:wspolpraca:1558137608029077635>",
        "description": "Zaproponuj współpracę z LineCode.",
        "channel_prefix": "wspolpraca",
        "questions": [
            ("serwer", "Jaki serwer?", "Nazwa i discord serwera", True),
            ("czlonkowie", "Ilu członków?", "Podaj liczbę członków Discord", True),
            ("zasady", "Na jakiej zasadzie współpraca?", "Opisz propozycję współpracy", True),
            ("korzysci", "Jaki plus dla nas?", "Co LineCode zyska na współpracy?", True),
        ],
    },
}

# =========================================================
# INTENTS I BOT
# =========================================================

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True


class LineCodeBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.verification_panel_sent = False
        self.lobby_panel_sent = False
        self.ticket_panel_sent = False

    async def setup_hook(self):
        self.add_view(VerificationView())
        self.add_view(ScreenDecisionView())
        self.add_view(TicketPanelView())
        self.add_view(TicketChannelView())
        print("System weryfikacji został załadowany.")
        print("System screenów został załadowany.")
        print("System ticketów został załadowany.")


bot = LineCodeBot()


# =========================================================
# START BOTA
# =========================================================

@bot.event
async def on_ready():
    print()
    print("========================================")
    print(f"Zalogowano jako: {bot.user}")
    print(f"ID bota: {bot.user.id}")
    print("========================================")

    if not bot.verification_panel_sent:
        bot.verification_panel_sent = True
        await send_verification_panel(bot)

    if not bot.lobby_panel_sent:
        bot.lobby_panel_sent = True
        await send_lobby_panel(bot)

    if not bot.ticket_panel_sent:
        bot.ticket_panel_sent = True
        await send_ticket_panel()


# =========================================================
# SYSTEM TICKETÓW
# =========================================================

class TicketPanelView(discord.ui.View):
    """Stały panel z wyborem kategorii ticketu."""

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketCategorySelect())


class TicketCategorySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=data["label"],
                value=key,
                emoji=data["emoji"],
                description=data["description"][:100],
            )
            for key, data in TICKET_TYPES.items()
        ]

        super().__init__(
            placeholder="Wybierz kategorię zgłoszenia...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="linecode_ticket_category_select",
        )

    async def callback(self, interaction: discord.Interaction):
        ticket_type = self.values[0]
        data = TICKET_TYPES[ticket_type]

        # Modal Discord może mieć maksymalnie 5 pól; wszystkie nasze formularze się mieszczą.
        await interaction.response.send_modal(
            TicketFormModal(ticket_type, data)
        )


class TicketFormModal(discord.ui.Modal):
    def __init__(self, ticket_type: str, data: dict):
        super().__init__(title=data["label"][:45], timeout=300)
        self.ticket_type = ticket_type
        self.data_config = data
        self.fields_by_key = {}

        for key, label, placeholder, required in data["questions"]:
            text_input = discord.ui.TextInput(
                label=label[:45],
                placeholder=placeholder[:100],
                required=required,
                style=discord.TextStyle.paragraph if key in (
                    "opis", "zasady", "korzysci"
                ) else discord.TextStyle.short,
                max_length=1000 if key in (
                    "opis", "zasady", "korzysci"
                ) else 100,
            )
            self.fields_by_key[key] = text_input
            self.add_item(text_input)

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Ten formularz działa tylko na serwerze Discord.",
                ephemeral=True,
            )
            return

        guild = interaction.guild
        category_id = TICKET_CATEGORY_IDS.get(self.ticket_type, 0)

        if not category_id:
            await interaction.response.send_message(
                "❌ Administracja nie ustawiła jeszcze kategorii Discord "
                "dla tego rodzaju ticketu. Uzupełnij TICKET_CATEGORY_IDS w kodzie.",
                ephemeral=True,
            )
            return

        category = guild.get_channel(category_id)
        if not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message(
                "❌ Nie znaleziono kategorii Discord dla tego ticketu. "
                "Sprawdź ID w konfiguracji.",
                ephemeral=True,
            )
            return

        # Blokada: jedna osoba może mieć tylko jeden otwarty ticket w danej kategorii.
        prefix = self.data_config["channel_prefix"]
        existing = discord.utils.find(
            lambda ch: isinstance(ch, discord.TextChannel)
                       and ch.category_id == category.id
                       and ch.topic
                       and f"ticket-owner:{interaction.user.id}" in ch.topic,
            guild.text_channels,
        )

        if existing:
            await interaction.response.send_message(
                f"Masz już otwarty ticket: {existing.mention}",
                ephemeral=True,
            )
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
                embed_links=True,
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_channels=True,
                manage_messages=True,
                attach_files=True,
                embed_links=True,
            ),
        }

        if TICKET_STAFF_ROLE_ID:
            staff_role = guild.get_role(TICKET_STAFF_ROLE_ID)
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    manage_messages=True,
                    attach_files=True,
                    embed_links=True,
                )

        safe_name = re.sub(
            r"[^a-z0-9-]",
            "-",
            interaction.user.name.lower(),
        ).strip("-")
        safe_name = re.sub(r"-+", "-", safe_name)[:35] or "uzytkownik"
        channel_name = f"{prefix}-{safe_name}"[:95]

        # Zapis właściciela w topic pozwala odnaleźć ticket również po restarcie bota.
        try:
            ticket_channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites,
                topic=(
                    f"ticket-owner:{interaction.user.id} | "
                    f"ticket-type:{self.ticket_type} | "
                    f"otworzyl:{interaction.user}"
                ),
                reason=f"Ticket {self.data_config['label']} od {interaction.user}",
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Bot nie ma uprawnień do tworzenia kanałów lub zarządzania kanałami.",
                ephemeral=True,
            )
            return
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"<:nie:1557787790132117634> Nie udało się utworzyć ticketu: {e}",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"{self.data_config['emoji']} {self.data_config['label']}",
            description=(
                f"> <:czlonek:1557772365725827218> Witaj {interaction.user.mention}!\n"

                "> Administracja odpowie kiedy będzie dostępna.\n\n"
                "**> <:gwiazdka:1557829650737135656>Dane ticketu:**"
            ),
            color=TICKET_COLOR,
            timestamp=discord.utils.utcnow(),
        )

        for key, label, placeholder, required in self.data_config["questions"]:
            value = self.fields_by_key[key].value.strip()
            embed.add_field(
                name=label,
                value=value[:1024] if value else "Nie podano",
                inline=False,
            )

        embed.set_footer(
            text=f"LineCode • Ticket użytkownika {interaction.user.id}"
        )

        staff_mention = ""
        if TICKET_STAFF_ROLE_ID:
            staff_role = guild.get_role(TICKET_STAFF_ROLE_ID)
            if staff_role:
                staff_mention = f"{staff_role.mention} "

        await ticket_channel.send(
            content=f"{interaction.user.mention} {staff_mention}".strip(),
            embed=embed,
            view=TicketChannelView(),
        )

        await interaction.response.send_message(
            f"<:tak:1557787871102894200> Utworzono ticket: {ticket_channel.mention}",
            ephemeral=True,
        )
        print(
            f" <:ostrzezenie:1557829272373043370>Ticket utworzony: {ticket_channel.name} "
            f"({self.data_config['label']}) — {interaction.user}"
        )


class TicketChannelView(discord.ui.View):
    """Przycisk zamknięcia widoczny w każdym tickecie."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Zamknij ticket",
        style=discord.ButtonStyle.danger,
        emoji="<:bariera:1557492086276759623>",
        custom_id="linecode_ticket_close",
    )
    async def close_ticket(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button,
    ):
        if interaction.guild is None or not isinstance(
                interaction.channel, discord.TextChannel
        ):
            await interaction.response.send_message(
                "<:nie:1557787790132117634> Nie można zamknąć tego ticketu.",
                ephemeral=True,
            )
            return

        channel = interaction.channel
        topic = channel.topic or ""
        owner_match = re.search(r"ticket-owner:(\d+)", topic)
        owner_id = int(owner_match.group(1)) if owner_match else None

        permissions = interaction.user.guild_permissions
        is_staff = (
                permissions.administrator
                or permissions.manage_channels
                or permissions.manage_messages
        )

        if interaction.user.id != owner_id and not is_staff:
            await interaction.response.send_message(
                "<:nie:1557787790132117634> Ticket może zamknąć jego założyciel lub administracja.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "<:bariera:1557492086276759623> Ticket zostanie zamkięty za 5 sekund.",
            ephemeral=True,
        )
        await channel.send(
            f"<:bariera:1557492086276759623> Ticket zamyka {interaction.user.mention}. "
            " <:ticket:1558144004355260476>Ticket zostanie usunięty za 5 sekund."
        )
        await asyncio.sleep(5)
        try:
            await channel.delete(
                reason=f" <:ticket:1558144004355260476>Ticket zamknięty przez {interaction.user}"
            )
        except discord.Forbidden:
            print("Bot nie ma uprawnień do usunięcia kanału ticketu.")
        except discord.HTTPException as e:
            print(f"Błąd usuwania ticketu: {e}")


async def send_ticket_panel():
    if not TICKET_PANEL_CHANNEL_ID:
        print(
            "System ticketów: ustaw TICKET_PANEL_CHANNEL_ID, "
            "aby bot automatycznie wysyłał panel."
        )
        return

    channel = bot.get_channel(TICKET_PANEL_CHANNEL_ID)
    if channel is None:
        try:
            channel = await bot.fetch_channel(TICKET_PANEL_CHANNEL_ID)
        except discord.HTTPException as e:
            print(f"Nie udało się pobrać kanału panelu ticketów: {e}")
            return

    embed = discord.Embed(
        title="        ``` 🎫 LineCode x TICKET   ```",
        description=(
            "> Wybierz kategorię z listy poniżej, aby otworzyć  ticket.\n\n"

            "> ** potrzebujesz pomocy otwórz **  \n"
            "> ** odpowiednią kategorie **"
            ""
            ""
            ""
            ""
            ""
            ""
        ),
        color=TICKET_COLOR,
    )
    # Banner wyświetlany pod treścią embeda panelu ticketów.
    if TICKET_BANNER_URL:
        embed.set_image(url=TICKET_BANNER_URL)
    embed.set_footer(text="LineCode • System ticketów")

    try:
        await channel.send(embed=embed, view=TicketPanelView())
        print("Panel ticketów został wysłany.")
    except discord.HTTPException as e:
        print(f"Błąd wysyłania panelu ticketów: {e}")


# =========================================================
# SYSTEM SCREENÓW
# =========================================================

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id != SCREEN_CHANNEL_ID:
        await bot.process_commands(message)
        return

    image_attachments = []
    for attachment in message.attachments:
        filename = attachment.filename.lower()
        is_image_by_type = (
                attachment.content_type is not None
                and attachment.content_type.startswith("image/")
        )
        is_image_by_extension = filename.endswith(
            (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff")
        )
        if is_image_by_type or is_image_by_extension:
            image_attachments.append(attachment)

    if not image_attachments:
        await bot.process_commands(message)
        return

    if len(image_attachments) > 2:
        try:
            await message.delete()
        except discord.HTTPException:
            pass
        await message.channel.send(
            f"{NO_EMOJI} {message.author.mention}, "
            "**możesz wysłać maksymalnie 2 zdjęcia!**",
            delete_after=5,
        )
        return

    print(
        f"Nowy screen od {message.author} (ID: {message.author.id}), "
        f"liczba zdjęć: {len(image_attachments)}"
    )

    files = []
    extensions = []
    try:
        for index, attachment in enumerate(image_attachments):
            image_data = await attachment.read()
            extension = attachment.filename.rsplit(".", 1)[-1].lower()
            if extension not in (
                    "png", "jpg", "jpeg", "webp", "gif", "bmp", "tiff"
            ):
                extension = "png"

            filename = f"linecode_screen_{index + 1}.{extension}"
            files.append(discord.File(BytesIO(image_data), filename=filename))
            extensions.append(extension)

        now = discord.utils.utcnow()
        embed = discord.Embed(
            title=f"{STAR_EMOJI} LINECODE × PROŚBA O DOSTĘP {STAR_EMOJI}",
            description=(
                f"• **{MEMBER_EMOJI} Użytkownik:** {message.author.mention}\n\n"
                f"• **{TIME_EMOJI} Czas wysłania:** "
                f"<t:{int(now.timestamp())}:R>\n\n"
                f"• **Status:** {WARNING_EMOJI} Oczekiwanie na decyzję..."
            ),
            color=TICKET_COLOR,
        )
        embed.set_footer(text=f"LineCode • UserID: {message.author.id}")
        embed.set_image(
            url=f"attachment://linecode_screen_1.{extensions[0]}"
        )
        embeds = [embed]

        if len(image_attachments) == 2:
            second_embed = discord.Embed(color=TICKET_COLOR)
            second_embed.set_image(
                url=f"attachment://linecode_screen_2.{extensions[1]}"
            )
            second_embed.set_footer(text="LineCode • Drugi screen")
            embeds.append(second_embed)

        await message.channel.send(
            embeds=embeds,
            files=files,
            view=ScreenDecisionView(),
        )
        try:
            await message.delete()
        except discord.Forbidden:
            print("Bot nie ma uprawnień do usuwania oryginalnej wiadomości.")
        except discord.NotFound:
            pass

    except discord.Forbidden:
        print("Bot nie ma wymaganych uprawnień do obsługi screenów.")
    except Exception as e:
        print(f"Błąd obsługi screena: {e}")

    await bot.process_commands(message)


def get_user_id_from_submission(interaction):
    if not interaction.message.embeds:
        return None

    for embed in interaction.message.embeds:
        if embed.footer:
            match = re.search(
                r"UserID:\s*(\d+)",
                embed.footer.text or "",
            )
            if match:
                return int(match.group(1))

    description = interaction.message.embeds[0].description or ""
    match = re.search(r"<@!?(\d+)>", description)
    return int(match.group(1)) if match else None


async def give_screen_approved_role(interaction, user_id):
    if user_id is None or interaction.guild is None:
        print("Nie udało się odczytać autora screena lub serwera.")
        return False

    role = interaction.guild.get_role(SCREEN_APPROVED_ROLE_ID)
    if role is None:
        print(
            f"Nie znaleziono rangi o ID {SCREEN_APPROVED_ROLE_ID}. "
            "Sprawdź konfigurację."
        )
        return False

    try:
        member = interaction.guild.get_member(user_id)
        if member is None:
            member = await interaction.guild.fetch_member(user_id)

        if role not in member.roles:
            await member.add_roles(
                role,
                reason=f"Zaakceptowany screen przez {interaction.user}",
            )
        return True

    except discord.NotFound:
        print("Użytkownik nie znajduje się już na serwerze.")
    except discord.Forbidden:
        print("Bot nie może nadać rangi. Sprawdź uprawnienia i hierarchię ról.")
    except discord.HTTPException as e:
        print(f"Błąd Discord API podczas nadawania rangi: {e}")
    return False


async def send_access_dm(user_id, accepted):
    if user_id is None:
        print("Nie znaleziono ID użytkownika do wysłania PW.")
        return

    try:
        user = bot.get_user(user_id)
        if user is None:
            user = await bot.fetch_user(user_id)

        if accepted:
            embed = discord.Embed(
                title=f"{YES_EMOJI} Dostęp przyznany!",
                description=(
                    "Twoje zgłoszenie na **LineCode** zostało zaakceptowane.\n\n"
                    f"{YES_EMOJI} **Dostęp został Ci przyznany!**\n\n"
                    "Dziękujemy za przesłanie poprawnego zgłoszenia."
                ),
                color=discord.Color.green(),
            )
        else:
            embed = discord.Embed(
                title=f"{NO_EMOJI} Dostęp nie został przyznany",
                description=(
                    "Twoje zgłoszenie na **LineCode** zostało odrzucone.\n\n"
                    f"{NO_EMOJI} **Dostęp nie został Ci przyznany.**\n\n"
                    "Jeżeli uważasz, że to pomyłka, skontaktuj się z administracją."
                ),
                color=discord.Color.red(),
            )

        embed.set_footer(text="LineCode • System zgłoszeń")
        await user.send(embed=embed)
        print(f"Wysłano PW do użytkownika {user_id}.")

    except discord.Forbidden:
        print(f"Nie można wysłać PW do użytkownika {user_id}.")
    except discord.NotFound:
        print(f"Nie znaleziono użytkownika {user_id}.")
    except discord.HTTPException as e:
        print(f"Błąd wysyłania PW: {e}")


class ScreenDecisionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def check_permissions(self, interaction):
        permissions = interaction.user.guild_permissions
        if not (permissions.administrator or permissions.manage_messages):
            await interaction.response.send_message(
                "Nie masz uprawnień do rozpatrywania screenów.",
                ephemeral=True,
            )
            return False
        return True

    async def delete_submission(self, interaction):
        try:
            await interaction.message.delete()
            print("Zgłoszenie screenowe zostało usunięte.")
        except discord.NotFound:
            pass
        except discord.Forbidden:
            print("Bot nie może usunąć zgłoszenia.")
        except discord.HTTPException as e:
            print(f"Błąd usuwania zgłoszenia: {e}")

    @discord.ui.button(
        label="Zaakceptuj",
        style=discord.ButtonStyle.success,
        emoji=discord.PartialEmoji(name="tak", id=1557787871102894200),
        custom_id="linecode_screen_accept",
    )
    async def accept_button(self, interaction, button):
        if not await self.check_permissions(interaction):
            return

        user_id = get_user_id_from_submission(interaction)
        await interaction.response.send_message(
            f"{YES_EMOJI} Rozpatruję zgłoszenie...",
            ephemeral=True,
        )

        role_given = await give_screen_approved_role(interaction, user_id)
        await send_access_dm(user_id, True)

        try:
            if role_given:
                await interaction.followup.send(
                    f"{YES_EMOJI} Screen zaakceptowany. Ranga została nadana "
                    "lub użytkownik już ją posiada.",
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(
                    f"{WARNING_EMOJI} Screen zaakceptowany, ale nie udało się "
                    "nadać rangi. Sprawdź konsolę bota.",
                    ephemeral=True,
                )
        except discord.HTTPException:
            pass

        await self.delete_submission(interaction)

    @discord.ui.button(
        label="Odrzuć",
        style=discord.ButtonStyle.danger,
        emoji=discord.PartialEmoji(name="nie", id=1557787790132117634),
        custom_id="linecode_screen_reject",
    )
    async def reject_button(self, interaction, button):
        if not await self.check_permissions(interaction):
            return

        user_id = get_user_id_from_submission(interaction)
        await interaction.response.send_message(
            f"{NO_EMOJI} Zgłoszenie zostało odrzucone.",
            ephemeral=True,
        )
        await send_access_dm(user_id, False)
        await self.delete_submission(interaction)


# =========================================================
# PANEL LOBBY I POWITANIA
# =========================================================

async def send_lobby_panel(bot):
    """Wysyła panel lobby w stylu z przykładowego zrzutu ekranu."""
    print("Przygotowywanie panelu lobby...")
    channel = bot.get_channel(LOBBY_CHANNEL_ID)

    if channel is None:
        try:
            channel = await bot.fetch_channel(LOBBY_CHANNEL_ID)
        except discord.HTTPException as e:
            print(f"Nie udało się pobrać kanału lobby: {e}")
            return

    member_count = channel.guild.member_count or 0
    embed = discord.Embed(
        title=" LINECODE × POWITANIA",
        description=(
            f"> <:members:1558860412328607805> Witaj na LineCode! Jesteś **{member_count} osobą na serwerze**\n\n"
            "> Miło Cię widzieć na LineCode!\n"
            "> Miłej zabawy  i mamy nadzieję, że zostaniesz z nami na dłużej!\n\n"
            f"> <:regulamin:1557782271346475018> Zapoznaj się z regulaminem  #・・<#{1557748733561667674}>"
        ),
        color=discord.Color.from_rgb(46, 204, 113)
    )
    embed.set_footer(text="    Witaj na LineCode     •••")
    if LOBBY_BANNER_URL:
        embed.set_image(url=LOBBY_BANNER_URL)

    try:
        await channel.send(embed=embed)
        print("Panel lobby został wysłany.")
    except discord.HTTPException as e:
        print(f"Błąd wysyłania panelu lobby: {e}")


@bot.event
async def on_member_join(member):
    print(f"Dołączyła nowa osoba: {member}")
    channel = bot.get_channel(LOBBY_CHANNEL_ID)

    if channel is None:
        try:
            channel = await bot.fetch_channel(LOBBY_CHANNEL_ID)
        except discord.HTTPException as e:
            print(f"Nie znaleziono lobby: {e}")
            return

    member_count = member.guild.member_count or 0
    embed = discord.Embed(
        title=" LINECODE × POWITANIA",
        description=(
            f"> <:members:1558860412328607805> Witaj {member.mention}! Jesteś **{member_count} osobą na serwerze**\n\n"
            "> Miło Cię widzieć na LineCode!\n"
            "> Miłej zabawy  i mamy nadzieję, że zostaniesz z nami na dłużej!\n\n"
            f"> <:regulamin:1557782271346475018> Zapoznaj się z regulaminem  <#{VERIFICATION_CHANNEL_ID}>"
        ),
        TICKET_COLOR=discord.Color.from_rgb(35, 200, 80)
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text="                         ```Witaj na LineCode```                         ")
    if LOBBY_BANNER_URL:
        embed.set_image(url=LOBBY_BANNER_URL)

    try:
        await channel.send(embed=embed)
        print(f"Powitano {member}.")
    except discord.HTTPException as e:
        print(f"Błąd powitania: {e}")


# =========================================================
# PANEL WERYFIKACJI
# =========================================================

async def send_verification_panel(bot):
    print("Przygotowywanie panelu weryfikacji...")
    channel = bot.get_channel(VERIFICATION_CHANNEL_ID)

    if channel is None:
        try:
            channel = await bot.fetch_channel(VERIFICATION_CHANNEL_ID)
        except discord.HTTPException as e:
            print(f"Nie znaleziono kanału weryfikacji: {e}")
            return

    embed = discord.Embed(
        title="Weryfikacja × LINECODE",
        description=(
            f"{ARROW_EMOJI} **Kliknij przycisk Zweryfikuj się poniżej.**\n\n"
            f"{ARROW_EMOJI} Następnie rozwiąż proste działanie matematyczne.\n\n"
            f"{ARROW_EMOJI} Po poprawnej odpowiedzi otrzymasz "
            f"rangę **{VERIFIED_ROLE_NAME}**."
        ),
        color=TICKET_COLOR,
    )
    embed.set_image(url=VERIFICATION_BANNER_URL)
    embed.set_footer(text="LineCode • System weryfikacji")

    try:
        await channel.send(embed=embed, view=VerificationView())
        print("Panel weryfikacji został wysłany.")
    except discord.HTTPException as e:
        print(f"Błąd panelu weryfikacji: {e}")


class VerificationModal(discord.ui.Modal):
    def __init__(self, number1, number2):
        super().__init__(title="Weryfikacja LineCode")
        self.number1 = number1
        self.number2 = number2
        self.answer = discord.ui.TextInput(
            label=f"Ile to {number1} + {number2}?",
            placeholder="Wpisz odpowiedź...",
            required=True,
            max_length=10,
        )
        self.add_item(self.answer)

    async def on_submit(self, interaction):
        correct_answer = self.number1 + self.number2
        try:
            user_answer = int(self.answer.value.strip())
        except ValueError:
            await interaction.response.send_message(
                "Wpisz poprawną liczbę.", ephemeral=True
            )
            return

        if user_answer != correct_answer:
            await interaction.response.send_message(
                "Niepoprawna odpowiedź. Spróbuj ponownie.",
                ephemeral=True,
            )
            return

        if interaction.guild is None:
            await interaction.response.send_message(
                "Nie znaleziono serwera.", ephemeral=True
            )
            return

        role = discord.utils.get(
            interaction.guild.roles,
            name=VERIFIED_ROLE_NAME,
        )
        if role is None:
            await interaction.response.send_message(
                f"Nie znaleziono roli {VERIFIED_ROLE_NAME}.",
                ephemeral=True,
            )
            return

        if role in interaction.user.roles:
            await interaction.response.send_message(
                f"{YES_EMOJI} Już się zweryfikowałeś!",
                ephemeral=True,
            )
            return

        try:
            await interaction.user.add_roles(
                role,
                reason="Poprawna weryfikacja LineCode",
            )
            await interaction.response.send_message(
                f"{YES_EMOJI} **Pomyślnie zweryfikowano!**",
                ephemeral=True,
            )
            print(f"Zweryfikowano: {interaction.user}")
        except discord.Forbidden:
            await interaction.response.send_message(
                "Bot nie może nadać tej roli. Sprawdź uprawnienie "
                "Zarządzanie rolami i hierarchię rang.",
                ephemeral=True,
            )
        except discord.HTTPException as e:
            print(f"Błąd nadawania roli weryfikacyjnej: {e}")
            await interaction.response.send_message(
                "Wystąpił błąd podczas weryfikacji.",
                ephemeral=True,
            )


class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Zweryfikuj się",
        style=discord.ButtonStyle.success,
        custom_id="linecode_verification_button",
        emoji=discord.PartialEmoji(
            name=VERIFICATION_EMOJI_NAME,
            id=VERIFICATION_EMOJI_ID,
        ),
    )
    async def verify_button(self, interaction, button):
        number1 = random.randint(1, 10)
        number2 = random.randint(1, 10)
        await interaction.response.send_modal(
            VerificationModal(number1, number2)
        )


# =========================================================
# URUCHOMIENIE
# =========================================================


app = Flask(__name__)


@app.route("/")
def home():
    return "Bot Discord działa!", 200


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


def keep_alive():
    server = Thread(target=run_web, daemon=True)
    server.start()


keep_alive()




if __name__ == "__main__":
    if not TOKEN:
        print(f"BŁĄD: Nie znaleziono DISCORD_TOKEN. Sprawdzono plik: {ENV_PATH}")
        print("Upewnij się, że plik nazywa się dokładnie .env i zawiera:")
        print("DISCORD_TOKEN=TWÓJ_TOKEN_BOTA")
    else:
        try:
            bot.run(TOKEN)
        except discord.LoginFailure:
            print(
                "Nieprawidłowy token. Wygeneruj nowy w Discord Developer Portal."
            )
        except Exception as e:
            print(f"Błąd uruchamiania bota: {e}")
