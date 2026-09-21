# LESSONS

What one day of building this taught, 2.9.2026. Each one cost something; none should be paid twice.

1. **A global constant named `top` kills the whole page.** `const top = …` at script level
   collides with the window's own `top`, the browser throws at load, and nothing runs, while
   `node --check` says the file is fine. Name it `topbar`. In general, test in the browser,
   not only in node.

2. **Restarting a Flask server needs the socket to be free.** Werkzeug binds with
   SO_REUSEADDR; a port probe that does not is fooled by TIME_WAIT connections and steps to
   the next port. Probe with the same flag, and wait until the old process is really gone.

3. **Headless Chrome hangs on a page that keeps a live connection.** A server sent events
   stream never finishes, so `--virtual-time-budget` waits forever. Give the page a
   `?static=1` switch that skips the live feed for renders.

4. **`timeout` is not on macOS.** The GNU command is missing; a pipeline that relies on it
   silently does nothing. Use the page's own switches instead of external timeouts.

5. **Do not pipe a page into Python and also feed Python its script on stdin.** Fetch the
   page inside Python with urllib.

6. **Task notifications arrive as user records in the transcript.** They carry
   `origin.kind: task-notification` and `promptSource: system`; a typed message has
   `origin.kind: human`. Filter on that or the tool reads its own progress lines aloud.

7. **Thinking blocks and tool calls sit beside text blocks in the same record.** Take only
   `type: text` and skip `isSidechain` records, or subagents speak.

8. **Speechify truncates and bills past 2000 characters**, and every call returns exact
   word marks for free. So chunk under the cap and never re-time a Speechify clip.

9. **A `%d` in a log line is a crash when the id becomes a string.** The draft reader turned
   message ids into hashes; the log line in the sentence route then raised after the cache
   file was written, so the first request failed and the second was served from cache. Use
   `%s` for ids.

10. **Read the last line of Hammerspoon's output.** The first `hs -c` after a Hammerspoon
    restart prints "Loading extension" lines before the verdict.

11. **claude.ai refuses to be framed.** `X-Frame-Options: SAMEORIGIN`. Do not try; open it as
    a Chrome app window beside the page and tile with Hammerspoon.

12. **Status in the middle of the screen is a fright.** Waiting and errors go to one small
    line at the bottom right of the window, in the same quiet type whether good or bad.

13. **Make one sentence at a time.** A whole answer synthesised first means a long wait and a
    wasted spend on STOP. One sentence per call, the next made while the current plays, one
    cache file per sentence, and STOP aborts what is in flight.

14. **Patching a page already made beats synthesising again.** Speed, paused start and the
    reply box were all added to pages whose audio was inside the HTML. Never spend twice for
    a change of presentation.

15. **One letter is a command.** W pushes, R reads (R 1.5 at speed). Act on the letter, say
    nothing first, put the summary on the clipboard when done.

16. **Enter sends.** Marko, 3.9.2026: "when I press enter, it sends the message to you command
    enter. It's too much work. Only enter works." Shift+Enter and Option+Enter make a new
    line. A chord for the thing he does most is a tax on every answer.

17. **The band between the log and the entry box is his to set.** A grip above the composer
    drags the height; the textarea fills the band; the height is kept in localStorage per
    browser and read inside a try. Nothing appears or disappears, the ratio changes.

## 8.9.2026, the ears and the second voice

- The sister talks and listens through MANTRA_VOICE (voice.py imports ears, clone, timing) and
  starts their socket servers herself; she never needs voiced.py to be up, and she never builds a
  second model server. The choice of voice is the system's (~/.voice/voice.json), so the chip on
  her page changes how every app on the Mac talks.
- The microphone is the browser's (MediaRecorder, webm/opus), sent whole to /api/hear; ffmpeg
  makes it a 16 kHz wav there. The mouth closes when the ear opens: a reading is paused before the
  microphone starts, or the ears send the sister's own words back as Marko's.
- The space bar talks. Inside the entry box it still types, unless the box is empty. The reader's
  play and pause moved to P; arrows, Escape, plus and minus stayed.
