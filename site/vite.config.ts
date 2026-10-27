import { defineConfig, type Plugin } from "vite";
import { cpSync, createReadStream, existsSync, statSync } from "node:fs";
import { extname, join, normalize, resolve } from "node:path";

// The site reads the repository's data/ and assets/web/ directly: served as they are while
// developing, copied into the build. There is only ever one copy of the data.
const ROOT = resolve(import.meta.dirname, "..");
const SHARED = ["data", "assets/web", "assets/site"];
const TYPES: Record<string, string> = { ".json": "application/json", ".jpg": "image/jpeg", ".md": "text/markdown; charset=utf-8" };

function sharedFiles(): Plugin {
  return {
    name: "shared-files",
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const path = decodeURIComponent((req.url ?? "").split("?")[0]).replace(/^\/+/, "");
        const file = normalize(join(ROOT, path));
        if (!SHARED.some((d) => path.startsWith(d + "/")) || !file.startsWith(ROOT) || !existsSync(file) || !statSync(file).isFile()) return next();
        res.setHeader("Content-Type", TYPES[extname(file)] ?? "application/octet-stream");
        createReadStream(file).pipe(res);
      });
    },
    closeBundle() {
      for (const d of SHARED) cpSync(join(ROOT, d), join(import.meta.dirname, "dist", d), { recursive: true });
    },
  };
}

export default defineConfig({
  base: "./", // works at lifeinavan.github.io/EuropeAfricaVanTour/ and locally
  plugins: [sharedFiles()],
  server: { port: 5173 },
  worker: { format: "es" },
  build: { chunkSizeWarningLimit: 1200 }, // MapLibre alone is about 1 MB
});
