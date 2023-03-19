import argparse
import logging

from db import ElectricityDatabase
from decorator import LogDecorator
from entsoee import Entsoee
from helen import Helen

def get_log_level(v):
    if v == 0:
        return logging.INFO
    if v > 0: # for now
        return logging.DEBUG

def init_logger(log_level):

    logger = logging.getLogger('electricity')
    logger.setLevel(log_level)
    c = logging.StreamHandler()
    c.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c.setFormatter(formatter)
    logger.addHandler(c)

def init_parser():
    p = argparse.ArgumentParser()
    p.add_argument("--db", nargs=1, help="sqlite3 filename", default="prices.sqlite3")
    p.add_argument("--apikey", nargs=1, help="Entsoe rest api-key", required=True)
    p.add_argument("--username", nargs=1, help="Helen username", required=True)
    p.add_argument("--password", nargs=1, help="Helen password", required=True)
    p.add_argument("--country", nargs=1, help="Entsoe country code", default="FI")
    p.add_argument("--tz", nargs=1, help="Entsoe timezone", default="Europe/Helsinki")
    p.add_argument("--start", nargs=1, help="Optional start date YYYY-MM-DD", default=None)
    p.add_argument("--delivery-site", help="alternate helen usage fetch", default=None)
    p.add_argument('-v', action='count', default=0)
    return p.parse_args()

@LogDecorator()
def main(args):
    db = ElectricityDatabase(args.db)
    Entsoee(database=db, api_key=args.apikey[0], country=args.country, tz=args.tz, start_date=args.start)
    Helen(database=db, username=args.username[0], password=args.password[0], start_date=args.start,verbose=args.v, tz=args.tz, delivery_site_id=args.delivery_site)
    db.close()

if __name__ == "__main__":
    args = init_parser()
    init_logger(get_log_level(args.v))
    main(args)