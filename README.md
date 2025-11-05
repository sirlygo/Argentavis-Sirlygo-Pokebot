
# Mew Pokébot Wip

This is a discord bot that allows random pokemon to spawn in a server. as users chat, they accrue battle points that they can spend to buy items.

## Installation

1. **Install Python** – Use Python 3.10 or newer. Confirm it is available by running `python --version`.
2. **Create a virtual environment** – For example, `python -m venv .venv` followed by `source .venv/bin/activate` on macOS/Linux or `.venv\Scripts\activate` on Windows.
3. **Install dependencies** – With the environment active, install packages via `pip install -r requirements.txt`.
4. **Set up bot token** – Create a Discord bot in the Developer Portal and save its token to a file named `token` in the project root (same folder as `main.py`).
5. **Run the bot** – Start the bot with `python main.py`. The bot expects the bundled `data/` directory to remain alongside the code so encounters, moves, and items load correctly.

Optional: if you want to isolate persistent data from the repository checkout, update the paths defined in `users.py` and `economy.py` to point at your own writable directories.


## Changelog


#### 0.1.0


* Original release.

#### 0.1.1


* Hardcoded a home channel

* Doubled pokemon spawn rate

* Catching a pokemon autosaves your profile

* You can see your pokeballs count on your profile

* updated admin help

