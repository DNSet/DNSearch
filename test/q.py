from socketserver import BaseRequestHandler
from socketserver import UDPServer

from dnslib import A
from dnslib import AAAA
from dnslib import CNAME
from dnslib import DNSRecord
from dnslib import QTYPE
from dnslib import RR

# 定义静态解析表
DNS_TABLE = {
    "example.com.": {
        "A": "1.2.3.4",
        "AAAA": "2001:db8::1",
        "CNAME": "alias.example.com.",
    },
    "alias.example.com.": {
        "A": "5.6.7.8",
    }
}


class DNSHandler(BaseRequestHandler):
    def handle(self):
        data, sock = self.request
        request = DNSRecord.parse(data)

        qname = str(request.q.qname)
        qtype = QTYPE[request.q.qtype]

        # print(f"收到查询: {qname} 类型: {qtype}")

        reply = request.reply()

        # 查询是否在表里
        if qname in DNS_TABLE:
            records = DNS_TABLE[qname]
            if qtype in records:
                if qtype == "A":
                    reply.add_answer(RR(qname, QTYPE.A, rdata=A(records["A"]), ttl=60))
                elif qtype == "AAAA":
                    reply.add_answer(
                        RR(qname, QTYPE.AAAA, rdata=AAAA(records["AAAA"]), ttl=60))
                elif qtype == "CNAME":
                    reply.add_answer(
                        RR(qname, QTYPE.CNAME, rdata=CNAME(records["CNAME"]), ttl=60))
            else:
                # 如果没指定类型，但请求了 A/AAAA，就尽量返回
                if "A" in records and qtype == "A":
                    reply.add_answer(RR(qname, QTYPE.A, rdata=A(records["A"]), ttl=60))
                if "AAAA" in records and qtype == "AAAA":
                    reply.add_answer(RR(qname, QTYPE.AAAA, rdata=AAAA(records["AAAA"]), ttl=60))
                if "CNAME" in records and qtype == "CNAME":
                    reply.add_answer(RR(qname, QTYPE.CNAME, rdata=CNAME(records["CNAME"]), ttl=60))

        # 返回响应
        sock.sendto(reply.pack(), self.client_address)


if __name__ == "__main__":
    server = UDPServer(("0.0.0.0", 5353), DNSHandler)  # 先用 5353 端口
    # print("权威DNS服务器运行在 UDP 5353 端口")
    server.serve_forever()
