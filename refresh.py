#!/usr/bin/env python3
"""
自动优选刷新器（精简版）
========================
每 2 小时由 GitHub Actions 运行：
  1. 拉取公共优选 API（cf.090227.xyz，电信/联通/移动三条线路）
  2. 合并去重，规范化为 edgetunnel 优选 API 能吃的 `IP:443#备注` 行
  3. 追加少量静态优选域名作兜底
  4. 输出 public/optimal.txt，由 GitHub Pages 发布

安全规则：三家 API 合计拉到的条目 < 3 时以失败退出，workflow 不会发布，
GitHub Pages 上保留上一版好列表，绝不发空表。
仅使用 Python 标准库，无第三方依赖。
"""

import os
import sys
import urllib.request
from datetime import datetime, timezone

APIS = [
    ("电信", "https://cf.090227.xyz/ct?ips=8&port=443"),
    ("联通", "https://cf.090227.xyz/cu?ips=8&port=443"),
    ("移动", "https://cf.090227.xyz/cmcc?ips=8&port=443"),
]

# 静态优选域名兜底（社区常用 CF 优选域名，仅作末尾补充）
STATIC_FALLBACK = [
    ("saas.sin.fan:443", "静态优选1"),
    ("cdn.204910.best:443", "静态优选2"),
    ("cf.877774.xyz:443", "静态优选3"),
    ("www.shopify.com:443", "静态优选4"),
]

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "optimal.txt")
MIN_API_ENTRIES = 3
TIMEOUT = 20


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (edge-optimal)"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read().decode("utf-8", "replace")


def parse(text):
    """解析 `IP#备注` 或 `IP:端口#备注` 行，返回裸 IP 列表（保序）。"""
    ips = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        addr = line.split("#")[0].strip()
        host = addr.split(":")[0].strip()
        # 只接受 IPv4 字面量
        parts = host.split(".")
        if len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
            ips.append(host)
    return ips


def main():
    lines = []
    seen = set()
    total_api = 0
    for carrier, url in APIS:
        try:
            ips = parse(fetch(url))
        except Exception as exc:
            print(f"[WARN] {carrier}优选 API 拉取失败: {exc}", flush=True)
            ips = []
        count = 0
        for ip in ips:
            if ip in seen:
                continue
            seen.add(ip)
            count += 1
            total_api += 1
            lines.append(f"{ip}:443#{carrier}优选{count:02d}")
        print(f"[OK] {carrier}: 新增 {count} 条", flush=True)

    if total_api < MIN_API_ENTRIES:
        print(f"[FATAL] 优选 API 合计仅 {total_api} 条 (< {MIN_API_ENTRIES})，判定本次运行失败，不发布。", flush=True)
        sys.exit(1)

    for addr, remark in STATIC_FALLBACK:
        host = addr.split(":")[0]
        if host not in seen:
            seen.add(host)
            lines.append(f"{addr}#{remark}")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[DONE] 共 {len(lines)} 条（API {total_api} + 静态 {len(lines) - total_api}），生成于 {stamp} -> {OUT_PATH}", flush=True)


if __name__ == "__main__":
    main()
