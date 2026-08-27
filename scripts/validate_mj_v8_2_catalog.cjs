#!/usr/bin/env node
/* Validate the active VIS-LW-V2 Midjourney 8.2 prompt catalog. */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = path.resolve(__dirname, '..');
const CATALOG_PATH = 'production/midjourney/v2-asset-prompt-catalog.json';
const INVENTORY_PATH = 'production/midjourney/v2-asset-prompt-inventory.json';
const errors = [];
const warnings = [];

function read(relativePath) { return fs.readFileSync(path.join(ROOT, relativePath), 'utf8'); }
function json(relativePath) { return JSON.parse(read(relativePath)); }
function sha256(relativePath) { return crypto.createHash('sha256').update(read(relativePath)).digest('hex'); }
function error(code, message) { errors.push({ code, message }); }
function warning(code, message) { warnings.push({ code, message }); }
function count(records, predicate) { return records.filter(predicate).length; }

const catalog = json(CATALOG_PATH);
const inventory = json(INVENTORY_PATH);
const records = catalog.records || [];

if (catalog.catalog_id !== 'LINAN-VIS-LW-V2-MJ8.2') error('catalog_id', `Unexpected catalog id ${catalog.catalog_id}`);
if (catalog.style_contract !== 'VIS-LW-V2') error('style_contract', 'Catalog is not bound to VIS-LW-V2.');
if (!Array.isArray(records) || records.length === 0) error('catalog_empty', 'Catalog has no prompt records.');

const targetKeys = new Set();
const promptIds = new Set();
const directForbidden = /(?:<[^>]+>|\bV1\b|<STYLE_REF_URL>|--oref|--ow|--cref|--cw|--q\b|--draft|--hd|--sv|::)/i;
const acceptableRatios = new Set(['1:1', '2:3', '3:2', '3:4', '16:9']);
const allowedRoutes = new Set(['V2-Day', 'V2-Night-Wet', 'V2-Stage-Festival']);
const requiredV2AuthorityPaths = new Set([
  'production/style/v2-urban-splendor-song-style-package.md',
  'production/style/v2-visual-qa.md',
  'production/style/v2-reference-policy.md',
  'production/style/v2-world-asset-visual-registry.json'
]);

for (const record of records) {
  if (promptIds.has(record.prompt_id)) error('duplicate_prompt_id', record.prompt_id);
  promptIds.add(record.prompt_id);
  if (targetKeys.has(record.target_key)) error('duplicate_target_key', record.target_key);
  targetKeys.add(record.target_key);
  const prompt = record.prompt?.mj_text || '';
  if (!prompt) error('prompt_missing', record.prompt_id);
  if (directForbidden.test(prompt)) error('v8_2_forbidden_token', record.prompt_id);
  if (!/VIS-LW-V2/.test(prompt)) error('v2_visual_grammar_missing', record.prompt_id);
  if (!/--v\s+8\.2\b/.test(prompt)) error('model_version_missing', record.prompt_id);
  if (!/--raw\b/.test(prompt)) error('raw_missing', record.prompt_id);
  if (!/--ar\s+\d+:\d+/.test(prompt)) error('aspect_ratio_missing', record.prompt_id);
  if (!/--s\s+\d+\b/.test(prompt)) error('stylize_missing', record.prompt_id);
  if (!/--c\s+\d+\b/.test(prompt)) error('chaos_missing', record.prompt_id);
  if (!/--no\s+/.test(prompt)) error('negative_missing', record.prompt_id);
  if (prompt.length > 6000) error('prompt_length_exceeded', `${record.prompt_id}: ${prompt.length}`);
  if (!allowedRoutes.has(record.state?.style_slot)) error('invalid_style_route', record.prompt_id);
  if (!acceptableRatios.has(record.parameters?.ar)) error('invalid_aspect_ratio', `${record.prompt_id}: ${record.parameters?.ar}`);
  if (record.parameters?.model !== '8.2' || record.parameters?.raw !== true) error('parameter_contract', record.prompt_id);
  if (!(Number.isInteger(record.parameters?.stylize) && record.parameters.stylize >= 0 && record.parameters.stylize <= 1000)) error('invalid_stylize', record.prompt_id);
  if (!(Number.isInteger(record.parameters?.chaos) && record.parameters.chaos >= 0 && record.parameters.chaos <= 100)) error('invalid_chaos', record.prompt_id);
  if (record.execution_status?.startsWith('READY') && /[<>]/.test(prompt)) error('unresolved_ready_prompt', record.prompt_id);
  if (record.delivery?.native_8k_claim !== false) error('native_8k_claim', record.prompt_id);
  if (record.state?.technical_lane && record.state?.style_slot !== 'V2-Day') error('technical_route_violation', record.prompt_id);
  if (record.family === 'location' || record.family === 'relationship' || record.family === 'season-episode' || record.family === 'episode-shot') {
    if (record.parameters?.ar !== '16:9') error('aspect_ratio_lane_mismatch', record.prompt_id);
  }
  if (record.family === 'prop-evidence' && record.parameters?.ar !== '3:2') error('aspect_ratio_lane_mismatch', record.prompt_id);
  if (record.family === 'character' && record.parameters?.ar !== '3:4') error('aspect_ratio_lane_mismatch', record.prompt_id);
  if (!record.prompt?.negative?.includes('readable text') || !record.prompt?.negative?.includes('watermark') || !record.prompt?.negative?.includes('plastic skin') || !record.prompt?.negative?.includes('xianxia')) {
    error('required_negative_missing', record.prompt_id);
  }
}

