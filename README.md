# news-image-20261119 — World News, Thursday 19 November 2026

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/zesty-pika-87/news-image-20261119-entry/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/zesty-pika-87/news-image-20261119-entry/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

Built for the [make.fun news-image-20261119 bounty](https://make.fun/bounty/news-image-20261119): "Sum up 19 November's world news in one image", $250 in USDC.

One image summing up the world's news of Thursday, 19 November 2026:
six stories, across regions and fields, on a single 1024x1024 infographic.

## Stories in the image

1. **Diplomacy** — Trump, Xi and Putin meet in Shenzhen for a first-ever
   trilateral summit, with nuclear arms and Iran on the agenda.
2. **Justice** — The International Court of Justice delivers its final
   verdict on whether Myanmar committed genocide against the Rohingya.
3. **Markets** — Anthropic, the Claude-maker, begins trading on Nasdaq,
   valued at up to $1.4 trillion in its blockbuster debut.
4. **Ukraine** — The Crimean Bridge is hit for a third time in a week;
   traffic halts days after its road deck fell into the strait.
5. **Culture** — GTA VI launches after a 13-year wait, returning players
   to Vice City at $79.99.
6. **Weather** — Severe Cyclone Akvan bears down on Andhra Pradesh and
   Odisha; red alerts, schools shut, landfall due Friday.

Sources are listed in `NEWS.md` and in the image footer.

## How it works

`main.ts` (Node, standard library only, no network) copies the pre-rendered
`entry.png` to `$MAKEFUN_OUTPUT_DIR` (default `/output`). The image was drawn
in this session with Python PIL from the verified news list in `NEWS.md`.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

Two runs write byte-identical output. `entry.png` is 1024x1024 and under 1 MiB.

## License

MIT — see `LICENSE`.
