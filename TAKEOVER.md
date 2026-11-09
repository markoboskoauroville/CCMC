# TAKEOVER

How to bring MANTRA CHAT back on a fresh Mac, or hand it to someone else. Written 2.9.2026.
Marko's rule: if a step changed something on the machine and it is not in here, the step is
not finished.

## 1. What has to exist on the machine

* macOS with Google Chrome installed. The page opens only in Chrome, as an app window.
* Python 3.10 with Flask. On Marko's Mac it is pyenv: `/Users/markobosko/.pyenv/shims/python3`
  with `flask` and `requests` installed. Everything else is the standard library.
* `ffmpeg` and `node` are not needed by the chat. `node --check` was only used to test the page script.
* Hammerspoon with `hs.ipc` (the `hs` command at `/opt/homebrew/bin/hs`) for the side pane
  that tiles claude.ai beside the page. Without it the pane opens claude.ai in a tab instead.
* Claude Code, logged in, with Remote Control available.

## 2. The clone

```
git clone https://github.com/markoboskoauroville/CCMC ~/Developer/CCMC
```

On Marko's Mac `~/Developer/brain_break/tools/speak` is a symbolic link to this folder, so
older notes that name that path still work.

## 3. The key file

`~/Developer/api/speechify_api.txt`. One label line, then the key on the next line, blank
lines between. Keys start with `sk_` and are 46 characters. The file is never committed
anywhere; `brain_break/.gitignore` covers `*api*.txt`. The ring's state lives in
`~/.tspeak/ring.json` and holds fingerprints only.

## 4. The hooks

In `~/.claude/settings.json`, merged with whatever is there:

```json
{
  "remoteControlAtStartup": true,
  "hooks": {
    "SessionStart": [{"hooks": [{"type": "command", "timeout": 20, "statusMessage": "Starting MANTRA CHAT",
      "command": "/Users/markobosko/.pyenv/shims/python3 /Users/markobosko/Developer/CCMC/chat_hook.py start"}]}],
    "UserPromptSubmit": [{"hooks": [{"type": "command", "timeout": 5, "async": true,
      "command": "/Users/markobosko/.pyenv/shims/python3 /Users/markobosko/Developer/CCMC/chat_hook.py prompt"}]}],
    "Stop": [{"hooks": [{"type": "command", "timeout": 10, "async": true,
      "command": "/Users/markobosko/.pyenv/shims/python3 /Users/markobosko/Developer/CCMC/chat_hook.py stop"}]}]
  }
}
```

Check with `jq -e '.hooks.SessionStart[].hooks[].command' ~/.claude/settings.json`. Hooks
added while a session runs are picked up on the next session or after opening `/hooks` once.

## 5. First start

```
echo '{}' | /Users/markobosko/.pyenv/shims/python3 ~/Developer/CCMC/chat_hook.py start
```

This starts the server, writes `~/.tspeak/port.txt`, opens the page in Chrome, and prints
the greeting instructions. Then `curl http://127.0.0.1:8825/health` should answer with ok.

## 6. What lives where

```
~/.tspeak/port.txt              the port the server took (8825 unless busy)
~/.tspeak/ring.json             key ring state, fingerprints only
~/.tspeak/speed.txt             last reading speed of the R command
~/.tspeak/chat/messages.jsonl   every card, one JSON per line
~/.tspeak/chat/audio/<id>/      plan.json and one <n>.json per sentence, cached audio, swept after a day
~/.tspeak/inbox/<stamp>.json    what Marko sent from a page; the session watches this folder
~/.tspeak/out/<stamp>.html      pages made by the R command
~/.tspeak/chatd.log             the server log
```

Nothing generated ever lands in a repository.

## 7. The session side

At the start of every session Claude says, in a few short lines: "Remote control: starting."
"Chat interface: starting at http://127.0.0.1:8825." Then the rules: R reads the last answer
aloud (R 1.5 sets the speed), W pushes the watch folder, what is typed in MANTRA CHAT
reaches the session, READ under any card plays it with Beatrice, the pane icon opens
claude.ai beside. Then it arms a persistent Monitor on `~/.tspeak/inbox`:

```
cd ~/.tspeak/inbox; seen=$(ls *.json 2>/dev/null | sort); while true; do cur=$(ls *.json 2>/dev/null | sort);
new=$(comm -13 <(echo "$seen") <(echo "$cur")); for f in $new; do python3 -c "import json,sys;d=json.load(open(sys.argv[1]));
print('MARKO REPLIED on page %s at %s: %s'%(d.get('page'),d.get('time'),d.get('text','')))" "$f"; done; seen=$cur; sleep 1; done
```

The memory files that carry this live in
`~/.claude/projects/-Users-markobosko-Developer-brain-break/memory/`: `mantra-chat-interface.md`,
`r-trigger-read.md`, `status-line-not-overlays.md`.