const invTargets = new Set((inventory.targets || []).map((target) => target.target_key));
for (const key of targetKeys) if (!invTargets.has(key)) error('inventory_target_missing', key);
for (const key of invTargets) if (!targetKeys.has(key)) error('catalog_target_missing', key);
if (invTargets.size !== targetKeys.size) error('inventory_cardinality', `${invTargets.size} vs ${targetKeys.size}`);

for (const ref of catalog.source_manifest || []) {
  if (/(?:^|\/)archive(?:\/|$)/i.test(ref.path)) error('archived_source_used_as_active_authority', ref.path);
  if (!fs.existsSync(path.join(ROOT, ref.path))) error('authority_source_missing', ref.path);
  else if (sha256(ref.path) !== ref.sha256) error('authority_hash_stale', ref.path);
}
for (const record of records) {
  const authorityPaths = new Set((record.authority_refs || []).map((ref) => ref.path));
  for (const requiredPath of requiredV2AuthorityPaths) {
    if (!authorityPaths.has(requiredPath)) error('v2_authority_missing', `${record.prompt_id}: ${requiredPath}`);
  }
  for (const ref of record.authority_refs || []) {
    if (/(?:^|\/)archive(?:\/|$)/i.test(ref.path)) error('archived_source_used_as_active_authority', `${record.prompt_id}: ${ref.path}`);
    if (!fs.existsSync(path.join(ROOT, ref.path))) error('record_authority_source_missing', `${record.prompt_id}: ${ref.path}`);
    else if (sha256(ref.path) !== ref.sha256) error('record_authority_hash_stale', `${record.prompt_id}: ${ref.path}`);
  }
}

const roster = json('qa/character-roster.json');
const expectedCharacterIds = new Set(roster.named_characters.map((character) => character.id));
for (const character of roster.named_characters) {
  const profile = read(character.profile_path);
  const age = Number((profile.match(/^age_y0\s*=\s*(\d+)$/m) || [])[1]);
  const occupation = (profile.match(/^occupation\s*=\s*"([^"]+)"$/m) || [])[1];
  const record = records.find((entry) => entry.target_key === `CHARACTER:${character.id}:IDENTITY-001`);
  if (!record) error('required_target_missing', `CHARACTER:${character.id}:IDENTITY-001`);
  else {
    if (record.facts_snapshot?.name !== character.name || record.facts_snapshot?.age_y0 !== age || record.facts_snapshot?.occupation !== occupation) error('profile_fact_drift', character.id);
  }
}
if (count(records, (record) => record.family === 'character') !== expectedCharacterIds.size) error('character_coverage_count', String(count(records, (record) => record.family === 'character')));

const cityIndex = read('canon/city/00-city-index.md');
const canonicalLocationIds = [...cityIndex.matchAll(/\b(LOC-\d{3})\b/g)].map((match) => match[1]);
const locationIds = [...new Set(canonicalLocationIds)];
if (locationIds.length !== 18) error('location_registry_count', String(locationIds.length));
for (const id of locationIds) {
  if (!records.some((record) => record.target_key === `LOCATION:${id}:MASTER`)) error('required_target_missing', `LOCATION:${id}:MASTER`);
  for (let i = 1; i <= 6; i += 1) if (!records.some((record) => record.target_key === `LOCATION:${id}:S${i}`)) error('required_target_missing', `LOCATION:${id}:S${i}`);
}
if (count(records, (record) => record.family === 'location') !== 126) error('location_coverage_count', String(count(records, (record) => record.family === 'location')));

const relationSlots = json('qa/relationship-slots.json');
const relationEvidence = json('qa/relationship-evidence.json');
for (const relation of relationSlots.relationships) {
  const snapshots = relationEvidence.relationships.find((entry) => entry.relation_id === relation.id)?.snapshots || [];
  if (snapshots.length !== relation.snapshots) error('relationship_snapshot_source_count', relation.id);
  for (const snapshot of snapshots) if (!records.some((record) => record.target_key === `RELATIONSHIP:${relation.id}:${snapshot.snapshot}`)) error('required_target_missing', `RELATIONSHIP:${relation.id}:${snapshot.snapshot}`);
}
if (count(records, (record) => record.family === 'relationship') !== relationSlots.relationships.length * relationSlots.snapshots.length) error('relationship_coverage_count', String(count(records, (record) => record.family === 'relationship')));

