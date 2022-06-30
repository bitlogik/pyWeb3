# pyweb3

### A Web3 RPC client for Ethereum compatible wallets in Python

A Python3 library to query Web3 calls to Ethereum compatible nodes from a Python wallet. This library connects a Python wallet to a blockchain node, using [the JSON-RPC node API standard](https://ethereum.org/en/developers/docs/apis/json-rpc/).

A software application can interact with the Ethereum blockchain using an Ethereum node. For this purpose, every Ethereum client implements a JSON-RPC specification, so there is a uniform set of methods that applications can rely on. JSON-RPC is a stateless, light-weight remote procedure call (RPC) protocol. Primarily the specification defines several data structures and the rules around their processing. It is transport agnostic in that the concepts can be used within the same process, over WebSocket or over HTTP. It uses JSON (RFC 4627) as data format.

pyWeb3 is compatible with the Ethereum nodes blockchain, and all the compatible derivatives such as Polygon, BSC, Arbitrum.

pyWeb3 doesn't handle the computation of the "hex" calls from functions, nor data format packing, nor decoding of the response data. Except for *get_balance*, *get_tx_num* and *get_tx_num* which decode to an integer. These parts must be done by the aplication using pyWeb3.

pyWeb3 manages automatically on its own all the Web3 RPC stack :

```
Web3 client
    |
 JSON-RPC
    |
WebSocket or HTTP
    |
   TLS
    |
  Socket
```

## Installation and requirements

Works with Python >= 3.6.

### Installation of this library

Easiest way :  
`python3 -m pip install pyweb3`  

From sources, download and run in this directory :  
`python3 -m pip  install .`

The only dependency is the [wsproto](https://pypi.org/project/wsproto/) v1.0.0 library.

### Use

Instanciate with `pyweb3.Web3Client`, then use methods of this object to send RPC queries.

Basic example :

```python
from pyweb3 import Web3Client

# Get Token0 address of the ETH/USDT SushiSwap AMM pair on Polygon
amm_pair_contract = "0xc2755915a85c6f6c1c0f3a86ac8c058f11caa9c9"
token0Call = "0dfe1681"  # Keccak256( "token0()" )

rpc_api = Web3Client("https://matic-mainnet.chainstacklabs.com")

# Get token0 address of the pair : WETH
res_hex = rpc_api.call(amm_pair_contract, token0Call)
print(f"Token 0 Address : 0x{res_hex[-40:]}")
```

See the web3_demo script in demo folder.

## Interface methods of Web3Client

`pyweb3.Web3Client( node_url, [user_agent], [retries] )`  
Create a Web3 client from an URL.  
node_url : the access URL (https or wss) to the RPC blockchain node.  
user_agent: optional User-Agent header to use, a default web browser value is used.  
retries: number of retries to the RPC after an error. 2 by default.  
The node URL can be HTTPS (https://...) or secure WebSocket (wss://...)  
In case the connection is WebSocket, the connection tunnel is maintained opened until the Web3Client object is deleted. When using HTTPS, the connection is one-time query (POST) for each method call.

`.get_balance( 0xAddress, [state] )`  
Give the native balance of an 0x address string. The balance is given as integer in Wei units (10^-18 ETH).  
Can return 0 Wei in case of issue when getting data.  
The following state options are possible :

* HEX String - an integer block number
* String "earliest" for the earliest/genesis block
* String "latest" for the latest mined block
* String "pending" for the pending state/transactions

Default value is "latest"

`.call( contractAddr, command_code, [data], [state] )`  
Call RPC eth_call.  
command_code and data must be provided in hex string (without "0x"). data is optional. For state options, see get_balance.  
Return the response, as "raw" 0x hex string.  

`.pushtx( TxHexStr )`  
Broadcast a transaction on the blockchain network.  
TxHexStr is the tx data as "raw" hex, without "0x".

`.get_tx_num( 0xAddress, [state] )`  
Give the number of transactions send from the given address, as integer.  
For state options, see get_balance.

`.get_gasprice()`  
Read the current node estimation for on-chain gas price. The gas price is given as integer in Wei units.  

`.get_logs( param )`  
Call "eth_getLogs" with the given parameter.

`.set_filter( param )`  
Call "eth_newFilter" with the given parameter.

`.get_filter( filter_id )`  
Call "eth_getFilterLogs" with the given filter_id parameter.

## License

Copyright (C) 2021-2022  BitLogiK SAS

This program is free software: you can redistribute it and/or modify  
it under the terms of the GNU General Public License as published by  
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,  
but WITHOUT ANY WARRANTY; without even the implied warranty of  
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details.

## Support

Open an issue in the Github repository for help about its use.
