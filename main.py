import config
import telebot
import psycopg2

# the main bot instance
bot = telebot.TeleBot(config.TOKEN)

# database table name
_TABLE='am2302.t_am2302'

def connect():
    return psycopg2.connect(config.DB_PARAMS)

class DbTemp:
    def __init__(self, date, temperature, humidity):
        self.date = date
        self.temperature = temperature
        self.humidity = humidity

def _last(db):
    with db.cursor() as cur:
        cur.execute(f'''
            select
                date,
                temperature,
                humidity
            from
                {_TABLE}
            order by
                date desc
            limit 1
            ''')
        row = cur.fetchone()
        if row:
            return DbTemp(*row)

#
# Commands
#

@bot.message_handler(commands=['current'])
def send_last(message):
    with connect() as db:
        l = _last(db)
        bot.reply_to(message,
            f'Aktuell {l.temperature}°C und {l.humidity}% Luftfeuchtigkeit. (Stand: {l.date})')


# run main
bot.polling()
