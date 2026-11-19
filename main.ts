// news-image-20261119 entrypoint.
// Rebuilt 19 Nov as a dense newspaper front page: 26 verified stories from one day
// (masthead + UTC timeline + 3 illustrated features + numbered grid + ALSO ON list
// + DATE CHECK box + a source label per story), drawn by draw_dense.py from data.json.
// Copies the pre-rendered entry.png into $MAKEFUN_OUTPUT_DIR
// (default /output). Node standard library only, no network.
// Deterministic: the output bytes are always identical to entry.png.
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

// Resolve relative output dirs against the current working directory,
// so `MAKEFUN_OUTPUT_DIR=out` works from anywhere.
const outDir = resolve(process.env.MAKEFUN_OUTPUT_DIR || "/output");
const here = dirname(fileURLToPath(import.meta.url));
const source = resolve(join(here, "entry.png"));
const target = join(outDir, "entry.png");

mkdirSync(outDir, { recursive: true });
// Refuse to overwrite the source file itself if the output dir is the repo.
if (source === resolve(target)) {
  throw new Error("MAKEFUN_OUTPUT_DIR must not be the entry directory");
}
copyFileSync(source, target);
console.log(`entry.png -> ${target}`);
