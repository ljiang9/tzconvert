# tzconvert — 不动脑子的时区换算

输一个时间、两个时区，直接告诉你换算结果。不用再心算 UTC+8 和 EDT 差几小时。

纯 Python 标准库（`zoneinfo` / `argparse` / `difflib`），零依赖，纯本地运行。

## 安装

```bash
git clone https://github.com/ljiang9/tzconvert.git
cd tzconvert
# 无需安装，直接跑：
python3 -m tzconvert "2026-10-05 15:00" --from Asia/Shanghai --to America/New_York
```

## 用法

```bash
# 基本换算（带星期）
tzconvert "2026-10-05 15:00" --from Asia/Shanghai --to America/New_York
# 2026-10-05 03:00 周一 (America/New_York)

# 多个目标时区
tzconvert "2026-10-05 15:00" --from Asia/Shanghai --to America/New_York,Europe/London,Asia/Tokyo

# 现在各地几点了
tzconvert now --to America/New_York,Europe/London,Asia/Tokyo

# 别名：不用记全名
tzconvert "15:00" --from beijing --to ny        # 今天 15:00（北京时间）-> 纽约时间
tzconvert now --to ny,london,tokyo,utc

# 会议规划：自动标出谁在半夜
tzconvert meet "2026-10-06 10:00" --from Asia/Shanghai --with "America/New_York,Europe/London"
#   Asia/Shanghai       2026-10-06 10:00 周二 (Asia/Shanghai)  ☀️ 工作时间
#   America/New_York    2026-10-05 22:00 周一 (America/New_York) 🌙 非工作时间
#   Europe/London       2026-10-06 03:00 周二 (Europe/London)  🌙 非工作时间

# 自定义格式 / JSON
tzconvert "2026-10-05 15:00" --to ny --format "%m-%d %H:%M"
tzconvert now --to ny,london --json

# 写错时区会给建议
tzconvert now --to "Amercia/New_York"
# error: 未知时区「Amercia/New_York」。你是不是想输入：America/New_York？
```

## 别名表

| 别名 | 时区 |
|---|---|
| shanghai / beijing / bj / nanchang / china | Asia/Shanghai |
| new_york / ny / nyc | America/New_York |
| los_angeles / la | America/Los_Angeles |
| chicago / denver | America/Chicago / America/Denver |
| london / paris / berlin | Europe/London / Europe/Paris / Europe/Berlin |
| tokyo / seoul / singapore / hongkong / hk | Asia/Tokyo / Asia/Seoul / Asia/Singapore / Asia/Hong_Kong |
| sydney | Australia/Sydney |
| utc / gmt | UTC |

也支持直接写 IANA 全名（如 `Australia/Melbourne`）。

## 说明

- `meet` 的"工作时间"定义为当地 9:00–18:00，只是启发式标注，不是日历。
- 只写 `15:00` 时按源时区的**今天**计算。
- 换算结果依赖系统 `zoneinfo` 数据库版本；夏令时边界附近以系统库为准。
- 默认源时区是 `Asia/Shanghai`（作者在国内），`--from` 可改。

## License

MIT
