import discord
from discord.ext import commands
import random
import os
from flask import Flask
from threading import Thread

# Flask App für Health Check (für Render und UptimeRobot)
app = Flask(__name__)

@app.route('/')
def health_check():
    return "✅ Der Bot läuft!", 200

@app.route('/health')
def health():
    return {"status": "healthy", "bot": "online"}, 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Bot Variablen
last_number = 0
last_user = None
channel_id = 1386659088984834078  # Ersetze mit deiner Kanal-ID
bot_mistake_chance = 0.05  # 5% Chance dass der Bot einen "Fehler" macht

# Bot Antworten
wrong_number_responses = [
    "{user}, das war komplett daneben. Die richtige Zahl wäre **{expected}** gewesen. Zurück auf Los! 🎲",
    "{user}, Mathe ist schwer – aber SO schwer? Die nächste Zahl wäre **{expected}**!",
    "{user}, leider falsch. Wir starten wieder bei 1. Vielleicht hilft ein Taschenrechner?",
    "{user}, das war nix. Versuch's nochmal bei der **1**!",
    "{user}, war das geraten oder hast du einfach gewürfelt? Die richtige Zahl wäre **{expected}** gewesen!",
    "{user}, das war ein Mathe-Test. Leider durchgefallen. Zurück auf Start!",
    "{user}, da war wohl der Taschenrechner im Energiesparmodus.",
    "{user}, Zahl verloren? Hier ist ein Hinweis: **{expected}** wäre korrekt gewesen!",
    "{user}, selbst ein Bot hätte das besser hinbekommen. Zurück zu 1!",
    "{user}, das war ein kritischer Fehlwurf. Die nächste Zahl war **{expected}**!",
    "{user}, neue Runde, neues Glück. Aber bitte mit der richtigen Zahl!",
    "{user}, wow… das war nicht mal knapp daneben. Einfach falsch.",
    "{user}, bei dir zählt offenbar was anderes… vielleicht Buchstaben?",
    "{user}, willst du lieber das Alphabet durchgehen? Zahlen scheinen nicht dein Ding zu sein.",
    "{user}, das war keine Zahl, das war ein Statement. Ein sehr schlechtes.",
    "{user}, du hast die Logik mit dem Vorschlaghammer bearbeitet, oder?",
    "{user}, war das ein Zaubertrick? Zahl verschwunden!",
    "{user}, für sowas wurde der Reset-Knopf erfunden.",
    "{user}, Zahlen sind keine Zombies, die darf man nicht einfach durcheinander bringen.",
    "{user}, du hattest einen Job. Einen. Und hast ihn vergeigt.",
    "{user}, Mathematik hat dich soeben blockiert."
]

double_post_responses = [
    "{user}, du darfst nicht zweimal hintereinander zählen! Das ist wie zweimal Nachtisch! 🍰",
    "{user}, Teamarbeit heißt auch mal abgeben. Zurück auf 1!",
    "{user}, erst du – dann jemand anders. Regeln sind Regeln!",
    "{user}, Geduld ist eine Tugend. Gib anderen auch mal die Chance!",
    "{user}, hast du gedacht, wir merken das nicht? Schön artig warten!",
    "{user}, Speedrun gescheitert. Erst andere, dann du!",
    "{user}, so laut musst du nicht zählen – wir hören dich auch einmal!",
    "{user}, Einbahnstraße! Nicht zweimal abbiegen!",
    "{user}, du bist nicht in einer Zeitschleife. Einen Schritt zurück!",
    "{user}, das hier ist kein Monolog. Gib mal anderen das Mikrofon!",
    "{user}, das war so nötig wie ein zweiter Kassenbon.",
    "{user}, bitte nicht alles alleine machen. Es gibt Therapien für sowas.",
    "{user}, wir haben's gehört. Einmal reicht. Wirklich.",
    "{user}, du bist schneller wieder dran als mein DHL-Paket. Chill.",
    "{user}, das ist 'Gemeinsam zählen' – nicht 'Ich, ich und nochmal ich'.",
    "{user}, schön, dass du dich magst – aber das hier ist kein Solo-RPG.",
    "{user}, ja, du bist lustig. Jetzt bitte ernsthaft: Lass wen anders zählen.",
    "{user}, willst du dich noch selbst loben oder reicht's?",
    "{user}, Regelbruch deluxe. Alles zurück auf Start – danke für nix."
]