## 8. Restarting the server

```
pkill -f 'CCMC/chatd.py'; sleep 2
echo '{}' | /Users/markobosko/.pyenv/shims/python3 ~/Developer/CCMC/chat_hook.py start
```

Wait for the old process to be gone before starting, or the new one binds the next port up.
The page in Chrome reconnects on its own; close the old app window if two are open.

## 9. Known limits

* claude.ai sends `X-Frame-Options: SAMEORIGIN`, so it can never sit inside the page. The
  side pane opens it as its own window beside.
* Chrome may block autoplay on the first READ after a fresh load; play on the pill is one tap.
* The Stop hook mirrors the whole visible text of a turn, interim lines included.
* Speechify's API is text to speech only; there is no transcription endpoint. Transcription
  stays with AssemblyAI, per the manifest.

## 10. What changed on 21.9.2026, and what a session must not undo

**CLEAR cuts Claude Code's transcript too.** The cards, `~/.tspeak/chat/messages.jsonl` and the
audio were never the whole chat: Claude Code keeps every session in
`~/.claude/projects/<slug>/<session>.jsonl` whatever the page does, and RECONNECT reads that file.
So CLEAR writes the moment it happened to **`~/.tspeak/chat/cleared.txt`** (UTC with a `Z`, the shape
Claude Code stamps every record with, so the two compare as plain strings), the mark is read back in
`main()` by `mark_load()`, and `transcript.cards(path, since=...)` drops every record at or before
it. Without this, clear-then-reconnect puts the whole thrown-away chat back on screen.

**His own words arrive in a wrapper.** Claude Code wraps a pasted or dictated prompt in
`<pasted_content id="..."> … </pasted_content id="...">`. Both ends of the page used to throw away
any user text beginning with `<`, a rule meant for system reminders, and his prompts went with it —
two of five echoed in one session. **`transcript.typed()` opens the wrapper and strips the machinery
by name** (`system-reminder`, `command-name`, `local-command-stdout`, `task-notification`, the IDE
tags); anything still starting with `<` afterwards is an unknown wrapper and is still dropped.
`transcript.cards()` and the `UserPromptSubmit` hook both use it. Do not reinstate a bare
`startswith('<')` test.

**Two roads, one card.** His words now reach the page by the hook (instantly) and by the mirror (a
second later), and an answer comes by the Stop hook and the mirror both. `append()` drops an
identical text from the same role inside thirty seconds. Removing that guard doubles every card.

**The page.** `--card` must stay defined: every drop-down asks for `background:var(--card)`, and for
a long time nothing defined it, so the declaration was invalid and the menus were transparent. It is
set in `:root` and repainted by `applyScheme()` from the scheme's panel colour. The card is
`max-width:100%` and `pre` wraps (`pre-wrap`, `overflow-wrap:anywhere`) — he cannot reach a sideways
scrollbar inside a card. There is no READ ALL button: the card body is the button, and a click reads
**the whole card** from the sentence clicked. Per-block reading was removed on his instruction; do
not put it back.

**The bar** holds VOICE (the switcher: Beatrice and every cloned voice, calling the same `setVoice`
as the gear panel), RECONNECT, CLEAR and MENU.


## From the former README (9.11.2026)

# CCMC

A local chat interface for Claude Code, built for one person who reads by ear.

It is a Flask page on the Mac, MANTRA CHAT, that follows every Claude Code session in every
project. What Marko types and what Claude answers appear on the page as cards. Every card
has READ: the text is spoken by Speechify's Beatrice, one sentence at a time, in a floating
Beatrice window where the sentence being read is pushed to the top edge and the spoken word
is lit red. A floating control pill carries previous and next sentence, play and pause,
speed, font size, and X to end. What is typed on the page reaches the Claude Code session.
A side pane opens claude.ai beside the page, tiled at the golden section. Every option lives under the
gear at the lower right of the entry band, and nowhere else (Marko, 10.9.2026): the voice, AUTO VOICE,
CLONE MY VOICE, claude.ai beside, the top bar.

Nothing here is invented. It was recombined on 2.9.2026 from code that already existed in
Marko's other projects: the reader script's offline player, the Streamlit project's key ring
and Speechify provider, the sample player's port handling.

## The menu at the top, and the mirror (21.9.2026)

MENU, top right of the page, holds three things and no more:

- **RECONNECT** — Marko: *"sometimes when you are running and I run the CCMC after that, it doesn't
  pick up what is going on in the terminal. Reconnect means starting from what is on the screen
  displayed and then continue."* It reads the session's own transcript off disk and rebuilds the log
  from it: every prompt, every answer, every tool call with the first lines of what it printed, in
  the terminal's own order. The audio is not touched.
