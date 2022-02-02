# -*- coding: utf8 -*-

# pyWeb3 : JSON RPC
# Copyright (C) 2021-2022 BitLogiK

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have receive a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>


"""JSON RPC for pyWeb3"""

from time import sleep
from logging import getLogger
from json import dumps, loads
from .http_client import HttpClient
from .websocket import WebSocketClient


class JSONRPCexception(Exception):
    """Exception when the Web3 call has no result, but an error field."""


logger = getLogger(__name__)

# ---- Helpers about messages encoding


def json_encode(dataobj):
    """Compact JSON encoding."""
    return dumps(dataobj, separators=(",", ":"))


# ---- JSON RPC functions to pack/unpack


def json_rpc_pack_response(idmsg, result_obj):
    """Build a JSON-RPC response."""
    request_obj = {
        "jsonrpc": "2.0",
        "id": idmsg,
        "result": result_obj,
    }
    return json_encode(request_obj).encode("utf8")


def json_rpc_unpack(buffer):
    """Decode a JSON-RPC call query : id, method, params."""
    try:
        resp_obj = loads(buffer)
    except Exception as exc:
        raise Exception(f"Error : not JSON response : {buffer}") from exc
    if resp_obj["jsonrpc"] != "2.0":
        raise Exception(f"Server is not JSONRPC 2.0 but {resp_obj.jsonrpc}")
    if "error" in resp_obj:
        raise JSONRPCexception(resp_obj["error"])
    return resp_obj["id"], resp_obj["result"]


class JSONRPCclient:
    """WebSocket and HTTPS JSON-RPC client"""

    def __init__(self, url_api, user_agent="pyWeb3", retries=3):
        if url_api.startswith("wss:"):
            self.cnx = WebSocketClient(url_api, user_agent)
        elif url_api.startswith("https:"):
            self.cnx = HttpClient(url_api, user_agent)
        else:
            raise Exception("Only accept HTTPS and WebSocket connection scheme")
        self.retry = retries
        self.req_id = 0

    def send_request(self, method_name, params=None):
        """Send a JSON RPC request"""
        if params is None:
            params = []
        self.req_id += 1
        request_obj = {
            "jsonrpc": "2.0",
            "id": self.req_id,
            "method": method_name,
            "params": params,
        }
        logger.log(5, "Sending RPC request method:%s with data:%s", method_name, params)
        self.cnx.send_message(json_encode(request_obj).encode("utf8"))

    def get_response(self):
        """Listen to response, expect same id as the latest request sent"""
        self.cnx.get_messages()
        msg = self.cnx.received_messages.pop()
        reqid, result = json_rpc_unpack(msg)
        logger.log(5, "Received RPC result: %s", result)
        if reqid != self.req_id:
            raise Exception("JSON RPC response id mismatch")
        return result

    def request(self, method_name, params=None):
        """Send a RPC query and listen to response"""
        if params is None:
            params = []
        for nret in range(self.retry):
            try:
                self.send_request(method_name, params)
                resp = self.get_response()
                return resp
            except KeyboardInterrupt as exc:
                raise exc
            except Exception as exc:
                if nret < self.retry - 1:
                    sleep(0.3)
                else:
                    raise exc
