const winkNLP = require('wink-nlp');
const model = require('wink-eng-lite-web-model');
const wn = require('./wordnet_5wn_index.json');

const nlp = winkNLP(model);
const its = nlp.its;

const VERB_POS = new Set(['VERB', 'AUX']);

function normToken(t) {
  const x = (t || '').toLowerCase().trim();
  return x.replace(/[^a-z0-9' -]/g, '').replace(/\s+/g, ' ');
}

function singularize(token) {
  if (token.endsWith('ies') && token.length > 4) return token.slice(0, -3) + 'y';
  if (token.endsWith('es') && token.length > 3) return token.slice(0, -2);
  if (token.endsWith('s') && token.length > 2) return token.slice(0, -1);
  return token;
}

function lookupLemma(token) {
  const t = normToken(token);
  if (!t) return null;
  return wn.lemmas[t] || wn.lemmas[singularize(t)] || null;
}

function extractEntities(text) {
  const doc = nlp.readDoc(text || '');
  const ranked = new Map();

  doc.entities().each((e) => {
    const val = normToken(e.out(its.value));
    if (!val) return;
    const hit = lookupLemma(val);
    if (!hit) return;
    ranked.set(val, (ranked.get(val) || 0) + 3);
  });

  doc.tokens().each((tk) => {
    const tok = normToken(tk.out(its.normal));
    if (!tok) return;
    const hit = lookupLemma(tok);
    if (!hit) return;
    ranked.set(tok, (ranked.get(tok) || 0) + 1);
  });

  return Array.from(ranked.entries())
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .slice(0, 14)
    .map(([lemma]) => {
      const hit = lookupLemma(lemma);
      return {
        noun: lemma,
        display: lemma.split(' ').map((w) => (w[0] ? w[0].toUpperCase() + w.slice(1) : w)).join(' '),
        kind: hit ? hit.kind : 'thing',
        synset: hit ? hit.synset : null,
      };
    });
}

function extractTriples(text) {
  const doc = nlp.readDoc(text || '');
  const sentences = doc.sentences().out();
  const out = [];

  const pickNouns = (sentence) => extractEntities(sentence).map((x) => x.display);

  for (const s of sentences) {
    const localDoc = nlp.readDoc(s);
    let pred = 'relates_to';
    localDoc.tokens().each((tk) => {
      if (pred !== 'relates_to') return;
      const pos = tk.out(its.pos);
      if (VERB_POS.has(pos)) pred = normToken(tk.out(its.normal)) || pred;
    });

    const nouns = pickNouns(s);
    if (nouns.length >= 2) out.push([nouns[0], pred, nouns[1]]);
    else if (nouns.length === 1) out.push([nouns[0], pred, 'Context']);
  }

  return out.slice(0, 12);
}

window.WNNLP = {
  extractEntities,
  extractTriples,
  lookupLemma,
  metadata: {
    source: wn.source,
    lemma_count: wn.lemma_count,
  },
};
