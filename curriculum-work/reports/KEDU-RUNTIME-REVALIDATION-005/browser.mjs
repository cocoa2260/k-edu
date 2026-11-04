import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { resolve } from "node:path";

const [url, dependencies] = process.argv.slice(2);
const requireBrowser = createRequire(resolve(dependencies, "package.json"));
const requireRuntime = createRequire(resolve(process.env.PLAYWRIGHT_ROOT, "package.json"));
const { chromium } = requireRuntime("playwright");
const swagger = requireBrowser("swagger-ui-dist");
const hash = text => createHash("sha256").update(text).digest("hex");
const version = async (requireFrom, name) => {
  try {
    return requireFrom(name + "/package.json").version;
  } catch {
    const entry = requireFrom.resolve(name);
    return JSON.parse(await readFile(resolve(entry, "../../../package.json"), "utf8")).version;
  }
};
const { message } = JSON.parse(readFileSync(0, "utf8"));
const assetBase = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/";
const assets = new Map([
  [assetBase + "swagger-ui-bundle.js", "application/javascript"],
  [assetBase + "swagger-ui.css", "text/css"],
]);
const browser = await chromium.launch({
  executablePath: resolve(dependencies, "chromium"), headless: true,
});
try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const served = {};
  await page.route("**/*", async route => {
    const requestUrl = route.request().url();
    if (requestUrl.startsWith(url + "/")) return route.continue();
    if (!assets.has(requestUrl)) return route.abort();
    const name = requestUrl.slice(assetBase.length);
    const body = await readFile(resolve(swagger.getAbsoluteFSPath(), name));
    served[name] = hash(body);
    await route.fulfill({ body, contentType: assets.get(requestUrl) });
  });
  const docs = await page.goto(url + "/docs");
  assert.equal(docs.status(), 200);
  const operation = page.locator(".opblock").filter({ hasText: "/ai/chat" });
  await operation.locator(".opblock-summary").click();
  await operation.getByRole("button", { name: "Try it out" }).click();
  const input = operation.locator("textarea").first();
  async function submit(value) {
    await input.fill(JSON.stringify({ message: value }));
    const received = page.waitForResponse(r =>
      r.url() === url + "/ai/chat" && r.request().method() === "POST", { timeout: 180000 });
    await operation.getByRole("button", { name: "Execute" }).click();
    const response = await received;
    const body = await response.json();
    assert.deepEqual(response.request().postDataJSON(), { message: value });
    const rendered = operation.locator(".live-responses-table .response-col_description pre").last();
    await rendered.waitFor();
    await page.waitForFunction(
      ({ renderedBody }) => {
        const blocks = document.querySelectorAll(".live-responses-table .response-col_description pre");
        return Array.from(blocks).some(block => {
          try { return JSON.stringify(JSON.parse(block.textContent)) === renderedBody; }
          catch { return false; }
        });
      },
      { renderedBody: JSON.stringify(body) },
    );
    return { status: response.status(), body };
  }
  const valid = await submit(message);
  assert.equal(valid.status, 200);
  assert.equal(valid.body.provider, "hf-cpu");
  assert.equal(valid.body.model, "Qwen/Qwen3-0.6B");
  assert.equal(typeof valid.body.answer, "string");
  const blank = await submit("   ");
  assert.equal(blank.status, 422);
  assert.equal(Object.keys(served).length, 2);
  process.stdout.write(JSON.stringify({
    browser: browser.version(),
    playwright: await version(requireRuntime, "playwright"),
    swagger_ui: await version(requireBrowser, "swagger-ui-dist"),
    asset_sha256: served, docs_status: docs.status(),
    success_status: valid.status, blank_status: blank.status,
    input_sha256: hash(message), displayed_answer_sha256: hash(valid.body.answer),
    success_rendered: true, blank_rendered: true,
  }) + "\n");
} finally {
  await browser.close();
}
