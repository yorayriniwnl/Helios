#!/usr/bin/env python3
"""Demo trigger helper

Usage:
  python backend/scripts/trigger_demo_alert.py --mode post --backend http://localhost:8000
  python backend/scripts/trigger_demo_alert.py --mode file --out docs/demo_assets/critical_alert.json

This script is for demo/staging only. It loads `docs/demo_assets/critical_alert.json` and either POSTS
it to a demo endpoint on the backend (`/demo/trigger_alert`) or writes a file for frontend injection.
"""
import argparse
import json
import os
import sys

def post_json(url, payload):
    try:
        import urllib.request
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            print('POST response:', resp.status, resp.reason)
            body = resp.read().decode('utf-8')
            if body:
                print(body)
            return True
    except Exception as e:
        print('POST failed:', e)
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('post','file'), default='post')
    parser.add_argument('--backend', default='http://localhost:8000')
    parser.add_argument('--in', dest='infile', default='docs/demo_assets/critical_alert.json')
    parser.add_argument('--out', default='docs/demo_assets/critical_alert.json')
    args = parser.parse_args()

    infile = args.infile
    if not os.path.exists(infile):
        print('Demo alert payload not found at', infile)
        sys.exit(2)

    with open(infile, 'r', encoding='utf-8') as f:
        payload = json.load(f)

    if args.mode == 'file':
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2)
        print('Wrote demo alert to', args.out)
        return

    # POST mode: try demo endpoint
    url = args.backend.rstrip('/') + '/demo/trigger_alert'
    ok = post_json(url, payload)
    if not ok:
        # fallback: write to out file
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2)
        print('Falling back: wrote demo alert to', args.out)

if __name__ == '__main__':
    main()
