import sys
from datetime import datetime, timedelta

import httpx
import asyncio
import platform


class HttpError(Exception):
    pass


async def request(url: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        # test = await client.get('https://www.google.com')
        # print(test.text)
        if r.status_code == 200:
            result = r.json()
            return result
        else:
            raise HttpError(f"Error status: {r.status_code} for {url}")

def extract_currency_rates(data, currencies):
    rates = {}
    for rate in data.get('exchangeRate', []):
        if rate['currency'] in currencies:
            rates[rate['currency']] = {
                'sale': rate.get('saleRate'),
                'purchase': rate.get('purchaseRate')
            }
    return rates

async def main(index_day: int):
    # d = datetime.now() - timedelta(day=2) -> d.strftime("%d.%m.%Y")
    for i in range(int(index_day)):
        d = datetime.now() - timedelta(days=int(index_day))
        shift = d.strftime("%d.%m.%Y")
        try:
            response = await request(f'https://api.privatbank.ua/p24api/exchange_rates?date={shift}')
            rate_usd = extract_currency_rates(response, ['USD'])
            rate_eur = extract_currency_rates(response, ['EUR'])
            return rate_usd, rate_eur
        except HttpError as err:
            print(err)
            return None


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print(sys.argv)
    r = asyncio.run(main(sys.argv[1]))
    print(r)