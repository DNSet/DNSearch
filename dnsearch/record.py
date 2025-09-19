# coding:utf-8

from typing import List
from typing import Optional

from dnslib import A
from dnslib import AAAA
from dnslib import CNAME
from dnslib import QTYPE
from dnslib import RR
from xkits_lib import LiveMeter
from xkits_network import Peer

from dnsearch.domain import Name


class Record(LiveMeter):
    def __init__(self, name: Name, data: str, ttl: int):
        self.__name: str = str(name)
        self.__data: str = data
        super().__init__(ttl)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def data(self) -> str:
        return self.__data

    def update(self, data: str, ttl: int) -> None:
        self.__data = data
        self.lease = ttl

    def answer(self, ttl: Optional[int] = None) -> RR:
        """DNS Resource Record"""
        raise NotImplementedError


class AddressRecord(Record):
    def __init__(self, name: Name, data: str, ttl: int):
        super().__init__(name=name, data=data, ttl=ttl)
        self.__peer: Optional[Peer] = None

    @property
    def peer(self) -> Peer:
        if self.__peer is None:
            self.__peer = Peer.from_string(address=self.data)
        return self.__peer


class RecordA(AddressRecord):
    """Address Record"""
    RTYPE: int = QTYPE.A

    def __init__(self, name: Name, ipv4: str, ttl: int):
        super().__init__(name=name, data=ipv4, ttl=ttl)

    def answer(self, ttl: Optional[int] = None) -> RR:
        return RR(rname=self.name, rtype=self.RTYPE, rdata=A(self.data),
                  ttl=int(self.lease) if ttl is None else ttl)


class RecordAAAA(AddressRecord):
    """Quad-A Record"""
    RTYPE: int = QTYPE.AAAA

    def __init__(self, name: Name, ipv6: str, ttl: int):
        super().__init__(name=name, data=ipv6, ttl=ttl)

    def answer(self, ttl: Optional[int] = None) -> RR:
        return RR(rname=self.name, rtype=self.RTYPE, rdata=AAAA(self.data),
                  ttl=int(self.lease) if ttl is None else ttl)


class RecordCNAME(Record):
    """Canonical Name Record"""
    RTYPE: int = QTYPE.CNAME

    def __init__(self, name: Name, cname: str, ttl: int):
        super().__init__(name=name, data=cname, ttl=ttl)

    def answer(self, ttl: Optional[int] = None) -> RR:
        return RR(rname=self.name, rtype=self.RTYPE, rdata=CNAME(self.data),
                  ttl=int(self.lease) if ttl is None else ttl)


class Addresses():
    def __init__(self):
        pass


class Resources():
    def __init__(self, domain_name: str):
        self.__name: Name = Name(domain_name)
        self.__rec_a: List[RecordA] = []

    @property
    def name(self) -> Name:
        return self.__name
