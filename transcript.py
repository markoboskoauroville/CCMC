#!/usr/bin/env python3
"""transcript.py: CLAUDE CODE'S TERMINAL, READ OFF DISK AND TURNED INTO CARDS.

Marko, 21.9.2026, two asks that are one job:

    "Please display everything from this chat in the terminal view window absolutely the same ...
     same format everything, I want to see exactly this text ... an exact carbon copy of what is
     happening here. Only when I hover over any block of text it will give me blob read."

    "and also there is a reconnect. Sometimes when you are running and I run the CCMC after that,
     it doesn't pick up what is going on in the terminal. Reconnect means starting from what is on
     the screen displayed and then continue."

Claude Code writes every session to a JSONL file under ~/.claude/projects/<slug>/<id>.jsonl, one
record a line, and that file IS the terminal: the prompts he typed, the answers, and every tool
call with what it printed. So the page does not need a new wire into the session - it needs to read
that file. RECONNECT reads it whole and rebuilds the log; after that the hooks keep it live.

WHAT IS KEPT AND WHAT IS DROPPED, and the dropping is the point. The terminal shows a stream of
three things: what Marko typed, what Claude said, and a line per tool with the first of its output.
Thinking is folded away in the terminal, so it is folded away here. A tool_result is not a card of
its own: it belongs under the call that caused it, exactly as the terminal draws it with its corner.

    MARKO   what he typed
    CLAUDE  the answer, and under it, in a code block, the tools it used:
                > Bash(Show git status)
                  L  On branch main
                     nothing to commit
                     ... +12 lines

Pure python3 from the Mac, no Flask, no imports of chatd: `python3 transcript.py <file>` prints the
cards so the shape can be checked without the page.
"""
import glob
import json
import os
import sys

PROJECTS = os.path.expanduser('~/.claude/projects')
HEAD_LINES = 6            # how much of a tool's output the terminal shows before it folds
WIDTH = 160               # a long line is cut, as the terminal cuts it


def newest(session=''):
    """The transcript to read: the named session if it is there, else the file written last."""
    if session:
        hit = glob.glob(os.path.join(PROJECTS, '*', session + '.jsonl'))
        if hit:
            return hit[0]
    files = glob.glob(os.path.join(PROJECTS, '*', '*.jsonl'))
    if not files:
        return ''
    return max(files, key=lambda p: os.path.getmtime(p))


def records(path):
    if not path or not os.path.isfile(path):
        return []
    out = []
    with open(path, encoding='utf-8', errors='replace') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return out


def _blocks(rec):
    c = (rec.get('message') or {}).get('content')
    if isinstance(c, str):
        return [{'type': 'text', 'text': c}]
    return c if isinstance(c, list) else []


def _flat(value):
    """A tool result, whatever shape it arrives in, as plain text."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = []
        for b in value:
            if isinstance(b, dict):
                if b.get('type') == 'text':
                    parts.append(str(b.get('text') or ''))
                elif b.get('type') == 'image':
                    parts.append('[an image]')
            else:
                parts.append(str(b))
        return '\n'.join(p for p in parts if p)
    if value is None:
        return ''
    return str(value)


def _call_line(block):
    """`Bash(Show git status)` - the tool and the one thing worth reading about the call."""
    name = str(block.get('name') or 'tool')
    args = block.get('input') if isinstance(block.get('input'), dict) else {}
    for key in ('description', 'file_path', 'path', 'pattern', 'command', 'prompt', 'url', 'query'):
        v = args.get(key)
        if isinstance(v, str) and v.strip():
            v = v.strip().split('\n')[0]
            if len(v) > 90:
                v = v[:89] + '…'
            return '%s(%s)' % (name, v)
    return name


def _result_lines(text):
    if not text:
        return []
    lines = [ln.rstrip() for ln in text.split('\n')]
    while lines and not lines[0]:
        lines.pop(0)
    shown = [(ln[:WIDTH - 1] + '…') if len(ln) > WIDTH else ln for ln in lines[:HEAD_LINES]]
    if len(lines) > HEAD_LINES:
        shown.append('… +%d lines' % (len(lines) - HEAD_LINES))
    return shown


def cards(path, limit=0, since=''):
    """The transcript as [{role, text}], oldest first, in the terminal's own order.

    `since` is CLEAR's watermark: an ISO UTC stamp ('2026-09-21T09:12:33.000Z') written the moment
    Marko threw the chat away. Claude Code keeps the whole session in the file whatever the page
    does, so without this RECONNECT would read the thrown-away chat straight back in - which is
    exactly the bug he found, 21.9.2026: "when I press clear, it clears only the display. It
    doesn't actually clear the cache because when I press reconnect, everything is back." Every
    record stamped at or before the watermark is gone for good; a record with no stamp at all
    cannot be shown to be after it, so it goes too.
    """
    recs = records(path)
    if since:
        recs = [r for r in recs if str(r.get('timestamp') or '') > since]
    results = {}
    for r in recs:
        if r.get('type') != 'user':
            continue
        for b in _blocks(r):
            if isinstance(b, dict) and b.get('type') == 'tool_result':
                results[b.get('tool_use_id')] = _flat(b.get('content'))

    out = []
    for r in recs:
        kind = r.get('type')
        if kind == 'user':
            text = ''
            for b in _blocks(r):
                if isinstance(b, dict) and b.get('type') == 'text':
                    text += b.get('text') or ''
                elif isinstance(b, str):
                    text += b
            text = text.strip()
            # a tool result, a hook's noise or a system reminder is not something he typed
            if not text or text.startswith('<') or r.get('isMeta'):
                continue
            out.append({'role': 'marko', 'text': text})
        elif kind == 'assistant':
            said, tools = [], []
            for b in _blocks(r):
                if not isinstance(b, dict):
                    continue
                if b.get('type') == 'text' and (b.get('text') or '').strip():
                    said.append(b['text'].strip())
                elif b.get('type') == 'tool_use':
                    lines = ['▸ ' + _call_line(b)]
                    for ln in _result_lines(results.get(b.get('id'), '')):
                        lines.append('    ' + ln)
                    tools.append('\n'.join(lines))
            text = '\n\n'.join(said)
            if tools:
                text = (text + '\n\n' if text else '') + '```\n' + '\n'.join(tools) + '\n```'
            if text.strip():
                out.append({'role': 'claude', 'text': text})
    if limit and len(out) > limit:
        out = out[-limit:]
    return out


if __name__ == '__main__':
    p = sys.argv[1] if len(sys.argv) > 1 else newest()
    got = cards(p)
    print('%s\n%d cards\n' % (p, len(got)))
    for c in got[-6:]:
        print('--- %s\n%s\n' % (c['role'].upper(), c['text'][:600]))
