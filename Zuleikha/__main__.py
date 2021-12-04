import argparse
import sys
from . import zuleikha

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", '--api_key', help='GPT-3 API key to load.')
    parser.add_argument('-l', '--log', action='store_true', help='Should I save the converstation to file.')
    parser.add_argument('-m', '--master', action='store_true', help='Should you start as the master')
    args = parser.parse_args()

    api_key = ''
    with open("api_keys/" + args.api_key, "r") as f:
        api_key = f.read()
    
    zul = zuleikha.Zuleikha(api_key, args.log, args.master)
    zul.run()


if __name__ == '__main__':
    sys.exit(main())