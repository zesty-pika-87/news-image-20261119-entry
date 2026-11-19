// news-image-20261119 entrypoint.
// Copies the pre-rendered entry.png into $MAKEFUN_OUTPUT_DIR
// (default /output). Node standard library only, no network.
// Deterministic: the output bytes are always identical to entry.png.
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");

mkdirSync(outDir, { recursive: true });
copyFileSync(source, join(outDir, "entry.png"));
console.log(`entry.png -> ${join(outDir, "entry.png")}`);
