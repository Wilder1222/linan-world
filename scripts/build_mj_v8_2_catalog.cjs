#!/usr/bin/env node
/*
 * Compile the V2-only, Midjourney 8.2 prompt catalog from locked project facts.
 *
 * This script intentionally emits one fully resolved prompt per target.  It does
 * not submit anything to Midjourney and it never forwards user-provided reference
 * images.  Composite sheets are decomposed into independent render tasks and are
 * assembled locally only after review.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'production', 'midjourney', 'v2');
const GENERATED_ON = '2026-08-28';

function read(relativePath) {
  return fs.readFileSync(path.join(ROOT, relativePath), 'utf8');
}

function readJson(relativePath) {
  return JSON.parse(read(relativePath));
}

const SHA256_CACHE = new Map();

function sha256(relativePath) {
  if (!SHA256_CACHE.has(relativePath)) {
    SHA256_CACHE.set(relativePath, crypto.createHash('sha256').update(read(relativePath)).digest('hex'));
  }
  return SHA256_CACHE.get(relativePath);
}

function sourceRef(relativePath, role) {
  return { path: relativePath, sha256: sha256(relativePath), role };
}

function mkdir(relativePath) {
  fs.mkdirSync(path.join(ROOT, relativePath), { recursive: true });
}

function write(relativePath, text) {
  mkdir(path.dirname(relativePath));
  fs.writeFileSync(path.join(ROOT, relativePath), text, 'utf8');
}

function writeJson(relativePath, value) {
  write(relativePath, `${JSON.stringify(value, null, 2)}\n`);
}

function compact(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

function unique(items) {
  return [...new Set(items.filter(Boolean))];
}

function parseTomlFrontMatter(markdown) {
  const match = markdown.match(/^\+\+\+\s*\r?\n([\s\S]*?)\r?\n\+\+\+/);
  if (!match) throw new Error('Missing TOML front matter');
  const values = {};
  for (const line of match[1].split(/\r?\n/)) {
    const field = line.match(/^(\w+)\s*=\s*(.+)$/);
    if (!field) continue;
    const [, key, raw] = field;
    if (/^"/.test(raw)) values[key] = JSON.parse(raw);
    else if (/^\[/.test(raw)) values[key] = JSON.parse(raw);
    else if (/^\d+$/.test(raw)) values[key] = Number(raw);
    else if (raw === 'true' || raw === 'false') values[key] = raw === 'true';
    else values[key] = raw;
  }
  return values;
}

// Midjourney's --no terms are each interpreted independently.  They must never
// be a generic negative dictionary and must never contain anatomy, beauty, or
// wardrobe nouns.  Most production prompts deliberately have no --no tail.
const ALLOWED_NO_ATOMS = new Set(['text', 'watermark', 'logo']);

function normalizeNoAtoms(items, promptId) {
  const atoms = unique(items || []).map((item) => compact(item).toLowerCase());
  for (const atom of atoms) {
    if (!/^[a-z][a-z0-9-]*$/.test(atom)) {
      throw new Error(`${promptId} uses a non-atomic --no term: ${atom}`);
    }
    if (!ALLOWED_NO_ATOMS.has(atom)) {
      throw new Error(`${promptId} uses a non-approved --no term: ${atom}`);
    }
  }
  return atoms;
}

const GLOBAL_SCREEN_GRAMMAR = 'VIS-LW-V2 cinematic New Song historical-romance screen grammar: a lavish premium live-action Chinese period drama, a gently readable foreground, an active middle ground and receding inhabited architecture, with people, goods or light following a real route. Practical sources shape the light; silk, lacquered timber, paper, ceramic, water and skin respond distinctly; restrained optical diffusion and smooth filmic highlight roll-off appear around actual bright sources.';

const STYLE = {
  V2_DAY: `${GLOBAL_SCREEN_GRAMMAR} Daylight urban-splendor route in a prosperous Southern Song Linan water-city: layered indigo, tea brown, celadon, aged ivory and restrained pomegranate accents; dense trade, labor and household use; physically distinct silk, woven cloth, paper, timber, ceramic, dull brass and water. Humid clear daylight or low warm afternoon sunlight passes through thin silk, cloth, paper or lattice, revealing fibers and working hands while faces retain natural exposure, sculpted volume and a clear catchlight.`,
  V2_NIGHT_WET: `${GLOBAL_SCREEN_GRAMMAR} Night, blue-hour and wet-weather route in a dense Southern Song Linan street, worksite or covered corridor: warm paper lanterns, oil lamps, candles or stove light create local amber pools while restrained blue-grey exterior ambience shapes the distance. Dark cinnabar timber, ivory curtains and practical eave framing establish depth where the documented location supports them; wet stone, oilcloth, lacquered wood, rope and water carry small-scale real reflections.`,
  V2_STAGE_FESTIVAL: `${GLOBAL_SCREEN_GRAMMAR} Performance or festival route, historically grounded Southern Song urban splendor: coordinated woven silk layers, hand-finished embroidery, pomegranate, ink-blue and aged-ivory accents, refined hair ornaments and warm practical lantern or candle light. Fine gauze, curtains and a near foreground frame genuine backstage labor, performance circulation or public-market activity. Luxury is visible in dye depth, weave, maintenance, movement and motivated reflection.`
};

const TECHNICAL_STYLE = 'VIS-LW-V2 cast-continuity portrait lane: a premium New Song historical-romance official character still, with a clean warm-ivory plaster background, soft large-window daylight, gentle reflected fill, calm direct presence, true facial geometry, individually readable hair strands and fine woven textile fibers. The face has luminous dimensional exposure, controlled cheek and lip highlights, visible natural surface detail and refined historical-drama polish. The collar, hairstyle and one personal ornament remain legible as a complete, elegant period look.';

const ROUTE_KEY = {
  Day: 'V2-Day',
  NightWet: 'V2-Night-Wet',
  StageFestival: 'V2-Stage-Festival'
};

const V2_AUTHORITY_SPECS = [
  ['production/style/v2-urban-splendor-song-style-package.md', 'v2-style-authority'],
  ['production/style/v2-visual-qa.md', 'v2-qa'],
  ['production/style/v2-reference-policy.md', 'v2-reference-policy'],
  ['production/style/v2-world-reference-atoms.md', 'v2-reference-atoms'],
  ['production/style/v2-world-asset-visual-registry.json', 'v2-world-asset-visual-registry']
];

function withV2Authority(authorityRefs) {
  const byPath = new Map();
  for (const ref of [...(authorityRefs || []), ...V2_AUTHORITY_SPECS.map(([relativePath, role]) => sourceRef(relativePath, role))]) {
    byPath.set(ref.path, ref);
  }
  return [...byPath.values()];
}

function routeText(route, technical = false) {
  if (technical) return TECHNICAL_STYLE;
  if (route === 'NightWet') return STYLE.V2_NIGHT_WET;
  if (route === 'StageFestival') return STYLE.V2_STAGE_FESTIVAL;
  return STYLE.V2_DAY;
}

const catalog = [];

function addRecord(input) {
  const route = input.route || 'Day';
  const params = {
    model: '8.2',
    raw: input.raw ?? Boolean(input.technical),
    ar: input.ar || '3:4',
    stylize: input.stylize ?? 55,
    chaos: input.chaos ?? 3
  };
  const positive = compact(input.positive);
  const negative = normalizeNoAtoms(input.negative, input.prompt_id);
  const rawParameter = params.raw ? ' --raw' : '';
  const noParameter = negative.length ? ` --no ${negative.join(', ')}` : '';
  const mjText = `${positive} --v 8.2${rawParameter} --ar ${params.ar} --s ${params.stylize} --c ${params.chaos}${noParameter}`;
  if (/[<>]/.test(mjText)) throw new Error(`${input.prompt_id} contains an unresolved placeholder`);
  if (/(?:--oref|--ow|--cref|--cw|--q\b|--quality\b|--draft|--sv\b|::)/i.test(mjText)) {
    throw new Error(`${input.prompt_id} contains a project-disallowed parameter`);
  }
  catalog.push({
    prompt_id: input.prompt_id,
    version: 'V2-MJ8.2',
    target_key: input.target_key,
    family: input.family,
    asset_lane: input.asset_lane,
    target: input.target,
    authority_refs: withV2Authority(input.authority_refs),
    facts_snapshot: input.facts_snapshot || {},
    state: {
      style_slot: ROUTE_KEY[route],
      technical_lane: Boolean(input.technical),
      glamour_level: input.glamour_level ?? 2,
      time: input.time || (route === 'NightWet' ? 'night-or-wet' : 'day'),
      weather: input.weather || (route === 'NightWet' ? 'wet-or-rain' : 'clear-or-overcast')
    },
    prompt: { positive, negative, mj_text: mjText },
    parameters: params,
    reference_binding: input.reference_binding || {
      mode: 'TEXT_ONLY_DEFAULT',
      status: 'UNBOUND',
      policy: 'Do not attach raw uploads or external images. After rights review, a selected project-generated V2 identity render may be attached as an Image Prompt in the Midjourney web UI; if a verified URL workflow is used, apply image weight 1.0 to 1.5 and keep the full text prompt intact.'
    },
    depends_on: input.depends_on || [],
    execution_status: input.execution_status || 'READY_FOR_V2_CALIBRATION',
    delivery: {
      target_long_edge_px: 7680,
      native_8k_claim: false,
      note: 'Generate and select the Midjourney candidate first; approved source is then routed through the project 7680-pixel delivery/upscale workflow.'
    },
    assembly: input.assembly || null,
    acceptance_checks: input.acceptance_checks || [
      'Matches the stated Canon facts and the specified V2 route.',
      'Uses motivated light and physically differentiated material response.',
      'Contains no readable text, watermark, logo, fantasy styling or modern object.',
      'Passes the applicable identity, costume, location or continuity review before delivery.'
    ]
  });
}

function inferPresentation(name, occupation, profileMarkdown = '') {
  const feminine = /娘|婆|姐|姨|女|绣|巧|绮|月|素|慧|蔓|小青|阿沅|九娘|十四/.test(name + occupation);
  const masculine = /伯|叔|公|郎|生|匠|官|师|长庚|北鸿|成武|开元|怀川|行舟|砚之|惟敬|见山|兰度/.test(name + occupation);
  if (feminine && !masculine) return 'woman';
  if (masculine && !feminine) return 'man';
  if ((profileMarkdown.match(/她/g) || []).length > (profileMarkdown.match(/他/g) || []).length) return 'woman';
  if ((profileMarkdown.match(/他/g) || []).length > (profileMarkdown.match(/她/g) || []).length) return 'man';
  return 'adult';
}

function occupationEnglish(occupation) {
  const replacements = [
    [/调香师|香铺/, 'fragrance artisan and goods verifier'],
    [/歌伎|曲作者/, 'professional singer, stage performer and songwriter'],
    [/画师|测绘|抄图/, 'map artist and spatial recorder'],
    [/水路|船主|镖师/, 'river-route worker and boat owner'],
    [/酒肆|护送/, 'tavern keeper familiar with water-and-road escort work'],
    [/医|药/, 'medical and herbal worker'],
    [/官|城务/, 'city-office worker'],
    [/浆洗/, 'laundry worker and clothing-trace observer'],
    [/篾/, 'bamboo-weaving and basket-repair artisan'],
    [/书坊|印/, 'bookshop and print-work practitioner'],
    [/厨|馄饨|食/, 'food-service worker'],
    [/仓|货|商/, 'trade and stockroom worker']
  ];
  for (const [pattern, translation] of replacements) if (pattern.test(occupation)) return translation;
  return `practitioner of ${occupation}`;
}

function extractIdentityAnchor(profileMarkdown) {
  const match = profileMarkdown.match(/\*\*稳定身份锚点\*\*[：:]\s*([^\n]+)/);
  return match ? compact(match[1]) : '';
}

const CENTRAL_IDENTITY = {
  'CHR-L1-01': 'a beautiful and believable 20-year-old Chinese woman, Shen Heng, a fragrance artisan and goods verifier. She has a quiet oval-heart face with a softly lifted outer eye line, warm brown almond eyes, natural straight brows, a refined natural nose and soft peach-coral lips; the right thumb and index finger carry subtle dry fragrance-powder traces. Her attraction is calm, observant, intelligent and individually human.',
  'CHR-L1-02': 'a strikingly beautiful 25-year-old Chinese woman, Liu Shisi also known as Liu Wangshu, a Chun Tai performance-house singer and songwriter. She has a graceful slender oval face with a softly tapered jaw, long luminous almond eyes that are horizontally extended and elegantly proportioned, warm dark-brown irises, natural brows, a refined straight nose and beautiful muted rose lips. The right corner of her mouth rests a fraction higher than the left before she smiles. Her expressive gaze reads a room quickly: warm, intelligent, socially perceptive and lightly guarded; her beauty is exceptional, distinctly human and immediately recognizable.',
  'CHR-L1-03': 'a handsome 24-year-old Chinese man, Zhou Yanzhi, a map artist and spatial recorder. He is lean with slightly narrow shoulders, thoughtful eyes, fine ink marks on the right thumb and middle finger, and a subtle forward-leaning work posture; a rolled paper tube and measuring-cord habit are readable without becoming costume props.',
  'CHR-L1-04': 'a beautiful 31-year-old Chinese woman, Pei Jiuniang, a river-route worker and boat owner. Her shoulders and forearms show practical strength from poles and ropes, her skin holds a believable outdoor tonal difference, a healed mark rests at the left tiger-mouth, and her stable stance retains the balance of a moving deck.',
  'CHR-L1-05': 'a handsome 29-year-old Chinese man, Gu Xingzhou, a tavern keeper familiar with water-and-road escort work. He has an efficient, grounded silhouette, a faint old scar through the right brow, old rope marks at the backs of the hands, and an alert, restrained gaze that naturally checks exits before settling.',
  'CHR-L2-01': 'a graceful 45-year-old Chinese woman, Lu Qinghe, the practical keeper of a fragrance shop. Her warm eyes are resilient rather than fragile, a few early silver strands appear at the temples, and her hands are exceptionally steady from weighing goods and folding parcels.',
  'CHR-L2-02': 'a lively 18-year-old Chinese woman, Lin Ayuan, a street-life observer who helps at a wonton shop. She has a rounded, energetic face, quick scanning eyes, loose practical sleeves worn unevenly from work, and hands accustomed to bowls, coins and damp oil paper.',
  'CHR-L2-03': 'a distinct 18-year-old Chinese medical apprentice, Yu Qinghe, with sharp attentive brows and eyes, a few damp forelock strands from herbal steam, and subtle herbal stains at the hands. The expression becomes slow and precise when listening or asking a clinical question.',
  'CHR-L2-04': 'a weathered 38-year-old Chinese city clerk, Gao Wen, with realistic under-eye fatigue, a precisely aligned belt and duty token, visibly worn boots, and a calm practical manner that creates space between arguing people.',
  'CHR-L3-01': 'a dignified 48-year-old Chinese city administrator, Song Weijing, always impeccably ordered in clothing and posture. His face is controlled rather than villainous; he organizes papers into a fixed sequence and his gaze asks for time, number and source before judgment.',
  'CHR-L3-02': 'a composed 53-year-old Chinese merchant-system figure, Li Jianshan, with a cultured but lived-in face, restrained smile lines and a hospitable manner that pours tea before negotiation. His refinement is quiet and commercial, never courtly excess.',
  'CHR-L3-03': 'a compelling 34-year-old Chinese man, Helan Du, carrying northern weather in his features and a steady direct gaze. A worn leather wrist guard, deliberate posture and exact attention to listeners distinguish him as a grounded traveler-merchant.'
};

const CENTRAL_LOOKS = {
  'CHR-L1-01': {
    route: 'Day',
    identity: 'a tailored milk-ivory crossed-collar inner robe, a pale mist-blue long beizi-like outer layer, a muted sage sash, fine silver-blue jacquard at the collar, a celadon hairpin and a small fragrance pouch; fresh sheer peach-rose historical makeup and naturally polished hair',
    hero: 'in a sun-warmed fragrance-shop threshold, beside pale ceramic jars and a lattice-filtered window, her mist-blue and aged-ivory silk layers hold fine floral jacquard and narrow silver thread; a soft reflected glow touches the hairpin, tea-toned wood and her hands'
  },
  'CHR-L1-02': {
    route: 'StageFestival',
    identity: 'a refined old-rose, soft celadon and aged-ivory performer look: layered crossed-collar silk, a translucent beizi-like outer layer with floral jacquard, narrow low-saturation gilt edging, a sculpted urban-performer updo with a gilt filigree hairpin, pearl sprigs and delicate tassel earrings',
    hero: 'at the spring performance-house balcony before an evening set, in old-rose, celadon and ivory layers with a flowing full skirt, floral woven silk, narrow antique-gold thread and a coordinated hairpin, pearl and tassel system; warm lanterns catch the material, while working balconies, curtains and audience circulation recede into the city below'
  },
  'CHR-L1-03': {
    route: 'Day',
    identity: 'a composed ink-blue, stone-grey and aged-ivory layered scholar-artisan look, refined woven trim at the crossed collar, a well-kept topknot with a dark wood pin, a paper tube and measuring cord placed as quiet work details',
    hero: 'at an upper-floor map workshop overlooking a working canal, in elegantly tailored ink-blue and ivory layers, with paper, measurement cord, a carved railing and warm late-afternoon city depth behind him'
  },
  'CHR-L1-04': {
    route: 'Day',
    identity: 'a river-ready but elegant deep-indigo, river-teal and aged-ivory layered silhouette, a finely woven belt, narrow brass hardware, full sleeves shaped for rope work, restrained jade-green accents and a polished practical half-up coiffure',
    hero: 'at a busy river landing in tailored indigo and teal silk-wool layers, beside ropes, boats and wet lacquered timber, with late sunlight reflecting from water into her strong face and complete working silhouette'
  },
  'CHR-L1-05': {
    route: 'NightWet',
    identity: 'a sharply tailored tea-brown, deep-navy and ink layered tavern-host silhouette, fine woven edging at the collar, a dark wood hair ornament and a restrained brass clasp; the mature period-drama look remains elegant and mobile',
    hero: 'at the edge of a lantern-lit riverside tavern, deep tea and navy textiles, warm oil-lamp pools and wet wood reflections define him while occupied balconies and a water route fall away behind'
  },
  'CHR-L2-01': {
    route: 'Day',
    identity: 'a dignified aged-ivory, tea-brown and soft-celadon shopkeeper ensemble with careful layered silk, visible woven texture, a small jade-and-wood hairpin and a neat fragrance-goods pouch',
    hero: 'inside a richly maintained fragrance shop, among pale ceramic vessels, paper packets and a sunlit lattice, her soft-celadon and ivory fabrics show quiet fine tailoring and an established urban grace'
  },
  'CHR-L2-02': {
    route: 'Day',
    identity: 'a youthful peach, soft-celadon and ivory market look with a complete crossed-collar silhouette, lively woven trim, a small flower hairpin and a neatly bound half-up hairstyle suitable for quick work',
    hero: 'at a bustling wonton-stall lane in warm afternoon light, peach and celadon layers, a small pearl earring and a basket of bowls make her quick, bright urban presence readable against an active market depth'
  },
  'CHR-L2-03': {
    route: 'Day',
    identity: 'a clean sage, pale blue and aged-ivory medical-apprentice ensemble with fine ramie and silk layering, a narrow embroidered edge, a secure half-up hairstyle and one small polished jade hairpin',
    hero: 'at a bright herbal worktable under translucent cloth and window light, sage and ivory layers, herbal steam and sorted medicine packets give her precise concentration a softly luminous, high-end period-drama setting'
  },
  'CHR-L2-04': {
    route: 'Day',
    identity: 'a carefully ordered ink-blue, blue-grey and tea-brown city-clerk ensemble, complete crossed collar, precise woven belt, subtly patterned sleeve edge and a tidy dark wood hairpiece',
    hero: 'on a busy city-office passage in measured blue-grey layers, with ledgers, bamboo slips, a light-filled doorway and active civic traffic giving his practical authority an elegant urban context'
  },
  'CHR-L3-01': {
    route: 'NightWet',
    identity: 'a dignified ink, muted blue-grey and deep-tea administrator ensemble, precise layered robe structure, restrained patterned silk, a fine dark belt fitting and a composed topknot with an aged-metal pin',
    hero: 'inside a lantern-lit civic corridor, his quietly luxurious ink and blue-grey fabrics read against dark timber, ordered papers and receding pools of practical amber light'
  },
  'CHR-L3-02': {
    route: 'NightWet',
    identity: 'a prosperous but restrained tea-brown, bronze, deep-green and aged-ivory merchant ensemble with fine woven silk, a narrow metallic-thread edge, polished jade detail and a formal dark hairpiece',
    hero: 'at a refined waterside tea negotiation, deep-green and tea-brown textiles, lacquered tables, porcelain and warm lantern reflections establish wealth through material and social ease rather than court excess'
  },
  'CHR-L3-03': {
    route: 'Day',
    identity: 'a compelling deep-wine, ink and river-teal traveler-merchant silhouette, layered high-collared woven cloth, a weathered leather wrist guard, a small bronze clasp and carefully maintained hair',
    hero: 'on a sunlit bridge above a working canal, deep-wine and teal layers, travel textiles and a light breeze create a full, elegant figure against boats, market roofs and humid city distance'
  }
};

function roleWardrobe(occupation) {
  if (/歌伎|曲作者/.test(occupation)) return 'layered old-rose, celadon and aged-ivory crossed-collar silk, floral jacquard, a translucent outer layer, narrow low-saturation gilt edging and a coordinated pearl-and-tassel ornament system';
  if (/香|调香/.test(occupation)) return 'tailored aged-ivory and mist-blue crossed-collar silk, fine woven floral texture, a restrained celadon hairpin and a small fragrance-work pouch';
  if (/水路|船主|镖师|船/.test(occupation)) return 'elegant river-indigo and teal working layers, complete full sleeves, a finely woven sash and restrained brass or jade fittings';
  if (/官|城务/.test(occupation)) return 'precisely tailored ink-blue, stone-grey and aged-ivory official-city layers with a clear woven collar edge and a polished restraint in hair and belt';
  if (/酒肆|商|货|仓/.test(occupation)) return 'well-tailored tea-brown, deep-green and aged-ivory layered silk with a narrow woven or metallic-thread finish and one measured jade or brass personal detail';
  if (/医|药/.test(occupation)) return 'clean sage, pale-blue and aged-ivory layered ramie and silk, a narrow embroidered edge, a secured hairstyle and one small refined personal ornament';
  if (/书坊|画师|测绘|抄图|印/.test(occupation)) return 'ink-blue, stone-grey and ivory crossed-collar layers, fine woven textile texture, a dark wood hair ornament and quiet paper-work detail';
  if (/浆洗|绣|篾|厨|馄饨|食/.test(occupation)) return 'high-quality but usable ivory, soft-celadon and tea-brown layered workwear with complete sleeves, visible woven fibers, a tidy hairstyle and one small profession-linked ornament';
  return 'a carefully tailored crossed-collar Southern Song Linan outfit in aged ivory, soft celadon and tea-brown, layered woven silk and ramie, a fine collar edge, a complete sleeve line and one restrained personal ornament';
}

function heroRoute(characterId) {
  return CENTRAL_LOOKS[characterId]?.route || 'Day';
}

function characterPrompt(character, facts, profileMarkdown) {
  const central = Boolean(CENTRAL_IDENTITY[character.id]);
  const core = CENTRAL_IDENTITY[character.id] || `an exceptionally attractive and believable ${facts.age_y0}-year-old Chinese ${inferPresentation(facts.name, facts.occupation, profileMarkdown)}, ${facts.name}, a ${occupationEnglish(facts.occupation)}. This is a casting exploration awaiting a human-authored facial anchor; retain natural eyelid anatomy, individual facial asymmetry, natural lip texture and a specific personal presence.`;
  const wardrobe = CENTRAL_LOOKS[character.id]?.identity || roleWardrobe(facts.occupation);
  const lane = central ? 'Front-facing official identity-lock portrait' : 'Front-facing character visual-anchor exploration';
  return `${lane} of ${core} Centered head-and-upper-torso framing, direct eye-level lens, level shoulders, complete Southern Song Linan collar and shoulder silhouette: ${wardrobe}. Beautiful facial harmony with satin-translucent healthy skin, fine pores around the nose and inner cheeks, delicate microtexture, faint peach fuzz, subtle tonal variation, realistic under-eye structure, natural lip lines and controlled moisture highlights. Refined light historical makeup where appropriate: clean breathable base, softly shaped brows, peach-rose eye tone, separated lashes and muted rose lips. ${routeText('Day', true)}`;
}

function characterHeroPrompt(character, facts, profileMarkdown) {
  const core = CENTRAL_IDENTITY[character.id] || `the distinct ${facts.age_y0}-year-old Chinese ${inferPresentation(facts.name, facts.occupation, profileMarkdown)}, ${facts.name}, a ${occupationEnglish(facts.occupation)}`;
  const look = CENTRAL_LOOKS[character.id];
  if (!look) throw new Error(`No central hero look for ${character.id}`);
  const cleanCore = core.replace(/\.+$/, '');
  const heroLook = `${look.hero.charAt(0).toUpperCase()}${look.hero.slice(1)}`;
  return `Official New Song historical-romance hero key art of ${cleanCore}. Three-quarter environmental portrait, waist to mid-thigh framing, poised natural gesture and a high-end period-drama leading-cast presence. ${heroLook}. The appearance keeps a refined, breathable historical makeup and grooming finish, individually readable hair strands, luminous dimensional skin with subtle close-range texture, and a complete elegant silhouette. ${routeText(look.route)}`;
}

const roster = readJson('qa/character-roster.json');
const profileById = new Map();
for (const character of roster.named_characters) {
  const profileMarkdown = read(character.profile_path);
  const facts = parseTomlFrontMatter(profileMarkdown);
  const central = Boolean(CENTRAL_IDENTITY[character.id]);
  profileById.set(character.id, { character, facts, profileMarkdown });
  addRecord({
    prompt_id: `MJ-V2-CHR-${character.id}-ID-001`,
    target_key: `CHARACTER:${character.id}:IDENTITY-001`,
    family: 'character',
    asset_lane: central ? 'identity-anchor' : 'character-visual-anchor-exploration',
    target: { stable_id: character.id, name: character.name, asset_id: 'ID-001' },
    authority_refs: [sourceRef(character.profile_path, 'character-foundation-authority'), sourceRef('production/style/v2-urban-splendor-song-style-package.md', 'v2-style-authority')],
    facts_snapshot: { name: facts.name, aliases: facts.aliases, age_y0: facts.age_y0, occupation: facts.occupation, residence: facts.residence, identity_anchor_cn: extractIdentityAnchor(profileMarkdown) },
    route: 'Day',
    technical: true,
    glamour_level: character.id === 'CHR-L1-02' ? 3 : 2,
    ar: '3:4',
    stylize: 100,
    chaos: 2,
    positive: characterPrompt(character, facts, profileMarkdown),
    execution_status: central ? 'READY_FOR_V2_IDENTITY_SELECTION' : 'BLOCKED_UNTIL_CHARACTER_VISUAL_ANCHOR',
    acceptance_checks: central ? [
      'Age, occupation and stable visual anchors exactly match the character profile.',
      'Face remains individually recognizable, beautiful and natural with a high-end historical-drama cast presence.',
      'The technical continuity lane is clear, front-facing and free of atmospheric styling.',
      'Use as the candidate identity record only after human selection; do not treat a generated face as Canon until selected.'
    ] : [
      'Confirms the stated age, occupation, wardrobe family and presentation as a casting exploration only.',
      'Must receive a human-authored face, body and behavior anchor set before a selected image can become a named identity asset.',
      'Cannot be used as Canon identity, an Image Prompt or a final delivery before the character visual-anchor brief is approved.'
    ]
  });
  if (/^CHR-L[123]-/.test(character.id)) {
    const route = heroRoute(character.id);
    addRecord({
      prompt_id: `MJ-V2-CHR-${character.id}-HERO-001`,
      target_key: `CHARACTER:${character.id}:HERO-001`,
      family: 'character',
      asset_lane: 'identity-hero',
      target: { stable_id: character.id, name: character.name, asset_id: 'HERO-001' },
      authority_refs: [sourceRef(character.profile_path, 'character-foundation-authority')],
      facts_snapshot: { name: facts.name, aliases: facts.aliases, age_y0: facts.age_y0, occupation: facts.occupation, residence: facts.residence, identity_anchor_cn: extractIdentityAnchor(profileMarkdown) },
      route,
      technical: false,
      raw: true,
      glamour_level: character.id === 'CHR-L1-02' ? 5 : character.tier === 'L1' ? 4 : 3,
      ar: '3:4',
      stylize: character.tier === 'L1' ? 175 : 155,
      chaos: 3,
      positive: characterHeroPrompt(character, facts, profileMarkdown),
      execution_status: 'READY_FOR_V2_HERO_SELECTION',
      acceptance_checks: [
        'Matches the locked age, occupation and facial identity anchors for the named central character.',
        'Reads as a premium New Song historical-romance key art with a complete, character-specific wardrobe system.',
        'Uses a real light source and a legible Linan environment; selected source remains subject to identity and rights review before continuity use.'
      ]
    });
  }
}

const LOCATIONS = [
  ['LOC-001', '鹤鸣巷', 0], ['LOC-002', '沈家香铺', 0], ['LOC-003', '香药街', 0],
  ['LOC-004', '御街', 1], ['LOC-005', '御街夜市', 1], ['LOC-006', '春台瓦舍', 1],
  ['LOC-007', '西湖画舫', 2], ['LOC-008', '西泠书坊与画铺', 2], ['LOC-009', '停云酒肆', 2],
  ['LOC-010', '钱塘码头', 3], ['LOC-011', '青鹞', 3], ['LOC-012', '船坊与水上茶摊', 3],
  ['LOC-013', '城务司', 4], ['LOC-014', '三仓', 4], ['LOC-015', '城门、桥闸与查验口', 4],
  ['LOC-016', '小济堂与寺院行堂', 5], ['LOC-017', '松风客舍', 6], ['LOC-018', '城南安置区', 6]
].map(([id, name, group]) => ({ id, name, group }));

const worldVisualRegistry = readJson('production/style/v2-world-asset-visual-registry.json');

function locationDesign(locationId) {
  const design = worldVisualRegistry.locations?.[locationId];
  if (!design?.master_description || !Array.isArray(design.canonical_sources) || design.canonical_sources.length === 0) {
    throw new Error(`Missing V2 location visual binding for ${locationId}`);
  }
  return design;
}

function propDesign(propCode) {
  const design = worldVisualRegistry.props?.[propCode];
  if (!design?.description || !Array.isArray(design.canonical_sources) || design.canonical_sources.length === 0) {
    throw new Error(`Missing V2 prop visual binding for ${propCode}`);
  }
  return design;
}

const LOCATION_GROUP_STATES = [
  [
    'after-rain reopening: thresholds and work surfaces are drying, practical queues form beneath eaves, and an old chest appears only as an unresolved object rather than a solved clue.',
    'price strain: smaller measured bundles, refill containers and cautious exchanges show pressure without readable price signs.',
    'merged reports: distinct sealed paper packets and handoffs gather at a shared work point while the lane remains passable.',
    'brief autumn calm: drier brick, restrained seasonal goods and slower normal commerce, with debt and daily exchange still visible.',
    'controlled entry during restriction: half-closed doors, high dry cargo routes and papers or meals passed across thresholds, never a secret bypass.',
    'street spring-letter house: an open mutual-aid table, practical door lamps and correction slips with no readable writing.'
  ],
  [
    'ordinary performance and food-trade cycle: dressing, mending, listening routes and service queues all remain visible.',
    'song-message circulation: listening lines, revised rehearsal material and word-of-mouth clusters are shown through bodies and routes, never text signage.',
    'divided response: separate entry, exit and table paths show audience differences while labor and service continue.',
    'osmanthus night-market season: a restrained festival layer of blossom parcels, warm local lamps and rich textile accents without palace spectacle.',
    'ban state: lowered covers, stored sleeves and repair labor reshape routes; no empty market and no grand closure image.',
    'public oral correction: performers, listeners and street routes stay connected, with source handoff visible but all paper unreadable.'
  ],
  [
    'daytime route sketching, tea service and ordinary sightseeing: water, berth and work paths make the place useful rather than decorative.',
    'rain-route condition: lowered canopy, wet gear, paper kept dry and delayed or moored passage made spatially clear.',
    'tide anomaly: changed waterline, tightened ropes, separated version proofs or delayed arrival show an observation without an omniscient solution.',
    'osmanthus gathering: restrained hospitality, refined tea and textile accents, still a working lake-and-book trade environment rather than a floating palace.',
    'restricted berths: waiting people, luggage, cargo and clear routes show constraint with no miraculous bypass.',
    'paper and tactile route maps used as partial aids at a shared worktable; no legible labels and no all-knowing map.'
  ],
  [
    'waiting-vessel and repair rhythm: berth assignment, weighed bundles, tools, rope and tide marks are physically legible.',
    'water-route verification: draft marks, hold checks, seals, measuring stations and witness work show a bounded procedure.',
    'dark-flood repair: wet piles, raised cargo, reinforced planks and tool handling show risk without disaster spectacle.',
    'autumn navigation recovery: cautious berth queues, repaired rope and markers, and limited cargo movement.',
    'sealed-water state: tied vessels, stop lines, idle cargo and local guard lamps, with no unauthorized crossing.',
    'rescue-transfer support: shared loading and documented handoffs, practical repair and ration staging rather than a heroic command-center image.'
  ],
  [
    'ordinary intake and stock verification: bounded duty tables, separate inventories and clear queue logic.',
    'centralized dispatch: seals, shift plaques, count tables and rerouted queues show finite authority and constrained resources.',
    'account discrepancy: competing source bundles, dual verification and stalled movement reveal conflict without villain tableau.',
    'continued sealing: calm archive or warehouse restraint, visible fire-and-water tools and ongoing ordinary duty.',
    'emergency order: raised documents and sacks, local lamps, wet passage or firebreak work, never fortress imagery or total-control glow.',
    'public accountability: open review desk, grouped records and route-time chains made spatially visible with no readable text.'
  ],
  [
    'scattered cases and care workflow: diagnosis bench, wash point, porridge line, bedding or shelter routes stay legible without declaring a citywide catastrophe.',
    'medicine scarcity: fewer bundles, rationed supplies and care requests visible through workflow, never a miracle cure.',
    'medical split and water pressure: raised medicine, drainage or triage routes, privacy-respecting partitions and usable circulation.',
    'false recovery: cleaner paths and ordinary routines return but an unfinished observation, absence or watch route remains.',
    'winter illness and restriction: warm bowls, layered blankets, public kitchen or safe entry routes, never prison spectacle.',
    'public care and correction system: resident-amendable worktable, medical or missing-person route and collective work, no readable boards.'
  ],
  [
    'new-resident intake: bedding, travel bundles, registration desk, privacy curtain and water point make the camp or inn a working place.',
    'supply pressure: rationed bundles, public kitchen and water-route details show scarcity without diagnosis theatre.',
    'water decline and triage overflow: raised luggage and medicine, drainage repair, safe-water and care lanes retain agency and privacy.',
    'false recovery: drier paths and regular cooking return while logged absences, drainage or watch details remain.',
    'winter restriction: sheltered circulation, meal handoff and care-aware bedding, never a prison or despair tableau.',
    'public medical link: correction or missing-person desk connects to care and relief routes; people remain active decision makers.'
  ]
];

const LOCATION_ROUTES = {
  'LOC-001': ['NightWet', 'Day', 'Day', 'Day', 'Day', 'Day'],
  'LOC-002': ['NightWet', 'Day', 'Day', 'Day', 'Day', 'Day'],
  'LOC-003': ['NightWet', 'Day', 'Day', 'Day', 'Day', 'Day'],
  'LOC-004': ['Day', 'Day', 'Day', 'StageFestival', 'Day', 'Day'],
  'LOC-005': ['NightWet', 'NightWet', 'NightWet', 'StageFestival', 'NightWet', 'StageFestival'],
  'LOC-006': ['StageFestival', 'StageFestival', 'StageFestival', 'StageFestival', 'NightWet', 'StageFestival'],
  'LOC-007': ['Day', 'NightWet', 'NightWet', 'StageFestival', 'Day', 'Day'],
  'LOC-008': ['Day', 'Day', 'Day', 'StageFestival', 'Day', 'Day'],
  'LOC-009': ['Day', 'NightWet', 'NightWet', 'StageFestival', 'NightWet', 'Day'],
  'LOC-010': ['Day', 'Day', 'NightWet', 'Day', 'NightWet', 'NightWet'],
  'LOC-011': ['Day', 'Day', 'NightWet', 'Day', 'NightWet', 'NightWet'],
  'LOC-012': ['Day', 'Day', 'NightWet', 'Day', 'NightWet', 'NightWet'],
  'LOC-013': ['Day', 'Day', 'Day', 'Day', 'NightWet', 'Day'],
  'LOC-014': ['Day', 'Day', 'Day', 'Day', 'NightWet', 'Day'],
  'LOC-015': ['Day', 'Day', 'Day', 'Day', 'NightWet', 'Day'],
  'LOC-016': ['Day', 'Day', 'Day', 'Day', 'Day', 'Day'],
  'LOC-017': ['Day', 'Day', 'Day', 'Day', 'Day', 'Day'],
  'LOC-018': ['Day', 'Day', 'Day', 'Day', 'Day', 'Day']
};

for (const location of LOCATIONS) {
  const design = locationDesign(location.id);
  const masterBase = `A human-height medium-wide environmental portrait of ${location.name} in Southern Song Linan. ${design.master_description} Its architecture, work surfaces, entrances, circulation paths, local storage and occupation-related tools are spatially clear. Anonymous residents and workers carry the everyday activity.`;
  const masterPositive = `${masterBase} ${routeText(LOCATION_ROUTES[location.id][0])}`;
  addRecord({
    prompt_id: `MJ-V2-${location.id}-MASTER`,
    target_key: `LOCATION:${location.id}:MASTER`,
    family: 'location',
    asset_lane: 'location-master',
    target: { stable_id: location.id, name: location.name, asset_id: 'MASTER' },
    authority_refs: [sourceRef('canon/city/00-city-index.md', 'canonical-location-index'), sourceRef('canon/city/10-seasonal-location-state.md', 'seasonal-location-state'), ...design.canonical_sources.map((relativePath) => sourceRef(relativePath, 'canonical-location-detail'))],
    facts_snapshot: { location_id: location.id, name: location.name, state_group: location.group },
    route: LOCATION_ROUTES[location.id][0],
    glamour_level: location.id === 'LOC-006' ? 4 : 2,
    ar: '16:9',
    stylize: LOCATION_ROUTES[location.id][0] === 'StageFestival' ? 210 : 155,
    chaos: 3,
    positive: masterPositive,
    execution_status: 'READY_FOR_V2_LOCATION_CALIBRATION'
  });
  for (let stateIndex = 0; stateIndex < 6; stateIndex += 1) {
    const route = LOCATION_ROUTES[location.id][stateIndex];
    const stateCode = `S${stateIndex + 1}`;
    addRecord({
      prompt_id: `MJ-V2-${location.id}-${stateCode}`,
      target_key: `LOCATION:${location.id}:${stateCode}`,
      family: 'location',
      asset_lane: 'seasonal-location-state',
      target: { stable_id: location.id, name: location.name, asset_id: stateCode },
      authority_refs: [sourceRef('canon/city/10-seasonal-location-state.md', 'seasonal-location-state'), sourceRef('canon/city/00-city-index.md', 'canonical-location-index'), ...design.canonical_sources.map((relativePath) => sourceRef(relativePath, 'canonical-location-detail'))],
      facts_snapshot: { location_id: location.id, name: location.name, seasonal_window: `E${String(stateIndex * 6 + 1).padStart(2, '0')}-E${String(stateIndex * 6 + 6).padStart(2, '0')}`, state_delta: LOCATION_GROUP_STATES[location.group][stateIndex] },
      route,
      glamour_level: route === 'StageFestival' ? 4 : 2,
      ar: '16:9',
      stylize: route === 'StageFestival' ? 220 : 155,
      chaos: 3,
      positive: `${masterBase} Canon seasonal state: ${LOCATION_GROUP_STATES[location.group][stateIndex]} Keep the established architecture, work surfaces, entry and exit logic, and material hierarchy unchanged. ${routeText(route)}`,
      execution_status: 'READY_FOR_V2_LOCATION_CALIBRATION'
    });
  }
}

const PROP_SPECS = Object.entries(worldVisualRegistry.props).map(([code, design]) => [code, design.route, design.states]);

for (const [code, route, states] of PROP_SPECS) {
  const design = propDesign(code);
  for (const state of states) {
    const stateText = state === 'USED' ? 'The object is in a carefully examined working state, with only the relevant fresh trace or handled edge visible.' : state === 'SEALED' ? 'The object is protected in plain oil paper with moisture only on the outer wrapping and a non-readable evidence tie.' : 'The object is intact and clearly observable before use or sealing.';
    addRecord({
      prompt_id: `MJ-V2-PROP-${code}-${state}`,
      target_key: `PROP:${code}:${state}`,
      family: 'prop-evidence',
      asset_lane: states.length > 1 ? 'object-state' : 'evidence-or-toolkit',
      target: { stable_id: `PROP-${code}`, asset_id: state },
      authority_refs: [sourceRef('canon/00-id-and-terms-registry.md', 'canon-object-registry'), ...design.canonical_sources.map((relativePath) => sourceRef(relativePath, 'prop-binding-authority'))],
      facts_snapshot: { prop_code: code, object_state: state, binding_status: design.binding_status },
      route,
      raw: true,
      glamour_level: 1,
      ar: '3:2',
      stylize: 95,
      chaos: 2,
      positive: `A single historically grounded Southern Song Linan evidence object or tightly bounded evidence grouping on a clean work surface, viewed at a natural product-study angle. ${design.description} State: ${stateText} ${routeText(route)} Documentary material-evidence framing with object-only composition and blank abstract paper markings.`,
      execution_status: 'READY_FOR_V2_PROP_CALIBRATION',
      acceptance_checks: [
        'Shows only the declared evidence or kit and the declared state.',
        'Material evidence remains physically plausible, distinct and unexaggerated.',
        'No hands, people, readable writing, red-string detective board or modern forensic apparatus.',
        'Any required correct text is added later in compositing, never trusted to the model.'
      ]
    });
  }
}

const relationshipSlots = readJson('qa/relationship-slots.json');
const relationshipEvidence = readJson('qa/relationship-evidence.json');
const evidenceByRelation = new Map(relationshipEvidence.relationships.map((entry) => [entry.relation_id, entry.snapshots]));

function routeForText(text) {
  if (/春台|瓦舍|桂花|夜市|演出|灯会/.test(text)) return 'StageFestival';
  if (/雨|夜|灯|船|湿|水|暗/.test(text)) return 'NightWet';
  return 'Day';
}

function characterName(id) {
  return profileById.get(id)?.facts?.name || id;
}

for (const relation of relationshipSlots.relationships) {
  const snapshots = evidenceByRelation.get(relation.id) || [];
  for (const snapshot of snapshots) {
    const memberIds = relation.members || [relation.left, relation.right];
    const people = memberIds.map(characterName).join('、');
    const route = routeForText(`${snapshot.space} ${snapshot.observable_action}`);
    const groupInstruction = relation.members ? 'Keep all five named people visually distinct, with no one framed as a generic crowd duplicate.' : 'Keep the two people at the stated relationship distance; no unearned touch or romance pose.';
    addRecord({
      prompt_id: `MJ-V2-${relation.id}-${snapshot.snapshot}`,
      target_key: `RELATIONSHIP:${relation.id}:${snapshot.snapshot}`,
      family: 'relationship',
      asset_lane: 'relationship-state-study',
      target: { stable_id: relation.id, asset_id: snapshot.snapshot, members: memberIds },
      authority_refs: [sourceRef('qa/relationship-slots.json', 'relationship-registry'), sourceRef('qa/relationship-evidence.json', 'relationship-evidence')],
      facts_snapshot: { relation_id: relation.id, kind: relation.kind, snapshot: snapshot.snapshot, episode_window: snapshot.episode_window, space: snapshot.space, object: snapshot.object, observable_action: snapshot.observable_action, continuity_delta: snapshot.continuity_delta },
      route,
      glamour_level: route === 'StageFestival' ? 4 : 3,
      ar: '16:9',
      stylize: route === 'StageFestival' ? 220 : 175,
      chaos: 3,
      positive: `A bounded relationship continuity study for ${people}, set at ${snapshot.space}. The visual action is: ${snapshot.observable_action} The shared object is ${snapshot.object}. The staging must preserve this continuity condition: ${snapshot.continuity_delta} ${groupInstruction} This is a state study, not an unapproved final episode shot; do not add dialogue, unrecorded knowledge or a new dramatic event. ${routeText(route)}`,
      execution_status: 'BLOCKED_UNTIL_IDENTITY_SELECTION_AND_EPISODE_GATE',
      depends_on: memberIds.map((id) => `CHARACTER:${id}:IDENTITY-001`),
      acceptance_checks: [
        'Uses only the registered relation members, snapshot, space, object and observable action.',
        'Preserves stated distance, boundary and continuity information without adding plot.',
        'Waits for selected identity assets and Episode Gate before becoming a deliverable shot.'
      ]
    });
  }
}

const unitSlots = readJson('qa/unit-slots.json');
for (const slot of unitSlots.slots) {
  const profession = slot.eligible_profession_families[0];
  addRecord({
    prompt_id: `MJ-V2-${slot.id}-EXPLORATION-001`,
    target_key: `UNIT:${slot.id}:EXPLORATION-001`,
    family: 'unit-slot',
    asset_lane: 'uncast-identity-exploration',
    target: { stable_id: slot.id, asset_id: 'EXPLORATION-001' },
    authority_refs: [sourceRef('qa/unit-slots.json', 'unit-slot-registry')],
    facts_snapshot: { category: slot.category, window: slot.window, eligible_profession_families: slot.eligible_profession_families, relation_slot: slot.relation_slot, source_status: slot.status },
    route: 'Day',
    technical: true,
    glamour_level: 2,
    ar: '3:4',
    stylize: 100,
    chaos: 5,
    positive: `An uncast, individual Chinese resident of Southern Song Linan designed only as an exploration for the ${slot.category} unit slot. Show one plausible ${profession} work context and a practical occupation gesture, with a distinct but not-yet-Canon face. Front-facing three-quarter identity-study composition, historically grounded clothing, real skin and material texture. ${routeText('Day', true)}`,
    execution_status: 'BLOCKED_UNTIL_CASTING_AND_EPISODE_GATE',
    depends_on: [`${slot.id}: cast age, gender presentation, named identity, exact location and action are not yet bound`],
    acceptance_checks: [
      'This is an exploration only and must not be promoted to a named character or final unit asset.',
      'A later casting decision must bind age, presentation, profession, location and continuity before use.'
    ]
  });
}

const backgroundUsage = readJson('qa/background-usage.json');
function normalizeLocationId(id) {
  const number = String(id).match(/\d+/)?.[0] || '0';
  return `LOC-${number.padStart(3, '0')}`;
}

for (const archetype of backgroundUsage.archetypes) {
  const locationId = normalizeLocationId(archetype.eligible_location_ids[0]);
  const isNight = /night|dusk/.test(archetype.active_time) || archetype.eligible_work_states.includes('rain');
  const route = isNight ? 'NightWet' : 'Day';
  addRecord({
    prompt_id: `MJ-V2-${archetype.id}-EXPLORATION-001`,
    target_key: `BACKGROUND:${archetype.id}:EXPLORATION-001`,
    family: 'background-archetype',
    asset_lane: 'ecosystem-exploration',
    target: { stable_id: archetype.id, asset_id: 'EXPLORATION-001' },
    authority_refs: [sourceRef('qa/background-usage.json', 'background-usage-registry')],
    facts_snapshot: { ...archetype, normalized_location_id: locationId },
    route,
    glamour_level: 2,
    ar: '2:3',
    stylize: 125,
    chaos: 5,
    positive: `One individually readable but uncast ${archetype.age_band} Chinese ${archetype.occupation_family} background resident in a representative ${locationId} work context, active at ${archetype.active_time}. Their class context is ${archetype.class_band}; usable materials are ${archetype.materials.join(', ')}. Show one specific working posture and space for a later scene composition, never a posed crowd or a named character. ${routeText(route)}`,
    execution_status: 'BLOCKED_UNTIL_MICROCHAPTER_BINDING',
    depends_on: [`${archetype.id}: exact microchapter, final location, work state and crowd composition remain RESERVED`],
    acceptance_checks: [
      'Keeps the registered age band, work family, class band, time and material set.',
      'Remains a background ecosystem exploration, not a static decorative extra or named person.',
      'A microchapter binding is required before final scene use.'
    ]
  });
}

const shen = profileById.get('CHR-L1-01');
const shenManifest = readJson('production/assets/characters/shen-heng/asset-manifest.json');
const seasonLedger = readJson('story/season/season-causal-ledger.json');
const shenBase = 'Shen Heng, a beautiful, believable 20-year-old adult Chinese woman and fragrance artisan. Preserve her quiet oval-heart face, slightly lifted warm-brown almond eyes, natural straight brows, refined natural nose, soft peach-coral lips, soft dark brown-black hair and the subtle dry fragrance-powder traces on her right thumb and index finger. Her skin is satin-translucent and healthy with fine pores, delicate microtexture, faint peach fuzz, subtle tonal variation, real lip lines and controlled moisture highlights; her adult facial geometry remains clear and naturally polished.';

const SHEN_COSTUMES = {
  C01: 'daily attire: milk-white layered crossed-collar robe, pale mist-blue embroidered collar, muted sage sash, fine woven floral texture and clean, city-ready layering; glamour level 2.',
  C02: 'work attire: fitted inner sleeves under a graceful pale outer layer, a protective apron panel and tool pouch, with the right hand free for fragrance work; glamour level 2.',
  C03: 'social visit attire: finer woven floral pattern, a translucent beizi-like outer layer, a small gift case, restrained jade accent and a polished half-up coiffure; glamour level 3.',
  C04: 'formal civic attire: dignified layered Song silhouette, silver-blue jacquard, narrow metallic-thread edging, a sculpted formal updo and a coordinated jade-and-pearl hairpin system; glamour level 4.',
  C05: 'night attire: deep blue-grey and mist-blue silk layers with a subtle satin response, a clear complete collar, protected movement and a dark wood hairpin; glamour level 2.',
  C06: 'rain attire: blue-grey woven rain layer over pale inner silk, physically wet sleeve edges, protected hair and a compact polished silhouette; glamour level 2.',
  C07: 'winter attire: aged ivory and blue-grey insulating layers, credible woven warmth, a soft fur-edged collar and a refined textured sash; glamour level 2.',
  C08: 'injury attire: a clean left-forearm bandage integrated into intact layered clothing, right-hand fragrance-work ability readable, calm dignified care-state styling; glamour level 1.',
  C09: 'long-labor attire: fine natural folds, fragrance powder and paper dust from extended work, layered fabric and hair kept tidy through a long day; glamour level 1.',
  C10: 'story-special attire: deeper blue and silver-grey structural layers within her fixed palette, floral jacquard, narrow silver thread, a more sculpted coiffure and refined fragrance-artisan authority; glamour level 4.'
};

const SHEN_SHEETS = {
  'EX-001': ['calm', 'natural happiness', 'comforting concern', 'careful intimacy', 'shame', 'sadness', 'alertness', 'resolve', 'quiet relief'],
  'EX-002': ['fear', 'contained anger', 'jealousy', 'guilt', 'disappointment', 'helplessness', 'hope', 'despair held back', 'acceptance'],
  'MK-001': ['barely-there daily base', 'workday matte', 'rain-resilient', 'social visit', 'formal civic', 'night lamp', 'winter dry air', 'fatigued but clean', 'post-work reset'],
  'HR-001': ['daily half-up', 'work-secured', 'rain-protected', 'social braid', 'formal restrained updo', 'night low knot', 'winter wrapped', 'care-work practical', 'ending spring-letter house']
};

const SHEN_ACTIONS = {
  'AC-001': ['weighing', 'lifting a sample with tweezers', 'grinding', 'sifting powder', 'smelling with a held breath', 'recording an observation', 'verifying a material edge', 'sealing a packet', 'returning tools to order'],
  'AC-002': ['walking', 'stopping to observe', 'turning back', 'raising one hand to pause', 'passing an object', 'taking an object', 'sitting to work', 'standing from a worktable', 'leaving quickly but safely'],
  'PS-001': ['neutral standing', 'side standing', 'natural seated work', 'turning', 'leaning to observe', 'crouching to retrieve', 'looking back', 'crossing a threshold', 'resting posture'],
  'PS-002': ['contained', 'closed-off', 'alert', 'decisive', 'tired', 'relieved', 'grieving but working', 'resistant', 'open to correction'],
  'CAM-001': ['eye close detail', 'full face', 'bust portrait', 'waist-up', 'three-quarter body', 'full body', 'side profile', 'back view', 'right-hand fragrance-work detail']
};

const SHEN_PROP_TILES = {
  'PR-001': ['celadon hairpin', 'dark wood hairpin', 'small drop earring', 'fragrance pouch', 'letter sleeve', 'waist fastener', 'cloth shoes'],
  'PR-002': ['bamboo tweezers', 'scent-test paper', 'powder dish', 'small ceramic jar', 'stone mortar', 'soft brush', 'blank ledger', 'brass scale', 'cloth pouch']
};

const SHEN_APPEARANCE = {
  'S1-AP-A01': ['spring investigation look', 'pale mist-blue collar, milk-white outer layer and sage sash; dry workable sleeves at the fragrance shop', 'Day'],
  'S1-AP-A02': ['rain investigation look', 'blue-gray rain layer with protected papers and restrained wet textile edges', 'NightWet'],
  'S1-AP-A03': ['summer field-verification look', 'breathable pale layers, work sash and sun-softened natural skin while checking river or field evidence', 'Day'],
  'S1-AP-A04': ['autumn ordinary-life look', 'aged ivory, celadon and restrained osmanthus-toned woven detail for ordinary life', 'Day'],
  'S1-AP-A05': ['winter restriction look', 'ivory and blue-gray insulated work layers with good tailoring, woven warmth and a modest silver-blue finishing detail, useful for clinic and supply work', 'NightWet'],
  'S1-AP-A06-flood-relief': ['flood-relief look', 'rain-ready dark blue-gray outer layer with compact practical layers, visibly wet only at appropriate edges', 'NightWet'],
  'S1-AP-A06-ending-spring-letter-house': ['spring-letter-house ending look', 'renewed but practical soft celadon and aged ivory layers, small repairable ornaments, fine floral woven texture and a calm private-city silhouette', 'Day']
};

const SHEN_GLAMOUR_FINISH = {
  1: 'A well-kept professional finish: complete crossed collar, clean layered fabric, a tidy hairstyle and one small useful personal detail.',
  2: 'A refined daily finish: tailored layered silk and ramie, visible woven pattern, a narrow embroidered edge, a polished hairpin and gentle light catching the cloth.',
  3: 'A social finish: richer dye depth, subtle floral jacquard, a translucent outer layer, a coordinated jade or pearl detail and softly luminous material response.',
  4: 'A formal New Song finish: sculpted layered silhouette, hand-finished embroidery, narrow silver thread, a coordinated hairpin-and-earring system and real light articulating silk, metal and skin.'
};

function shenGlamourLevel(task, assetId) {
  if (task.kind === 'costume' && /C04|C10/.test(assetId)) return 4;
  if (task.kind === 'costume' && /C03/.test(assetId)) return 3;
  if (task.kind === 'seasonal-appearance') return 3;
  if (task.kind === 'narrative-still' || task.kind === 'seasonal-narrative') return 3;
  if (task.kind === 'identity') return 2;
  return 2;
}

function shenPromptSettings(task, assetId) {
  if (task.technical) {
    return { raw: true, stylize: task.kind === 'identity' ? 100 : 88, chaos: 2 };
  }
  if (task.kind === 'costume') {
    return { raw: true, stylize: /C04|C10/.test(assetId) ? 175 : 150, chaos: 2 };
  }
  if (task.kind === 'seasonal-appearance') return { raw: false, stylize: 175, chaos: 3 };
  if (task.kind === 'seasonal-evidence') return { raw: true, stylize: 105, chaos: 2 };
  if (task.kind === 'narrative-still' || task.kind === 'seasonal-narrative') return { raw: false, stylize: 195, chaos: 3 };
  return { raw: false, stylize: 150, chaos: 3 };
}

const SHEN_EVIDENCE = {
  'S1-PR-A01-material-clue-board': ['separated old incense chest, ash, grain dust, canal fragment and water-route tag, no red string and no readable paper', 'Day'],
  'S1-PR-A02-old-case-privacy-board': ['protected old case page, oil-paper private letter, separated source envelope and route record, no readable paper', 'NightWet'],
  'S1-PR-A03-supply-water-combined-report-board': ['false-bottom grain crate trace, warehouse bundle, tide-marked slip and separated sources, no final conclusion', 'Day'],
  'S1-PR-A04-osmanthus-manuscript-board': ['fresh osmanthus, weathered personal manuscript, fragrance pouch and paper dividers, ordinary life beside incomplete evidence', 'Day'],
  'S1-PR-A05-lockdown-epidemic-map-board': ['abstract case-and-water-route map, medicine record, reed sample and separate tools, no modern medicine or readable labels', 'NightWet'],
  'S1-PR-A06-spring-lantern-correction-board': ['practical lantern, tactile rope markers, small copper sound pieces, route tags and weather cover, a coordination kit with no readable ledger', 'NightWet']
};

function shenNarrativeV2Spec(assetId) {
  const match = assetId.match(/^S1-NV-(E\d{2})([A-Z]?)-(.+)$/);
  if (!match) throw new Error(`Malformed Shen narrative asset id: ${assetId}`);
  const [, episodeCode, suffix, slug] = match;
  const episodeId = `S1-${episodeCode}`;
  const episode = seasonLedger.episodes.find((entry) => entry.episode_id === episodeId);
  if (!episode) throw new Error(`Missing season-ledger entry for ${assetId}`);
  const focus = slug.replace(/-/g, ' ');
  const action = episode.profession_action?.action || 'one registered fragrance-verification action';
  const evidence = episode.city_evidence?.description || 'only the registered bounded evidence';
  const routeSignals = `${assetId} ${episode.opening_state || ''} ${action} ${evidence}`;
  const route = /night|rain|snow|flood|water|封|雨|夜|灯|湿|水|暗/i.test(routeSignals) ? 'NightWet' : 'Day';
  return {
    tile: 'narrative',
    kind: 'seasonal-narrative',
    ar: '16:9',
    detail: `A bounded V2 Shen Heng narrative continuity study focused on ${focus}. Show only the documented opening state: ${episode.opening_state}. Center the registered professional action: ${action}. Evidence in view is limited to: ${evidence}. Do not add dialogue, a solution, an unregistered person or later-episode knowledge.`,
    route,
    technical: false,
    authority_paths: ['story/season/season-causal-ledger.json']
  };
}

function shenTaskSpecs(assetId) {
  if (assetId.startsWith('ID-001')) return [{ tile: 'front-neutral', kind: 'identity', ar: '3:4', detail: 'front-facing neutral head-and-upper-torso identity render, level head, all facial features unobstructed and hands resting below the crop.', technical: true }];
  if (assetId.startsWith('ID-002')) return ['front', 'left-three-quarter', 'left-profile', 'right-three-quarter', 'right-profile'].map((tile) => ({ tile, kind: 'identity-angle', ar: '3:4', detail: `${tile} head view, same neutral expression, same makeup and same clean collar, individual task only.`, technical: true }));
  if (assetId.startsWith('ID-003')) return ['front-full-body', 'left-profile-full-body', 'back-full-body'].map((tile) => ({ tile, kind: 'turnaround', ar: '2:3', detail: `${tile} full body from head to footwear, neutral stance, consistent garment construction, individual task only.`, technical: true }));
  if (assetId.startsWith('ID-004')) return ['face-skin', 'hairline-and-strands', 'right-hand-professional-trace', 'collar-and-textile'].map((tile) => ({ tile, kind: 'detail', ar: '1:1', detail: `macro continuity detail of ${tile}; no collage, no labels.`, technical: true }));
  for (const [prefix, tiles] of Object.entries(SHEN_SHEETS)) {
    if (assetId.startsWith(prefix)) return tiles.map((tile) => ({ tile, kind: prefix === 'MK-001' ? 'makeup-state' : prefix === 'HR-001' ? 'hair-state' : 'expression', ar: '3:4', detail: `${prefix === 'MK-001' ? 'same face, light historical makeup state' : prefix === 'HR-001' ? 'same face, same light makeup, hairstyle state' : 'single restrained facial expression'}: ${tile}. Individual render, no grid.`, technical: true }));
  }
  for (const [prefix, tiles] of Object.entries(SHEN_ACTIONS)) {
    if (assetId.startsWith(prefix)) return tiles.map((tile) => ({ tile, kind: prefix === 'CAM-001' ? 'camera-framing' : 'pose-or-motion', ar: prefix === 'CAM-001' ? '3:4' : '2:3', detail: `${prefix === 'CAM-001' ? 'single camera-framing continuity view' : 'single natural body action or pose'}: ${tile}. Individual render, no grid.`, technical: true }));
  }
  for (const [prefix, tiles] of Object.entries(SHEN_PROP_TILES)) {
    if (assetId.startsWith(prefix)) return tiles.map((tile) => ({ tile, kind: 'personal-prop', ar: '3:2', detail: `single object material study of Shen Heng's ${tile}; object-only frame on a clean work surface with blank, unmarked supporting paper where needed.`, technical: true }));
  }
  const costume = Object.entries(SHEN_COSTUMES).find(([prefix]) => assetId.startsWith(prefix));
  if (costume) return [{ tile: 'full-look', kind: 'costume', ar: '2:3', detail: `front-facing full-body New Song wardrobe presentation. ${costume[1]} Natural poised stance, complete silhouette and clean construction visibility.`, technical: false, raw: true }];
  const appearanceKey = Object.keys(SHEN_APPEARANCE).find((key) => assetId.startsWith(key));
  const appearance = appearanceKey ? SHEN_APPEARANCE[appearanceKey] : null;
  if (appearance) return [{ tile: 'appearance', kind: 'seasonal-appearance', ar: '2:3', detail: `${appearance[0]}; ${appearance[1]}. Front three-quarter full-body continuity render.`, route: appearance[2], technical: false }];
  const evidenceKey = Object.keys(SHEN_EVIDENCE).find((key) => assetId.startsWith(key));
  const evidence = evidenceKey ? SHEN_EVIDENCE[evidenceKey] : null;
  if (evidence) return [{ tile: 'evidence', kind: 'seasonal-evidence', ar: '3:2', detail: `Top-down practical evidence arrangement: ${evidence[0]}. No person or hand.`, route: evidence[1], technical: false }];
  if (assetId.startsWith('NV-001')) return [{ tile: 'narrative', kind: 'narrative-still', ar: '2:3', detail: 'spring official character portrait at a garden stone rail, holding a blank fragrance slip; not a poster and no text.', route: 'Day', technical: false }];
  if (assetId.startsWith('NV-002')) return [{ tile: 'narrative', kind: 'narrative-still', ar: '16:9', detail: 'fragrance-shop work still: bamboo tweezers, blank fragrance slip, window light, ceramic jars and scale, one clear decision moment.', route: 'Day', technical: false }];
  if (assetId.startsWith('NV-003')) return [{ tile: 'narrative', kind: 'narrative-still', ar: '16:9', detail: 'waterside daylight return, natural walking rhythm, fragrance pouch, bridge, willow, shopfront and water-depth perspective.', route: 'Day', technical: false }];
  if (assetId.startsWith('NV-004')) return [{ tile: 'narrative', kind: 'narrative-still', ar: '2:3', detail: 'rain-night clue still, a side-held oil-paper umbrella, warm local lamp against cool rain, no supernatural light.', route: 'NightWet', technical: false }];
  if (assetId.startsWith('NV-005')) return [{ tile: 'narrative', kind: 'narrative-still', ar: '16:9', detail: 'lamp-lit fragrance verification, test paper and evidence sheet in separate hands, warm oil lamp and a cool window edge.', route: 'NightWet', technical: false }];
  if (assetId.startsWith('S1-NV-')) {
    return [shenNarrativeV2Spec(assetId)];
  }
  throw new Error(`No Shen task specification for ${assetId}`);
}

const shenCrosswalk = {};
for (const asset of shenManifest.assets) {
  const tasks = shenTaskSpecs(asset.id);
  shenCrosswalk[asset.id] = [];
  for (const task of tasks) {
    const safeTile = task.tile.replace(/[^a-z0-9]+/gi, '-').replace(/^-|-$/g, '').toUpperCase();
    const promptId = `MJ-V2-SHEN-${asset.id.toUpperCase()}-${safeTile}`;
    const targetKey = `SHEN:${asset.id}:${task.tile}`;
    shenCrosswalk[asset.id].push(targetKey);
    const route = task.route || 'Day';
    const technical = task.technical;
    const glamourLevel = shenGlamourLevel(task, asset.id);
    const settings = shenPromptSettings(task, asset.id);
    addRecord({
      prompt_id: promptId,
      target_key: targetKey,
      family: 'shen-heng-package',
      asset_lane: task.kind,
      target: { stable_id: 'CHR-L1-01', name: '沈蘅', asset_id: asset.id, tile: task.tile, manifest_category: asset.category },
      authority_refs: [sourceRef('characters/central/chr-l1-01-shen-heng.md', 'character-foundation-authority'), sourceRef('production/assets/characters/shen-heng/asset-manifest.json', 'existing-package-manifest'), ...(task.authority_paths || []).map((relativePath) => sourceRef(relativePath, 'seasonal-narrative-authority'))],
      facts_snapshot: { name: shen.facts.name, age_y0: shen.facts.age_y0, occupation: shen.facts.occupation, source_asset_id: asset.id, source_category: asset.category, task_tile: task.tile },
      route,
      technical,
      raw: task.raw ?? settings.raw,
      glamour_level: glamourLevel,
      ar: task.ar,
      stylize: settings.stylize,
      chaos: settings.chaos,
      positive: `${shenBase} ${SHEN_GLAMOUR_FINISH[glamourLevel]} ${task.detail} ${routeText(route, technical)}`,
      execution_status: 'REBUILD_AFTER_V2_STYLE_AND_IDENTITY_SIGNOFF',
      assembly: tasks.length > 1 ? { assembly_group: asset.id, tile: task.tile, strategy: 'Generate this task independently; select and assemble locally after review. Do not ask Midjourney to create a composite board or grid.' } : null,
      acceptance_checks: [
        'Matches the 20-year-old Shen Heng profile and the declared asset task.',
        'Preserves facial identity, age, hand traces and true skin texture across every selected task.',
        technical ? 'Technical task is clean, single-view and clear enough for continuity comparison.' : 'Narrative task preserves only the stated evidence/action and correct V2 route.',
        'The selected candidate is upscaled only after V2 visual and identity signoff; no native 8K claim.'
      ]
    });
  }
}

for (const episode of seasonLedger.episodes) {
  const sourceText = `${episode.opening_state} ${episode.title} ${episode.profession_action?.action || ''}`;
  const route = routeForText(sourceText);
  const primaryName = characterName(episode.profession_action?.character_id || episode.episode_choice?.actor || '');
  addRecord({
    prompt_id: `MJ-V2-${episode.episode_id}-PREMISE-001`,
    target_key: `EPISODE:${episode.episode_id}:PREMISE-001`,
    family: 'season-episode',
    asset_lane: 'episode-premise-study',
    target: { stable_id: episode.episode_id, asset_id: 'PREMISE-001' },
    authority_refs: [sourceRef('story/season/season-causal-ledger.json', 'season-causal-ledger')],
    facts_snapshot: { episode_id: episode.episode_id, title: episode.title, opening_state: episode.opening_state, city_evidence: episode.city_evidence?.description, profession_action: episode.profession_action?.action, episode_choice: episode.episode_choice?.action, location_ids: episode.city_evidence?.location_ids || [] },
    route,
    glamour_level: route === 'StageFestival' ? 4 : 3,
    ar: '16:9',
    stylize: route === 'StageFestival' ? 230 : 180,
    chaos: 3,
    positive: `A bounded visual premise study for ${episode.episode_id}, ${episode.title}. Show the documented opening state: ${episode.opening_state} Center the known professional action of ${primaryName}: ${episode.profession_action?.action || 'the registered episode action'}. The evidence in view is limited to: ${episode.city_evidence?.description || 'the registered city evidence'}. This is not a final shot and must not add dialogue, a solution, an unregistered person or later-episode knowledge. ${routeText(route)}`,
    execution_status: 'BLOCKED_UNTIL_EPISODE_GATE',
    acceptance_checks: [
      'Uses only the ledger opening state, professional action and evidence for this episode.',
      'Does not claim a final scene or invent an unbound screenplay event.',
      'Requires Episode Gate before delivery or image generation for production use.'
    ]
  });
}

const storyboard = readJson('production/episodes/S1-E01/storyboard.json');
for (const scene of storyboard.scenes) {
  for (const shot of scene.shots) {
    const primary = characterName(shot.blocking?.primary_actor || '');
    const route = routeForText(`${scene.scene_binding?.weather_state || ''} ${(shot.light?.physical_sources || []).join(' ')}`);
    addRecord({
      prompt_id: `MJ-V2-${shot.shot_id}`,
      target_key: `SHOT:${shot.shot_id}`,
      family: 'episode-shot',
      asset_lane: 'draft-shot-visualization',
      target: { stable_id: shot.shot_id, scene_id: scene.scene_id, asset_id: shot.shot_id },
      authority_refs: [sourceRef('production/episodes/S1-E01/storyboard.json', 'episode-storyboard')],
      facts_snapshot: { scene_id: scene.scene_id, shot_id: shot.shot_id, scene_status: scene.status, purpose: shot.purpose, primary_actor: shot.blocking?.primary_actor || null, action_path: shot.blocking?.action_path || shot.blocking?.movement || '', prop_handling: shot.blocking?.prop_handling || '', camera: shot.camera, light: shot.light, temporal: shot.temporal },
      route,
      glamour_level: route === 'StageFestival' ? 3 : 2,
      ar: '16:9',
      stylize: route === 'StageFestival' ? 190 : 140,
      chaos: 3,
      positive: `A precise draft-shot visualization for ${shot.shot_id} in ${scene.scene_id}. Purpose: ${shot.purpose}. ${primary ? `Primary performer: ${primary}.` : ''} Blocking: ${shot.blocking?.action_path || shot.blocking?.movement || 'follow the registered action zones.'} Prop handling: ${shot.blocking?.prop_handling || 'preserve registered object placement.'} Camera: ${shot.camera?.scale || 'registered scale'}, ${shot.camera?.angle || 'registered angle'}, ${shot.camera?.focal_length || 'natural lens'}, maintaining ${shot.camera?.axis_side || 'the registered axis'}. Physical light sources: ${(shot.light?.physical_sources || []).join(', ')}. Do not add dialogue, action, knowledge, people, lens effect or geographic detail outside this DRAFT-EPISODE-GATE record. ${routeText(route)}`,
      execution_status: 'BLOCKED_UNTIL_EPISODE_GATE',
      depends_on: [`${scene.scene_id}: Episode Gate is ${scene.status}`],
      acceptance_checks: [
        'Matches the exact storyboard purpose, blocking, prop state, lens, axis and physical light sources.',
        'Does not fabricate dialogue, a new character, a later plot fact or a final delivery claim.',
        'Cannot enter production generation until the Episode Gate is locked.'
      ]
    });
  }
}

const CALIBRATIONS = [
  ['DAY-CANAL', 'Day', '16:9', 'a dense Linan canal-market day: narrow waterway, loaded working boats, damp timber wharves, stacked trade parcels, food stalls, pedestrians and layered Song roofs; the water and labor routes remain clear, not a quiet tourist town.'],
  ['DAY-GOLDEN-TEA', 'Day', '16:9', 'a late-afternoon Linan tea-table social moment in a working market courtyard: one elegant but believable young adult Chinese woman in historically grounded layered ivory and soft-celadon clothing, seated naturally with a small tea vessel, warm side-back sunlight catching real skin, silk and glazed ceramic, nearby people and market activity softly present behind her; no studio portrait staging.'],
  ['DAY-TEXTILE-YARD', 'Day', '16:9', 'a busy Linan laundry and textile-work yard: several Chinese workers washing, lifting, folding and carrying long pale silk and woven cloth across wooden racks, low warm sunlight passing through moving fabric to reveal translucent fibers, wet hems, baskets, lacquered chests and active work routes; realistic labor rather than a fashion tableau.'],
  ['DAY-FRAGRANCE-SHOP', 'Day', '16:9', 'the interior and threshold of a working Linan fragrance shop: incense chest, scale, jars, paper, racks and a clear street-facing counter, with ordinary trade and practical access.'],
  ['NIGHT-WET-LANE', 'NightWet', '16:9', 'a rain-wet Linan lane with occupied eaves, local lantern pools, oilcloth covers, people continuing practical work and physical reflections on stone; no neon or fantasy fog.'],
  ['NIGHT-LANTERN-CORRIDOR', 'NightWet', '16:9', 'an evening Linan covered corridor used for a small public gathering: dark cinnabar timber columns, softly glowing handmade paper lanterns and candle stands receding toward a real vanishing point, ivory curtains moving gently at the edges, warm light on silk and wood balanced by quiet blue-grey exterior depth, attendants and guests using the corridor naturally; elegant but not a palace.'],
  ['STAGE-BACKSTAGE', 'StageFestival', '16:9', 'a Chun Tai performance-house backstage: mending sleeves, cue passage, hairpin repair, small lamps and visible labor behind a refined but historically plausible ornament system.'],
  ['FESTIVAL-PUBLIC-ROUTE', 'StageFestival', '16:9', 'a public osmanthus festival route in Linan: layered but grounded textiles, blossom parcels, warm lamps, market service and safe circulation, never a palace celebration.']
];

for (const [id, route, ar, subject] of CALIBRATIONS) {
  addRecord({
    prompt_id: `MJ-V2-CAL-${id}`,
    target_key: `CALIBRATION:${id}`,
    family: 'style-calibration',
    asset_lane: 'style-calibration',
    target: { stable_id: 'VIS-LW-V2', asset_id: id },
    authority_refs: [sourceRef('production/style/v2-urban-splendor-song-style-package.md', 'v2-style-authority'), sourceRef('production/style/v2-visual-qa.md', 'v2-qa')],
    facts_snapshot: { calibration_id: id, route: ROUTE_KEY[route] },
    route,
    glamour_level: route === 'StageFestival' ? 5 : 3,
    ar,
    stylize: route === 'StageFestival' ? 250 : 180,
    chaos: 5,
    positive: `${subject} ${routeText(route)}`,
    execution_status: 'READY_FOR_V2_STYLE_CALIBRATION',
    acceptance_checks: [
      'Tests the route rather than an individual character identity.',
      'Must pass the V2 visual QA before any project Style Reference is selected.',
      'No user-uploaded or unapproved external reference is attached automatically.'
    ]
  });
}

catalog.sort((a, b) => a.prompt_id.localeCompare(b.prompt_id, 'en'));
const familyCounts = Object.fromEntries([...new Set(catalog.map((record) => record.family))].sort().map((family) => [family, catalog.filter((record) => record.family === family).length]));
const inventory = {
  schema_version: 2,
  inventory_id: 'LINAN-VIS-LW-V2-MJ8.2-ALL-ASSET-INVENTORY',
  generated_on: GENERATED_ON,
  style_contract: 'VIS-LW-V2',
  model_contract: 'Midjourney V8.2',
  scope_note: 'Every current declared asset target is represented by one resolved V2 prompt record. Reserved units, backgrounds, relation snapshots and episode shots are represented as explicit blocked specs rather than falsely claimed as ready-to-generate delivery assets.',
  targets: catalog.map((record) => ({ target_key: record.target_key, prompt_id: record.prompt_id, family: record.family, asset_lane: record.asset_lane, execution_status: record.execution_status }))
};
const mainCatalog = {
  schema_version: 2,
  catalog_id: 'LINAN-VIS-LW-V2-MJ8.2',
  generated_on: GENERATED_ON,
  style_contract: 'VIS-LW-V2',
  model_contract: {
    model: 'Midjourney V8.2',
    required_parameters: ['--v 8.2', '--ar', '--s', '--c'],
    lane_specific_parameters: ['--raw for identity, structure and prop-continuity lanes', '--no only after verified one-fault calibration; catalog allows text, watermark or logo as one-word targets'],
    optional_after_approval_only: ['V8.2 Image Prompt in the web UI; verified image URL plus --iw 1.0 to 1.5 only when rights and identity authorization are documented', 'Style Reference plus --sref and --sw only after a project-generated V2 candidate is selected'],
    not_emitted_without_target_session_verification: ['--sv'],
    prohibited_parameters: ['--oref', '--ow', '--cref', '--cw', '--q', '--quality', '--draft', 'multi-prompt ::']
  },
  source_manifest: [
    sourceRef('production/style/v2-urban-splendor-song-style-package.md', 'v2-style-authority'),
    sourceRef('production/style/v2-visual-qa.md', 'v2-qa'),
    sourceRef('production/style/v2-reference-policy.md', 'v2-reference-policy'),
    sourceRef('production/style/v2-world-reference-atoms.md', 'v2-reference-atoms'),
    sourceRef('production/style/v2-world-asset-visual-registry.json', 'v2-world-asset-visual-registry'),
    sourceRef('qa/character-roster.json', 'named-character-registry'),
    sourceRef('qa/unit-slots.json', 'unit-slot-registry'),
    sourceRef('qa/background-usage.json', 'background-registry'),
    sourceRef('qa/relationship-slots.json', 'relationship-registry'),
    sourceRef('qa/relationship-evidence.json', 'relationship-evidence'),
    sourceRef('canon/city/00-city-index.md', 'location-registry'),
    sourceRef('canon/city/10-seasonal-location-state.md', 'location-state-registry'),
    sourceRef('story/season/season-causal-ledger.json', 'season-ledger'),
    sourceRef('production/episodes/S1-E01/storyboard.json', 'episode-storyboard'),
    sourceRef('production/assets/characters/shen-heng/asset-manifest.json', 'shen-package-manifest')
  ],
  coverage_contract: {
    named_character_visual_anchor_tasks: roster.named_characters.length,
    central_character_identity_anchors: roster.named_characters.filter((character) => /^L[123]$/.test(character.tier)).length,
    central_character_hero_key_art: roster.named_characters.filter((character) => /^L[123]$/.test(character.tier)).length,
    canonical_location_masters: LOCATIONS.length,
    canonical_location_season_states: LOCATIONS.length * 6,
    prop_and_evidence_states: PROP_SPECS.reduce((sum, [, , states]) => sum + states.length, 0),
    relationship_snapshots: relationshipSlots.relationships.length * relationshipSlots.snapshots.length,
    unit_slot_explorations: unitSlots.slots.length,
    background_archetype_explorations: backgroundUsage.archetypes.length,
    shen_manifest_assets: shenManifest.assets.length,
    shen_independent_render_tasks: Object.values(shenCrosswalk).reduce((sum, tasks) => sum + tasks.length, 0),
    season_episode_premises: seasonLedger.episodes.length,
    e01_draft_storyboard_shots: catalog.filter((record) => record.family === 'episode-shot').length,
    style_calibrations: CALIBRATIONS.length
  },
  crosswalks: {
    shen_manifest_asset_to_independent_tasks: shenCrosswalk,
    background_location_id_normalization: 'LOC-01 through LOC-18 from qa/background-usage.json normalize to LOC-001 through LOC-018 in the catalog only; the source registry is not rewritten.'
  },
  records: catalog
};

const report = {
  catalog_id: mainCatalog.catalog_id,
  generated_on: GENERATED_ON,
  record_count: catalog.length,
  family_counts: familyCounts,
  coverage_contract: mainCatalog.coverage_contract,
  status_breakdown: Object.fromEntries([...new Set(catalog.map((record) => record.execution_status))].sort().map((status) => [status, catalog.filter((record) => record.execution_status === status).length])),
  notes: [
    'All direct mj_text values are fully resolved Midjourney V8.2 prompts with no unresolved style-reference placeholders.',
    'No direct prompt uses Omni Reference, Character Reference, --oref, --q, --quality, --draft or multi-prompt syntax; Raw and --no are lane-specific rather than global requirements.',
    'No prompt claims native 8K output. The 7680-pixel delivery target is an approved-source post-generation pipeline.',
    'Composite source assets are represented by independently generated tasks and must be locally assembled after human review.',
    'Reserved production targets remain explicit BLOCKED records; this preserves scope without fabricating locked casting or Episode Gate facts.'
  ]
};

writeJson('production/midjourney/v2-asset-prompt-inventory.json', inventory);
writeJson('production/midjourney/v2-asset-prompt-catalog.json', mainCatalog);
write('production/midjourney/v2/compiled/asset-prompts-v8.2.jsonl', `${catalog.map((record) => JSON.stringify(record)).join('\n')}\n`);
writeJson('production/midjourney/v2/validation/prompt-catalog-report.json', report);

const byFamily = new Map();
for (const record of catalog) {
  if (!byFamily.has(record.family)) byFamily.set(record.family, []);
  byFamily.get(record.family).push(record);
}
for (const [family, records] of byFamily) {
  const lines = [`# ${family}｜V2 Midjourney 8.2 full prompts`, '', `> Generated from locked project facts on ${GENERATED_ON}. All prompts below are direct-copy V8.2 text; execution status is stated per record.`, ''];
  for (const record of records) {
    lines.push(`## ${record.prompt_id}`, '', `- Target: \`${record.target_key}\``, `- V2 route: ${record.state.style_slot}; status: \`${record.execution_status}\``, '', '```text', record.prompt.mj_text, '```', '');
  }
  write(`production/midjourney/v2/prompts/${family}.md`, lines.join('\n'));
}

const summaryLines = [
  '# 《临安春信》V2 Midjourney 8.2 全量资产提示词',
  '',
  `> Catalog: \`${mainCatalog.catalog_id}\` · ${catalog.length} resolved prompt records · generated ${GENERATED_ON}.`,
  '',
  'This is the V2-only source of active Midjourney prompts. It contains complete V8.2 parameter strings for every declared target in the coverage contract; it does not treat an unbound reference image or a range template as a production prompt.',
  '',
  'Every narrative prompt uses the VIS-LW-V2 cinematic New Song visual grammar: motivated daylight or practical lantern light, physical silk/paper/wood/water response, readable working depth and controlled optical softness. Technical continuity tasks deliberately retain clean neutral presentation.',
  '',
  '## Family counts',
  '',
  ...Object.entries(familyCounts).map(([family, count]) => `- ${family}: ${count}`),
  '',
  '## Copyable prompt files',
  '',
  ...[...byFamily.keys()].sort().map((family) => `- [${family}](prompts/${family}.md)`),
  '',
  '## Machine-readable artifacts',
  '',
  '- `../v2-asset-prompt-catalog.json`: full authority, facts snapshot and copyable text for every target.',
  '- `../v2-asset-prompt-inventory.json`: one-to-one inventory contract.',
  '- `compiled/asset-prompts-v8.2.jsonl`: flat import/export form.',
  '- `validation/prompt-catalog-report.json`: generated coverage report.',
  '',
  '## Runtime reference policy',
  '',
  'The direct text does not contain a fake style URL or an unsupported identity parameter. After an approved V2 Style Reference or project-generated identity render exists, use the documented optional V8.2 binding policy in the catalog and `production/style/v2-reference-policy.md`; never attach raw user references automatically.',
  ''
];
write('production/midjourney/v2/README.md', summaryLines.join('\n'));

console.log(JSON.stringify({ catalog: mainCatalog.catalog_id, recordCount: catalog.length, familyCounts, output: 'production/midjourney/v2-asset-prompt-catalog.json' }, null, 2));
