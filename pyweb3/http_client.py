# -*- coding: utf8 -*-

# pyWeb3 : HTTP client
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

from h11 import (
    Connection,
    Request,
    Response,
    Data,
    EndOfMessage,
    ConnectionClosed,
    NEED_DATA,
    CLIENT,
)

from .tls_socket import TLSsocket


DEFAULT_HTTPS_PORT = 443


logger = getLogger(__name__)


class HttpClientException(Exception):
    """Exception from the WebSocket client."""


class HttpClient:
    """HTTP client with a host within TLS, send and decode messages."""

    def __init__(self, httpURL, ua):
        """Open the HTTPS connection to a given a URL."""
        http_url = urlparse(httpURL)
        assert http_url.scheme == "https"
        self.conn = None
        self.ssocket = None
        self.received_messages = []
        self.port_num = http_url.port or DEFAULT_HTTPS_PORT
        self.domain = http_url.hostname
        self.endpoint = http_url.path or "/"
        self.user_agent = ua

    def close(self):
        """Close the TLS connection when deleting the object."""
        if self.ssocket is not None:
            logger.log(5, "Closing TLS")
            self.ssocket.close()
            self.ssocket = None

    def send_message(self, message):
        """Send a message to the host, POST data message"""
        try:
            logger.log(
                5,
                "Connecting to HTTPS Host: %s  Port: %s",
                self.domain,
                self.port_num,
            )
            self.ssocket = TLSsocket(self.domain, self.port_num)
            logger.log(
                5,
                "Connected to HTTPS Host=%s PathTarget=%s",
                self.domain,
                self.endpoint,
            )
        except Exception as exc:
            logger.error("Error during TLS connection : %s", str(exc), exc_info=exc)
            raise HttpClientException(exc) from exc
        self.conn = Connection(our_role=CLIENT)
        raw_message = self.conn.send(
            Request(
                method=b"POST",
                target=self.endpoint,
                headers=[
                    ("Host", self.domain),
                    ("User-Agent", self.user_agent),
                    ("Connection", "close"),
                    ("Content-Type", "application/json"),
                    ("Content-Length", str(len(message))),
                ],
            )
        )
        raw_message += self.conn.send(Data(data=message))
        raw_message += self.conn.send(EndOfMessage())
        logger.log(5, "Sending HTTP POST data : %s", raw_message)
        self.ssocket.send(raw_message)

    def get_messages(self):
        """Read data from server"""
        if self.ssocket.conn is None:
            self.close()
            logger.debug("Socket was closed by remote party")
            return
        # Listen to server data
        while True:
            event = self.conn.next_event()
            if isinstance(event, EndOfMessage):
                self.conn.send(ConnectionClosed())
                self.close()
                return
            if event is NEED_DATA:
                self.conn.receive_data(self.ssocket.receive())
                continue
            if isinstance(event, Response):
                if event.status_code != 200:
                    raise HttpClientException(
                        f"Error in response code {event.status_code}"
                    )
            if isinstance(event, Data):
                logger.log(5, "Data received from HTTP query : %s", event.data)
                self.received_messages.append(event.data)
