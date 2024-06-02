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

async def main(days):
    results = []
    for i in range(int(days)):
        d = datetime.now() - timedelta(days=i)
        date_str = d.strftime("%d.%m.%Y")
        try:
            response = await request(f'https://api.privatbank.ua/p24api/exchange_rates?date={date_str}')
            rates = extract_currency_rates(response, ['USD', 'EUR'])
            if rates:
                results.append({date_str: rates})
        except HttpError as err:
            print(err)
            return None
    return results

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: main.py <days>")
        sys.exit(1)

    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        days = int(sys.argv[1])
        if not 1 <= days <= 10:
            raise ValueError("Days must be between 1 and 10")
    except ValueError as e:
        print(e)
        sys.exit(1)

    results = asyncio.run(main(days))
    print(results)