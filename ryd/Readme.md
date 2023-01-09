# ryd
> Scan your message for yt links and fetch dislikes from [Return YouTube Dislike](https://returnyoutubedislike.com/)

- [How-to](#How to use)
- [Scanner toggle](#How to disable scanner)
- [Whitelist mode](#Whitelist mode)

### How to use
Just send any yt link, or use `ryd` command like `[p]ryd youtu.be/kxOuG8jMIgI`

### How to disable scanner
- `[p]ryd-config global disable` - toggle scanning bot-widely (bot owners only)
- `[p]ryd-config guild disable` - toggle scanning in server (admin only)
- `[p]ryd-config guild channel` - toggle scanning in channel. You can specify channel or just call this command from needed channel
- `[p]ryd-config me disable` - toggle scanning for user's messages in this server

### Whitelist mode
You can specify which channels of your server can be scanned for yt links

1. Enable whitelist mode `[p]ryd-config guild whitelist`
2. Use `[p]ryd-config guild channel` to whitelist channel