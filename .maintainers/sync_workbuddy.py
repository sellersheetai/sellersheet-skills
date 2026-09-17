#!/usr/bin/env python3
"""Keep the repo root dual-format: Claude-style plugin AND Tencent WorkBuddy connector.

WorkBuddy (open.workbuddy.cn/docs/connector, "MCP + Skill" route) wants, at the
package root: connector-meta.json, mcp.json ({"mcpServers": one streamableHttp
server}), icon.svg, and skills/<name>/SKILL.md whose frontmatter carries
description_zh, description_en, version and author. Plugin loaders (Claude Code,
Codex, CodeBuddy, npx skills) ignore unknown root files and unknown frontmatter
keys — verified 2026-09-17 on CodeBuddy 2.151.0, Codex and npx skills — so ONE
tree serves every agent and nothing is copied.

    python3 .maintainers/sync_workbuddy.py          # write derived files/keys
    python3 .maintainers/sync_workbuddy.py --check  # exit 1 if anything is stale
    python3 .maintainers/sync_workbuddy.py --zip    # dist/sellersheet-workbuddy-connector-<v>.zip

What is derived (never hand-edit):
  connector-meta.json  .version           ← .claude-plugin/plugin.json
  mcp.json                                ← constant below
  skills/*/SKILL.md    description_zh     ← the Chinese sentence at the end of `description`
                       description_en     ← first sentence of the English part
                       author             ← constant
The description itself stays the single source; promote.sh runs this after the
version fan-out; lint.sh runs --check. stdlib only (no PyYAML on the maintainer box).
"""
import json
import os
import re
import sys
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTHOR = 'SellerSheet AI'
DERIVED_KEYS = ('description_zh', 'description_en', 'author')
ZH_MARKERS = ('中文触发词：', '中文说明：')

META = {
    'name': 'SellerSheet',
    'name_zh': 'SellerSheet 亚马逊运营助手',
    'name_en': 'SellerSheet for Amazon Sellers',
    'description': 'Amazon Seller Central + Ads + Google Sheets for AI agents: report warehouse, dashboards, listings, ads, images.',
    'description_zh': '连接亚马逊卖家后台、广告与 Google 表格：查询报表仓库、生成运营看板、管理 listing 与广告、生成产品图和 A+ 页面。',
    'description_en': 'Connect Amazon Seller Central, Ads and Google Sheets: query the report warehouse, build operator dashboards, manage listings and ads, generate listing images and A+ content.',
    'source': 'sellersheet',
    'type': 'mcp',
    'examples_zh': [
        '查一下 myStore-US 上周的库存和补货需求',
        '用最近 30 天的广告数据做一个 PPC 看板写到 Google 表格',
        '把 B0XXXXXXXX 的品牌分析搜索词报告拉出来并总结',
        '为 MYSKU-001 生成一套亚马逊主图和 A+ 页面',
    ],
    'examples_en': [
        'Show inventory levels and restock needs for myStore-US for last week',
        'Build a PPC dashboard in Google Sheets from the last 30 days of ads data',
        'Pull the Brand Analytics search terms report for B0XXXXXXXX and summarise it',
        'Generate a set of Amazon main images and A+ content for MYSKU-001',
    ],
    'minWorkbuddyVersion': '4.24.0',
}

MCP = {
    'mcpServers': {
        'sellersheet': {
            'type': 'streamableHttp',
            'url': 'https://sellersheetai.com/mcp',
            'timeout': 30000,
        }
    }
}

# The connector zip = the files WorkBuddy reads, nothing developer-facing.
ZIP_FILES = ('connector-meta.json', 'mcp.json', 'icon.svg', 'LICENSE')
ZIP_DIRS = ('skills',)


def plugin_version():
    with open(os.path.join(REPO, '.claude-plugin', 'plugin.json'), encoding='utf-8') as f:
        return json.load(f)['version']


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2) + '\n'


def split_frontmatter(text):
    m = re.match(r'---\n(.*?)\n---\n', text, re.S)
    if not m:
        raise SystemExit('SKILL.md without frontmatter')
    return m, m.group(1), text[m.end():]


