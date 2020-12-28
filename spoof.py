import sys
from spoofer import conf


def main():
    args = conf.parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    sys.exit(main())
