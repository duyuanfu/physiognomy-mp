import { defineConfig } from "vite";
import uni from "@dcloudio/vite-plugin-uni";

function cleanDCloudDeadAssets() {
  return {
    name: "clean-dcloud-dead-assets",
    enforce: "post" as const,
    generateBundle(_: any, bundle: any) {
      for (const fileName in bundle) {
        if (fileName.endsWith(".wxss")) {
          const chunk = bundle[fileName];
          if ("source" in chunk && typeof chunk.source === "string") {
            chunk.source = chunk.source.replace(
              /https:\/\/cdn1\.dcloud\.net\.cn\/[^)]+\/shadow-grey\.png/g,
              ""
            );
          }
        }
      }
    }
  };
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [uni(), cleanDCloudDeadAssets()],
  server: {
    port: 5173,
    host: "0.0.0.0"
  }
});
