# set locale from environment
import locale
locale.setlocale(locale.LC_ALL, '')

import telegram
import telegram.ext
import psycopg2

import bme280.i2c

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

def _history(db, limit=None):
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
            limit %s
            ''',
            (limit,))
        return list(cur.fetchall())

#
# Commands
#

def temp(update, context):
    _i2c = bme280.i2c.i2c()
    _i2c.open()
    _i2c.runForcedMode()
    update.message.reply_text(
        f'{_i2c.temperature:.2f}°C\n'
        f'{_i2c.pressure / 100 :.2f}hPa\n'
        f'{_i2c.humidity:.2f}% Luftfeuchtigkeit'
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