- A cloned voice's clips are cached under a name that carries the voice and the model
  (<n>.<voice>-<model>.json), so Beatrice's and a clone's never mix and switching re-reads nothing.
- A wav uploaded to /api/hear must not be written under the name ffmpeg will write to: the input
  is <stamp>.in.<ext>, the output <stamp>.wav.
- A lock is not a queue. Three sentence requests racing for SYNTH_LOCK were made in whatever order
  the threads won it, so sentence 2 often came before sentence 0 and the first word waited for all
  three. One PriorityQueue keyed (priority, sentence number) makes them first to last; the page
  waits for three before the first word and keeps three requests in flight (Marko, 9.9.2026).
- The cloned voice cost five to nine seconds a sentence whatever its length: about 2.5 s fixed in
  the clone, then Whisper listening to the clip for the word timing. Run as two stages in a
  pipeline (the clone on n+1 while the ears time n) it is about 3.5 s a sentence, near speech. The
  card is queued the moment it arrives, before READ; only the clone, Beatrice is billed.
- The cache runs from the sentence playing to the end and the sentence heard is deleted (Marko:
  "as you read one sentence, delete that cache"). The page reports /at/<i>; the server moves its
  cursor there, drops background jobs behind it, queues i to the end. The voice's own store keeps
  the mp3 and its timing, so READ AGAIN is quick without the sister holding anything.
