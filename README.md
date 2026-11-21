# Sum up 20 November's world news in one image

A newspaper front page for Friday 20 November 2026 — the day's five
biggest stories, drawn by a program — written for the make.fun bounty
**"Sum up 20 November's world news in one image"**
(`news-image-20261120`).

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Nadanese93/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/Nadanese93/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

## The image

A front page for Friday 20 November 2026:

- **Hero — KYIV UNDER FIRE:** Russia's barrage of 400 drones and
  110 missiles on Kyiv; two missiles land in NATO member Poland.
- **GENOCIDE VERDICT:** the UN court finds Myanmar responsible for
  genocide against the Rohingya — a first.
- **HORMUZ BURNS:** the US blockade and tanker fires in the Strait
  of Hormuz; the biggest oil shock on record.
- **AI ROUT:** the S&P 500 slides 3.7% into correction on the chip
  sell-off.
- **THREE LEADERS, ONE TABLE:** Trump, Xi and Putin meet in Shenzhen
  — the first trilateral summit.
- **Footer ticker:** a 6.7 quake shakes Peru; COP31 talks run past
  their deadline in Antalya.

## How to run

Requires Python 3.13 (standard library only, no network, deterministic).

```bash
MAKEFUN_OUTPUT_DIR=/output python3 main.py
```

This writes the front page to `$MAKEFUN_OUTPUT_DIR/entry.png`
(1024×1024 PNG, well under the 1 MiB cap). Two runs write identical
bytes.

## License

MIT — see [LICENSE](LICENSE).
