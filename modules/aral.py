from dataclasses import dataclass, asdict
from typing import Optional
from urllib.request import urlopen
from datetime import datetime, timezone
import json

import psycopg2

__API_URL__ = 'https://api.tankstelle.aral.de/api/v2/stations/{station_id}/prices'

@dataclass
class on_conflict:
    action: str

def do_nothing(): return on_conflict('do nothing')

class db_object:
    def insert(self, database,
            on_conflict: Optional[on_conflict] = None,
            ):

        # build data tuples
        dct = { k:v for k,v in asdict(self).items() if v is not None }
        fields = ', '.join(dct.keys())
        data = tuple(dct.values())
        values = ', '.join('%s' for _ in data)

        # handle on conflict
        if on_conflict is not None:
            on_conflict = 'on conflict ' + on_conflict.action
        else:
            on_conflict = ''

        with database.cursor() as cur:
            cur.execute(f'''
                insert into
                    {self.table()}
                    ({ fields })
                values
                    ({ values })
                { on_conflict }
                returning id
                ''', data)
            r = cur.fetchone()
            if r:
                self.id, = r

    @classmethod
    def by_id(cls, database, id):
        with database.cursor() as cur:
            cur.execute(f'select * from {cls.table()} where id = %s', (id,))
            r = cur.fetchone()
            if r:
                return cls(*r)

    @classmethod
    def by_api_key(cls, database, api_key):
        with database.cursor() as cur:
            cur.execute(f'select * from {cls.table()} where api_key = %s', (api_key,))
            r = cur.fetchone()
            if r:
                return cls(*r)

    @classmethod
    def all(cls, database):
        with database.cursor() as cur:
            cur.execute(f'select * from {cls.table()}')
            return [ cls(*r) for r in cur.fetchall() ]

@dataclass
class station (db_object):
    @staticmethod
    def table(): return 'tgbot_2203.t_aral_stations'

    id: Optional[int]
    api_key: int
    name: str

    def update_prices(self, database, verbose=True):
        with urlopen(__API_URL__.format(station_id=self.api_key)) as response:
            if verbose:
                limit = response.headers['x-ratelimit-limit']
                remaining = response.headers['x-ratelimit-remaining']
                print(f'Ratelimit: {remaining} of {limit} remaining.')

            data = json.loads(response.read())
            for p in data['data']:

                f = fuel.by_api_key(database, p['aral_id'])
                if f is None:
                    f = fuel(None, p['aral_id'], p['name'])
                    f.insert(database)

                p = price(None, self.id, f.id,
                        convert_api_time(p['price']['valid_from']),
                        p['price']['price'])

                p.insert(database, on_conflict=do_nothing())

    def most_recent_prices(self, database):
        __VIEW__ = 'tgbot_2203.v_aral_prices_most_recent_by_fuel'

        assert self.id is not None

        with database.cursor() as cur:
            cur.execute(f'select * from {__VIEW__} where station_id = %s', (self.id,))
            return [ price(*r) for r in cur.fetchall() ]

@dataclass
class fuel (db_object):
    @staticmethod
    def table(): return 'tgbot_2203.t_aral_fuels'

    id: Optional[int]
    api_key: int
    name: str

@dataclass
class price (db_object):
    @staticmethod
    def table(): return 'tgbot_2203.t_aral_prices'

    id: Optional[int]
    station_id: int
    fuel_id: int
    valid_from: datetime
    price: float

    def fuel(self, database):
        return fuel.by_id(database, self.fuel_id)

    def station(self, database):
        return station.by_id(database, self.station_id)

def convert_api_time(s: str):
    '''Convert time from API ISO UTC string to local timestamp with time zone.'''
    return datetime \
        .fromisoformat(s) \
        .replace(tzinfo=timezone.utc) \
        .astimezone()







@dataclass
class fuel_price:
    station_id: int
    api_key: str
    name: str
    price: float
    valid_from: datetime

    def insert(self, database):
        pass

def get_prices(url: str, verbose=True):
    with urlopen(url) as response:
        if verbose:
            limit = response.headers['x-ratelimit-limit']
            remaining = response.headers['x-ratelimit-remaining']
            print(f'Ratelimit: {remaining} of {limit} remaining.')

        data = json.loads(response.read())
        for p in data['data']:


            yield fuel_price(
                p['aral_id'],
                p['name'],
                p['price']['price'],
                convert_time(p['price']['valid_from']),
                )

if __name__ == '__main__':

    __URL = 'https://api.tankstelle.aral.de/api/v2/stations/15032600/prices'

    with psycopg2.connect('') as db:
        #s = station(id=None, api_key=15032600, name='Aral Renning')
        #s.insert(db, on_conflict=do_nothing())
        #print(s.id, s.name)

        # for s in station.all(db):
        #     s = station.by_id(db, 1)
        #     print(s.id, s.name)

        s = station.by_api_key(db, 15032600)
        print(s.id, s.name)

        #s.update_prices(db)

        for p in s.prices(db):
            f = p.fuel(db)
            print(f'{f.name}: {p.price}')

    #for p in get_prices(__URL):
        #print(f'{p.name}: {p.price} ({p.valid_from.time()})')
