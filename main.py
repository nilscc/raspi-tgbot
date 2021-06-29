# set locale from environment
import locale
locale.setlocale(locale.LC_ALL, '')

import telegram
import telegram.ext
import psycopg2

import bme280.i2c

# local config
import config
import plots

# database table name
_TABLE='bme280.t_bme280'

def connect():
    return psycopg2.connect(config.DB_PARAMS)

class DbTemp:
    def __init__(self, date, temperature, humidity, pressure):
        self.date = date
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure

def _history(db, limit=None):
    with db.cursor() as cur:
        cur.execute(f'''
            select
                date,
                temperature,
                humidity,
                pressure
            from
                {_TABLE}
            order by
                date desc
            limit %s
            ''',
            (limit,))
        return list(cur.fetchall())

def _current():
    _i2c = bme280.i2c.i2c()
    _i2c.open()
    _i2c.runForcedMode()
    return _i2c

#
# Commands
#

def temp(update, context):
    cur = _current()
    with connect() as db:
        fig = plots.temp_history(_history(db, limit=60*12))
    update.message.reply_photo(
        photo = plots.to_bytes(fig),
        caption = f'{cur.temperature:.2f}°C\n'
            f'{cur.pressure / 100 :.2f}hPa\n'
            f'{cur.humidity:.2f}% Luftfeuchtigkeit',
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