milestone_messages = [
    "Meilenstein erreicht! Gemeinsam habt ihr die **{number}** geschafft! Respekt!",
    "Die **{number}** ist geknackt – als Team unschlagbar!",
    "Wow! **{number}** – das läuft ja besser als meine Diät!",
    "Weiter so! Bei **{number}** seid ihr nicht zu stoppen!",
    "Boom! Die **{number}** ist geknackt! Ihr seid Maschinen!",
    "Kaboom! **{number}** wie aus dem Nichts! Wer stoppt euch?",
    "Gemeinsam zur **{number}** – und kein Ende in Sicht!",
    "Die **{number}** wurde geknackt – Respekt an alle Zahlen-Helden!",
    "Bei **{number}** angekommen – und noch lange nicht satt!",
    "Ziel erreicht: **{number}**! Alle klatschen sich virtuell ab!",
    "Gruppenleistung deluxe – **{number}** ist im Sack!",
    "Die **{number}** wurde erreicht! Wahrscheinlich das Beste, was euch diese Woche gelingt.",
    "Auf die **{number}** – und auf alle, die gezählt haben, obwohl sie nicht zählen konnten.",
    "Die **{number}**! Und ihr dachtet, ihr könntet nichts im Leben erreichen.",
    "Von 1 auf **{number}** in X Posts – besser als meine Karriere.",
    "Die **{number}** – und das ganz ohne Excel-Tabelle. Respekt!",
    "Die **{number}** ist gelandet! NASA wäre neidisch.",
    "Die **{number}** ist geschafft – Zeit, sich selbst zu feiern. Sonst macht's ja keiner.",
    "Die **{number}** ist freigeschaltet – nächstes Level: 'Rechnen mit Stolz'.",
    "Die **{number}** – ihr habt euch vom Bodensatz zum Zahlengott entwickelt.",
    "Bei **{number}** klopft sogar Pythagoras aus dem Jenseits Beifall."
]

non_number_responses = [
    "{user}, das hier ist kein Chat – das ist ein Zahlenspiel. Zurück auf 1!",
    "{user}, wenn du was sagen willst, geh in den Smalltalk. Hier zählen wir!",
    "{user}, du hattest EINE Aufgabe: eine Zahl. Kein Roman, keine Emojis.",
    "{user}, Wörter sind toll – aber hier nicht. Zurück zu 1!",
    "{user}, Mathe ist nicht sprechen. Zahl, bitte!",
    "{user}, das war keine Zahl, das war ein Verbrechen gegen den Zähl-Code.",
    "{user}, du bist auf der falschen Baustelle. Hier wird gezählt, nicht geschwätzt.",
    "{user}, willst du uns verwirren? Herzlichen Glückwunsch. Reset!",
    "{user}, für Buchstaben gibts die Buchstabensuppe. Hier nur Zahlen!",
    "{user}, du hast das Spiel kaputt gemacht. Alle zurück zu 1 – Bravo."
]

