import { stitch } from "@google/stitch-sdk";
import fs from "node:fs/promises";
import path from "node:path";
import { execFileSync } from "node:child_process";

const projectId = "2578042310822076666";

const requestedIds = [
  "3b9696c0512c4a97aaf197e000eba2ee",
  "ec422da8aaf54eacad3704a0f9dab211",
  "fc9c2ea9b6184fc982f75a1bf5d7e424",
  "7d23e3699ca2429495e5232dc34de734",
  "2db52102a35f481e9f04652a2823d351",
];

const outDir = path.resolve("ai-purchase-order-assistant");
await fs.mkdir(outDir, { recursive: true });

try {
  const project = stitch.project(projectId);
  const screens = await project.screens();

  console.log("Screens accessible:", screens.length);
  console.log(screens.map((s) => `${s.id} | ${s.screenId}`).join("\n"));

  for (let i = 0; i < requestedIds.length; i++) {
    const id = requestedIds[i];
    const screen = screens.find((s) => s.id === id || s.screenId === id);

    if (!screen) {
      console.error(`Screen not found in project: ${id}`);
      continue;
    }

    const dir = path.join(outDir, `screen-${i + 1}`);
    await fs.mkdir(dir, { recursive: true });

    try {
      const [htmlUrl, imageUrl] = await Promise.all([
        screen.getHtml(),
        screen.getImage(),
      ]);

      execFileSync(
        "curl",
        ["-fL", "--retry", "2", htmlUrl, "-o", path.join(dir, "screen.html")],
        { stdio: "inherit" },
      );

      execFileSync(
        "curl",
        ["-fL", "--retry", "2", imageUrl, "-o", path.join(dir, "screen.png")],
        { stdio: "inherit" },
      );

      console.log(`Downloaded: ${id}`);
    } catch (error) {
      console.error(`Download failed for ${id}:`, error.message);
    }
  }
} catch (error) {
  console.error("Stitch request failed:", error.message);
  process.exitCode = 1;
}

console.log("Output folder:", outDir);
id = "d8k1qa";
