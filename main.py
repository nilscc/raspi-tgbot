# set locale from environment
import locale
locale.setlocale(locale.LC_ALL, '')

import telegram
import telegram.ext
import psycopg2
import logging

import bme280.i2c

# local config
import config
import modules.plots
from modules.heat_index import heat_index

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
        return list(DbTemp(*row) for row in cur.fetchall())

def _last(db):
    return _history(db, limit=1)[0]

#
# Commands
#

def weather(update: telegram.Update, context: telegram.ext.CallbackContext, hours: int = 12):
    with connect() as db:
        cur = _last(db)
        fig = modules.plots.temp_history(_history(db, limit=60*hours))

    # calculate heat index
    hi = ''
    if cur.temperature >= 27.0 and cur.humidity >= 40.0:
        hi = f'(gefühlt {heat_index(cur.temperature, cur.humidity):.1f}°C) '
        
    # send formatted response
    update.message.reply_photo(
        photo = modules.plots.to_bytes(fig),
        caption =
            f'Aktuell: {cur.temperature:.1f}°C {hi}/ {cur.pressure / 100 :.1f}hPa / {cur.humidity:.1f}% rF\n'
            f'Stand: {cur.date:%X}',
    )

    modules.plots.close(fig)

def weather24(update: telegram.Update, context: telegram.ext.CallbackContext):
    weather(update, context, hours=24)

def weather72(update: telegram.Update, context: telegram.ext.CallbackContext):
    weather(update, context, hours=72)

# Aral Module

import modules.aral

def aral(update: telegram.Update, context: telegram.ext.CallbackContext):
    l = []
    with connect() as db:
        s = modules.aral.station.by_id(db, 1)
        s.update_prices(db)

        for i,p in enumerate(s.most_recent_prices(db)):
            f = p.fuel(db)
            l.append(f'`  {p.price}  ` *{f.name}* ({p.valid_from.strftime("%X, %x")})')

    l = '\n'.join(l)
    update.message.reply_markdown(f'{s.name}: \n{l}')

#
# Main
#

if __name__ == '__main__':

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

    # the main bot instance
    bot = telegram.ext.Updater(token=config.TOKEN)
    
    # commands
    bot.dispatcher.add_handler(telegram.ext.CommandHandler('weather', weather))
    bot.dispatcher.add_handler(telegram.ext.CommandHandler('weather24', weather24))
    bot.dispatcher.add_handler(telegram.ext.CommandHandler('weather72', weather72))

    bot.dispatcher.add_handler(telegram.ext.CommandHandler('aral', aral))

    # main event loop
    bot.start_polling()
    bot.idle()
