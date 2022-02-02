# -*- coding: utf8 -*-

# pyWeb3 : WebSocket client
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


"""WebSocket client"""


from logging import getLogger
from urllib.parse import urlparse
from time import sleep

from wsproto import WSConnection, ConnectionType
from wsproto.events import (
    Request,
    AcceptConnection,
    RejectConnection,
    CloseConnection,
    Ping,
    Message,
    TextMessage,
    BytesMessage,
)
from .tls_socket import TLSsocket


DEFAULT_HTTPS_PORT = 443

GLOBAL_TIMEOUT = 8  # seconds
UNIT_WAITING_TIME = 0.4
CYCLES_TIMEOUT = int(GLOBAL_TIMEOUT / UNIT_WAITING_TIME)


logger = getLogger(__name__)


class WebSocketClientException(Exception):
    """Exception from the WebSocket client."""


class WebSocketClient:
    """WebSocket client with a host within HTTPS, send and decode messages."""

    def __init__(self, wsURL, ua):
        """Open the WebSocket connection to a given a URL."""
        ws_url = urlparse(wsURL)
        assert ws_url.scheme == "wss"
        self.partial_txtmessages = []
        self.partial_binmessages = []
        self.received_messages = []
        port_num = ws_url.port or DEFAULT_HTTPS_PORT
        try:
            self.ssocket = TLSsocket(ws_url.hostname, port_num)
            self.websock_conn = WSConnection(ConnectionType.CLIENT)
            logger.debug(
                "Connecting to WebSocket Host=%s PathTarget=%s",
                ws_url.hostname,
                ws_url.path,
            )
            self.send(
                Request(
                    host=ws_url.hostname,
                    target=ws_url.path or "/",
                    extra_headers=[("User-Agent", ua)],
                )
            )
            cyclew = 0
            while cyclew < CYCLES_TIMEOUT:
                logger.debug("Waiting WebSocket handshake : %ith loop.", cyclew + 1)
                sleep(UNIT_WAITING_TIME)
                self.get_messages()
                while len(self.received_messages) > 0:
                    res = self.received_messages.pop()
                    if res == "established":
                        return
                    if res == "rejected":
                        raise WebSocketClientException("WebSocket handshake rejected")
                cyclew += 1
            if cyclew == CYCLES_TIMEOUT:
                raise WebSocketClientException("WebSocket handshake timeout")
        except Exception as exc:
            logger.error(
                "Error during WebSocket connection : %s", str(exc), exc_info=exc
            )
            raise WebSocketClientException(exc) from exc

    def close(self):
        """Stop read timer and close the TLS connection when deleting the object."""
        logger.debug("Cancelling the WebSocket reading timer")
        if hasattr(self, "ssocket"):
            if self.ssocket is not None:
                logger.debug("Closing WebSocket")
                self.ssocket.close()
                self.ssocket = None

    def send(self, data_frame):
        """Send a WebSocket data frame to the host."""
        frame_bin = self.websock_conn.send(data_frame)
        self.ssocket.send(frame_bin)

    def send_message(self, data_message):
        """Send a message to the host."""
        raw_message = Message(data_message)
        logger.log(5, "Sending message : %s", raw_message.data)
        self.send(raw_message)

    def get_messages(self):
        """Read data from server and decode messages.
        Return a list of messages.
        "established", "rejected", <text>, <bytes>.
        Text and Bytes messages are given as their content.
        Close underlying TLS socket if WS connection closed.
        Auto-reply to ping messages.
        """
        # Test if socket is still opened
        if self.ssocket.conn is None:
            logger.debug("Socket was closed by remote party")
            self.close()
            return
        # Listen to server data and build a queue list
        datarcv = self.ssocket.receive()
        if datarcv:
            self.websock_conn.receive_data(datarcv)
            for event in self.websock_conn.events():
                if isinstance(event, AcceptConnection):
                    logger.debug("WebSocket connection established.")
                    self.received_messages.append("established")
                elif isinstance(event, RejectConnection):
                    logger.debug("WebSocket connection rejected.")
                    self.received_messages.append("rejected")
                elif isinstance(event, CloseConnection):
                    logger.error(
                        "WebSocket Connection closed: code=%i reason=%s",
                        event.code,
                        event.reason,
                    )
                    self.close()
                elif isinstance(event, Ping):
                    logger.debug("Ping received in WebSocket")
                    self.send(event.response())
                    logger.debug("Pong reply sent")
                elif isinstance(event, TextMessage):
                    self.partial_txtmessages.append(event.data)
                    if event.message_finished:
                        full_message = "".join(self.partial_txtmessages)
                        logger.log(
                            5, "WebSocket Text message received : %s", full_message
                        )
                        self.received_messages.append(full_message)
                        self.partial_txtmessages = []
                elif isinstance(event, BytesMessage):
                    self.partial_binmessages.append(event.data)
                    if event.message_finished:
                        full_message = b"".join(self.partial_binmessages)
                        logger.log(
                            5, "WebSocket Binary message received : %s", full_message
                        )
                        self.received_messages.append(full_message)
                        self.partial_binmessages = []

                else:
                    Exception(f"Unknown WebSocket event : {event}")