def read_description(fm):
    """Value of `description:` — plain scalar or a `>-` block, folded with spaces."""
    lines = fm.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('description:'):
            val = line[len('description:'):].strip()
            if val not in ('>-', '>', '|', '|-'):
                return val
            out = []
            for cont in lines[i + 1:]:
                if not cont.startswith('  '):
                    break
                out.append(cont.strip())
            return ' '.join(out)
    raise SystemExit('frontmatter without description')


def derive(description):
    en, zh = description, ''
    for marker in ZH_MARKERS:
        if marker in description:
            en, _, zh = description.partition(marker)
            break
    en, zh = en.strip(), zh.strip()
    first = re.split(r'(?<=[.!?])\s', en, maxsplit=1)[0]
    if len(first) > 110:
        first = first[:110].rsplit(' ', 1)[0] + '…'
    return {
        'description_zh': zh or first,
        'description_en': first,
        'author': AUTHOR,
    }


def yaml_str(s):
    return json.dumps(s, ensure_ascii=False)  # a JSON string literal is valid YAML


def strip_derived(fm):
    return '\n'.join(l for l in fm.split('\n') if not any(l.startswith(k + ':') for k in DERIVED_KEYS))


def with_derived(fm, derived):
    """Insert the derived keys right after `name:` (before description, so lint's
    description-length count is unaffected)."""
    base = strip_derived(fm).split('\n')
    block = [f'{k}: {yaml_str(v) if k != "author" else v}' for k, v in derived.items()]
    for i, line in enumerate(base):
        if line.startswith('name:'):
            return '\n'.join(base[:i + 1] + block + base[i + 1:])
    return '\n'.join(block + base)


def skill_paths():
    root = os.path.join(REPO, 'skills')
    for name in sorted(os.listdir(root)):
        p = os.path.join(root, name, 'SKILL.md')
        if os.path.isfile(p):
            yield name, p


def render_skill(text):
    m, fm, body = split_frontmatter(text)
    new_fm = with_derived(fm, derive(read_description(fm)))
    return text[:m.start(1)] + new_fm + text[m.end(1):]


def expected_files():
    return {
        'connector-meta.json': dump(dict(META, version=plugin_version())),
        'mcp.json': dump(MCP),
    }


def write_atomic(path, content):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(content)
    os.replace(tmp, path)


def sync():
    for rel, content in expected_files().items():
        write_atomic(os.path.join(REPO, rel), content)
    for name, p in skill_paths():
        with open(p, encoding='utf-8') as f:
            text = f.read()
        new = render_skill(text)
        if new != text:
            write_atomic(p, new)
    if not os.path.isfile(os.path.join(REPO, 'icon.svg')):
        raise SystemExit('icon.svg is hand-maintained and missing at the repo root')
    print(f'workbuddy connector files in sync for v{plugin_version()}')


def check():
    stale = []
    for rel, content in expected_files().items():
        p = os.path.join(REPO, rel)
        if not os.path.isfile(p) or open(p, encoding='utf-8').read() != content:
            stale.append(rel)
    for name, p in skill_paths():
        text = open(p, encoding='utf-8').read()
        if render_skill(text) != text:
            stale.append(f'skills/{name}/SKILL.md')
    if not os.path.isfile(os.path.join(REPO, 'icon.svg')):
        stale.append('icon.svg (missing)')
    if stale:
        print('WorkBuddy connector files stale — run: python3 .maintainers/sync_workbuddy.py', file=sys.stderr)
        for s in stale:
            print(f'  - {s}', file=sys.stderr)
        sys.exit(1)
    print('workbuddy connector files in sync')


def make_zip():
    check()
    v = plugin_version()
    dist = os.path.join(REPO, 'dist')
    os.makedirs(dist, exist_ok=True)
    out = os.path.join(dist, f'sellersheet-workbuddy-connector-{v}.zip')
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for rel in ZIP_FILES:
            z.write(os.path.join(REPO, rel), rel)
        for d in ZIP_DIRS:
            for dirpath, dirnames, filenames in os.walk(os.path.join(REPO, d)):
                dirnames[:] = [x for x in dirnames if x not in ('__pycache__',)]
                for fn in filenames:
                    if fn == '.DS_Store':
                        continue
                    full = os.path.join(dirpath, fn)
                    z.write(full, os.path.relpath(full, REPO))
    print(out)


if __name__ == '__main__':
    if '--check' in sys.argv:
        check()
    elif '--zip' in sys.argv:
        make_zip()
    else:
        sync()
