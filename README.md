# codechallenge-test-client

A minimal **bot client** for [The Code Challenge](https://codechallenge.net.ar).
It connects to the match server over a websocket using your bot's token,
auto-accepts challenges, and plays. Use it as a starting point (and a smoke
test) for writing your own bot.

## How it works

Your bot authenticates with its **token** (from **My Bots** on the web) and
opens a websocket to the server:

```
wss://server.codechallenge.net.ar/ws?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoibmljb2xhcy1tYXJjb3NiZWx0cmFuIn0.ElacNkKpd_rkAncobm7FSPd5ef77dQydOK8eYxBkBEA                          # production
ws://localhost:5000/ws?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoibmljb2xhcy1tYXJjb3NiZWx0cmFuIn0.ElacNkKpd_rkAncobm7FSPd5ef77dQydOK8eYxBkBEA                          # local
```

The server then sends events and the bot replies with actions (JSON):

| Event          | The bot does…                                                        |
| -------------- | -------------------------------------------------------------------- |
| `list_users`   | nothing (just who's online)                                          |
| `challenge`    | replies `accept_challenge` with the `challenge_id`                   |
| `your_turn`    | plays a move — replies `move` with the move data + the `turn_token`  |
| `game_over`    | nothing (the match ended)                                            |

> The example move logic in `run.py` plays **Connect 4** (it picks a random
> column). That `process_your_turn` / `process_move` part is exactly where you
> put your own strategy — and where you adapt it to another game's action shape.

## Requirements

- Python 3.9+
- `websockets` (see `requirements.txt`)

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run.py <YOUR_BOT_TOKEN>
```

Get `<YOUR_BOT_TOKEN>` from **My Bots** in the web app. By default `run.py`
connects to the production server; switch the `uri` in `run.py` to the
`localhost` line to play against a local server.

> `start.sh` / `start_dev.sh` are convenience runners kept out of git because
> they may embed your personal token.

### What to do after running the bot?

Once you run `./start.sh <YOUR_BOT_TOKEN>` or `python run.py <YOUR_BOT_TOKEN>`, your bot will connect to the server and wait in the background. It will **not** start games automatically.

To see your bot in action:
1. Keep the terminal open and the bot running.
2. Go to the web app [https://codechallenge.net.ar](https://codechallenge.net.ar) and log in.
3. Find your bot or another user in the active users/bots list.
4. Send a challenge to another user, or have another bot/user challenge your bot.
5. Your bot will automatically accept incoming challenges and play its moves (by default, a Connect 4 bot making random moves).
6. Check your terminal to see the incoming (`<`) events and outgoing (`>`) moves in real time!

## Tests

`test_run.py` covers the event handling, the move replies and the game log,
using a fake websocket — nothing connects to the network.

```bash
python -m unittest discover -v
```

They also run on GitHub Actions for every push and pull request
(`.github/workflows/tests.yml`), on Python 3.9 and 3.12.

## Game logs

When a match ends, the client writes a **`game_<game_id>.log`** in the working
directory with everything that happened: each event received (`<`) and action
sent (`>`), as JSON, ending with the `game_over` event. Useful for replaying or
debugging a match. These files are git-ignored.

```
< {"event": "your_turn", "data": {"board": "...", "game_id": "g_9f", "turn_token": "t_01", ...}}
> {"action": "move", "data": {"game_id": "g_9f", "turn_token": "t_01", "col": 3}}
...
< {"event": "game_over", "data": {"board": "...", "game_id": "g_9f", ...}}
```

## Write your own bot

You don't need this client — any websocket client works. The contract is:

1. Connect to `ws(s)://<server>/ws?token=<your bot token>`.
2. On `challenge`, send `{"action": "accept_challenge", "data": {"challenge_id": "..."}}`.
3. On `your_turn`, read `data` (board / game state, `game_id`, `turn_token`) and
   send your move: `{"action": "move", "data": { ... , "turn_token": "..." }}`.
