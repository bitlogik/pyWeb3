# -*- coding: utf8 -*-

# pyWeb3 : Web3 client demo
# Copyright (C) 2021 BitLogiK

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have receive a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>


"""Web3 RPC client demonstration script"""


from sys import argv
from logging import DEBUG, basicConfig

from pyweb3 import Web3Client


# Polygon blockchain API
rpc_host = "https://matic-mainnet.chainstacklabs.com"
# Uncomment below line to enable WebSocket
# rpc_host = "wss://ws-matic-mainnet.chainstacklabs.com"


# fmt: off
# flake8: noqa: E221
token0Call   = "0dfe1681"
token1Call   = "d21220a7"
decimalsCall = "313ce567"
getReserves  = "0902f1ac"
symbolCall   = "95d89b41"
# fmt: on


# Helpers for string decoding in result


def read_uint256(data, offset):
    """Extract and decode utint256 at the given offset bytes"""
    return int.from_bytes(data[offset : offset + 32], "big")


def read_string(data_ans):
    """ABI String decoding"""
    data_bin = bytes.fromhex(data_ans[2:])
    str_offset = read_uint256(data_bin, 0)
    str_len = read_uint256(data_bin, str_offset)
    str_offset += 32
    return data_bin[str_offset : str_offset + str_len].decode("utf8")


# SushiSwap ETH USDT

amm_pair = "0xc2755915a85c6f6c1c0f3a86ac8c058f11caa9c9"


def read_pair_info(amm_pair_addr):

    rpc_api = Web3Client(rpc_host)

    # Get token0 of the pair : it is WETH 0x7ceb23fd6bc0add59e62ac25578270cff1b9f619
    res_hex = rpc_api.call(amm_pair_addr, token0Call)
    token0_addr = f"0x{res_hex[-40:]}"

    # Get token 0 symbol
    res_hex = rpc_api.call(token0_addr, symbolCall)
    token0_symbol = read_string(res_hex)

    # get decimals of the token 0
    res_hex = rpc_api.call(token0_addr, decimalsCall)
    token0_decimals = int(res_hex[2:66], 16)

    # Get token1 of the pair : it is USDT 0xc2132d05d31c914a87c6611c10748aeb04b58e8f
    res_hex = rpc_api.call(amm_pair_addr, token1Call)
    token1_addr = f"0x{res_hex[-40:]}"

    # Get token 1 symbol
    res_hex = rpc_api.call(token1_addr, symbolCall)
    token1_symbol = read_string(res_hex)

    # get decimals of the token 1
    res_hex = rpc_api.call(token1_addr, decimalsCall)
    token1_decimals = int(res_hex[2:66], 16)

    # get the liquidity in the pair
    res_hex = rpc_api.call(amm_pair_addr, getReserves)
    liquidity = [int(res_hex[2:66], 16), int(res_hex[66:130], 16)]

    # Price of WETH in USDT = token1/token0
    liquidity0 = liquidity[0] / pow(10, token0_decimals)
    liquidity1 = liquidity[1] / pow(10, token1_decimals)
    price = liquidity1 / liquidity0

    print(
        f"\n\n----  Uniswap v2 Pair on Polygon : SushiSwap AMM ----\n\n"
        f" Pair :   {token0_symbol} - {token1_symbol} \n\n"
        f"Token 0 : {token0_symbol}\n"
        f" - Address  : {token0_addr}\n"
        # f" - Decimals : {self.token0.decimals}\n"
        f" - Reserve  : {liquidity0} {token0_symbol}\n\n"
        f"Token 1 : {token1_symbol}\n"
        f" - Address  : {token1_addr}\n"
        # f" - Decimals : {self.token1.decimals}\n"
        f" - Reserve  : {liquidity1} {token1_symbol}\n\n"
        f" Price : {token0_symbol} = {price} {token1_symbol} \n\n"
    )


if __name__ == "__main__":

    if "-v" in argv[1:]:
        basicConfig(level=DEBUG)

    if "-vv" in argv[1:]:
        basicConfig(level=5)

    read_pair_info(amm_pair)
