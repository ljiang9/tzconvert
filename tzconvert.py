#!/usr/bin/env python3
"""tzconvert — 不动脑子的时区换算。纯标准库，纯本地。"""

import argparse
import difflib
import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones

VERSION = "0.1.0"

# 常用别名：模糊输入 -> IANA 时区名
ALIASES = {
    "shanghai": "Asia/Shanghai", "beijing": "Asia/Shanghai", "bj": "Asia/Shanghai",
    "new_york": "America/New_York", "ny": "America/New_York", "nyc": "America/New_York",
    "london": "Europe/London", "tokyo": "Asia/Tokyo", "paris": "Europe/Paris",
    "berlin": "Europe/Berlin", "sydney": "Australia/Sydney", "singapore": "Asia/Singapore",
    "hongkong": "Asia/Hong_Kong", "hk": "Asia/Hong_Kong", "seoul": "Asia/Seoul",
    "los_angeles": "America/Los_Angeles", "la": "America/Los_Angeles",
    "chicago": "America/Chicago", "denver": "America/Denver",
    "utc": "UTC", "gmt": "UTC",
    "nanchang": "Asia/Shanghai", "china": "Asia/Shanghai",
}

WEEKDAYS = ["一", "二", "三", "四", "五", "六", "日"]

DEFAULT_FMT = "%Y-%m-%d %H:%M 周{wd} ({tz})"


def resolve_zone(name):
    """别名或 IANA 名 -> IANA 名；失败时抛带建议的 ValueError。"""
    key = name.strip().lower().replace(" ", "_").replace("-", "_")
    if key in ALIASES:
        return ALIASES[key]
    try:
        ZoneInfo(name)
        return name
    except ZoneInfoNotFoundError:
        pass
    # did-you-mean: 先在别名里找，再在全部时区里找
    pool = list(ALIASES.keys()) + sorted(available_timezones())
    sug = difflib.get_close_matches(key, pool, n=3, cutoff=0.55)
    hint = f"你是不是想输入：{', '.join(sug)}？" if sug else ""
    raise ValueError(f"error: 未知时区「{name}」。{hint}")


def parse_dt(text, zone_name):
    """解析 'YYYY-MM-DD HH:MM'（或只有 HH:MM 时用今天）。返回 aware datetime。"""
    text = text.strip()
    fmts = ["%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M", "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d", "%H:%M"]
    for fmt in fmts:
        try:
            dt = datetime.strptime(text, fmt)
            break
        except ValueError:
            continue
    else:
        raise ValueError(
            f"error: 无法解析时间「{text}」，支持格式如 2026-10-05 15:00 或 15:00（今天）")
    if fmt == "%H:%M":
        today = datetime.now(ZoneInfo(zone_name)).date()
        dt = datetime.combine(today, dt.time())
    return dt.replace(tzinfo=ZoneInfo(zone_name))


def fmt_dt(dt, zone_name, fmt):
    wd = WEEKDAYS[dt.weekday()]
    return dt.strftime(fmt).format(wd=wd, tz=zone_name)


def split_zones(s):
    return [z.strip() for z in s.split(",") if z.strip()]


def cmd_convert(args):
    if args.when.lower() == "now":
        return cmd_now(args)
    src = resolve_zone(args.from_)
    dt = parse_dt(args.when, src)
    out = []
    for zname in split_zones(args.to):
        z = resolve_zone(zname)
        c = dt.astimezone(ZoneInfo(z))
        out.append({"zone": z, "time": fmt_dt(c, z, args.format)})
    if args.json:
        print(json.dumps({"from": src, "input": args.when, "results": out},
                         ensure_ascii=False, indent=2))
    else:
        for r in out:
            print(f"{r['time']}")
    return 0


def cmd_now(args):
    zones = split_zones(args.to) if args.to else ["local"]
    rows = []
    for zname in zones:
        if zname == "local":
            dt = datetime.now().astimezone()
            z = str(dt.tzinfo)
        else:
            z = resolve_zone(zname)
            dt = datetime.now(ZoneInfo(z))
        rows.append((z, fmt_dt(dt, z, args.format)))
    if args.json:
        print(json.dumps([{"zone": z, "time": t} for z, t in rows],
                         ensure_ascii=False, indent=2))
        return 0
    w = max(len(z) for z, _ in rows)
    print(f"{'时区':<{w}}  当前时间")
    for z, t in rows:
        print(f"{z:<{w}}  {t}")
    return 0


def cmd_meet(args):
    src = resolve_zone(args.from_)
    dt = parse_dt(args.when, src)
    zones = [src] + split_zones(args.with_)
    rows = []
    for z in dict.fromkeys(zones):  # 去重保序
        zname = resolve_zone(z)
        c = dt.astimezone(ZoneInfo(zname))
        hour = c.hour + c.minute / 60
        ok = 9 <= hour < 18
        rows.append((zname, fmt_dt(c, zname, args.format), ok))
    if args.json:
        print(json.dumps(
            [{"zone": z, "time": t, "working_hours": ok} for z, t, ok in rows],
            ensure_ascii=False, indent=2))
        return 0
    w = max(len(z) for z, _, _ in rows)
    print(f"会议时间（发起：{fmt_dt(dt, src, args.format)}）")
    for z, t, ok in rows:
        flag = "☀️ 工作时间" if ok else "🌙 非工作时间"
        print(f"  {z:<{w}}  {t}  {flag}")
    return 0


def build_parser(prog="tzconvert"):
    ap = argparse.ArgumentParser(
        prog=prog,
        description="不动脑子的时区换算：tzconvert \"2026-10-05 15:00\" "
                    "--from Asia/Shanghai --to America/New_York；"
                    "会议规划：tzconvert meet \"2026-10-06 10:00\" "
                    "--from Asia/Shanghai --with \"America/New_York,Europe/London\"")
    ap.add_argument("--version", action="version", version=f"tzconvert {VERSION}")
    ap.add_argument("when", nargs="?", default=None,
                   help="时间，如 2026-10-05 15:00；now=现在")
    ap.add_argument("--from", dest="from_", default="Asia/Shanghai",
                    help="源时区（默认 Asia/Shanghai）")
    ap.add_argument("--to", default="UTC", help="目标时区，逗号分隔多个")
    ap.add_argument("--format", default=DEFAULT_FMT,
                    help="输出格式（strftime，支持 {wd} 星期、{tz} 时区）")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    return ap


def build_meet_parser():
    m = argparse.ArgumentParser(
        prog="tzconvert meet",
        description="会议时间规划：看各时区是否在工作时间")
    m.add_argument("when", help="会议时间，如 2026-10-06 10:00")
    m.add_argument("--from", dest="from_", default="Asia/Shanghai")
    m.add_argument("--with", dest="with_", required=True, help="参会时区，逗号分隔")
    m.add_argument("--format", default=DEFAULT_FMT)
    m.add_argument("--json", action="store_true")
    return m


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # "meet" 作为第一个参数时走会议规划（避免与 when 位置参数冲突）
    if argv and argv[0] == "meet":
        args = build_meet_parser().parse_args(argv[1:])
        try:
            return cmd_meet(args)
        except ValueError as e:
            print(e, file=sys.stderr)
            return 1
    ap = build_parser()
    args = ap.parse_args(argv)
    if not args.when:
        ap.print_help()
        return 2
    try:
        return cmd_convert(args)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
