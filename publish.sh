#!/usr/bin/env bash
# 一键发布：构建 → 提交 → 推送 → GitHub Pages 自动部署
#
# 用法：
#   ./publish.sh                    # 自动生成提交说明（带时间）
#   ./publish.sh "新增某某文章"      # 自定义提交说明
#   ./publish.sh --no-build "只改样式"  # 跳过构建，直接提交推送
set -euo pipefail
cd "$(dirname "$0")"

MSG="更新站点 $(date '+%Y-%m-%d %H:%M')"
DO_BUILD=1
if [ "${1:-}" = "--no-build" ]; then
  DO_BUILD=0; shift
fi
[ $# -gt 0 ] && MSG="$1"

if [ "$DO_BUILD" = 1 ]; then
  echo "==> [1/3] 构建"
  python3 build_articles.py
  python3 build_notes.py
  python3 build_site.py
  python3 fix_nav.py
else
  echo "==> [1/3] 跳过构建"
fi

echo "==> [2/3] 提交"
git add -A
if git diff --cached --quiet; then
  echo "    没有新变更"
else
  git commit -m "$MSG"
fi

echo "==> [3/3] 推送"
git push

echo
echo "✔ 已推送。约 1 分钟后同步到："
echo "  https://xu2388.github.io"
echo "  部署进度：https://github.com/xu2388/xu2388.github.io/actions"