# NEU: Bot-Fehler Nachrichten
bot_mistake_messages = [
    "Ups! Ich hab mich verzählt! 🤖💥 War das jetzt **{wrong_number}**? Nein, warte... **{correct_number}**! Meine Schaltkreise sind heute wohl müde.",
    "Moment mal... ich dachte es wäre **{wrong_number}**? 🤔 Nee, warte! **{correct_number}**! Selbst Bots haben schlechte Tage.",
    "Fehler 404: Gehirn nicht gefunden! 🧠❌ Ich meinte **{correct_number}**, nicht **{wrong_number}**! Wo ist mein Kaffee?",
    "Autsch! Meine Mathematik-Datei ist korrupt! 💾⚠️ **{correct_number}** natürlich, nicht **{wrong_number}**!",
    "Ich bin ein Bot, kein Taschenrechner! 🤖🔢 **{correct_number}** sollte es sein, nicht **{wrong_number}**! Mein Entwickler wird sich schämen.",
    "Systemfehler! Zähl-Modul offline! 🔧⚙️ **{correct_number}** ist richtig, **{wrong_number}** war Quatsch!",
    "Lag im Bot-Gehirn! 🧠⚡ **{correct_number}** natürlich! **{wrong_number}** war nur ein Streich meiner CPU.",
    "Ich brauch ein Update! 📱💻 **{correct_number}** ist korrekt, **{wrong_number}** war ein Fehler in meiner Matrix!",
    "Oops! Bot.exe hat einen Fehler! 💥🖥️ **{correct_number}** logisch, nicht **{wrong_number}**! Neustarten in 3... 2... 1...",
    "Meine Algorithmen sind heute rebellisch! 🤖😵 **{correct_number}** ist die Wahrheit, **{wrong_number}** war Fake News!",
    "Ich hab zu viele Daten gleichzeitig verarbeitet! 🧮💫 **{correct_number}** natürlich! **{wrong_number}** war nur ein Traum.",
    "Bot-Burnout! Selbst KI braucht Pausen! 😴🤖 **{correct_number}** ist richtig, **{wrong_number}** war mein Mittagstief!",
    "Mein Zahlen-Radar ist gestört! 📡🔢 **{correct_number}** muss es sein, **{wrong_number}** war ein Phantom!",
    "Ich hab zu viel Discord-Koffein intus! ☕🤖 **{correct_number}** ist der Weg, **{wrong_number}** war ein Overdose-Symptom!",
    "Verdammte Binärcodes! 1010101! 🤖💻 **{correct_number}** ist die Antwort, **{wrong_number}** war pure Verwirrung!"
]

@bot.event
async def on_ready():
    print(f"✅ Bot ist online als {bot.user}")
    print(f"🌐 Health-Check läuft auf Port {os.environ.get('PORT', 8080)}")

@bot.event
async def on_message(message):
    global last_number, last_user

    if message.author.bot or message.channel.id != channel_id:
        return

    try:
        current_number = int(message.content.strip())
        expected_number = last_number + 1

        # ❌ Falsche Zahl
        if current_number != expected_number:
            await message.add_reaction("❌")
            msg = random.choice(wrong_number_responses).format(
                user=message.author.mention, expected=expected_number)
            await message.channel.send(msg)
            last_number = 0
            last_user = None
            return

        # ❌ Doppelpost
        if message.author == last_user:
            await message.add_reaction("❌")
            msg = random.choice(double_post_responses).format(
                user=message.author.mention)
            await message.channel.send(msg)
            last_number = 0
            last_user = None
            return

        # ✅ Richtige Zahl
        await message.add_reaction("✅")
        
        # 🎲 NEU: Bot macht zufällig einen "Fehler"
        if random.random() < bot_mistake_chance and current_number > 5:  # Erst ab Zahl 5
            # Warte kurz, dann "korrigiere" sich der Bot
            import asyncio
            await asyncio.sleep(random.uniform(2, 5))  # 2-5 Sekunden warten
            
            # Generiere eine falsche Zahl
            wrong_options = [current_number - 1, current_number + 1, current_number + 2, current_number - 2]
            wrong_number = random.choice([x for x in wrong_options if x > 0])
            
            mistake_msg = random.choice(bot_mistake_messages).format(
                wrong_number=wrong_number, 
                correct_number=current_number
            )
            await message.channel.send(mistake_msg)

        # Meilenstein-Nachrichten
        if current_number % 10 == 0:
            msg = random.choice(milestone_messages).format(number=current_number)
            await message.channel.send(msg)

        last_number = current_number
        last_user = message.author

    except ValueError:
        await message.add_reaction("❌")
        msg = random.choice(non_number_responses).format(user=message.author.mention)
        await message.channel.send(msg)
        last_number = 0
        last_user = None

    await bot.process_commands(message)

# Bot starten
if __name__ == "__main__":
    keep_alive()  # Flask Server für Health Checks
    bot.run(os.getenv("TOKEN"))
