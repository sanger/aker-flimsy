#!/usr/bin/env python

"""Send product catalogue (read from a file) to a specified Aker url.
If messages don't get through, try unsetting the proxy in your shell.
"""

import os
import argparse
import requests
import json

HEADERS = { 'Content-type': 'application/json', 'Accept': 'application/json' }

def build_data(filename, lims_url=None):
    """Read the given filename and builds a catalogue message (a dict)
    out of it, that can be sent as JSON to the work orders appliaction.
    """
    product = None
    catalog_data = {'products': []}
    with open(filename, 'r') as fin:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            if line.lower()=='product':
                product = {}
                catalog_data['products'].append(product)
                continue
            k,v = map(str.strip, line.split(':', 1))
            if product is None:
                if k.lower()=='url' and lims_url:
                    v = lims_url
                catalog_data[k] = v
            else:
                product[k] = v
    return {'catalogue': catalog_data}

def send_request(data, url, proxy, cert=None, headers=None):
    """Send the given data to the given url."""
    session = requests.Session()
    session.trust_env = False
    session.proxies = { 'http': proxy, 'https': proxy } if proxy else {}
    session.headers = HEADERS if headers is None else headers
    if cert is not None:
        session.verify = cert
    r = session.post(url=url, data=data)
    print "Status:", r.status_code
    print r.text

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', '-u', metavar='AKER_URL', required=True,
                        help="url to post products to")
    parser.add_argument('--file', '-f', metavar='FILENAME', required=True,
                        help="file to read catalogue information from")
    parser.add_argument('--proxy', '-p', metavar='PROXY',
                        help="proxy to use for posts (default none)")
    parser.add_argument('--lims', '-l', metavar='LIMS_URL',
                        help="url for Aker to post its work orders to")
    args = parser.parse_args()
    req = build_data(args.file, args.lims)
    print json.dumps(req, indent=4)
    cert = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cert.crt')
    if not os.path.isfile(cert):
        print "[No cert.crt file in folder -- proceeding without verification]"
        cert = False
    send_request(json.dumps(req), args.url, args.proxy, cert)
    
if __name__ == '__main__':
    main()
