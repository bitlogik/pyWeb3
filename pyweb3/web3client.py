# -*- coding: utf8 -*-

# pyWeb3 : Web3 client
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


"""Web3 RPC client"""


from .json_rpc import JSONRPCclient


class Web3Client:
    """Web3 RPC client"""

    def __init__(self, node_url, user_agent="pyWeb3"):
        self.jsonrpc = JSONRPCclient(node_url, user_agent)

    def get_balance(self, address, state="latest"):
        """Get native token balance"""
        balraw = self.jsonrpc.request("eth_getBalance", [address, state])[2:]
        if balraw == "":
            return 0
        balance = int(balraw, 16)
        return balance

    def call(self, contract, command_code, data="", state="latest"):
        """eth call query"""
        # https://eth.wiki/json-rpc/API#eth_call
        # The following state options are possible :
        #   HEX String - an integer block number
        #   String "earliest" for the earliest/genesis block
        #   String "latest" for the latest mined block
        #   String "pending" for the pending state/transactions
        datab = f"0x{command_code}{data}"
        return self.jsonrpc.request(
            "eth_call", [{"to": contract, "data": datab}, state]
        )

    def pushtx(self, txhex):
        """Upload a transaction"""
        return self.jsonrpc.request("eth_sendRawTransaction", ["0x" + txhex])

    def get_tx_num(self, addr, state="latest"):
        """Read number of transaction done by this address"""
        tx_count_raw = self.jsonrpc.request(
            "eth_getTransactionCount", ["0x" + addr, state]
        )[2:]
        if tx_count_raw == "":
            return 0
        return int(tx_count_raw, 16)

    def get_gasprice(self):
        """Get the gas price in wei units"""
        gas_price_raw = self.jsonrpc.request("eth_gasPrice")[2:]
        if gas_price_raw == "":
            raise Exception("Node has no gas price method")
        return int(gas_price_raw, 16)
