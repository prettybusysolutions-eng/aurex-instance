import { spawnSync } from 'node:child_process';
import os from 'node:os';
import path from 'node:path';

const TM_PATH = path.join(os.homedir(), '.openclaw', 'thread_manager.py');
const PE_PATH = path.join(os.homedir(), '.openclaw', 'payload_extractor.py');

function extractString(value) {
  return typeof value === 'string' && value.trim() ? value.trim() : '';
}

function collectCandidates(event) {
  const candidates = [];
  const directPaths = [
    event?.input,
    event?.userInput,
    event?.message,
    event?.prompt,
    event?.text,
    event?.context?.input,
    event?.context?.text,
    event?.context?.message,
    event?.payload?.text,
    event?.payload?.message,
    event?.session?.lastUserMessage?.content,
    event?.session?.lastUserMessage?.text,
  ];
  for (const value of directPaths) {
    const s = extractString(value);
    if (s) candidates.push(s);
  }
  const arrays = [event?.messages, event?.context?.messages, event?.session?.messages];
  for (const arr of arrays) {
    if (!Array.isArray(arr)) continue;
    for (let i = arr.length - 1; i >= 0; i--) {
      const item = arr[i];
      const role = item?.role || item?.author || item?.type;
      if (role && !String(role).toLowerCase().includes('user')) continue;
      const s = extractString(item?.content || item?.text || item?.message);
      if (s) {
        candidates.push(s);
        break;
      }
    }
  }
  return [...new Set(candidates)];
}

function runPy(scriptPath, args) {
  const result = spawnSync('python3', [scriptPath, ...args], { encoding: 'utf8' });
  if (result.status !== 0) {
    return { ok: false, stdout: result.stdout || '', stderr: result.stderr || '' };
  }
  return { ok: true, stdout: (result.stdout || '').trim(), stderr: (result.stderr || '').trim() };
}

function runTm(args) {
  return runPy(TM_PATH, args);
}

function extractPayload(rawText) {
  const result = runPy(PE_PATH, ['extract', rawText]);
  if (!result.ok || !result.stdout) return null;
  try {
    return JSON.parse(result.stdout);
  } catch {
    return null;
  }
}

export default function register(api) {
  try { api?.logger?.info?.('[thread-context] register() invoked'); } catch {}

  api.on('before_prompt_build', (event) => {
    const channel = event?.session?.source?.channel || event?.context?.source?.channel || '';
    const config = api?.config?.plugins?.entries?.['thread-context']?.config || {};
    const enabledChannels = config.enabledForChannels || [];
    const maxMessages = Number(config.maxMessages || 8);
    const includeExtractionNotes = Boolean(config.includeExtractionNotes ?? true);
    if (enabledChannels.length && !enabledChannels.includes(channel)) return {};

    const candidates = collectCandidates(event);
    const rawInput = candidates[0] || '';
    if (!rawInput) {
      try { api?.logger?.warn?.('[thread-context] no user input detected for hook'); } catch {}
      return {};
    }

    const extraction = extractPayload(rawInput);
    const userInput = extractString(extraction?.payload_text) || rawInput;
    const extractionConfidence = extraction?.confidence ?? 0;
    const extractionReasons = Array.isArray(extraction?.reasons) ? extraction.reasons : [];

    let augmentedInput = userInput;
    if (userInput.startsWith('/weave ')) {
      const parts = userInput.trim().split(/\s+/);
      if (parts.length >= 4) {
        const source = parts[1];
        const target = parts[2];
        const query = parts.slice(3).join(' ');
        const weave = runTm(['weave', source, target, query]);
        if (weave.ok && weave.stdout) {
          augmentedInput = `${weave.stdout}\n\n${userInput}`;
        }
      }
    }

    const resolutionRes = runTm(['resolve', augmentedInput]);
    let resolution = null;
    if (resolutionRes.ok && resolutionRes.stdout) {
      try {
        resolution = JSON.parse(resolutionRes.stdout);
      } catch {
        resolution = null;
      }
    }

    const detect = runTm(['detect', augmentedInput]);
    if (!detect.ok || !detect.stdout || detect.stdout === 'None') return {};
    const topic = detect.stdout;

    runTm(['add', topic, userInput, 'user']);
    const contextRes = runTm(['context', topic]);
    if (!contextRes.ok || !contextRes.stdout) return {};

    let context;
    try {
      context = JSON.parse(contextRes.stdout);
    } catch {
      return {};
    }

    const recent = Array.isArray(context?.messages) ? context.messages.slice(-maxMessages) : [];
    const contextBlock = [
      'THREAD-AWARE CONTEXT SYSTEM:',
      `- Active thread: ${context?.topic || topic}`,
      `- Thread id: ${context?.thread_id || 'unknown'}`,
      `- Message count: ${context?.message_count ?? recent.length}`,
      `- Continuity score: ${resolution?.score ?? context?.continuity_score ?? 0}`,
      `- Continuity matched existing thread: ${resolution?.matched ? 'yes' : 'no'}`,
      `- Isolation rule: use only this thread by default; do not merge unrelated histories.`,
      `- Cross-thread rule: only use /weave source target query for targeted context injection.`,
      '',
      'Payload extraction:',
      `- Extraction confidence: ${extractionConfidence}`,
      `- Using payload text, not transport wrapper: ${userInput !== rawInput ? 'yes' : 'no'}`,
      '',
      'Thread summary:',
      context?.summary || 'No summary yet.',
      '',
      'Recent thread messages:'
    ];

    if (includeExtractionNotes && extractionReasons.length) {
      contextBlock.splice(11, 0, `- Extraction reasons: ${extractionReasons.join(', ')}`);
    }
    if (resolution?.reasons?.length) {
      contextBlock.splice(7, 0, `- Continuity reasons: ${resolution.reasons.join(', ')}`);
    }

    if (recent.length === 0) {
      contextBlock.push('- (none)');
    } else {
      for (const msg of recent) {
        const role = msg?.role || 'unknown';
        const content = String(msg?.content || '').replace(/\n/g, ' ').slice(0, 220);
        contextBlock.push(`- ${role}: ${content}`);
      }
    }

    try {
      api?.logger?.info?.(`[thread-context] injected context for topic=${topic} channel=${channel} extracted=${userInput !== rawInput} continuity=${resolution?.score ?? 0}`);
    } catch {}

    return { appendSystemContext: contextBlock.join('\n') };
  }, { priority: 60 });
}
