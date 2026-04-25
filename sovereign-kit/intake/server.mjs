import express from 'express';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import { execFile } from 'node:child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');
const REPORTS_DIR = path.join(ROOT, 'playwright', 'reports', 'fault-verification');
const PUBLIC_DIR = path.join(__dirname, 'public');
const PORT = Number(process.env.PORT || 8935);
const PAYMENT_LINK = process.env.DIAGNOSTIC_PAYMENT_LINK || 'https://busybee51.gumroad.com/l/stripe-mirror-check';
const PLAYWRIGHT_CONTAINER = process.env.PLAYWRIGHT_CONTAINER || 'controlplane-playwright';

const app = express();
app.use(express.json({ limit: '512kb' }));
app.use(express.static(PUBLIC_DIR));

function safeSlug(input) {
  return String(input || 'target')
    .toLowerCase()
    .replace(/^https?:\/\//, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 120);
}

function normalizeTargetForContainer(targetUrl) {
  return String(targetUrl)
    .replace('http://127.0.0.1:', 'http://host.docker.internal:')
    .replace('http://localhost:', 'http://host.docker.internal:')
    .replace('https://127.0.0.1:', 'https://host.docker.internal:')
    .replace('https://localhost:', 'https://host.docker.internal:');
}

function runCommand(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    execFile(command, args, options, (error, stdout, stderr) => {
      if (error) {
        reject(new Error((stderr || stdout || error.message || '').trim()));
        return;
      }
      resolve({ stdout, stderr });
    });
  });
}

function readLatestDiagnostic(targetUrl) {
  const slug = safeSlug(targetUrl);
  if (!fs.existsSync(REPORTS_DIR)) return null;
  const files = fs.readdirSync(REPORTS_DIR)
    .filter((name) => name.startsWith(`${slug}-`) && name.endsWith('.json'))
    .map((name) => ({
      name,
      fullPath: path.join(REPORTS_DIR, name),
      mtimeMs: fs.statSync(path.join(REPORTS_DIR, name)).mtimeMs,
    }))
    .sort((a, b) => b.mtimeMs - a.mtimeMs);
  if (!files.length) return null;
  return JSON.parse(fs.readFileSync(files[0].fullPath, 'utf8'));
}

app.get('/api/health', (_req, res) => {
  res.json({ ok: true, port: PORT, paymentLink: PAYMENT_LINK });
});

app.post('/api/intake/scan', async (req, res) => {
  try {
    const targetUrl = String(req.body?.url || '').trim();
    if (!targetUrl || !/^https?:\/\//i.test(targetUrl)) {
      return res.status(400).json({ ok: false, error: 'invalid_url' });
    }

    const containerTargetUrl = normalizeTargetForContainer(targetUrl);

    await runCommand('docker', [
      'exec',
      '-e', `DIAGNOSTIC_PAYMENT_LINK=${PAYMENT_LINK}`,
      '-e', 'DIAGNOSTIC_DISPATCH_TO=',
      '-e', 'DIAGNOSTIC_DISPATCH_URL=',
      PLAYWRIGHT_CONTAINER,
      'sh',
      '-lc',
      `cd /workspace && node fault_verify_contact_paths.js ${JSON.stringify(containerTargetUrl)}`,
    ]);

    const report = readLatestDiagnostic(containerTargetUrl);
    if (!report) {
      return res.status(500).json({ ok: false, error: 'missing_report_artifact' });
    }

    return res.json({
      ok: true,
      target: targetUrl,
      scannedTarget: containerTargetUrl,
      summary: {
        faultCount: report.summary?.faultCount || 0,
        highSeverity: report.summary?.highSeverity || 0,
        mediumSeverity: report.summary?.mediumSeverity || 0,
        lowSeverity: report.summary?.lowSeverity || 0,
      },
      gate: {
        locked: true,
        paymentLink: PAYMENT_LINK,
        message: `Scan complete. ${report.summary?.faultCount || 0} verified structural faults detected on ${targetUrl}.`,
      },
    });
  } catch (error) {
    return res.status(500).json({ ok: false, error: String(error.message || error) });
  }
});

app.listen(PORT, () => {
  console.log(`[intake] listening on http://127.0.0.1:${PORT}`);
});