- **EVERYTHING HE TYPES IS ECHOED** — Marko: *"I want everything echoed. It's like a remote view of
  this session."* Claude Code wraps a pasted or dictated prompt in `<pasted_content …>`, and the
  page used to drop anything starting with a `<` along with the system reminders.
  `transcript.typed()` opens the wrapper and strips only the machinery by name, so his words come
  through — down two roads, the `UserPromptSubmit` hook instantly and the mirror a second later,
  with an identical card inside thirty seconds dropped so nothing is said twice.
- **MIRROR** — follows that file live, once a second, so the page is a carbon copy of the terminal
  without a hook in the middle. On by default. (Remote Control has no local end to attach to;
  `LESSONS.md` has the whole reason.)
- **VOICE** — the voice switcher on the bar, Marko's ask of 21.9.2026: *"one more command in the top
  of CCMC, and this is a voice switcher. Since we are using voices, we need to have a voice switcher
  there."* The button carries the name of whoever is talking, so the bar answers the question
  without being opened, and the list under it holds Beatrice and every cloned voice on the Mac. A
  reading already going on carries on from its own sentence in the new voice.
- **CLEAR THE WHOLE CHAT** — Marko: *"one clear command to clear the whole chat and start from the
  scratch. Now I have chats from last year. It should clear it from the screen and from the memory,
  also included all audio files generated for that chat."* Every card, the file they are kept in,
  every wav and plan the voice made for them, and the teleprompter pages under `~/.tspeak/out`. It
  asks once, because it cannot be undone. **His own microphone recordings are never touched.**
  It also cuts Claude Code's own transcript at that moment and writes the cut to
  `~/.tspeak/chat/cleared.txt`, so RECONNECT can never read the thrown-away chat back in — Marko,
  21.9.2026: *"when I press clear, it clears only the display. It doesn't actually clear the cache
  because when I press reconnect, everything is back."* A cleared chat stays cleared across a
  restart of the server and of the Mac; what the session says after the cut still arrives.

**The log does not scroll under his hand any more** (*"only the window is not scrolling, I am
scrolling it manually"*): a new card is appended where it belongs and the view stays where he put
it, unless he is already standing at the bottom.

## The files

| file | what |
|---|---|
| `chatd.py` | the Flask server, 127.0.0.1 only, base port 8825, port in `~/.tspeak/port.txt` |
| `chat_page.py` | the page: side pane, cards, composer, the Beatrice window, the pill |
| `chat_hook.py` | the Claude Code hooks: SessionStart, UserPromptSubmit, Stop |
| `ring.py` | the Speechify key ring: sticky working key, dead on 401 402 403, cool on 429, fingerprints only on disk |
| `speechify.py` | one call to `api.sws.speechify.com` with word marks, voice `beatrice_32`, model `simba-3.2` |
| `lastanswer.py` | reads Claude's last answer from the session transcript, strips markdown, splits sentences |
| `page.py` | the standalone reading page used by the R command |
| `tspeak.py` | the R command: read the last answer into a self contained page, local and remote |
| `test_speak.py` | tests without spend: `python3 test_speak.py` |

## How it runs

Three hooks in `~/.claude/settings.json` run `chat_hook.py` for every project:

* **SessionStart** starts `chatd.py` if `/health` does not answer, opens the page in Chrome
  as an app window if nobody has it open, posts a session line, and prints into Claude's
  context the greeting to say and the inbox watch to arm.
* **UserPromptSubmit** mirrors what was typed in the terminal.
* **Stop** mirrors Claude's finished answer out of the transcript.

The composer posts to `/api/send`, which writes `~/.tspeak/inbox/<stamp>.json`; the session
keeps a Monitor on that folder and treats each file as a message from Marko.

READ is progressive. `POST /api/read/<id>/plan` returns the sentences. `POST
/api/read/<id>/sent/<n>` makes exactly one sentence, one Speechify call, one cache file under
`~/.tspeak/chat/audio/<id>/`. The page plays sentence 0 as soon as it arrives and asks for
n+1 the moment n starts playing. STOP aborts what is in flight and asks for nothing more.
`POST /api/read/draft/plan` does the same for text not yet sent, keyed by a hash of the text.
Before a card is cached, at the plan and when the card arrives, `sweep_cache` deletes every
cache entry under `~/.tspeak/chat/audio/` untouched for a day, except the card being read.

## Rules that shaped it

* Never print a key. The key file is `~/Developer/api/speechify_api.txt`, a label above each
  key; the ring stores sha256 fingerprints, never keys.
* Status goes in a small line at the bottom right of the window, never in the middle of the
  screen, never a fright.
* The sentence being read sits at the top edge, instantly. A smooth scroll is a delay by
  another name.
* Colour changes nothing about layout, weight does. The word is lit by colour only.
* Chrome only, as an app window: no address bar, no menus. The top bar hides itself.
* No dashes as punctuation in anything written for Marko.

See `TAKEOVER.md` to rebuild it on a fresh Mac and `LESSONS.md` for what was learned.
