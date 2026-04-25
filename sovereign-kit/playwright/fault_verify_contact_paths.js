const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const REPORTS_DIR = path.resolve(__dirname, './reports/fault-verification');
const PAYMENT_LINK = process.env.DIAGNOSTIC_PAYMENT_LINK || 'https://busybee51.gumroad.com/l/stripe-mirror-check';
const RAW_DISPATCH_URL = process.env.DIAGNOSTIC_DISPATCH_URL;
const RAW_DISPATCH_TO = process.env.DIAGNOSTIC_DISPATCH_TO;
const DISPATCH_URL = RAW_DISPATCH_URL === undefined ? 'http://127.0.0.1:8918/api/dispatch/email' : RAW_DISPATCH_URL;
const DISPATCH_TO = RAW_DISPATCH_TO === undefined ? 'prettybusysolutions@gmail.com' : RAW_DISPATCH_TO;

function safeSlug(input) {
  return String(input || 'target')
    .toLowerCase()
    .replace(/^https?:\/\//, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 120);
}

function absoluteUrl(base, maybeRelative) {
  try {
    return new URL(maybeRelative, base).toString();
  } catch {
    return maybeRelative || null;
  }
}

function classifySocialLink(url) {
  if (!url) return null;
  const lowered = url.toLowerCase();
  if (lowered.includes('facebook.com')) return 'facebook';
  if (lowered.includes('instagram.com')) return 'instagram';
  if (lowered.includes('linkedin.com')) return 'linkedin';
  if (lowered.includes('x.com') || lowered.includes('twitter.com')) return 'x';
  if (lowered.includes('youtube.com') || lowered.includes('youtu.be')) return 'youtube';
  return null;
}

async function fetchStatus(page, url) {
  try {
    const result = await page.evaluate(async (target) => {
      try {
        const res = await fetch(target, { method: 'GET', redirect: 'follow' });
        return { ok: true, status: res.status, finalUrl: res.url };
      } catch (error) {
        return { ok: false, error: String(error) };
      }
    }, url);
    return result;
  } catch (error) {
    return { ok: false, error: String(error) };
  }
}

async function postDispatchEmail({ to, subject, body }) {
  if (!DISPATCH_URL || !to) {
    return { ok: false, status: null, body: 'dispatch_disabled' };
  }
  const response = await fetch(DISPATCH_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ to, subject, body }),
  });

  const text = await response.text();
  return {
    ok: response.ok,
    status: response.status,
    body: text,
  };
}

