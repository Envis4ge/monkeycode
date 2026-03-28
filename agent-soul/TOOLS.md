# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## 搜索工具优先级

1. **百度搜索**（baidu-search）— **优先使用**
   - 命令：`python3 ~/workspace/agent/workspace/skills/baidu-search/scripts/search.py '{"query":"关键词","count":10}'`
   - 支持 freshness：`pd`(24h) / `pw`(7天) / `pm`(31天) / `py`(年)
2. **妙搭搜索**（miaoda-web-search）— 备选
   - 命令：`miaoda-studio-cli search-summary --query "关键词"`
