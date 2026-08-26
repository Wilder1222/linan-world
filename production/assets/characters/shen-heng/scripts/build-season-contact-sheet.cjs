const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

const root = path.resolve(process.argv[2]);
const sourceRoot = path.join(root, 'source');
const outputPath = path.join(root, 'qa', 'season-1-contact-sheet.jpg');
const columns = 5;
const tileWidth = 360;
const imageHeight = 230;
const labelHeight = 54;
const tileHeight = imageHeight + labelHeight;

const collect = (dir) => {
  const files = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.isDirectory() && entry.name === 'drafts') continue;
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) files.push(...collect(fullPath));
    else if (entry.name.startsWith('S1-') && entry.name.toLowerCase().endsWith('.png')) files.push(fullPath);
  }
  return files;
};

const escapeXml = (value) => value
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;');

async function main() {
  const files = collect(sourceRoot).sort((a, b) => path.basename(a).localeCompare(path.basename(b)));
  const rows = Math.ceil(files.length / columns);
  const canvas = sharp({
    create: {
      width: columns * tileWidth,
      height: rows * tileHeight,
      channels: 3,
      background: '#111418',
    },
  });
  const composites = [];
  for (let index = 0; index < files.length; index += 1) {
    const left = (index % columns) * tileWidth;
    const top = Math.floor(index / columns) * tileHeight;
    const name = path.basename(files[index], '.png');
    const image = await sharp(files[index])
      .resize({ width: tileWidth - 12, height: imageHeight - 12, fit: 'contain', background: '#20252b' })
      .jpeg({ quality: 88 })
      .toBuffer();
    const label = Buffer.from(`<svg width="${tileWidth}" height="${labelHeight}" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="#111418"/><text x="12" y="24" fill="#f2f4f7" font-family="Arial, sans-serif" font-size="15">${escapeXml(name.slice(0, 42))}</text><text x="12" y="44" fill="#aeb7c2" font-family="Arial, sans-serif" font-size="13">${escapeXml(name.slice(42))}</text></svg>`);
    composites.push({ input: image, left: left + 6, top: top + 6 });
    composites.push({ input: label, left, top: top + imageHeight });
  }
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  await canvas.composite(composites).jpeg({ quality: 92, chromaSubsampling: '4:4:4' }).toFile(outputPath);
  process.stdout.write(`${outputPath}\nassets=${files.length}\n`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
