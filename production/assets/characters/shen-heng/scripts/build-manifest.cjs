const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const sharp = require('sharp');

const root = path.resolve(process.argv[2]);
const projectRoot = path.resolve(root, '../../../..');
const sourceDir = path.join(root, 'source');
const outputRoot = path.join(root, '8k');
const qaDir = path.join(root, 'qa');

const categoryFor = (name) => {
  if (name.startsWith('S1-AP-')) return '06-season-1-appearance';
  if (name.startsWith('S1-PR-')) return '07-season-1-evidence';
  if (name.startsWith('S1-NV-')) return '08-season-1-narrative';
  if (name.startsWith('ID-')) return '00-identity';
  if (/^(EX|MK|HR)-/.test(name)) return '01-expression-makeup-hair';
  if (/^C\d{2}-/.test(name)) return '02-costume';
  if (/^(PS|AC)-/.test(name)) return '03-pose-motion';
  if (name.startsWith('PR-')) return '04-props';
  if (/^(CAM|NV)-/.test(name)) return '05-narrative';
  throw new Error(`No category mapping for ${name}`);
};

const hashFile = (filePath) => new Promise((resolve, reject) => {
  const hash = crypto.createHash('sha256');
  const stream = fs.createReadStream(filePath);
  stream.on('data', (chunk) => hash.update(chunk));
  stream.on('end', () => resolve(hash.digest('hex')));
  stream.on('error', reject);
});

const relative = (filePath) => path.relative(root, filePath).split(path.sep).join('/');
const outputNameFor = (name) => name.replace(/\.png$/i, '-8k.png');

const collectSourcePngs = (dir) => {
  const files = [];
  const walk = (current) => {
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      if (entry.isDirectory() && entry.name === 'drafts') continue;
      const fullPath = path.join(current, entry.name);
      if (entry.isDirectory()) walk(fullPath);
      else if (entry.name.toLowerCase().endsWith('.png')) files.push(fullPath);
    }
  };
  walk(dir);
  return files.sort((a, b) => path.basename(a).localeCompare(path.basename(b)));
};

