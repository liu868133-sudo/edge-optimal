# edge-optimal — edgetunnel 自动优选刷新器

每 2 小时由 GitHub Actions 自动拉取公共优选 API（cf.090227.xyz 电信/联通/移动三线），
合并去重后生成 `optimal.txt` 并发布到 GitHub Pages，供 cmliu 版 edgetunnel 的
「优选 API」直接引用，实现优选 IP 自动保鲜，免手动优选。

## 产出

`https://<你的GitHub用户名>.github.io/edge-optimal/optimal.txt`

每行格式：`IP:443#电信优选01`（edgetunnel 优选 API 标准格式）。

## 接入 edgetunnel

1. 打开 edgetunnel 后台（你的 Worker 域名 `/admin`）。
2. 把上面的 optimal.txt 地址填入「优选 API」输入框，点「验证优选API」确认能拉到列表后保存。
3. 之后订阅里的优选节点每 2 小时自动更新，无需再动。

## 保险设计

- 三家 API 合计拉到少于 3 条时脚本直接失败退出，本次不发布，Pages 上保留上一版好列表。
- 末尾附 4 条静态优选域名作兜底。
- 刷新频率为每 2 小时一次，远低于 GitHub Actions 免费额度（2000 分钟/月）的消耗。

## 手动刷新

Actions 页面 → `Refresh optimal IPs` → `Run workflow`。
