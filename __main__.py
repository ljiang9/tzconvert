"""python -m tzconvert 入口。"""
import sys

try:
    from .tzconvert import main  # python -m tzconvert
except ImportError:  # 直接跑 __main__.py
    from tzconvert import main

if __name__ == "__main__":
    sys.exit(main())
