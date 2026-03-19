#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');

const parityPath = path.join(ROOT, 'tests', 'parity_vectors.json');
const goldenPath = path.join(ROOT, 'tests', 'golden_parity.json');

function mask(n, x) {
  const mod = 1n << BigInt(n);
  return x & (mod - 1n);
}

function rotl(n, x, k) {
  const bn = BigInt(n);
  const bk = BigInt(k % n);
  return mask(n, (x << bk) | (x >> (bn - bk)));
}

function rotr(n, x, k) {
  const bn = BigInt(n);
  const bk = BigInt(k % n);
  return mask(n, (x >> bk) | (x << (bn - bk)));
}

function constantOfWidth(n) {
  let c = 0n;
  for (let i = 0; i < n / 8; i += 1) {
    c = (c << 8n) | 0x1dn;
  }
  return c;
}

function delta(n, x) {
  const C = constantOfWidth(n);
  return mask(n, rotl(n, x, 1) ^ rotl(n, x, 3) ^ rotr(n, x, 2) ^ C);
}

function replay(n, seed, steps) {
  let x = mask(n, seed);
  const out = [];
  for (let i = 0; i < steps; i += 1) {
    out.push(x);
    x = delta(n, x);
  }
  return out;
}

function fmtHex(n, x) {
  const width = n / 4;
  const body = x.toString(16).toUpperCase().padStart(width, '0');
  return `0x${body}`;
}

function main() {
  const parity = JSON.parse(fs.readFileSync(parityPath, 'utf8'));
  const golden = JSON.parse(fs.readFileSync(goldenPath, 'utf8'));
  const goldenMap = new Map(golden.map((g) => [`${g.width}:${g.seed}:${g.steps}`, g.states]));

  let allOk = true;

  for (const vector of parity) {
    const key = `${vector.width}:${vector.seed}:${vector.steps}`;
    const expected = goldenMap.get(key);
    if (!expected) {
      console.error(`MISSING golden vector for ${key}`);
      allOk = false;
      continue;
    }

    const states = replay(vector.width, BigInt(vector.seed), vector.steps).map((x) => fmtHex(vector.width, x));
    const ok = states.length === expected.length && states.every((s, i) => s === expected[i]);
    if (ok) {
      console.log(`✓ width=${vector.width} seed=${vector.seed}`);
    } else {
      console.error(`✗ width=${vector.width} seed=${vector.seed}`);
      for (let i = 0; i < Math.max(states.length, expected.length); i += 1) {
        if (states[i] !== expected[i]) {
          console.error(`  step ${i}: got ${states[i]} expected ${expected[i]}`);
        }
      }
      allOk = false;
    }
  }

  if (!allOk) {
    process.exit(1);
  }
  console.log('ALL PARITY VECTORS MATCH');
}

main();
