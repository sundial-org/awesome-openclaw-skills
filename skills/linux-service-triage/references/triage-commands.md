# Linux Service Triage Commands (safe first)

## Logs
- systemd: `journalctl -u <service> -n 200 --no-pager`
- live: `journalctl -u <service> -f`
- PM2: `pm2 logs <name> --lines 200`

## Status
- systemd: `systemctl status <service> --no-pager`
- ports: `ss -ltnp | grep <port>`
- processes: `ps aux | grep <name>`

## Permissions
- `ls -la <path>`
- `namei -l <path>` (checks each directory in path)

## Nginx
- config test: `nginx -t`
- reload: `systemctl reload nginx`
- logs: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`

## DNS sanity
- `dig +short <host>`
- `dig +trace <host>`
