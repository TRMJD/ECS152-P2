# DNS Client implementation
# performs iterative DNS resolution, makes HTTP request to verify, and measures RTT for each step

import socket
import struct
import sys
import random
import time
# imports for socket programming, binary data handling, arguments, random number generation, and timing

# sources used : https://realpython.com/python-type-checking/ ,
# https://www.liquidweb.com/blog/how-to-demystify-the-dns-process/ , https://www.youtube.com/watch?v=WfkJ7xvngd0 ,
# https://datatracker.ietf.org/doc/html/rfc1035

# List of Root DNS servers to start resolution
ROOT_SERVERS = [
"198.41.0.4",
"199.9.14.201",
"192.33.4.12",
"199.7.91.13"
]
# Standard DNS port for queries
DNS_PORT = 53

# Encode domain name by converting string to DNS formatting
def encode_domain(domain: str) -> bytes:
    # encodes DNS names as length-prefixed labels
    parts = domain.split(".")
    encoded = b""
    for part in parts:
        # add length byte followed by label
        encoded += bytes([len(part)])
        encoded += part.encode()
    # adds null byte at end for end
    encoded += b'\x00'
    return encoded


# Build DNS request packet
def build_dns_request(domain: str) -> bytes:
    # create DNS header using random transaction ID
    transaction_id = random.randint(0,65535)
    # DNS standard query
    flags = 0x0100

    # establishes one question with no answers, authority, or additional records
    qdcount = 1
    ancount = 0
    nscount = 0
    arcount = 0
    # uses Big Endian format for network byte order in header
    header = struct.pack(
        "!HHHHHH",
        transaction_id,
        flags,
        qdcount,
        ancount,
        nscount,
        arcount
    )
    # encodes domain name and appends type and class fields
    qname = encode_domain(domain)
    # sets query type=A, class=IN
    qtype = 1
    qclass = 1
    question = qname + struct.pack("!HH", qtype, qclass)
    # forms complete DNS query packet
    return header + question


# Send DNS request with UDP socket and take RTT
def send_dns_request(server_ip: str, packet: bytes):
    # uses UDP socket to transmit DNS query
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(10)
    # records time before sending request to calculate RTT
    start = time.time()
    # sends DNS query to specified server IP and port
    sock.sendto(packet, (server_ip, DNS_PORT))
    # waits for response and recordds time after receiving
    response, _ = sock.recvfrom(4096)
    # calculates RTT
    rtt = (time.time() - start) * 1000
    # close socket after complete
    sock.close()

    return response, rtt


# Parses domain name and handles compression
def parse_name(response: bytes, ptr: int):
    # represents domain name as label sequence
    labels = []
    has_jumped = False
    orig_offset = ptr

    while True:
        length = response[ptr]
        # length of 0 means end
        if length == 0:
            ptr += 1
            break
        # checks for pointer using first two bits of length byte
        if (length & 0xC0) == 0xC0:
            # extracts 14-bit pointer offset
            pointer = struct.unpack("!H", response[ptr:ptr+2])[0]
            pointer &= 0x3FFF
            # saves original offset if this is the first jump
            if not has_jumped:
                orig_offset = ptr + 2
            ptr = pointer
            has_jumped = True
            continue

        ptr += 1
        labels.append(response[ptr:ptr+length].decode())
        ptr += length

    full_name = ".".join(labels)

    if has_jumped:
        return full_name, orig_offset
    else:
        return full_name, ptr


# Decode DNS response and extract records
def decode_dns_response(response: bytes):
    # unpacks DNS header to get counts of questions and resource records
    header = struct.unpack("!HHHHHH", response[:12])
    qdcount = header[2]
    ancount = header[3]
    nscount = header[4]
    arcount = header[5]

    offset = 12
    # skips question section
    for _ in range(qdcount):
        _, offset = parse_name(response, offset)
        # skips type and class
        offset += 4

    records = []
    total_rr = ancount + nscount + arcount

    for _ in range(total_rr):
        name, offset = parse_name(response, offset)
        # collects type, class, TTL, and RDLENGTH fields for resource records
        rtype, rclass, ttl, rdlength = struct.unpack(
            "!HHIH",
            response[offset:offset+10]
        )
        offset += 10
        rdata = response[offset:offset+rdlength]
        offset += rdlength

        # processes A record
        if rtype == 1:
            value = socket.inet_ntoa(rdata)
            rtype_name = "A"
        # processes AAAA record
        elif rtype == 28:
            value = socket.inet_ntop(socket.AF_INET6, rdata)
            rtype_name = "AAAA"
        # processes NS record
        elif rtype == 2:
            value, _ = parse_name(response, offset-rdlength)
            rtype_name = "NS"
        # processes CNAME record
        elif rtype == 5:
            value, _ = parse_name(response, offset-rdlength)
            rtype_name = "CNAME"
        # ignores other record types
        else:
            continue

        records.append((rtype_name, value))
    return records


# DNS resolver that iteratively resolves domain
def resolve(domain: str):
    # starts with root and queries name servers down hierarchy
    current_server = ROOT_SERVERS[0]

    while True:
        # builds DNS request packet for the domain being resolved
        packet = build_dns_request(domain)
        # prints current server and domain being queried
        print("--------------------------------------------")
        print(f"Querying {current_server} for {domain}")
        print("--------------------------------------------")

        response, rtt = send_dns_request(current_server, packet)
        records = decode_dns_response(response)

        next_server = None
        ns_found = False
        # iterates through resource records to find NS and A records
        for rtype, value in records:
            print(f"{rtype} : {value}")
            if rtype == "NS":
                ns_found = True
            if rtype == "A" and next_server is None:
                next_server = value

        print(f"RTT: {round(rtt,2)} ms")
        # if no NS recordds but found A record, return as host IP
        if not ns_found and next_server:
            return next_server

        if next_server:
            current_server = next_server
        else:
            raise Exception("Resolution failed")

# HTTP request testing function to verify resolved IP can serve HTTP requests
def http_client_request(ip: str, domain: str):
    # uses TCP socket to connect and resloves IP address for HTTP request
    print("--------------------------------------------")
    print(f"Making HTTP request to {ip}")
    print("--------------------------------------------")
    # AF_INET is IPv4, SOCK_STREAM is TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)

    start = time.time()
    sock.connect((ip,80))
    # constructs a simple HTTP GET request for the root path with Host header
    request = f"GET / HTTP/1.1\r\nHost: {domain}\r\nConnection: close\r\n\r\n"
    # sends HTTP request and waits for response, measuring RTT
    sock.sendall(request.encode())
    response = sock.recv(4096)
    rtt = (time.time()-start)*1000
    # close socket after complete
    sock.close()

    # extracts HTTP status, prints status and RTT
    status = response.decode(errors="ignore").split("\r\n")[0].split()[1]
    print(status)
    print(f"RTT: {round(rtt,2)} ms")


# Main function to run DNS client
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python DNS_client.py <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    # resolves domain to IP using iterative DNS resolver
    final_ip = resolve(domain)
    # uses IP to make HTTP request and verify response
    http_client_request(final_ip, domain)