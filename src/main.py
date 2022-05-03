import asyncio
import matplotlib.pyplot as plt
from api import Api

async def main():
    # From polkaswap.io
    ASSET_ADDRESSES = {
        'xor': '0x0200000000000000000000000000000000000000000000000000000000000000',
        'val': '0x0200040000000000000000000000000000000000000000000000000000000000',
        'pswap': '0x0200050000000000000000000000000000000000000000000000000000000000',
        'dai': '0x0200060000000000000000000000000000000000000000000000000000000000',
        'eth': '0x0200070000000000000000000000000000000000000000000000000000000000',
        'xstusd': '0x0200080000000000000000000000000000000000000000000000000000000000',
    }

    SWAP_PAIRS = [
        ['xor', 'eth'], ['xor', 'dai'],
        ['val', 'eth'], ['val', 'dai'],
        ['xstusd', 'eth'], ['xstusd', 'dai'],
        ['pswap', 'eth'], ['pswap', 'dai'],
    ]

    # Values on x axis in $
    X_VALUES = [
        10, 25, 50, 75, 100,
        150, 200, 250, 300, 400, 500, 700, 1000,
        2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10_000,
    ]

    all_y_values = []
    api = Api()
    try:
        await api.ws_connect()

        # Currencies in $
        asset_currencies = {}
        for asset, address in ASSET_ADDRESSES.items():
            asset_currencies[asset] = api.get_usd_currency(address)

        print('Currencies:')
        for asset, currency in asset_currencies.items():
            print(f'{asset.upper()}: ${currency}')

        xlim, ylim = plt.xlim(), plt.ylim()
        for pair in SWAP_PAIRS:
            y_values = []
            asset_from = ASSET_ADDRESSES[pair[0]]
            asset_to = ASSET_ADDRESSES[pair[1]]
            for amount in X_VALUES:
                amount_in_crypto = amount / asset_currencies[pair[0]]
                swapped_amount_in_crypto = await api.get_swap_currency(
                    asset_from, asset_to, amount_in_crypto
                )
                swapped_amount = swapped_amount_in_crypto * asset_currencies[pair[1]]
                y_values.append(swapped_amount)
                # Drawing dotted line
                plt.plot(
                    [amount, amount, xlim[0]],
                    [ylim[0], swapped_amount, swapped_amount],
                    linestyle='--'
                )
            all_y_values.extend(y_values)
            plt.plot(X_VALUES, y_values, label=f'{pair[0].upper()}―{pair[1].upper()}')
    finally:
        await api.ws_close()

    plt.xlabel("To swap, $")
    plt.xticks(X_VALUES)
    plt.ylabel("To receive, $")
    plt.yticks(all_y_values)
    plt.legend(loc='right')
    plt.show()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
