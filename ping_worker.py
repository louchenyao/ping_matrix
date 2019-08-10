#! /usr/bin/env python3

import numpy as np
import pandas as pd
import socket
import time

from datetime import datetime
from multiping import MultiPing

def domain_to_ip(d):
    try:
        addr_info = socket.getaddrinfo(d, None)
    except socket.gaierror:
        return None

    addr = None
    for res in addr_info:
        if res[0] == socket.AF_INET:
            # We found the first IPv4 address! Use this result
            addr = res[4][0]
            break
        elif not addr:
            # Otherwise, we record the first of the IPv6 addresses
            addr = res[4][0]
    return addr
    

def domains_to_ips(domains):
    return list(map(domain_to_ip, domains))

def ping(host, targets, df=None):
    ips = domains_to_ips(targets)
    t_to_ip = dict(zip(targets, ips))

    date = datetime.now()
    mp = MultiPing(ips, ignore_lookup_errors=True)
    mp.send()
    responses, no_responses = mp.receive(1)
    
    if type(df) == type(None):
        df = pd.DataFrame(columns=["date", "host", "target", "target_ip", "rtt"])

    for t, ip in t_to_ip.items():
        if ip in responses:
            df.loc[len(df)] = [date, host, t, ip, responses[ip] * 1000]
        else:
            df.loc[len(df)] = [date, host, t, ip, np.NaN]
    
    return df

def main():
    try:
        df = pd.read_csv("ping.csv").drop(columns=['Unnamed: 0'])
    except Exception:
        df = None
    while True:
        time.sleep(1)
        df = ping(host="laptop", targets=["lcy.im", "bj.lcybox.com", "do.lcybox.com", "yeah.moe"], df=df)
        df.to_csv("ping.csv")
        if (len(df) >= 1000):
            break

if __name__ == "__main__":
    main()