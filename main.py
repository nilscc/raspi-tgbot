import telegram
import telegram.ext
import psycopg2

# local config
import config

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

def temp(update, context):
    with connect() as db:
        l = _last(db)
        update.message.reply_text(
            f'Aktuell {l.temperature}°C und {l.humidity}% Luftfeuchtigkeit. (Stand: {l.date})'
        )

#
# Main
#

if __name__ == '__main__':

    # the main bot instance
    bot = telegram.ext.Updater(token=config.TOKEN)
    
    # commands
    bot.dispatcher.add_handler(telegram.ext.CommandHandler('temp', temp))
    
    # main event loop
    bot.start_polling()
    bot.idle()