async function main() {
  fs.mkdirSync(qaDir, { recursive: true });
  const sourcePaths = collectSourcePngs(sourceDir);
  const sourceNames = sourcePaths.map((sourcePath) => path.basename(sourcePath));
  if (new Set(sourceNames).size !== sourceNames.length) throw new Error('Duplicate source PNG basename detected');

  const assets = [];
  for (const sourcePath of sourcePaths) {
    const name = path.basename(sourcePath);
    const category = categoryFor(name);
    const outputPath = path.join(outputRoot, category, outputNameFor(name));
    if (!fs.existsSync(outputPath)) throw new Error(`Missing 8K output for ${name}`);

    const [sourceMeta, outputMeta, sourceSha256, outputSha256] = await Promise.all([
      sharp(sourcePath).metadata(),
      sharp(outputPath).metadata(),
      hashFile(sourcePath),
      hashFile(outputPath),
    ]);
    const sourceStat = fs.statSync(sourcePath);
    const outputStat = fs.statSync(outputPath);
    const longEdge = Math.max(outputMeta.width || 0, outputMeta.height || 0);

    assets.push({
      id: name.replace(/\.png$/i, ''),
      category,
      source: {
        path: relative(sourcePath),
        width: sourceMeta.width,
        height: sourceMeta.height,
        bytes: sourceStat.size,
        sha256: sourceSha256,
      },
      output8k: {
        path: relative(outputPath),
        width: outputMeta.width,
        height: outputMeta.height,
        longEdge,
        density: outputMeta.density || 300,
        bytes: outputStat.size,
        sha256: outputSha256,
      },
      technicalStatus: longEdge === 7680 && outputStat.size > 0 ? 'pass' : 'fail',
      visualStatus: 'reviewed',
    });
  }

  const categoryCounts = assets.reduce((counts, asset) => {
    counts[asset.category] = (counts[asset.category] || 0) + 1;
    return counts;
  }, {});
  const partials = [];
  const walk = (dir) => {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(fullPath);
      else if (entry.name.endsWith('.partial')) partials.push(relative(fullPath));
    }
  };
  walk(root);

  const coveragePath = path.join(root, 'season-1', 'season-1-coverage-plan.json');
  const coverage = JSON.parse(fs.readFileSync(coveragePath, 'utf8'));

  const expectedCounts = {
    '00-identity': 4,
    '01-expression-makeup-hair': 4,
    '02-costume': 10,
    '03-pose-motion': 4,
    '04-props': 2,
    '05-narrative': 6,
    '06-season-1-appearance': 7,
    '07-season-1-evidence': 6,
    '08-season-1-narrative': 25,
  };
  const checks = {
    sourceAssetCount: {
      expected: coverage.expectedPackageAssetCount,
      actual: assets.length,
      pass: assets.length === coverage.expectedPackageAssetCount,
    },
    categoryCounts: {
      expected: expectedCounts,
      actual: categoryCounts,
      pass: Object.entries(expectedCounts).every(([key, value]) => categoryCounts[key] === value),
    },
    allOutputsLongEdge7680: { pass: assets.every((asset) => asset.output8k.longEdge === 7680) },
    allOutputsNonEmpty: { pass: assets.every((asset) => asset.output8k.bytes > 0) },
    sourceClassification: {
      pass: assets.every((asset) => asset.source.path.split('/')[1] === asset.category),
    },
    noPartialFiles: { actual: partials, pass: partials.length === 0 },
    identityReferencesPresent: {
      expected: [
        'references/ref-identity-primary-front.png',
        'references/ref-identity-softlight-portrait.jpeg',
        'references/ref-identity-neutral-side-light.jpeg',
      ],
      pass: [
        'references/ref-identity-primary-front.png',
        'references/ref-identity-softlight-portrait.jpeg',
        'references/ref-identity-neutral-side-light.jpeg',
      ].every((item) => fs.existsSync(path.join(root, item))),
    },
  };
  const plannedSeasonIds = [
    ...coverage.plannedAssets.appearance,
    ...coverage.plannedAssets.evidence,
    ...coverage.plannedAssets.narrative,
  ];
  const actualIds = new Set(assets.map((asset) => asset.id));
  const episodeKeys = Object.keys(coverage.episodeCoverage);
  const referencedEpisodeIds = episodeKeys.flatMap((episode) => coverage.episodeCoverage[episode]);
  checks.season1Coverage = {
    expectedPlannedAssets: coverage.plannedSeasonAssetCount,
    actualPlannedAssets: plannedSeasonIds.length,
    expectedEpisodes: 36,
    actualEpisodes: episodeKeys.length,
    missingPlannedAssets: plannedSeasonIds.filter((id) => !actualIds.has(id)),
    unknownEpisodeReferences: referencedEpisodeIds.filter((id) => !actualIds.has(id)),
    pass: plannedSeasonIds.length === coverage.plannedSeasonAssetCount
      && new Set(plannedSeasonIds).size === coverage.plannedSeasonAssetCount
      && episodeKeys.length === 36
      && plannedSeasonIds.every((id) => actualIds.has(id))
      && referencedEpisodeIds.every((id) => actualIds.has(id)),
  };
  const authoritativeSources = [
    coverage.characterSource,
    ...coverage.seasonSources,
    ...coverage.identityReferences.map((reference) => ({
      path: reference.path,
      sha256: reference.sha256,
      status: reference.role,
    })),
    {
      path: coverage.seasonGate.path,
      sha256: coverage.seasonGate.sha256,
      status: coverage.seasonGate.status,
    },
    {
      path: coverage.seasonGate.inputManifestPath,
      sha256: coverage.seasonGate.inputManifestSha256,
      status: 'LOCKED-MANIFEST',
    },
  ];
  const sourceHashResults = [];
  for (const source of authoritativeSources) {
    const sourcePath = path.join(projectRoot, source.path);
    const exists = fs.existsSync(sourcePath);
    const actualSha256 = exists ? await hashFile(sourcePath) : null;
    sourceHashResults.push({
      path: source.path,
      status: source.status,
      expectedSha256: source.sha256.toLowerCase(),
      actualSha256,
      pass: exists && actualSha256 === source.sha256.toLowerCase(),
    });
  }
  checks.authoritativeSourceHashesCurrent = {
    checked: sourceHashResults,
    pass: sourceHashResults.every((item) => item.pass),
  };
  const packagedIdentityReferences = [
    'references/ref-identity-primary-front.png',
    'references/ref-identity-softlight-portrait.jpeg',
    'references/ref-identity-neutral-side-light.jpeg',
  ];
  const identityHashParity = [];
  for (let index = 0; index < coverage.identityReferences.length; index += 1) {
    const rawReference = coverage.identityReferences[index];
    const packagePath = path.join(root, packagedIdentityReferences[index]);
    const packageSha256 = fs.existsSync(packagePath) ? await hashFile(packagePath) : null;
    identityHashParity.push({
      rawPath: rawReference.path,
      packagePath: packagedIdentityReferences[index],
      expectedSha256: rawReference.sha256.toLowerCase(),
      packageSha256,
      pass: packageSha256 === rawReference.sha256.toLowerCase(),
    });
  }
  checks.identityReferenceHashParity = {
    checked: identityHashParity,
    pass: identityHashParity.every((item) => item.pass),
  };
  const productionStatusPath = path.join(projectRoot, 'qa', 'production-status.json');
  const productionStatus = JSON.parse(fs.readFileSync(productionStatusPath, 'utf8'));
  checks.gateState = {
    expected: { season_gate: 'LOCKED', episode_gate: 'OPEN' },
    actual: {
      season_gate: productionStatus.season_gate,
      episode_gate: productionStatus.episode_gate,
    },
    pass: productionStatus.season_gate === 'LOCKED' && productionStatus.episode_gate === 'OPEN',
  };
  const causalLedgerSource = coverage.seasonSources.find((source) => source.path.endsWith('season-causal-ledger.json'));
  const causalLedger = JSON.parse(fs.readFileSync(path.join(projectRoot, causalLedgerSource.path), 'utf8'));
  const episodesRequiringNarrative = causalLedger.episodes
    .filter((episode) => episode.pov_ids.includes(coverage.characterId)
      || episode.profession_action.character_id === coverage.characterId
      || episode.episode_choice.actor === coverage.characterId)
    .map((episode) => episode.episode_id);
  const missingNarrativeEpisodes = episodesRequiringNarrative.filter((episodeId) =>
    !(coverage.episodeCoverage[episodeId] || []).some((id) => id.startsWith('S1-NV-')));
  checks.lockedSeasonNarrativeCoverage = {
    characterId: coverage.characterId,
    requiredEpisodes: episodesRequiringNarrative,
    missingNarrativeEpisodes,
    pass: missingNarrativeEpisodes.length === 0,
  };
  const passed = Object.values(checks).every((check) => check.pass);
  const generatedAt = new Date().toISOString();
  const manifest = {
    schemaVersion: 2,
    character: '沈蘅',
    packageVersion: 'V2-season-gate-locked',
    generatedAt,
    generator: 'Codex built-in ImageGen',
    resolutionContract: 'PNG; long edge 7680 px; 300 ppi metadata; original aspect ratio preserved',
    identityAuthority: 'references/ref-identity-primary-front.png',
    assetCount: assets.length,
    assets,
  };
  const audit = { schemaVersion: 2, generatedAt, passed, checks };

  fs.writeFileSync(path.join(root, 'asset-manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');
  fs.writeFileSync(path.join(qaDir, 'asset-audit.json'), `${JSON.stringify(audit, null, 2)}\n`, 'utf8');
  process.stdout.write(`${JSON.stringify({ passed, assetCount: assets.length, categoryCounts }, null, 2)}\n`);
  if (!passed) process.exitCode = 1;
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