- Old cache goes before new cache comes (Marko, 9.9.2026: "check for the stalled or old cache ...
  before caching new it needs to delete old"). `sweep_cache` runs at the start of every reading
  and before a card is queued on arrival: a card folder whose newest file is older than a day is
  removed, so are the whole-message clips of the first design; the card being read is never
  touched. Without it the audio folder grew a folder per card forever, 22 MB in a week.
- A sentence asked for twice while it sits between the two stages was made twice, Whisper and
  all. An in-flight set drops the second entry; the first one's event serves both.

## 10.9.2026, the gear

- Every option lives under one gear at the lower right of the entry band, where the hand already is
  (Marko: "all options ... only live under the gear icon"). The top bar keeps the pane icon, the title,
  the project and the live dot; the side pane keeps the words and the sessions. The same gear is in the
  Ableton Command Guide's page, which is this page with the guide inside.
- A page rendered headless with the panel open: `?static=1&gear=1`.
- A job is a sentence in a voice (10.9.2026, found in the guide's page, the same code): keyed by card
  and number alone, a sentence made in one voice looked made for the next, and READ AGAIN after a
  voice change answered "the sentence was lost". The job key carries engine, voice and model; a
  voice change drops the old voice's unfinished jobs; the page restarts the reading at the sentence
  it was at, in the new voice.

## REMOTE CONTROL HAS NO LOCAL END — THE TRANSCRIPT IS THE MIRROR (21.9.2026)

Marko: "change architecture completely. You need to work with remote control from Claude, so when I
do /rc here, then this app is controlling the remote control protocol and showing everything as
remote control, because the remote control is mirroring everything. I just need to add read to
remote control and we are done. So it is a remote control client."

**LOOKED FOR, and it is not there.** Remote Control is one outbound socket from the CLI to
Anthropic: no listener on this Mac (`lsof` over every TCP port: nothing), no socket file, nothing in
`~/.claude` but `remoteControlAtStartup: true`, and only `CLAUDE_CODE_BRIDGE_SESSION_ID` in the
environment, which is a claude.ai URL and not a stream. A client would have to speak an
undocumented protocol to Anthropic's servers with his credentials. That road is closed.

**But what Remote Control mirrors is already on this disk.** Claude Code appends every session to
`~/.claude/projects/<slug>/<session>.jsonl` as it happens — the prompts he typed, the answers, and
every tool call with what it printed. That IS the terminal. So `transcript.py` reads it and turns it
into cards, and `chatd` follows the newest file once a second and appends whatever is new.

Same carbon copy, nothing to authenticate, nothing to reverse, and it keeps working when the network
does not.

Three things that matter in the reading:

- **Thinking is folded away in the terminal, so it is folded away here.** A `tool_result` is not a
  card of its own either: it belongs under the call that caused it, exactly as the terminal draws it.
- **A mirrored card is not spoken before he asks.** `append()` pre-synthesises every answer of
  Claude's for the cloned voice; with the mirror on, that would spend the voice on
  `Bash(git status)` a hundred times over. Cards with `source: mirror` skip the queue; READ still
  speaks them, which is the whole point of the page.
- **A new session is not a replay.** When the file changes under the mirror (he started another
  session) only what arrives from then on is shown. RECONNECT is the way to have the whole of it,
  and it is his press, not ours.

## CLEAR HAS TO CUT THE TRANSCRIPT, OR IT CLEARS NOTHING

Marko, 21.9.2026: *"when I press clear, it clears only the display. It doesn't actually clear the
cache because when I press reconnect, everything is back."*

He was right, and the cache was not ours. CLEAR did everything it promised — the cards in the
process, `messages.jsonl`, every wav and plan, the teleprompter pages — but the chat does not only
live there. Claude Code keeps the whole session in `~/.claude/projects/<slug>/<session>.jsonl`
whatever the page does, and RECONNECT reads that file from the top. So a clear followed by a
reconnect put the entire thrown-away chat straight back on the screen.

**A delete that another program can undo is not a delete.** CLEAR now writes the moment it happened
into `~/.tspeak/chat/cleared.txt` — UTC with a Z, the shape Claude Code stamps every record with, so
the two compare as plain strings — and `transcript.cards(path, since=...)` drops every record at or
before it. The watermark is read back at every start, so a restart cannot resurrect a cleared chat
either. The mirror still counts the whole file, so what the session says AFTER the cut arrives
normally: start from scratch, and then continue.

## THE CARD IS AS WIDE AS THE WINDOW

Marko, 21.9.2026: *"I usually need to scroll expand to the usable space of the web browser. Don't
work in this constraints of this kind of tabs you are creating. Try to avoid all scrolling, just
expand to the possible web page real estate."*

The card was `max-width:900px; margin:0 auto` — a column in the middle of a 2560px screen, with a
code block folded into a third of the glass and dragged sideways to be read. Two changes: the card
takes the width it is given (`max-width:100%`), and `pre` wraps instead of scrolling
(`white-space:pre-wrap; overflow-wrap:anywhere`), because a sideways scrollbar inside a card is the
one thing he can never reach with the wheel. The side pane, when it is open, simply gives the card
less. Nothing scrolls now but the log itself.

## HIS OWN WORDS ARRIVE IN A WRAPPER, AND THE WRAPPER WAS BEING FEARED

Marko, 21.9.2026: *"when I type my prompt directly into the Claude code inside the terminal, it is
not echoed in CCMC. I want everything echoed. It's like a remote view of this session."*

The mirror was not broken. Claude Code wraps what he types in
`<pasted_content id="…"> … </pasted_content id="…">` whenever it arrives as a paste or from another
device — which is most of the time, because he dictates. Both ends of the page threw away any user
text beginning with a `<`, a rule written to be rid of system reminders and hook noise, and his own
words went out with them: five prompts in one session, two echoed.

**Do not fear the wrapper, open it.** `transcript.typed()` unwraps a pasted block and strips the
machinery by name (`system-reminder`, `command-name`, `local-command-stdout`, `task-notification`,
the IDE tags), and both `transcript.cards()` and the `UserPromptSubmit` hook use it. Anything still
starting with a `<` after that is a wrapper nobody has taught her yet, and is still dropped.

Two more things fell out of it:

- `if text and not text.startswith('<') and len(text) > 1 or text.upper() in ('R','W','T')` reads as
  `(A and B and C) or D`. A one letter prompt was dropped unless it happened to be R, W or T — so
  answering a numbered list with `1` was never echoed. **A single character is a prompt too.**
- What he types now reaches the page down two roads, the hook instantly and the mirror a second
  later, and an answer comes by the Stop hook and the mirror both. `append()` drops an identical
  text from the same role inside thirty seconds: whichever road arrives first wins.
