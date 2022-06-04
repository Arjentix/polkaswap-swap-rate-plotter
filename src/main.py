import asyncio
import matplotlib.pyplot as plt
from labellines import labelLines

from api import Api

# From polkaswap.io
ASSET_ADDRESSES = {
    'xor': '0x0200000000000000000000000000000000000000000000000000000000000000',
    'val': '0x0200040000000000000000000000000000000000000000000000000000000000',
    'pswap': '0x0200050000000000000000000000000000000000000000000000000000000000',
    'dai': '0x0200060000000000000000000000000000000000000000000000000000000000',
    'eth': '0x0200070000000000000000000000000000000000000000000000000000000000',
    'xstusd': '0x0200080000000000000000000000000000000000000000000000000000000000',
    'noir': '0x0044aee0776cfb826434af8ef0f8e2c7e9e6644cfda0ae0f02c471b1eebc2483',
    'usdc': '0x00ef6658f79d8b560f77b7b20a5d7822f5bc22539c7b4056128258e5829da517',
}

SWAP_PAIRS = [
    ['xor', 'eth'], ['xor', 'dai'], ['xor', 'usdc'],
    ['val', 'eth'], ['val', 'dai'], ['val', 'usdc'],
    ['xstusd', 'eth'], ['xstusd', 'dai'], ['xstusd', 'usdc'],
    ['pswap', 'eth'], ['pswap', 'dai'], ['pswap', 'usdc'],
    ['noir', 'eth'], ['noir', 'dai'], ['noir', 'usdc'],
]

# Values on x axis in $
X_VALUES = [
    10, 25, 50, 75, 100,
    150, 200, 250, 300, 400, 500, 700, 1000,
    2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10_000,
]

async def main():
    fig = plt.figure()
    fig.canvas.manager.set_window_title('Swap rate')
    ax = fig.subplots()

    all_y_values = []
    api = Api()
    xlim, ylim = plt.xlim(), plt.ylim()
    try:
        await api.ws_connect()

        # Currencies in $
        asset_currencies = {}
        for asset, address in ASSET_ADDRESSES.items():
            asset_currencies[asset] = api.get_usd_currency(address)

        print('Currencies:')
        for asset, currency in asset_currencies.items():
            print(f'{asset.upper()}: ${currency}')
        print()

        tasks = [draw_pair(ax, pair, xlim, ylim, api, asset_currencies) for pair in SWAP_PAIRS]
        for y_values in await asyncio.gather(*tasks):
            all_y_values.extend(y_values)
    finally:
        await api.ws_close()

    # Drawing labels
    for x in X_VALUES:
        lines_num = len(SWAP_PAIRS)
        x_min = max(min(X_VALUES), x - lines_num * 10)
        labelLines(xvals=(x_min, x), align=False, color='k')

    plt.xlabel('To swap, $')
    plt.xticks(X_VALUES)
    plt.ylabel('To receive, $')
    plt.yticks(all_y_values)
    plt.legend(loc='right')
    plt.show()

async def draw_pair(ax, pair, xlim, ylim, api, asset_currencies):
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
        ax.plot(
            [amount, amount, xlim[0]],
            [ylim[0], swapped_amount, swapped_amount],
            linestyle='--'
        )
    ax.plot(X_VALUES, y_values, label=f'{pair[0].upper()}―{pair[1].upper()}')
    return y_values

if __name__ == '__main__':
    asyncio.run(main())
