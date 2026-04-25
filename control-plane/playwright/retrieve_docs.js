const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function main() {
  const targetUrl = process.argv[2];
  if (!targetUrl) {
    console.error('Usage: node retrieve_docs.js <url>');
    process.exit(1);
  }

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });

  const title = await page.title();
  const bodyText = await page.locator('body').innerText();

  const outDir = path.resolve(__dirname, '../reports');
  fs.mkdirSync(outDir, { recursive: true });
  const stamp = new Date().toISOString().replace(/[:.]/g, '-');
  const outPath = path.join(outDir, `docs-${stamp}.json`);

  fs.writeFileSync(
    outPath,
    JSON.stringify(
      {
        fetched_at: new Date().toISOString(),
        url: targetUrl,
        title,
        content_preview: bodyText.slice(0, 5000),
      },
      null,
      2
    )
  );

  await browser.close();
  console.log(outPath);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
