# Commands (examples)

## Install/build

- Build from repo: `go build ./cmd/ip`
- Run local binary: `./ip ...`
- If installed: `ip ...`

## Auth and config

- Login (stdin password):
  - `printf '%s' "pass" | ip auth login --username "you@example.com" --password-stdin`
  - Add `--no-input` to disable prompts.
- Check auth:
  - `ip auth status` or `ip --json auth status`
- Config:
  - `ip config path`
  - `ip config show`
  - `ip config get defaults.list_limit`
  - `ip config set defaults.list_limit 100`
  - `ip config unset defaults.resolve_final_url`

## List

- Basic:
  - `ip list --folder unread --limit 25`
  - `ip list --folder archive --json`
  - `ip list --ndjson`
- Select fields:
  - `ip list --fields "bookmark_id,title,url" --ndjson`
- Incremental:
  - `ip list --cursor ~/.config/ip/cursor.json`
  - `ip list --cursor-dir ~/.config/ip/cursors`
  - `ip list --since bookmark_id:12345`
  - `ip list --until time:2025-01-01T00:00:00Z`
  - `ip list --updated-since 2025-01-01T00:00:00Z`
- Filter client-side:
  - `ip list --select "starred=1,tag~news"`

## Add

- Add URL:
  - `ip add https://example.com/article --title "Example" --tags "go,readlater" --folder unread`
- Add from stdin:
  - `cat urls.txt | ip add -`

## Export/import

- Export (default ndjson):
  - `ip export --cursor ~/.config/ip/cursor.json`
  - `ip export --cursor-dir ~/.config/ip/cursors`
  - `ip export --fields "bookmark_id,title,url" --ndjson`
  - `ip export --output-dir ./exports --cursor-dir ~/.config/ip/cursors`
- Import:
  - `ip import --input urls.txt --input-format plain`
  - `ip import --input bookmarks.ndjson --input-format ndjson --progress-json`

## Mutations

- Archive/star/move:
  - `ip archive 123456`
  - `ip unarchive 123456`
  - `ip star 123456`
  - `ip unstar 123456`
  - `ip move --folder "Work" 123456`
- Delete (requires confirmation):
  - `ip delete 123456 --yes-really-delete`
  - `ip delete 123456 --confirm 123456`
- Bulk:
  - `ip archive --ids 1,2,3`
  - `printf "10\n11\n12\n" | ip unarchive --stdin`
  - `ip archive --ids 1,2,3 --batch 2`
- Safe modes:
  - `ip --dry-run archive 123456`
  - `ip --idempotent highlights add 123456 --text "Some quote"`

## Text view

- `ip text 123456 --out article.html`
- `ip text 123456 --out article.html --open`
- `printf "1\n2\n3\n" | ip text --stdin --out ./articles`

## Progress

- `ip progress 123456 --progress 0.5 --timestamp 1700000000`

## Folders

- `ip folders list`
- `ip folders add "New Folder"`
- `ip folders delete "New Folder" --yes`
- Reorder:
  - `ip folders order "100:1,200:2,300:3"`

## Highlights

- `ip highlights list 123456`
- `ip highlights add 123456 --text "Some quote" --position 0`
- `ip highlights delete 98765`

## Health/verify/doctor

- `ip health`
- `ip verify`
- `ip doctor --json`

## Schemas

- `ip schema bookmarks`
- `ip schema auth`

