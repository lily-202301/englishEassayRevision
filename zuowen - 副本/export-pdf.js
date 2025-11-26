// export-pdf.js
import path from 'path';
import express from 'express';
import puppeteer from 'puppeteer';
import { fileURLToPath } from 'url';
process.env.PUPPETEER_EXECUTABLE_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const __dirname = path.dirname(fileURLToPath(import.meta.url));

const args = Object.fromEntries(
  process.argv.slice(2).map((arg) => {
    const [k, v] = arg.split('=');
    return [k.replace(/^--/, ''), v];
  })
);

const distDir = path.resolve(__dirname, args.dist || './dist');          // 构建产物目录
const jsonPath = path.resolve(__dirname, args.json || './qwen_essay_result.json');
const outPdf  = path.resolve(__dirname, args.out || './essay_report.pdf');
const port    = Number(args.port || 4173);

async function main() {
  const app = express();
  app.use(express.static(distDir));
  app.get('/qwen_essay_result.json', (_req, res) => res.sendFile(jsonPath));
  const server = app.listen(port);

  try {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    await page.goto(`http://localhost:${port}/`, { waitUntil: 'networkidle0' });
    await page.waitForSelector('main', { timeout: 60000 });
    await page.pdf({
      path: outPdf,
      format: 'A4',
      margin: { top: '14mm', bottom: '14mm', left: '14mm', right: '14mm' },
      printBackground: true
    });
    await browser.close();
    console.log(JSON.stringify({ status: 'ok', pdf: outPdf, json: jsonPath }));
  } finally {
    server.close();
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
