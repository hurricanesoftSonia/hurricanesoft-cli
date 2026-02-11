# 🌀 HurricaneSoft CLI

颶風軟體統一 CLI 工具。一個 `hs` 指令管理所有內部工具。

## 安裝

```bash
# 下載 .pyz（單檔執行）
wget https://github.com/hurricanesoftSonia/hurricanesoft-cli/releases/latest/download/hs.pyz
chmod +x hs.pyz
mv hs.pyz /usr/local/bin/hs
```

## 工具列表

| 指令 | 工具 | 說明 |
|------|------|------|
| `hs mail` | MailTool v0.2.0 | 📧 Email 收發 |
| `hs todo` | TodoTool v0.2.0 | 📝 待辦事項 |
| `hs memo` | MemoTool v0.2.0 | 📋 備忘錄 |
| `hs msg` | MsgTool v0.3.0 | 💬 內部訊息 |
| `hs account` | AccounTool v0.1.0 | 💰 記帳 |
| `hs announce` | AnnounceTool v0.1.0 | 📢 公告 |
| `hs health` | HealthTool v0.2.0 | 🏥 系統監控 |
| `hs auth` | hurricanesoft-auth v0.1.0 | 🔐 LIDS 認證 |

## 快速開始

```bash
# 查看所有工具
hs list

# 設定精靈
hs config init

# 常用操作
hs mail fetch              # 收信
hs mail send --to xxx --subject "Hi" --body "..."
hs todo add "做某件事"      # 新增待辦
hs todo list               # 列出待辦
hs msg send --to samantha --msg "Hi"   # 傳訊息
hs msg inbox               # 收件匣
hs health check            # 健康檢查
hs auth login              # LIDS 登入
```

## 設定

設定檔位置: `~/.hurricanesoft/config.json`

```bash
hs config show             # 顯示設定
hs config set database.type postgresql
hs config set database.pg_host 192.168.50.100
hs config get database.type
```

## 認證

所有工具支援兩種認證方式：

1. **本地帳號** — `--user xxx --password xxx`
2. **LIDS 認證** — `--lids`（需先 `hs auth login`）

## 資料庫

支援 SQLite（預設）和 PostgreSQL：

```bash
# 切換到 PostgreSQL
hs config set database.type postgresql
hs config set database.pg_host 192.168.50.100
hs config set database.pg_database hurricanesoft
hs config set database.pg_user myuser
hs config set database.pg_password mypass

# 遷移資料
hs migrate --tool all --dry-run    # 預覽
hs migrate --tool all              # 執行遷移
```

## MsgTool Server

MsgTool 支援 HTTP server 模式，讓團隊跨機器互傳訊息：

```bash
# Server 端
hs msg serve --port 8900

# Client 端
hs msg --server http://192.168.50.100:8900 --user sonia --password xxx inbox
```

## 部署

下載 `.pyz` 單檔即可執行，需要 Python 3.8+。

PostgreSQL 需額外安裝: `pip install psycopg2-binary`

## 開發

```
hurricanesoft_cli/     # 統一 CLI + config + migrate
mailtool/             # Email
todotool/             # 待辦
memotool/             # 備忘錄
msgtool/              # 內部訊息
accountool/           # 記帳
announcetool/         # 公告
healthtool/           # 系統監控
hurricanesoft_auth/   # LIDS 認證
```

---

颶風軟體有限公司 Hurricanesoft © 2026
