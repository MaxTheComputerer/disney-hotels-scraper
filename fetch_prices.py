from datetime import date, timedelta
import json
import requests
from lxml import html

def get_cookies():
    session = requests.session()
    session.post("https://www.disneypackages.co.uk/?DHredirect=DisneyPackages")
    return session

"""
holiday_type can be "Hotel" for hotels only, or "Package" for hotels and tickets
But only the hotel prices are downloaded
"""
def get_prices(session, day, month, year, holiday_type="Hotel", nights=1, adults=2, children=0, flights_from="LON", flights_to="MCO", flights_cabin="Economy"):
    url = "https://www.disneyholidays.co.uk/walt-disney-world/"

    payload=f'holiday={holiday_type}&day={day}&month={month}%5E{year}&nights={nights}&adults={adults}&children={children}&flights-from={flights_from}&flights-to={flights_to}&flights-cabin={flights_cabin}&package-category=ALL&hotel-category=ALL'
    headers = {
    'authority': 'www.disneyholidays.co.uk',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'cache-control': 'max-age=0',
    'content-type': 'application/x-www-form-urlencoded'
    }

    response = session.post(url, headers=headers, data=payload)
    tree = html.fromstring(response.content)

    hotel_names = tree.xpath('//*[contains(@class, "accommodation")]//h2/text()')
    hotel_prices = [int(p.replace(',', '')) for p in tree.xpath('//*[contains(@class, "accommodation")]//span[@class="pounds"]/text()')]
    return dict(zip(hotel_names, hotel_prices))


if __name__ == "__main__":
    session = get_cookies()

    dates = {}
    current_date = date(2023, 1, 1)
    end_date = date(2024, 1, 1)
    delta = timedelta(days=1)

    while current_date < end_date:
        print('Fetching ' + current_date.strftime("%m-%d") + '...', end='', flush=True)
        prices = get_prices(session, current_date.day, current_date.month, current_date.year)
        dates[current_date.strftime("%m-%d")] = prices
        current_date += delta
        print('Done')

    print('Writing to JSON...', end='', flush=True)
    with open(f'disney_hotel_prices_{date.today().isoformat()}.json', 'w') as file:
        json.dump(dates, file, indent=6)
    print('Done')