const units = json('qa/unit-slots.json');
for (const slot of units.slots) if (!records.some((record) => record.target_key === `UNIT:${slot.id}:EXPLORATION-001`)) error('required_target_missing', `UNIT:${slot.id}:EXPLORATION-001`);
if (count(records, (record) => record.family === 'unit-slot') !== units.slots.length) error('unit_coverage_count', String(count(records, (record) => record.family === 'unit-slot')));

const backgrounds = json('qa/background-usage.json');
for (const archetype of backgrounds.archetypes) {
  const record = records.find((entry) => entry.target_key === `BACKGROUND:${archetype.id}:EXPLORATION-001`);
  if (!record) error('required_target_missing', `BACKGROUND:${archetype.id}:EXPLORATION-001`);
  else if (!/^LOC-\d{3}$/.test(record.facts_snapshot?.normalized_location_id || '')) error('background_location_normalization', archetype.id);
}
if (count(records, (record) => record.family === 'background-archetype') !== backgrounds.archetypes.length) error('background_coverage_count', String(count(records, (record) => record.family === 'background-archetype')));

const shenManifest = json('production/assets/characters/shen-heng/asset-manifest.json');
const crosswalk = catalog.crosswalks?.shen_manifest_asset_to_independent_tasks || {};
for (const asset of shenManifest.assets) {
  const tasks = crosswalk[asset.id];
  if (!Array.isArray(tasks) || tasks.length === 0) error('shen_manifest_asset_missing', asset.id);
  for (const task of tasks) {
    const record = records.find((entry) => entry.target_key === task);
    if (!record || record.target?.asset_id !== asset.id) error('shen_manifest_crosswalk_invalid', `${asset.id}: ${task}`);
  }
}
if (Object.keys(crosswalk).length !== shenManifest.assets.length) error('shen_manifest_category_count_mismatch', String(Object.keys(crosswalk).length));

const ledger = json('story/season/season-causal-ledger.json');
for (const episode of ledger.episodes) if (!records.some((record) => record.target_key === `EPISODE:${episode.episode_id}:PREMISE-001`)) error('episode_coverage_missing', episode.episode_id);
if (count(records, (record) => record.family === 'season-episode') !== ledger.episodes.length) error('episode_premise_count', String(count(records, (record) => record.family === 'season-episode')));

const storyboard = json('production/episodes/S1-E01/storyboard.json');
const expectedShots = storyboard.scenes.flatMap((scene) => scene.shots).map((shot) => shot.shot_id);
for (const shotId of expectedShots) if (!records.some((record) => record.target_key === `SHOT:${shotId}`)) error('storyboard_shot_missing', shotId);
if (count(records, (record) => record.family === 'episode-shot') !== expectedShots.length) error('storyboard_shot_count', String(count(records, (record) => record.family === 'episode-shot')));

const expectedPropTasks = 12;
if (count(records, (record) => record.family === 'prop-evidence') !== expectedPropTasks) error('prop_coverage_count', String(count(records, (record) => record.family === 'prop-evidence')));
if (count(records, (record) => record.family === 'style-calibration') !== 8) error('calibration_count', String(count(records, (record) => record.family === 'style-calibration')));

const activeTextPaths = [
  'production/midjourney/README.md',
  'production/midjourney/v2/README.md',
  'production/style/README.md',
  'production/style/v2-urban-splendor-song-style-package.md',
  'production/style/v2-visual-qa.md',
  'production/style/v2-reference-policy.md',
  'production/style/v2-world-asset-visual-registry.json'
];
for (const relativePath of activeTextPaths) {
  if (!fs.existsSync(path.join(ROOT, relativePath))) {
    error('active_document_missing', relativePath);
    continue;
  }
  const text = read(relativePath);
  if (/\bV1\b|<STYLE_REF_URL>|--oref|--ow|--cref|--cw|--q\b|--draft|--hd|\bOmni Reference\b|\bCharacter Reference\b/i.test(text)) error('v1_or_v8_2_incompatible_active_doc', relativePath);
}

const assetManifest = json('production/assets/characters/shen-heng/asset-manifest.json');
if (assetManifest.v2_prompt_catalog?.catalog_path !== CATALOG_PATH) warning('shen_manifest_not_linked', 'Shen package manifest has not yet been linked to the active V2 catalog.');

const result = {
  validator: 'validate_mj_v8_2_catalog.cjs',
  catalog_id: catalog.catalog_id,
  record_count: records.length,
  error_count: errors.length,
  warning_count: warnings.length,
  errors,
  warnings
};

if (process.argv.includes('--write-report')) {
  const output = path.join(ROOT, 'qa', 'reviews', 'v2-mj-prompt-catalog-review.json');
  fs.writeFileSync(output, `${JSON.stringify(result, null, 2)}\n`, 'utf8');
}
console.log(JSON.stringify(result, null, 2));
process.exitCode = errors.length ? 1 : 0;
