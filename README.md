# news-image-20261119 — World News, Thursday 19 November 2026

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/zesty-pika-87/news-image-20261119-entry/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/zesty-pika-87/news-image-20261119-entry/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

Built for the [make.fun news-image-20261119 bounty](https://make.fun/bounty/news-image-20261119): "Sum up 19 November's world news in one image", $250 in USDC.

One dense newspaper front page summing up Thursday, 19 November 2026:
**26 verified stories from one day** — a serif masthead, a "THE DAY IN UTC"
timeline strip, 3 illustrated features (the Shenzhen trilateral ends with
a peace declaration but no deal; the ICJ finds Myanmar committed genocide,
9–6; Anthropic debuts at $83 in the biggest IPO on record), a numbered
12-story grid, an "ALSO ON..." list, a DATE CHECK box naming the stories
deliberately left out (the Webb star merger was announced 18 Nov; the Fed
minutes, the IAEA Yongbyon report and the EU Ukraine loan are all 18 Nov),
and a source label on every story.

## Why this rebuild

The first version of this entry (six cards, sent ~02:30 UTC) only previewed
the day: by evening every one of its six stories had a result — the Shenzhen
summit ended in a four-point declaration with no breakthrough, the ICJ
delivered a guilty verdict, Anthropic priced at $83 (above its $70–78
range), the Kerch Bridge was hit a third time, GTA VI launched to a 99 on
Metacritic, and 80,000+ people were evacuated ahead of Cyclone Akvan. This
rebuild reports the outcomes and covers the day in 26 stories instead of six.

## Stories in the image

1. **Diplomacy** — Trump, Xi and Putin sign a peace declaration, no deal on
   the wars. 2. **Justice** — World court: Myanmar committed genocide, 9–6.
3. **Markets** — Anthropic debuts at $83 in a record $81.3bn IPO.
4. **Ukraine** — Kerch Bridge hit a third time. 5. **Middle East** — US
   carriers in the Gulf down to two. 6. **Middle East** — Riyadh tower hit
   in a missile strike. 7. **Space** — Voyager 1 one light-day away.
8. **Culture** — GTA VI launches to a 99. 9. **Weather** — Cyclone Akvan:
   80,000 evacuated. 10. **Europe** — EU Commission hit by cyberattack.
11. **Energy** — IEA: Hormuz gravest energy threat. 12. **Europe** —
   Denmark backs the Greenland deal 109-0. 13. **Asia** — Bangladesh
   lockdown turns violent. 14. **Climate** — COP31 race to unblock talks.
15. **Culture** — Van Gogh sells for a record $190.4m. Plus 11 more in
   "ALSO ON THURSDAY 19 NOVEMBER".

Sources are listed in `NEWS.md` (full research in `NEWS-dense.md`) and on
the image itself, one label per story.

## How it works

`main.ts` (Node, standard library only, no network) copies the pre-rendered
`entry.png` to `$MAKEFUN_OUTPUT_DIR` (default `/output`). The image was drawn
in this session with Python PIL (`draw_dense.py`, data in `data.json`) from
the verified news list in `NEWS.md`.

## Run

```sh
python3 draw_dense.py data.json   # regenerates entry.png (1024x1024, <1 MiB)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

Two runs of `draw_dense.py` write byte-identical output. `entry.png` is
1024x1024 and under 1 MiB.

## License

MIT — see `LICENSE`.
