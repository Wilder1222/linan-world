const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

sharp.cache({ files: 0, items: 64, memory: 256 });
sharp.concurrency(2);

const sourceDir = path.resolve(process.argv[2]);
const outputRoot = path.resolve(process.argv[3]);
const targetLongEdge = 7680;

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

const targetNameFor = (name) => name.replace(/\.png$/i, '-8k.png');

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

async function renderOne(sourcePath) {
  const name = path.basename(sourcePath);
  const category = categoryFor(name);
  const targetDir = path.join(outputRoot, category);
  const targetPath = path.join(targetDir, targetNameFor(name));
  fs.mkdirSync(targetDir, { recursive: true });

  if (fs.existsSync(targetPath)) {
    const existing = await sharp(targetPath).metadata();
    if (Math.max(existing.width || 0, existing.height || 0) === targetLongEdge) {
      return { name, category, targetPath, width: existing.width, height: existing.height, status: 'verified-existing' };
    }
  }

  const meta = await sharp(sourcePath).metadata();
  if (!meta.width || !meta.height) throw new Error(`Missing dimensions for ${name}`);
  const landscape = meta.width >= meta.height;
  const width = landscape ? targetLongEdge : Math.round((meta.width / meta.height) * targetLongEdge);
  const height = landscape ? Math.round((meta.height / meta.width) * targetLongEdge) : targetLongEdge;
  await sharp(sourcePath, { limitInputPixels: false, sequentialRead: true })
    .resize({ width, height, fit: 'fill', kernel: sharp.kernel.lanczos3 })
    .sharpen({ sigma: 0.55 })
    .withMetadata({ density: 300 })
    .png({ compressionLevel: 9, adaptiveFiltering: true, palette: false, effort: 6 })
    .toFile(targetPath);
  return { name, category, targetPath, width, height, status: 'rendered' };
}

async function main() {
  const files = collectSourcePngs(sourceDir);
  const names = files.map((file) => path.basename(file));
  if (new Set(names).size !== names.length) throw new Error('Duplicate source PNG basename detected');

  const results = [];
  for (let index = 0; index < files.length; index += 2) {
    const batch = files.slice(index, index + 2);
    const completed = await Promise.all(batch.map(renderOne));
    for (const item of completed) {
      results.push(item);
      process.stdout.write(`${results.length}/${files.length}\t${item.status}\t${item.width}x${item.height}\t${item.name}\n`);
    }
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
