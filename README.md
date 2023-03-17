## Description

Fetches nordpool day ahead prices from Entsoe rest api and own electricity consumption data from helen.fi using Selenium(geckodriver). Fetched data inserted and/or updated into sqlite database. 

get costs grouped by month:

   select STRFTIME("%Y-%m",date) as mdate,sum(kwh),sum((price*1.1*kwh)+(kwh*7.68))/100 from electricity group by mdate order by mdate;

## Notes

- Selenium firefox profile download location and its directory doesn't get created automatically.
- Waiting for content is a bit iffy