async function main() {
  const targetUrl = process.argv[2];
  if (!targetUrl) {
    console.error('Usage: node fault_verify_contact_paths.js <url>');
    process.exit(1);
  }

  fs.mkdirSync(REPORTS_DIR, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const faults = [];
  const observations = [];

  try {
    const response = await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
    observations.push({
      type: 'landing',
      url: targetUrl,
      status: response ? response.status() : null,
      title: await page.title(),
    });

    const pageData = await page.evaluate(() => {
      const forms = Array.from(document.querySelectorAll('form')).map((form, index) => ({
        index,
        action: form.getAttribute('action'),
        method: (form.getAttribute('method') || 'get').toLowerCase(),
        id: form.getAttribute('id'),
        className: form.getAttribute('class'),
        inputCount: form.querySelectorAll('input, textarea, select').length,
        submitCount: form.querySelectorAll('button[type="submit"], input[type="submit"]').length,
      }));

      const links = Array.from(document.querySelectorAll('a[href]')).map((a) => ({
        href: a.getAttribute('href'),
        text: (a.textContent || '').trim().slice(0, 120),
      }));

      return { forms, links };
    });

    const contactishLinks = pageData.links.filter((link) => {
      const href = (link.href || '').toLowerCase();
      const text = (link.text || '').toLowerCase();
      return href.startsWith('mailto:') || href.startsWith('tel:') || text.includes('contact') || text.includes('call');
    });

    for (const form of pageData.forms) {
      if (!form.action || form.action.trim() === '') {
        faults.push({
          severity: 'high',
          kind: 'missing_form_action',
          detail: `Form ${form.index} has no action attribute.`,
          evidence: form,
        });
        continue;
      }

      const resolvedAction = absoluteUrl(targetUrl, form.action);
      const actionStatus = await fetchStatus(page, resolvedAction);
      observations.push({
        type: 'form_action_probe',
        formIndex: form.index,
        action: resolvedAction,
        result: actionStatus,
      });

      if (!actionStatus.ok) {
        faults.push({
          severity: 'high',
          kind: 'unreachable_form_action',
          detail: `Form ${form.index} action could not be reached.`,
          evidence: { form, actionStatus },
        });
      } else if (actionStatus.status >= 400) {
        faults.push({
          severity: 'high',
          kind: 'dead_form_action',
          detail: `Form ${form.index} action returned HTTP ${actionStatus.status}.`,
          evidence: { form, actionStatus },
        });
      }

      if (form.submitCount === 0) {
        faults.push({
          severity: 'medium',
          kind: 'missing_submit_control',
          detail: `Form ${form.index} has no submit control.`,
          evidence: form,
        });
      }
    }

    for (const link of contactishLinks) {
      const href = link.href || '';
      if (href.toLowerCase().startsWith('mailto:')) {
        const address = href.replace(/^mailto:/i, '').split('?')[0].trim();
        if (!address || !address.includes('@')) {
          faults.push({
            severity: 'medium',
            kind: 'broken_mailto',
            detail: `Mailto link is malformed: ${href}`,
            evidence: link,
          });
        }
      }

      if (href.toLowerCase().startsWith('tel:')) {
        const digits = href.replace(/^tel:/i, '').replace(/[^0-9]/g, '');
        if (digits.length < 10) {
          faults.push({
            severity: 'medium',
            kind: 'broken_tel',
            detail: `Telephone link looks incomplete: ${href}`,
            evidence: link,
          });
        }
      }
    }

    const socialLinks = pageData.links
      .map((link) => ({ ...link, network: classifySocialLink(link.href) }))
      .filter((link) => link.network);

    for (const link of socialLinks) {
      const resolved = absoluteUrl(targetUrl, link.href);
      const status = await fetchStatus(page, resolved);
      observations.push({
        type: 'social_probe',
        network: link.network,
        url: resolved,
        result: status,
      });

      if (!status.ok || (status.status && status.status >= 400)) {
        faults.push({
          severity: 'low',
          kind: 'dead_social_link',
          detail: `${link.network} link failed${status.status ? ` with HTTP ${status.status}` : ''}.`,
          evidence: { link, status },
        });
      }
    }

    const stamp = new Date().toISOString().replace(/[:.]/g, '-');
    const slug = safeSlug(targetUrl);
    const jsonPath = path.join(REPORTS_DIR, `${slug}-${stamp}.json`);
    const mdPath = path.join(REPORTS_DIR, `${slug}-diagnostic_report.md`);

    const payload = {
      paymentLink: PAYMENT_LINK,
      scanned_at: new Date().toISOString(),
      target: targetUrl,
      observations,
      faults,
      summary: {
        faultCount: faults.length,
        highSeverity: faults.filter((f) => f.severity === 'high').length,
        mediumSeverity: faults.filter((f) => f.severity === 'medium').length,
        lowSeverity: faults.filter((f) => f.severity === 'low').length,
      },
    };

    fs.writeFileSync(jsonPath, JSON.stringify(payload, null, 2));

    const lines = [
      `# Diagnostic Report: ${targetUrl}`,
      '',
      `Scanned at: ${payload.scanned_at}`,
      '',
      '## Summary',
      '',
      `- Total faults: ${payload.summary.faultCount}`,
      `- High severity: ${payload.summary.highSeverity}`,
      `- Medium severity: ${payload.summary.mediumSeverity}`,
      `- Low severity: ${payload.summary.lowSeverity}`,
      '',
      '## Verified Faults',
      '',
    ];

    if (!faults.length) {
      lines.push('No verified contact-path or social-link faults were detected in this scan.');
    } else {
      for (const fault of faults) {
        lines.push(`### ${fault.kind}`);
        lines.push(`- Severity: ${fault.severity}`);
        lines.push(`- Detail: ${fault.detail}`);
        lines.push(`- Evidence: ${JSON.stringify(fault.evidence)}`);
        lines.push('');
      }
    }

    lines.push('## Unlock');
    lines.push('');
    lines.push(`- Payment link: ${PAYMENT_LINK}`);
    lines.push('');
    lines.push('## Locked Remediation');
    lines.push('');
    lines.push('Detailed remediation steps intentionally withheld in this artifact.');
    lines.push('Unlock path should be attached separately to the approved payment bridge.');

    fs.writeFileSync(mdPath, lines.join('\n'));

    let dispatch = null;
    const targetEmail = DISPATCH_TO;
    if (faults.length > 0 && targetEmail) {
      const subject = `Automated Diagnostic Alert: ${targetUrl}`;
      const body = [
        'This is an automated system notification.',
        '',
        'A routine diagnostic verification of your public contact pathway detected a structural fault that may be interrupting inbound lead flow.',
        '',
        'We compiled a domain-specific diagnostic artifact showing the verified failure surface and the exact remediation path.',
        '',
        `Unlock the full diagnostic report here for $50.00: ${PAYMENT_LINK}`,
        '',
        'End of transmission.',
      ].join('\n');

      dispatch = await postDispatchEmail({ to: targetEmail, subject, body });
    }

    console.log(JSON.stringify({ ok: true, jsonPath, mdPath, faultCount: faults.length, dispatch }, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
