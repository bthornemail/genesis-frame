#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import bwipjs from 'bwip-js';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const TESTS = path.join(ROOT, 'tests');
const PACKAGE_PATH = path.join(TESTS, 'artifact_package_v1.json');
const PNG_PATH = path.join(TESTS, 'artifact_package_aztec.png');
const SHA_PATH = path.join(TESTS, 'artifact_package_aztec_png_sha256.txt');

function sha256Hex(buf) {
  return 'sha256:' + crypto.createHash('sha256').update(buf).digest('hex');
}

function canonicalOneLine(raw) {
  const obj = JSON.parse(raw);
  return JSON.stringify(obj);
}

function readPackageText() {
  const raw = fs.readFileSync(PACKAGE_PATH, 'utf8');
  return canonicalOneLine(raw);
}

async function renderPngBuffer(text) {
  return bwipjs.toBuffer({
    bcid: 'azteccode',
    text,
    scale: 4,
    includetext: false,
    paddingwidth: 8,
    paddingheight: 8,
  });
}

async function writeFixture() {
  if (!fs.existsSync(PACKAGE_PATH)) {
    throw new Error(`missing package fixture: ${PACKAGE_PATH}`);
  }
  const text = readPackageText();
  const png = await renderPngBuffer(text);
  fs.writeFileSync(PNG_PATH, png);
  fs.writeFileSync(SHA_PATH, sha256Hex(png) + '\n', 'utf8');
  console.log('WROTE', PNG_PATH);
  console.log('WROTE', SHA_PATH);
}

async function verifyFixture() {
  if (!fs.existsSync(PACKAGE_PATH) || !fs.existsSync(PNG_PATH) || !fs.existsSync(SHA_PATH)) {
    throw new Error('missing fixture file(s); run --write first');
  }
  const text = readPackageText();
  const regenerated = await renderPngBuffer(text);
  const got = sha256Hex(regenerated);
  const stored = fs.readFileSync(SHA_PATH, 'utf8').trim();
  if (got !== stored) {
    throw new Error(`png sha mismatch: got ${got} stored ${stored}`);
  }
  console.log('OK: artifact package aztec png fixture deterministic');
}

const args = new Set(process.argv.slice(2));
if (args.has('--write')) {
  await writeFixture();
} else if (args.has('--verify')) {
  await verifyFixture();
} else {
  console.error('use --write or --verify');
  process.exit(2);
}
