import argparse
import logging
import yaml

from db import ElectricityDatabaseSQ
from psqldb import ElectricityDatabasePG
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
    p.add_argument("--psql-user", help="", default=None)
    p.add_argument("--psql-pass", help="", default=None)
    p.add_argument("--psql-host", help="", default=None)
    p.add_argument("--psql-db", help="", default=None)    
    p.add_argument("--db", nargs=1, help="sqlite3 filename", default="prices.sqlite3")
    p.add_argument("--apikey", nargs=1, help="Entsoe rest api-key (required if no config file)")
    p.add_argument("--username", nargs=1, help="Helen username (required if no config file)")
    p.add_argument("--password", nargs=1, help="Helen password (required if no config file)")
    p.add_argument("--country", nargs=1, help="Entsoe country code", default="FI")
    p.add_argument("--tz", nargs=1, help="Entsoe timezone", default="Europe/Helsinki")
    p.add_argument("--start", nargs=1, help="Optional start date YYYY-MM-DD", default=None)
    p.add_argument("--delivery-site", help="alternate helen usage fetch", default=None)
    p.add_argument("--config", help="Yaml config", default=None)
    p.add_argument('-v', action='count', default=0)
    return p.parse_args()

@LogDecorator()
def main():
    args = init_parser()
    init_logger(get_log_level(args.v))

    if args.config:
        with open(args.config, "r") as s:
            try:
                conf = yaml.safe_load(s)
                psql_db=conf['psql_db']
                psql_user=conf['psql_user']
                psql_pass=conf['psql_pass']
                psql_host=conf['psql_host']
                apikey = conf['apikey']
                country = args.country
                tz = args.tz
                start_date = None
                username = conf['username']
                password = conf['password']
                verbose = args.v
                delivery_site = conf['delivery_site']
            except yaml.YAMLError as ex:
                print(ex)
    else: 
        psql_db=args.psql_db
        psql_user=args.psql_user
        psql_pass=args.psql_pass
        psql_host=args.psql_host
        apikey = args.apikey[0]
        country = args.country
        tz = args.tz
        start_date = args.start
        username = args.username[0]
        password = args.password[0]
        verbose = args.v
        delivery_site = args.delivery_site
    if psql_db is not None:
        db =  ElectricityDatabasePG(psql_db, psql_user, psql_pass, psql_host)
    else:
        db = ElectricityDatabaseSQ(args.db)
    Entsoee(database=db, api_key=apikey, country=country, tz=tz, start_date=start_date)
    Helen(database=db, username=username, password=password, start_date=start_date,verbose=verbose, tz=tz, delivery_site_id=delivery_site)
    db.close()

if __name__ == "__main__":
    main()
