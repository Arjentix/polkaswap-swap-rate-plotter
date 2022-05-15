import requests
from jsonrpc_websocket import Server

class Api:
    def __init__(self):
        # Send POST queries until all pages are retrieved
        body = {
            'query': '\n'
                     'query PoolXYKEntities (\n'
                     '  $first: Int = 1,\n'
                     '  $orderBy: [PoolXykEntitiesOrderBy!] = UPDATED_DESC\n'
                     '  $filter: PoolXYKEntityFilter\n'
                     '  $poolsAfter: Cursor = \"\"\n'
                     '  $poolsFirst: Int = 100)\n'
                     '{\n'
                     '  poolXYKEntities (\n'
                     '    first: $first\n'
                     '    orderBy: $orderBy\n'
                     '    filter: $filter\n'
                     '  )\n'
                     '  {\n'
                     '    nodes {\n'
                     '      id\n'
                     '      pools (\n'
                     '        first: $poolsFirst\n'
                     '        after: $poolsAfter\n'
                     '      ) {\n'
                     '        pageInfo {\n'
                     '          hasNextPage\n'
                     '          endCursor\n'
                     '        }\n'
                     '       nodes {\n'
                     '          targetAssetId,\n'
                     '          priceUSD,\n'
                     '        }\n'
                     '      }\n'
                     '    }\n'
                     '  }\n'
                     '}\n',
            'variables': {
                'poolsAfter': ''
            }
        }

        self._currencies = {}

        i = 1
        hasNextPage = True
        while hasNextPage:
            print(f'Receiving currencies page #{i}')
            response = requests.post(
                url='https://api.subquery.network/sq/sora-xor/sora',
                json=body,
            ).json()

            pools = response['data']['poolXYKEntities']['nodes'][0]['pools']
            for node in pools['nodes']:
                self._currencies[node["targetAssetId"]] = float(node['priceUSD'])

            pageInfo = pools['pageInfo']
            hasNextPage = pageInfo['hasNextPage']
            body['variables']['poolsAfter'] = pageInfo['endCursor']
            i += 1
        print()
        self._server = Server("wss://ws.mof.sora.org")

    async def ws_connect(self):
        await self._server.ws_connect()

    async def ws_close(self):
        await self._server.close()

    def get_usd_currency(self, address):
        return self._currencies[address]

    async def get_swap_currency(self, asset_from, asset_to, amount):
        DIMENSION = 10 ** 18

        dex_id = 0
        amount = int(amount * DIMENSION)
        swap_variant = 'WithDesiredInput'
        selected_source_types = ['XYKPool']
        filter_mode = 'Disabled'
        res = await self._server.liquidityProxy_quote(
            dex_id,
            asset_from,
            asset_to,
            str(amount),
            swap_variant,
            selected_source_types,
            filter_mode
        )
        return int(res['amount']) / DIMENSION
