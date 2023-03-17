import argparse

from entsoee import Entsoee
from helen import Helen
from db import ElectricityDatabase


def init_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', nargs=1, help='sqlite3 filename', default='prices.sqlite3')
    parser.add_argument('--apikey', nargs=1,help='Entsoe rest api-key', required=True)
    parser.add_argument('--username', nargs=1,help='Helen username', required=True)
    parser.add_argument('--password', nargs=1,help='Helen password', required=True)
    parser.add_argument('--country', nargs=1,help='Entsoe country code',default="FI")
    parser.add_argument('--tz', nargs=1,help='Entsoe timezone',default="Europe/Helsinki")
    args = parser.parse_args()
    return args

def main():
    args = init_parser()

    db = ElectricityDatabase(args.db)
    Entsoee(database=db,api_key=args.apikey[0],country=args.country, tz=args.tz)    
    Helen(db, args.username[0], args.password[0])
    db.close()

if __name__ == "__main__":
    main()


