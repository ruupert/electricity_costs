import argparse

from entsoee import Entsoee
from helen import Helen
from db import ElectricityDatabase


def init_parser():
    p = argparse.ArgumentParser()
    p.add_argument("--db", nargs=1, help="sqlite3 filename", default="prices.sqlite3")
    p.add_argument("--apikey", nargs=1, help="Entsoe rest api-key", required=True)
    p.add_argument("--username", nargs=1, help="Helen username", required=True)
    p.add_argument("--password", nargs=1, help="Helen password", required=True)
    p.add_argument("--country", nargs=1, help="Entsoe country code", default="FI")
    p.add_argument("--tz", nargs=1, help="Entsoe timezone", default="Europe/Helsinki")
    args = p.parse_args()
    return args

def main():
    args = init_parser()
    db = ElectricityDatabase(args.db)
    Entsoee(database=db, api_key=args.apikey[0], country=args.country, tz=args.tz)
    Helen(db, args.username[0], args.password[0])
    db.close()

if __name__ == "__main__":
    main()