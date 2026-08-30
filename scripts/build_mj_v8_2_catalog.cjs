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
const GENERATED_ON = '2026-08-30';

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

function sentence(value) {
  const text = compact(value).replace(/[.\s]+$/, '');
  return text ? `${text.charAt(0).toUpperCase()}${text.slice(1)}.` : '';
}

function normalizePromptBody(value) {
  return compact(value)
    .replace(/\.{2,}/g, '.')
    .replace(/([.!?]\s+)([a-z])/g, (match, lead, letter) => `${lead}${letter.toUpperCase()}`);
}

function promptNameFromCharacter(character) {
  const stem = path.basename(character.profile_path, path.extname(character.profile_path));
  const prefix = `${character.id.toLowerCase()}-`;
  const latin = stem.startsWith(prefix) ? stem.slice(prefix.length) : character.id.toLowerCase();
  return latin.split('-').filter(Boolean).map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1)}`).join(' ');
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
  if (atoms.length > 2) {
    throw new Error(`${promptId} uses more than two --no atoms`);
  }
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

const GLOBAL_SCREEN_GRAMMAR = 'Cinematic live-action Chinese historical-romance screen grammar: a lavish premium period drama, a gently readable foreground, an active middle ground and receding inhabited architecture, with people, goods or light following a real route. Practical sources shape the light; silk, lacquered timber, paper, ceramic, water and skin respond distinctly; restrained optical diffusion and smooth filmic highlight roll-off appear around actual bright sources.';

const STYLE = {
  V2_DAY: `${GLOBAL_SCREEN_GRAMMAR} Daylight urban-splendor route in a prosperous Southern Song Linan water-city: layered indigo, tea brown, celadon, aged ivory and restrained pomegranate accents; dense trade, labor and household use; physically distinct silk, woven cloth, paper, timber, ceramic, dull brass and water. Humid clear daylight or low warm afternoon sunlight passes through thin silk, cloth, paper or lattice, revealing fibers and working hands while faces retain natural exposure, sculpted volume and a clear catchlight.`,
  V2_NIGHT_WET: `${GLOBAL_SCREEN_GRAMMAR} Night and blue-hour route in a dense Southern Song Linan street, worksite or covered corridor: warm paper lanterns, oil lamps, candles or stove light create local amber pools while restrained blue-grey exterior ambience shapes the distance. Dark cinnabar timber, ivory curtains and practical eave framing establish depth where the documented location supports them; stone, lacquered wood, rope and water carry restrained reflections motivated by the actual weather and local light source.`,
  V2_STAGE_FESTIVAL: `${GLOBAL_SCREEN_GRAMMAR} Performance or festival route, historically grounded Southern Song urban splendor: coordinated woven silk layers, hand-finished embroidery, pomegranate, ink-blue and aged-ivory accents, refined hair ornaments and warm practical lantern or candle light. Fine gauze, curtains and a near foreground frame genuine backstage labor, performance circulation or public-market activity. Luxury is visible in dye depth, weave, maintenance, movement and motivated reflection.`
};

const TECHNICAL_STYLE = 'Cast-continuity portrait lane: a premium live-action Chinese historical-romance official character still, with a clean warm-ivory plaster background, soft large-window daylight, gentle reflected fill, calm direct presence, true facial geometry, individually readable hair strands and fine woven textile fibers. The face has luminous dimensional exposure, controlled cheek and lip highlights, visible natural surface detail and refined historical-drama polish. The collar, hairstyle and one personal ornament remain legible as a complete, elegant period look.';

const NATURAL_SKIN_SURFACE = 'Natural skin carries fine pores, subtle skin grain, delicate tonal variation around the eyelids and nostrils, soft under-eye volume, tiny natural highlights on the nose bridge and lips, visible lip lines and a believable response to the same light as hair, fabric and hands.';

function costumeConstruction(glamourLevel, presentation, occupation = '') {
  const waterWork = /水路|船|码头|镖/.test(occupation);
  const closeWork = /香|医|药|书|画|厨|馄饨|浆洗|绣|篾|伞|门|仓/.test(occupation);
  const silhouette = presentation === 'woman'
    ? 'a long vertical skirt line with controlled narrow pleats and a softly defined waist'
    : 'a tailored long-robed line with a clear waist fastening and controlled vertical folds';
  const workingFit = waterWork
    ? 'full sleeves gathered at the cuffs, a compact belt, shortened controlled outer panels and footwear suited to wet timber and boat movement'
    : closeWork
      ? 'full sleeves with workable inner cuffs, a secure waist sash, a clear hand-working zone and complete practical footwear'
      : 'full sleeves with a clear activity-ready cuff, a secure waist sash and complete footwear';
  const outerLayer = glamourLevel >= 4
    ? waterWork
      ? 'a fine river-teal outer panel with a water-ripple jacquard and a controlled edge that stays close to the body'
      : 'a lightweight semi-transparent silk-gauze outer layer that reveals the structured layers beneath'
    : glamourLevel >= 3
      ? 'a fine woven outer layer with a restrained translucent edge'
      : 'a fine woven outer layer with clear layer separation';
  const craft = glamourLevel >= 4
    ? 'One concentrated zone of raised floral jacquard, low-reflective silver or antique-gold thread and narrow woven brocade sits at the collar, cuffs, sash or hem, with a smaller matching border and large luminous areas of plain fabric.'
    : glamourLevel >= 3
      ? 'A concentrated floral jacquard or narrow woven border sits at the collar, cuffs or sash, balanced by broad plain fabric.'
      : 'A narrow woven edge or subtle tonal jacquard defines one collar, cuff or sash zone.';
  return `Complete crossed-collar construction with a visibly separate inner layer and structured middle layer, ${silhouette}, ${workingFit}, ${outerLayer}. ${craft} Matte silk, ramie, sheer gauze, woven brocade and small metal or pearl details show visibly different weave, thickness, fold and light response.`;
}

const ROUTE_KEY = {
  Day: 'V2-Day',
  NightWet: 'V2-Night-Wet',
  StageFestival: 'V2-Stage-Festival'
};

const V2_AUTHORITY_SPECS = [
  ['production/style/v2-urban-splendor-song-style-package.md', 'v2-style-authority'],
  ['production/style/v2-scene-composition-standard.md', 'v2-scene-composition-standard'],
  ['production/style/v2-costume-construction-standard.md', 'v2-costume-construction-authority'],
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
const POSITIVE_PROSE_NEGATIVE_PATTERN = /\b(?:no|not|never|without)\b|do not/i;

function addRecord(input) {
  const route = input.route || 'Day';
  const params = {
    model: '8.2',
    raw: input.raw ?? Boolean(input.technical),
    ar: input.ar || '3:4',
    stylize: input.stylize ?? 55,
    chaos: input.chaos ?? 3
  };
  const positive = normalizePromptBody(input.positive);
  if (POSITIVE_PROSE_NEGATIVE_PATTERN.test(positive)) {
    throw new Error(`${input.prompt_id} puts negative workflow or visual prose in the positive prompt body`);
  }
  if (/[\u3400-\u9fff]/.test(positive)) {
    throw new Error(`${input.prompt_id} puts untranslated CJK metadata or story prose in the direct Midjourney prompt`);
  }
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
      time: input.time || (route === 'NightWet' ? 'night-or-blue-hour' : route === 'StageFestival' ? 'performance-or-festival' : 'day'),
      weather: input.weather || (route === 'NightWet' ? 'night-or-blue-hour' : route === 'StageFestival' ? 'clear-or-lantern-lit' : 'clear-or-overcast')
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
  const femininePronouns = (profileMarkdown.match(/她/g) || []).length;
  const masculinePronouns = (profileMarkdown.match(/他/g) || []).length;
  if (femininePronouns > masculinePronouns + 2) return 'woman';
  if (masculinePronouns > femininePronouns + 2) return 'man';
  const feminine = /娘|婆|姐|姨|女|绣|巧|绮|月|素|慧|蔓|小青|阿沅|九娘|十四/.test(name + occupation);
  const masculine = /伯|叔|公|郎|生|匠|官|师|长庚|北鸿|成武|开元|怀川|行舟|砚之|惟敬|见山|兰度/.test(name + occupation);
  if (feminine && !masculine) return 'woman';
  if (masculine && !feminine) return 'man';
  if (femininePronouns > masculinePronouns) return 'woman';
  if (masculinePronouns > femininePronouns) return 'man';
  return 'adult';
}

function occupationEnglish(occupation) {
  const replacements = [
    [/调香师|香铺/, 'fragrance artisan and goods verifier'],
    [/歌伎|曲作者/, 'professional singer, stage performer and songwriter'],
    [/春台|瓦舍|戏|琵琶|说书|杂技|妆娘/, 'performance-house artist or theatre worker'],
    [/修伞|递铺/, 'umbrella-repair artisan and street-message runner'],
    [/北归社|赈济|施粥|安置/, 'mutual-aid and relief organizer'],
    [/签押|书吏|城门|军士|捕快/, 'civic record, gate or route worker'],
    [/画师|测绘|抄图/, 'map artist and spatial recorder'],
    [/水路|船主|镖师|船行|船工|船匠|渡工|水上|码头|押运|鱼/, 'river-route, dock or boat worker'],
    [/酒肆|护送/, 'tavern keeper familiar with water-and-road escort work'],
    [/医|药/, 'medical and herbal worker'],
    [/官|城务/, 'city-office worker'],
    [/浆洗|针线|绣/, 'textile and garment artisan'],
    [/篾/, 'bamboo-weaving and basket-repair artisan'],
    [/书坊|印|刻版|装裱/, 'bookshop, print or paper-work artisan'],
    [/厨|馄饨|食|豆腐|煎饼|粥摊/, 'food-service worker'],
    [/仓|货|商|账房|牙人|债/, 'trade, accounts or stockroom worker'],
    [/客舍/, 'guesthouse service and lodging worker'],
    [/寺|僧|行堂/, 'temple service and care worker'],
    [/花市/, 'flower-market worker and festival-goods maker'],
    [/佃农|草席/, 'rural migrant and woven-mat artisan']
  ];
  for (const [pattern, translation] of replacements) if (pattern.test(occupation)) return translation;
  return 'Linan urban craft, trade or service worker';
}

function extractIdentityAnchor(profileMarkdown) {
  const match = profileMarkdown.match(/\*\*稳定身份锚点\*\*[：:]\s*([^\n]+)/);
  return match ? compact(match[1]) : '';
}

const CENTRAL_IDENTITY = {
  'CHR-L1-01': 'a beautiful and believable 20-year-old Chinese woman, Shen Heng, a fragrance artisan and goods verifier. She has a quiet oval-heart face with a softly lifted outer eye line, warm brown almond eyes, natural straight brows, a refined natural nose and soft peach-coral lips; the right thumb and index finger carry subtle dry fragrance-powder traces. Her attraction is calm, observant, intelligent and individually human.',
  'CHR-L1-02': 'a strikingly beautiful 25-year-old Chinese woman, Liu Shisi also known as Liu Wangshu, a Chun Tai performance-house singer and songwriter. She has a graceful slender oval face with a softly tapered jaw, long luminous almond eyes that are horizontally extended and elegantly proportioned, warm dark-brown irises, natural brows, a refined straight nose and beautiful muted rose lips. The right corner of her mouth rests a fraction higher than the left before she smiles. Her expressive gaze reads a room quickly: warm, intelligent, socially perceptive and lightly guarded; her beauty is exceptional, distinctly human and immediately recognizable.',
  'CHR-L1-03': 'a handsome 24-year-old Chinese man, Zhou Yanzhi, a map artist and spatial recorder. He is lean with slightly narrow shoulders, thoughtful eyes, fine ink marks on the right thumb and middle finger, and a subtle forward-leaning work posture; a rolled paper tube and measuring cord form a quiet, profession-linked personal detail.',
  'CHR-L1-04': 'a beautiful 31-year-old Chinese woman, Pei Jiuniang, a river-route worker and boat owner. Her shoulders and forearms show practical strength from poles and ropes, her skin holds a believable outdoor tonal difference, a healed mark rests at the left tiger-mouth, and her stable stance retains the balance of a moving deck.',
  'CHR-L1-05': 'a handsome 29-year-old Chinese man, Gu Xingzhou, a tavern keeper familiar with water-and-road escort work. He has an efficient, grounded silhouette, a faint old scar through the right brow, old rope marks at the backs of the hands, and an alert, restrained gaze that naturally checks exits before settling.',
  'CHR-L2-01': 'a graceful 45-year-old Chinese woman, Lu Qinghe, the practical keeper of a fragrance shop. Her warm eyes are resilient rather than fragile, a few early silver strands appear at the temples, and her hands are exceptionally steady from weighing goods and folding parcels.',
  'CHR-L2-02': 'a lively 18-year-old Chinese woman, Lin Ayuan, a street-life observer who helps at a wonton shop. She has a rounded, energetic face, quick scanning eyes, loose practical sleeves worn unevenly from work, and hands accustomed to bowls, coins and damp oil paper.',
  'CHR-L2-03': 'a distinct 21-year-old Chinese medical apprentice, Yu Qinghe, with sharp attentive brows and eyes, a few damp forelock strands from herbal steam, and subtle herbal stains at the hands. The expression becomes slow and precise when listening or asking a clinical question.',
  'CHR-L2-04': 'a weathered 38-year-old Chinese city clerk, Gao Wen, with realistic under-eye fatigue, a precisely aligned belt and duty token, visibly worn boots, and a calm practical manner that creates space between arguing people.',
  'CHR-L3-01': 'a dignified 47-year-old Chinese city administrator, Song Weijing, always impeccably ordered in clothing and posture. His face carries controlled, principled civic authority; he organizes papers into a fixed sequence and his gaze asks for time, number and source before judgment.',
  'CHR-L3-02': 'a composed 53-year-old Chinese merchant-system figure, Li Jianshan, with a cultured but lived-in face, restrained smile lines and a hospitable manner that pours tea before negotiation. His refinement is quiet, commercial and materially exacting.',
  'CHR-L3-03': 'a compelling 34-year-old Chinese man, Helan Du, carrying northern weather in his features and a steady direct gaze. A worn leather wrist guard, deliberate posture and exact attention to listeners distinguish him as a grounded traveler-merchant.'
};

// Central-character presentation is Canon-checked rather than inferred from an
// occupation title; occupations such as “master/artisan” are gender-neutral.
const CENTRAL_PRESENTATIONS = {
  'CHR-L1-01': 'woman',
  'CHR-L1-02': 'woman',
  'CHR-L1-03': 'man',
  'CHR-L1-04': 'woman',
  'CHR-L1-05': 'man',
  'CHR-L2-01': 'woman',
  'CHR-L2-02': 'woman',
  'CHR-L2-03': 'woman',
  'CHR-L2-04': 'man',
  'CHR-L3-01': 'man',
  'CHR-L3-02': 'man',
  'CHR-L3-03': 'man'
};

const CENTRAL_LOOKS = {
  'CHR-L1-01': {
    route: 'Day',
    identity: 'a matte milk-ivory crossed-collar inner robe, a pale mist-blue structured middle layer with fine vertical folds, a muted sage-grey sash, silver-blue floral jacquard concentrated at the collar and cuffs, a celadon hairpin and a small fragrance pouch; fresh sheer peach-rose historical makeup and naturally polished hair',
    hero: 'in a sun-warmed fragrance-shop threshold, beside pale ceramic jars and a lattice-filtered window, her mist-blue and aged-ivory silk layers show a moon-white gauze edge, silver-blue floral jacquard at the collar and cuffs, narrow silver thread and restrained pleated drape; a soft reflected glow touches the hairpin, tea-toned wood and her hands'
  },
  'CHR-L1-02': {
    route: 'StageFestival',
    identity: 'a refined old-rose crossed-collar inner robe, a soft-celadon pleated middle skirt, an aged-ivory translucent outer layer with floral jacquard, a deep peacock-ink collar border with narrow low-saturation gilt edging, a sculpted urban-performer updo with a gilt filigree hairpin, pearl sprigs and delicate tassel earrings',
    hero: 'at the spring performance-house balcony during blue hour before an evening set, in old-rose, celadon and ivory layers with a long controlled full skirt, translucent outer sleeves, floral woven silk, locally raised flower embroidery at the collar, cuffs and hem, narrow antique-gold thread and a coordinated hairpin, pearl and tassel system; warm lantern pools catch the material while a muted blue-grey city distance, working balconies, curtains and audience circulation recede below'
  },
  'CHR-L1-03': {
    route: 'Day',
    identity: 'a composed ink-blue, stone-grey and aged-ivory layered scholar-artisan look, refined woven trim at the crossed collar, a well-kept topknot with a dark wood pin, a paper tube and measuring cord placed as quiet work details',
    hero: 'at an upper-floor map workshop overlooking a working canal, in elegantly tailored ink-blue and ivory layers, with paper, measurement cord, a carved railing and warm late-afternoon city depth behind him'
  },
  'CHR-L1-04': {
    route: 'Day',
    identity: 'a river-ready but elegant deep-indigo matte-silk inner layer, a river-teal tightly woven middle layer, an aged-ivory high collar, a finely woven belt with narrow brass hardware, full sleeves gathered for rope work, a controlled water-ripple jacquard edge, restrained jade-green accents and a polished practical half-up coiffure',
    hero: 'at a busy river landing in tailored indigo and teal silk-wool layers, a compact water-ready outer panel, restrained water-ripple jacquard and narrow brass fittings, beside ropes, boats and wet lacquered timber, with late sunlight reflecting from water into her strong face and complete working silhouette'
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

// These are casting-direction anchors, not biological Canon.  They turn each
// Foundation role's age, occupation and observable practice into an individually
// reviewable V2 candidate before a human approves an identity render.
const NONCENTRAL_VISUAL_ANCHORS = {
  'CHR-A1-01': { age: 42, presentation: 'woman', portrait: 'a warm rounded-square face, steady kind eyes and a firm caring mouth, with a mature ensemble-leading presence', wardrobe: 'warm ivory, pomegranate and tea-brown silk-cotton work layers with a narrow floral weave and a heat-safe cuff', gesture: 'bamboo chopsticks level scallions along a bowl rim while one hand keeps the bowl steady', setting: 'a warm, busy wonton-shop counter with steaming bowls and a visible neighborhood service route', route: 'Day', glamour: 3 },
  'CHR-A1-02': { age: 58, presentation: 'man', portrait: 'a weathered refined oval face, close-reading eyes, fine smile lines and precise fingers, with a charismatic elder-artisan presence', wardrobe: 'rain blue, ink and damp taupe ramie-and-silk layers with a subtle lacquer-dark edge', gesture: 'his thumb pauses over one repaired bamboo umbrella rib beside an umbrella-rib needle', setting: 'a covered umbrella-repair stall facing a rain-ready lane', route: 'NightWet', glamour: 2 },
  'CHR-A1-03': { age: 54, presentation: 'man', portrait: 'a calm broad-oval mature face, focused lowered gaze and composed mouth, with the stature of a trusted physician', wardrobe: 'sage jade, aged ivory and deep herbal-teal ramie silk with a restrained medicinal-leaf weave', gesture: 'dry fingertips settle a brass scale pan beside an orderly line of medicine packets', setting: 'a luminous small clinic worktable with herbal drawers and a patient-ready threshold', route: 'Day', glamour: 3 },
  'CHR-A1-04': { age: 50, presentation: 'woman', portrait: 'a striking mature oval face, decisive eyes and a poised expressive mouth, with commanding theatre-leader charisma', wardrobe: 'pomegranate, peacock ink and antique-gold floral-jacquard silk, a translucent shoulder layer and a low-saturation gilt edge', gesture: 'a contract folio rests in hand as three fingers complete a deliberate table-corner tap', setting: 'the working office edge of Chun Tai, with repaired curtains, cue papers and practical lamp glow', route: 'StageFestival', glamour: 4 },
  'CHR-A1-05': { age: 28, presentation: 'woman', portrait: 'a fine oval face, gentle alert eyes and a restrained firm mouth, with luminous civic-intellectual presence', wardrobe: 'mist blue, parchment ivory and muted berry layered ramie silk with a narrow hand-stitched collar border', gesture: 'one hand shelters wet ink on a two-column name ledger', setting: 'a modest relief-record table open to a busy public courtyard', route: 'Day', glamour: 3 },
  'CHR-A1-06': { age: 41, presentation: 'man', portrait: 'a long composed face, level assessing eyes, a precise brow line and a controlled jaw', wardrobe: 'ink blue, blue-grey and muted cinnabar structured official-city silk with a discreet seal-pattern weave', gesture: 'a fingertip tests the edge of red seal paste beside a closed document', setting: 'a sunlit city-office desk with layered civic circulation beyond', route: 'Day', glamour: 3 },
  'CHR-A1-07': { age: 26, presentation: 'woman', portrait: 'an elegant oval-diamond face, sharp calculating eyes and a composed mouth, with intelligent commercial-romance lead presence', wardrobe: 'deep peacock green, bronze tea and ivory tailored woven silk with a fine metallic-thread edge and jade-green lining', gesture: 'abacus beads separate into three groups while a true account page sits beneath a cover sheet', setting: 'a richly maintained Huchuan trading-house account room above a working canal', route: 'Day', glamour: 4 },
  'CHR-A1-08': { age: 40, presentation: 'man', portrait: 'a strong rectangular face, disciplined brow, alert steady eyes and a restrained expression', wardrobe: 'charcoal ink, bronze and dark cinnabar structured guard layers with a woven collar, polished leather wrist guard and dull brass trim', gesture: 'a gate token rests at the belt as one hand moves toward the wooden door bar', setting: 'a high-traffic city-gate passage with orderly civilian and cart movement', route: 'Day', glamour: 3 },
  'CHR-A2-01': { age: 63, presentation: 'woman', portrait: 'a dignified lined oval face, clear investigative eyes and a gentle unsentimental mouth', wardrobe: 'soap white, smoke blue and mulberry-brown washed ramie with subtle wet-fiber sheen', gesture: 'fingers check a freshly folded cloth edge beside one wooden laundry tally', setting: 'a sunlit laundry yard with drying cloth, wash basins and shared work lanes', route: 'Day', glamour: 2 },
  'CHR-A2-02': { age: 17, presentation: 'man', portrait: 'a bright youthful narrow-oval face, quick observant eyes and an age-appropriate fresh presence', wardrobe: 'ink blue, weathered ivory and a restrained pomegranate lining in light courier layers with a woven edge', gesture: 'a wax-sealed letter remains level as he reties one checked shoe tie', setting: 'a lively side lane where a delivery route opens toward the city', route: 'Day', glamour: 2 },
  'CHR-A2-03': { age: 49, presentation: 'man', portrait: 'a quiet mature oval face, scent-sensitive observant eyes and a reserved mouth, seen as a pre-disappearance archive-state casting candidate', wardrobe: 'amber tea, herb green and ivory fragrance-pharmacist silk and ramie with a dark lacquer edge', gesture: 'fingertips inspect a repaired record-folio join beside a small scent blade', setting: 'a remembered fragrance workroom with ordered jars, record folios and gentle window light', route: 'Day', glamour: 3 },
  'CHR-A2-04': { age: 36, presentation: 'man', portrait: 'a sun-warmed broad face, clear water-reading eyes and a practical closed smile', wardrobe: 'river teal, brine grey and a coral-rust accent in fine durable woven cloth with water-sheen trim', gesture: 'one hand studies fish gills while a shallow brass scoop catches water light', setting: 'a busy riverside fish stall with wet boards, baskets and an active canal edge', route: 'Day', glamour: 2 },
  'CHR-A2-05': { age: 33, presentation: 'man', portrait: 'a square-jawed approachable face, broad shoulder line and patient calculating eyes', wardrobe: 'dock indigo, ochre and tea-brown tightly woven work silk with a linen forearm guard', gesture: 'wooden tally tokens accompany a double-weight test on one wrapped load', setting: 'a wharf cargo lane with crates, porters and moored working boats', route: 'Day', glamour: 2 },
  'CHR-A2-06': { age: 45, presentation: 'man', portrait: 'a long weathered face, polished watchful eyes and a restrained negotiator expression', wardrobe: 'deep river green, taupe and mist blue merchant-broker silk with a narrow metallic-thread edge', gesture: 'a fingertip draws a route line on a folded water chart over a family-name slip', setting: 'a boat-office balcony over real boat traffic and accounting work', route: 'Day', glamour: 3 },
  'CHR-A2-07': { age: 67, presentation: 'man', portrait: 'a distinguished weathered face, fine arched brows and sharp still eyes, with elegant elder-artisan presence', wardrobe: 'ink wash, faded mineral blue and warm paper ivory in layered scholar-artisan cloth with a subtle brushstroke weave', gesture: 'a very fine brush corrects the smallest line on a map', setting: 'a bookshop-street painting desk with paper, pigments and a sunlit shopfront', route: 'Day', glamour: 3 },
  'CHR-A2-08': { age: 38, presentation: 'woman', portrait: 'a refined oval face, decisive scholarly brows and concentrated eyes, with confident bookshop-proprietress presence', wardrobe: 'black ink, pomegranate and parchment ivory finely tailored printed silk with a narrow carved-block motif', gesture: 'a bamboo strip pins a proof page while measured paper stock rises at one side', setting: 'a refined printing-shop counter with blocks, proofs and working customers', route: 'Day', glamour: 3 },
  'CHR-A3-01': { age: 19, presentation: 'woman', portrait: 'a fresh heart-oval face, bright selective eyes and an anxious-soft smile, with age-appropriate young ensemble presence', wardrobe: 'apricot, pale celadon and warm ivory flower-pattern woven silk with a translucent oversleeve', gesture: 'a flower-card and grouped blossoms pause as fingertips touch a small blossom-and-jade hairpin', setting: 'a vivid flower-market stall with tags, baskets and afternoon customer flow', route: 'Day', glamour: 3 },
  'CHR-A3-02': { age: 23, presentation: 'man', portrait: 'a lively narrow-oval face, expressive brows, a quick smile and observant eyes, with charismatic street-storyteller energy', wardrobe: 'wine red, ink blue and warm ochre mobile layered cloth with a narrative-pattern cuff', gesture: 'an open hand stops just before a flourish while a wake-up block rests silent on the table', setting: 'a crowded daylight market corner with listeners, tea cups and receding shop signs', route: 'Day', glamour: 3 },
  'CHR-A3-03': { age: 27, presentation: 'woman', portrait: 'a long luminous oval face, dark listening eyes and a poised muted-rose mouth, with refined performer charisma', wardrobe: 'smoky lilac, teal, old rose and aged gold flowing silk gauze with floral jacquard and full sleeves', gesture: 'one fingernail taps the pipa frame precisely at the end of a beat', setting: 'a Chun Tai rehearsal edge with soft lamps, cue passage and silk curtains in motion', route: 'StageFestival', glamour: 4 },
  'CHR-A3-04': { age: 22, presentation: 'woman', portrait: 'a fine oval face, precise observant eyes and a compassionate restrained expression', wardrobe: 'peach ivory, ink and cinnabar-red theatrical-workshop silk with subtle stitched cuffs and a narrow colored lining', gesture: 'she checks the back of her hand before setting a closed makeup box aside', setting: 'a practical Chun Tai makeup and care station with lamps, brushes and clean cloth', route: 'StageFestival', glamour: 3 },
  'CHR-A3-05': { age: 26, presentation: 'man', portrait: 'a lean thoughtful face, intelligent furrowed brow and quietly vulnerable mouth, with literary ensemble-lead presence', wardrobe: 'ink blue, muted plum and aged ivory refined scholar layers with a soft paper-texture collar', gesture: 'a failed essay sheet turns to its blank back before he writes a public notice', setting: 'a paper-strewn street-side writing desk under warm city daylight', route: 'Day', glamour: 3 },
  'CHR-A3-06': { age: 30, presentation: 'man', portrait: 'a warm angular face, alert exit-checking eyes and a restrained friendly mouth', wardrobe: 'deep tea, navy and rust-red mobile tavern silk-cotton layers with a narrow woven collar edge', gesture: 'both hands hold a hot-water tray steady while his eyes check the door seam', setting: 'a bustling tavern service passage where kitchen heat meets a lantern-lit entry', route: 'NightWet', glamour: 3 },
  'CHR-A3-07': { age: 36, presentation: 'woman', portrait: 'a controlled oval face, clear assessing eyes and a calm businesslike mouth, with elegant innkeeper presence', wardrobe: 'deep teal, bronze, tobacco and ivory tailored guesthouse silk with patterned cuffs and polished lining', gesture: 'a guest ledger closes immediately beneath one hand at the threshold', setting: 'a busy guesthouse reception with keys, luggage and layered traveler circulation', route: 'Day', glamour: 3 },
  'CHR-A3-08': { age: 44, presentation: 'woman', portrait: 'a calm mature oval face, firm compassionate eyes and a measured mouth, with dignified temple-manager presence', wardrobe: 'ash ivory, soft celadon and muted saffron full modest temple-work layers with fine woven texture', gesture: 'a ladle pauses horizontally beside a grain tally while a queue remains orderly', setting: 'a temple relief courtyard with grain stores, bowl lines and daylight under eaves', route: 'Day', glamour: 3 },
  'CHR-B-001': { age: 29, presentation: 'woman', portrait: 'an attentive oval face, capable steady eyes and ink-dusted fingers', wardrobe: 'mist blue, ivory and pale sage layers with a fragrant-paper apron panel and fine woven collar', gesture: 'she folds a scent packet while charcoal-marking its count', setting: 'a fragrance-shop packing bench with paper, jars and a narrow active threshold', route: 'Day', glamour: 2 },
  'CHR-B-002': { age: 36, presentation: 'man', portrait: 'a sun-warmed angular face, patient measuring gaze and strong graceful hands', wardrobe: 'bamboo ochre, indigo and tea brown tightly woven work silk with a braided edge', gesture: 'he tests a repaired basket bottom by lifting its handle', setting: 'a small basket-repair bay opening onto an occupied lane', route: 'Day', glamour: 2 },
  'CHR-B-003': { age: 43, presentation: 'woman', portrait: 'a composed oval face, focused brows and a quiet resilient mouth', wardrobe: 'muted mulberry, warm ivory and ink fine needlework layers with a stitched cuff', gesture: 'the left hand supports an aching right wrist while she tests a sleeve seam', setting: 'a shared clothing-repair table with theatre fabric and a drying line behind', route: 'Day', glamour: 2 },
  'CHR-B-004': { age: 10, presentation: 'man', portrait: 'a bright age-appropriate round face and alert observing eyes', wardrobe: 'soft ivory, scallion green and restrained brick red clean practical child layers', gesture: 'he counts bowls beside a folded scallion cloth', setting: 'the safe side of a family wonton-shop counter', route: 'Day', glamour: 1 },
  'CHR-B-005': { age: 26, presentation: 'man', portrait: 'an open youthful face, practical eyes and a calm mouth', wardrobe: 'soybean cream, moss green and tea brown full-sleeve market layers with a water-safe cuff', gesture: 'one hand presses tofu while the other saves whey for a neighbor', setting: 'a morning tofu stall with cloth filters, basins and market movement', route: 'Day', glamour: 2 },
  'CHR-B-006': { age: 57, presentation: 'man', portrait: 'a compact lined face, listening eyes and precise fingertips', wardrobe: 'midnight blue, wet-stone grey and dull brass tailored night-work cloth', gesture: 'his hand tests a lock spring and the rain line at a door seam', setting: 'a covered night lane with doors, eaves and a small practical lantern', route: 'NightWet', glamour: 2 },
  'CHR-B-007': { age: 68, presentation: 'woman', portrait: 'a bright weathered face, lively kindly eyes and a strong mouth', wardrobe: 'saffron tea, cream and muted mulberry well-kept practical market cloth', gesture: 'she tilts her head toward the oil sound while wrapping a remaining pancake', setting: 'a dusk market stove with a real crowd and warm cooking light', route: 'NightWet', glamour: 2 },
  'CHR-B-008': { age: 47, presentation: 'man', portrait: 'a prosperous expressive face, social-reading eyes and a measured smile', wardrobe: 'deep teal, pomegranate and bronze restaurant-host silk with narrow metallic thread', gesture: 'he separates debt tags by color beside a lacquered account board', setting: 'a thriving lantern-lit restaurant balcony above an active night market', route: 'NightWet', glamour: 3 },
  'CHR-B-009': { age: 23, presentation: 'woman', portrait: 'a fine face, imaginative observant eyes and a playful controlled smile', wardrobe: 'paper ivory, cinnabar and ink-blue theatre-workshop silk with a pigment-specked cuff', gesture: 'she holds a paper mask at shoulder height while marking its hidden back', setting: 'a Chun Tai prop-workshop table beside backstage lamp light', route: 'StageFestival', glamour: 3 },
  'CHR-B-010': { age: 30, presentation: 'woman', portrait: 'a warm oval face, watchful night eyes and a calm generous mouth', wardrobe: 'midnight indigo, amber and old-rose refined stall layers that take steam light', gesture: 'she keeps the last bowl warm at the pot bottom', setting: 'a humid night porridge stall under occupied market eaves', route: 'NightWet', glamour: 3 },
  'CHR-B-011': { age: 37, presentation: 'man', portrait: 'an athletic mature face, alert eyes and a restrained pained smile', wardrobe: 'rust, charcoal and antique-gold brown fitted stage-work layers with reinforced knee cloth', gesture: 'one knee braces a ladder foot while both hands check a wood wedge', setting: 'a spring-performance backstage rigging lane with cue traffic', route: 'StageFestival', glamour: 3 },
  'CHR-B-012': { age: 44, presentation: 'man', portrait: 'a long night-weathered face, listening gaze and a controlled jaw', wardrobe: 'deep navy, black lacquer and warm lantern-brown elegant night-watch layers', gesture: 'he holds the time clapper low while his ears follow an alley sound', setting: 'a damp patrol route beneath occupied eaves and paper lamps', route: 'NightWet', glamour: 2 },
  'CHR-B-013': { age: 51, presentation: 'man', portrait: 'a sturdy thoughtful face, grounded eyes and fine sawdust at the hands', wardrobe: 'sapwood brown, deep green and pomegranate-lined tailored timber-worker cloth', gesture: 'he tests a mortise joint before returning spare bamboo', setting: 'a Chun Tai carpentry bay with stage timber, curtain rail and work lamps', route: 'StageFestival', glamour: 2 },
  'CHR-B-014': { age: 27, presentation: 'man', portrait: 'a narrow attentive face, ink-dark eyes and a reserved mouth', wardrobe: 'ink blue, paper ivory and soft teal elegant copyist layers with a sleeve guard', gesture: 'he turns waste paper to its blank side beside a brush', setting: 'a daytime copyist bench at a bookshop window', route: 'Day', glamour: 2 },
  'CHR-B-015': { age: 34, presentation: 'man', portrait: 'a focused square-oval face, close-reading eyes and quiet resolve', wardrobe: 'charcoal, carved-wood amber and muted bronze printmaker cloth with a woven collar edge', gesture: 'he brushes wood chips aside with one injured finger wrapped in old cloth', setting: 'a print-block workbench with carved wood, proof paper and side light', route: 'Day', glamour: 2 },
  'CHR-B-016': { age: 41, presentation: 'woman', portrait: 'a refined oval face, patient eyes and a self-possessed mouth', wardrobe: 'paper ivory, moss green and muted coral layered mounting-artisan silk with a matte glue-safe cuff', gesture: 'she aligns a paper edge then feels for returning damp through the backing', setting: 'a calm mounting table with brushes, paper sheets and filtered daylight', route: 'Day', glamour: 2 },
  'CHR-B-017': { age: 48, presentation: 'man', portrait: 'a cultured lived-in face, appraising eyes and a hospitable half-smile', wardrobe: 'tea brown, peacock green and low antique gold art-merchant silk with patterned lining', gesture: 'he angles paper toward light to judge its color before naming the price', setting: 'a paper-and-painting shop threshold with browsing customers', route: 'Day', glamour: 3 },
  'CHR-B-018': { age: 24, presentation: 'woman', portrait: 'a clear gentle face, exact browsing eyes and a protective mouth', wardrobe: 'pale blue, ivory and plum polished catalogue-worker cloth with narrow stitched trim', gesture: 'she ties editions into a set while hiding a practice sheet beneath the ledger', setting: 'a bookshop catalog desk surrounded by orderly bound volumes', route: 'Day', glamour: 2 },
  'CHR-B-019': { age: 25, presentation: 'man', portrait: 'a wind-shaped youthful face, keen river eyes and relaxed strong shoulders', wardrobe: 'river indigo, teal and wine accent crisp boat-worker layers with a rope-texture sash', gesture: 'he tests a rope knot while marking bow drift on a wooden tab', setting: 'a working canal landing with boats, cargo and bright water reflection', route: 'Day', glamour: 2 },
  'CHR-B-020': { age: 38, presentation: 'man', portrait: 'a broad capable face, grain-reading eyes and steady hands', wardrobe: 'navy, warm timber ochre and ivory sturdy shipwright cloth with a fine metal fastening', gesture: 'he sorts old nails by length beside a tested plank', setting: 'a sunlit boatyard with timber frames and wet hull reflections', route: 'Day', glamour: 2 },
  'CHR-B-021': { age: 45, presentation: 'woman', portrait: 'a strong poised face, clear water-reading eyes and a resolute mouth', wardrobe: 'lake blue, aged ivory and muted pomegranate elegant ferry layers with a woven river sash', gesture: 'she shortens a wet line before the wind changes', setting: 'a ferry landing with passengers, rope posts and a wide water route', route: 'Day', glamour: 3 },
  'CHR-B-022': { age: 52, presentation: 'woman', portrait: 'a warm mature face, commanding hospitable eyes and a calm smile', wardrobe: 'cedar brown, river teal and copper water-tea-host silk with a robust woven oversleeve', gesture: 'she steadies a tea cup and presses a wet reed mat at the hatch', setting: 'a floating tea stall with boat households and moving water beyond', route: 'Day', glamour: 3 },
  'CHR-B-023': { age: 28, presentation: 'man', portrait: 'a lively broad-oval face, clear organizing eyes and a grounded stance', wardrobe: 'dock indigo, ochre and dull brass tailored porter-leader layers with a broad woven belt', gesture: 'one open palm fixes the queue while the other checks a cargo tally', setting: 'a crowded wharf loading lane with parcels, porters and boats', route: 'Day', glamour: 2 },
  'CHR-B-024': { age: 35, presentation: 'woman', portrait: 'a sun-touched oval face, sensing eyes and a firm composed mouth', wardrobe: 'brine grey, weathered coral and tea brown refined salt-work fabric with dry textured trim', gesture: 'she tests fish-salt texture between finger and thumb at a drying rack', setting: 'a riverbank drying yard with baskets, fish racks and working neighbors', route: 'Day', glamour: 2 },
  'CHR-B-025': { age: 15, presentation: 'man', portrait: 'an age-appropriate eager face, clear river eyes and an eager careful expression', wardrobe: 'river teal, weathered ivory and a ginger accent in light youth boat layers with woven cord detail', gesture: 'he shows a newly tied rope knot while keeping the coil orderly', setting: 'a family boat deck beside a working canal route', route: 'Day', glamour: 1 },
  'CHR-B-026': { age: 49, presentation: 'woman', portrait: 'a mature decisive face, kitchen-reading eyes and a practical warm mouth', wardrobe: 'tea brown, deep navy and cinnabar lining in high-end back-kitchen layers with a neat woven apron panel', gesture: 'she sorts rice by pot batch and turns leftovers into a next-meal bowl', setting: 'a tavern kitchen service passage with steam, bowls and night orders', route: 'NightWet', glamour: 2 },
  'CHR-B-027': { age: 25, presentation: 'man', portrait: 'a polished narrow face, watchful social eyes and a pleasant guarded smile', wardrobe: 'deep green, old gold and ivory mobile broker silk with a discreet door-token clasp', gesture: 'he checks a door plate while sliding an old debt slip into a folio', setting: 'a busy lodging and trade lane with doors, notices and passing clients', route: 'Day', glamour: 3 },
  'CHR-B-028': { age: 32, presentation: 'man', portrait: 'an elegant travel-worn face, scent-focused eyes and a composed mouth', wardrobe: 'lapis blue, mulberry and ivory prosperous spice-trader textiles with a fine woven edge', gesture: 'he tests a sealed spice sack and marks a delayed route on a lodging-wall chart', setting: 'a merchant courtyard with spice bales, travelers and a city route map', route: 'Day', glamour: 3 },
  'CHR-B-029': { age: 39, presentation: 'woman', portrait: 'a precise oval face, competent eyes and a welcoming restrained expression', wardrobe: 'dusty rose, ash blue and ivory tailored guesthouse-service layers with clean woven cuffs', gesture: 'she separates wet linen and counts a small key ring', setting: 'a guesthouse wash-and-entry threshold with luggage and sheets', route: 'Day', glamour: 2 },
  'CHR-B-030': { age: 46, presentation: 'man', portrait: 'a composed sea-weathered face, calculating warm eyes and merchant gravitas', wardrobe: 'sea green, bronze and ivory rich maritime merchant silk with a narrow metallic-thread edge', gesture: 'he checks wind direction while dividing ropes among work positions', setting: 'a canal-side maritime trade dock with cargo, boat crews and distant water', route: 'Day', glamour: 3 },
  'CHR-B-031': { age: 22, presentation: 'man', portrait: 'a young refined face, exact brows and studious alert eyes', wardrobe: 'ink blue, blue-grey and restrained cinnabar low-clerk layers with a neat seal-pattern cuff', gesture: 'he keeps original and copied pages distinct while circling one wrong character', setting: 'a light-filled low-clerk desk with seal tools and civic traffic beyond', route: 'Day', glamour: 2 },
  'CHR-B-032': { age: 58, presentation: 'man', portrait: 'a dignified lined face, grain-reading eyes and patient authority', wardrobe: 'grain ochre, ink and aged ivory weather-safe storehouse silk-ramie with subtle seam texture', gesture: 'he checks a sack stitch then reads a tide mark on the warehouse door', setting: 'a riverside storehouse entry with grain sacks and freight traffic', route: 'Day', glamour: 2 },
  'CHR-B-033': { age: 36, presentation: 'man', portrait: 'an alert practical face, direct eyes and a composed professional expression', wardrobe: 'charcoal, dark cinnabar and aged brass structured constable layers with a complete formal collar', gesture: 'he touches a duty token then repeats an order toward the next shift', setting: 'a wet evening patrol junction with a guard lamp and active eaves', route: 'NightWet', glamour: 2 },
  'CHR-B-034': { age: 14, presentation: 'man', portrait: 'a thoughtful age-appropriate face and quick careful eyes', wardrobe: 'slate blue, ivory and restrained pomegranate lining in rain-ready courier youth layers', gesture: 'he holds a sealed letter high while choosing the dry alley line', setting: 'a daylight delivery lane with covered eaves and busy crossings', route: 'Day', glamour: 1 },
  'CHR-B-035': { age: 50, presentation: 'man', portrait: 'a firm mature face, watchful eyes softened by private care', wardrobe: 'forest ink, bronze and muted red city-gate soldier layers with polished woven guard trim', gesture: 'he directs people with one hand while his thumb rests on a child tooth pouch', setting: 'a sunlit city-gate queue with carts, papers and family movement', route: 'Day', glamour: 2 },
  'CHR-B-036': { age: 26, presentation: 'woman', portrait: 'a clear work-worn face, keen trace-reading eyes and contained strength', wardrobe: 'soap blue, dusty rose and ivory refined laundry layers with a water-reflective woven border', gesture: 'she wrings cloth and separates uniforms by their marked corner', setting: 'a daylight laundry yard serving a military and warehouse route', route: 'Day', glamour: 2 },
  'CHR-B-037': { age: 33, presentation: 'woman', portrait: 'a focused oval face, scent-aware eyes and a careful mouth', wardrobe: 'sage green, faded teal and ivory herb-grinding ramie silk with a powder-soft texture', gesture: 'she screens ground medicine and marks its scent on a paper corner', setting: 'a medicinal preparation room with mortar, sieve and amber daylight', route: 'Day', glamour: 2 },
  'CHR-B-038': { age: 40, presentation: 'man', portrait: 'a poised clinical face, calm resting eyes and exact hands', wardrobe: 'pale blue, ivory and aged brass medical-worker layers with a discreet embroidered edge', gesture: 'one hand closes a needle case after washing while the other checks a dressing', setting: 'a modest treatment table with clean cloth, water and medicine light', route: 'Day', glamour: 2 },
  'CHR-B-039': { age: 47, presentation: 'man', portrait: 'a tranquil mature face, observant fair-minded eyes and a steady mouth', wardrobe: 'ash ivory, muted saffron and ink complete temple-service robes with woven utilitarian texture', gesture: 'he checks bowl bottoms while registering familiar and unfamiliar guests alike', setting: 'a temple meal line with grain jars, covered eaves and active civic care', route: 'Day', glamour: 2 },
  'CHR-B-040': { age: 23, presentation: 'woman', portrait: 'a gentle young face, tired compassionate eyes and a quietly resilient expression', wardrobe: 'faded celadon, ivory and soft rose clean caregiving layers with a thin woven oversleeve', gesture: 'she records a patient sleep mark before reaching for her own meal', setting: 'a daylight charitable medical tent with orderly bedding and care tools', route: 'Day', glamour: 2 },
  'CHR-B-041': { age: 70, presentation: 'woman', portrait: 'a dignified weathered face, vivid remembering eyes and a warm clear mouth', wardrobe: 'reed gold, mulberry and aged ivory finely kept northern textile layers with grass-fiber detail', gesture: 'she feels a mat knot and traces a remembered northern route in the air', setting: 'a temple-side craft corner with finished mats, baskets and listening neighbors', route: 'Day', glamour: 2 },
  'CHR-B-042': { age: 13, presentation: 'woman', portrait: 'an age-appropriate heart-oval face, intelligent quiet eyes and a hopeful guarded expression', wardrobe: 'soft celadon, ash ivory and a tiny berry accent in modest clean temple youth layers', gesture: 'she sorts old tokens by color beside her carefully practiced name', setting: 'a quiet temple desk near grain sacks and shared care routines', route: 'Day', glamour: 1 },
  'CHR-B-043': { age: 44, presentation: 'man', portrait: 'a polished intelligent face, orderly brows and cautious calculating eyes', wardrobe: 'deep peacock, ink and bronze refined account-house silk with a restrained metallic edge', gesture: 'he leaves a correction visible beside a copied transport page', setting: 'a Huchuan account room overlooking cargo routes and ledger shelves', route: 'Day', glamour: 3 },
  'CHR-B-044': { age: 51, presentation: 'man', portrait: 'a solid weathered face, scanning eyes and restrained loyalty', wardrobe: 'deep teal, charcoal and dull bronze tailored escort-travel cloth with a leather-accented belt', gesture: 'his body shields a ledger chest at a cart turn while eyes read the road', setting: 'a busy cargo courtyard where carts meet canal traffic', route: 'Day', glamour: 2 },
  'CHR-B-045': { age: 27, presentation: 'man', portrait: 'a sun-touched working face, clear anxious eyes and a resilient jaw', wardrobe: 'field green, clay brown and worn ivory elevated farm-to-market layers with woven hemp-silk texture', gesture: 'he points to a rent date beside a repaired short-dike plan', setting: 'a rural-market edge with produce bundles, river mud and working visitors', route: 'Day', glamour: 2 },
  'CHR-B-046': { age: 34, presentation: 'woman', portrait: 'a steady caring face, exact organizing eyes and a strong gentle mouth', wardrobe: 'mist blue, dusty plum and ivory civic-relief silk-ramie layers with a braided route sash', gesture: 'she holds a child securely while marking a dangerous route on a board', setting: 'an active relief distribution point with supplies, care lanes and volunteers', route: 'Day', glamour: 3 },
  'CHR-B-047': { age: 22, presentation: 'man', portrait: 'an intense youthful face, bright demanding eyes and a conflicted mouth', wardrobe: 'ink, pomegranate and charcoal disciplined organizer layers with a restrained torch-red lining', gesture: 'he checks a torch while keeping the flame lowered beside a handbill', setting: 'a rain-dark night meeting edge with covered eaves and tense public circulation', route: 'NightWet', glamour: 3 },
  'CHR-B-048': { age: 62, presentation: 'man', portrait: 'a rugged dignified face, far-seeing eyes and a calm weathered expression', wardrobe: 'horseshoe brown, stone grey and deep indigo northern-traveler layers with a rope-texture sash', gesture: 'he tests mud depth and adjusts a cart rope by remembered route', setting: 'a city-edge cart track with mud, river distance and incoming travelers', route: 'Day', glamour: 2 }
};

function noncentralGrooming(anchor) {
  if (anchor.age < 18) return 'Age-appropriate clean historical grooming: fresh natural skin with fine visible texture, simple tidy hair, bare clean eyelids and natural lip color.';
  if (anchor.presentation === 'woman') return 'Refined breathable historical makeup: sheer base, softly shaped brows, restrained peach-rose tone, natural lashes and muted lip color, with real skin visible.';
  if (anchor.presentation === 'man') return 'Clean refined historical grooming with natural brow and lip texture, realistic skin and individually readable hair detail.';
  return 'Natural clean historical grooming with visible skin and hair texture; the exact presentation-specific finish is selected during casting review.';
}

function noncentralCastingTone(anchor) {
  return anchor.age < 18
    ? 'a bright, age-appropriate, individually memorable young presence'
    : 'a distinctive, compelling and believable high-end historical-drama ensemble presence';
}

function supportingLook(characterId) {
  const anchor = NONCENTRAL_VISUAL_ANCHORS[characterId];
  if (!anchor) throw new Error(`Missing noncentral visual anchor for ${characterId}`);
  return anchor;
}

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

function agePresentation(facts, presentation) {
  return `${facts.age_y0}-year-old Chinese ${presentation}`;
}

const CENTRAL_MASTER_PORTRAIT_STYLE = 'Premium live-action Chinese historical-romance casting portrait, glamorous and believable urban period elegance, a cinematic natural eye-level portrait lens, delicate dimensional exposure, gentle filmic highlight roll-off, clear individual hair strands and fine woven silk detail.';

function centralMasterGrooming(presentation) {
  return presentation === 'woman'
    ? `Clean translucent historical makeup: sheer breathable base, softly brushed brows, muted peach-rose eyes, individually separated lashes, gentle rose warmth at the cheeks and naturally stained lips. ${NATURAL_SKIN_SURFACE}`
    : `High-end natural historical grooming: individually readable brows and hair, refined natural lip texture, controlled cheek and brow highlights. ${NATURAL_SKIN_SURFACE}`;
}

function centralHeroFinish(route) {
  if (route === 'StageFestival') return 'Warm paper lantern and candle light catches silk, pearl, gilt and skin with refined blue-hour depth beyond the performance house. Light curtains, audience movement and working balconies give the image a prosperous living-city scale.';
  if (route === 'NightWet') return 'Warm practical lantern and oil-lamp pools shape the actor, silk and lacquered timber while muted blue-hour distance carries real water-city depth. The material richness comes from dye, weave, polished fittings and motivated reflection.';
  return 'Low warm daylight and pale reflected fill shape the actor, silk, timber and working objects; the inhabited water-city remains softly legible behind the complete costume silhouette.';
}

function characterPrompt(character, facts, profileMarkdown) {
  const central = Boolean(CENTRAL_IDENTITY[character.id]);
  const anchor = central ? null : supportingLook(character.id);
  const core = central
    ? CENTRAL_IDENTITY[character.id]
    : `${promptNameFromCharacter(character)}, a ${agePresentation(facts, anchor.presentation)} and ${occupationEnglish(facts.occupation)}. ${sentence(anchor.portrait)} ${sentence(noncentralCastingTone(anchor))}`;
  const wardrobe = central ? CENTRAL_LOOKS[character.id].identity : anchor.wardrobe;
  if (central) {
    const presentation = CENTRAL_PRESENTATIONS[character.id];
    const construction = costumeConstruction(2, presentation, facts.occupation);
    return `Cinematic front-facing lead-character casting portrait of ${core} Signature wardrobe: ${wardrobe}. ${construction} ${centralMasterGrooming(presentation)} Centered head-and-upper-torso framing, direct eye-level lens, level shoulders, calm direct gaze, complete high crossed collar and one profession-linked personal ornament held in crisp focus. A clean warm-ivory plaster ground, soft large-window daylight and pale reflected fill keep face, hair, skin and fine textile work immediately legible. ${CENTRAL_MASTER_PORTRAIT_STYLE}`;
  }
  const visibleAction = ` Signature occupational action: ${anchor.gesture}.`;
  const construction = costumeConstruction(anchor.glamour, anchor.presentation, facts.occupation);
  return `Front-facing character visual-anchor exploration of ${core} Centered head-and-upper-torso framing, direct eye-level lens, level shoulders, complete Southern Song Linan collar and shoulder silhouette: ${wardrobe}. ${construction}${visibleAction} Beautiful facial harmony with satin-translucent healthy skin. ${NATURAL_SKIN_SURFACE} ${noncentralGrooming(anchor)} ${routeText('Day', true)}`;
}

function characterHeroPrompt(character, facts, profileMarkdown) {
  const core = CENTRAL_IDENTITY[character.id] || `the distinct ${facts.age_y0}-year-old Chinese ${inferPresentation(facts.name, facts.occupation, profileMarkdown)}, ${facts.name}, a ${occupationEnglish(facts.occupation)}`;
  const look = CENTRAL_LOOKS[character.id];
  if (!look) throw new Error(`No central hero look for ${character.id}`);
  const cleanCore = core.replace(/\.+$/, '');
  const heroLook = `${look.hero.charAt(0).toUpperCase()}${look.hero.slice(1)}`;
  const presentation = CENTRAL_PRESENTATIONS[character.id];
  const glamourLevel = character.id === 'CHR-L1-02' ? 5 : character.tier === 'L1' ? 4 : 3;
  return `Cinematic live-action Chinese historical-romance hero still of ${cleanCore}. Full-body three-quarter environmental portrait at natural eye level, poised practical gesture, complete long silhouette and a high-end period-drama leading-cast presence. ${heroLook}. ${costumeConstruction(glamourLevel, presentation, facts.occupation)} Refined breathable historical makeup and grooming, individually readable hair strands. ${NATURAL_SKIN_SURFACE} ${centralHeroFinish(look.route)} Premium live-action Chinese historical-romance key art with tactile silk, polished metal or jade accents, cinematic optical softness and a cohesive prosperous Linan world.`;
}

function supportingStatePrompt(character, facts) {
  const anchor = supportingLook(character.id);
  const tier = character.tier;
  const framing = /^A[123]$/.test(tier) ? 'a three-quarter environmental portrait from waist to mid-thigh' : 'a waist-up occupational portrait';
  const movement = anchor.route === 'StageFestival'
    ? 'A light backstage or corridor breeze gives physical lift to the weighted outer silk and a few hair strands.'
    : '';
  return `A premium live-action Chinese historical-romance occupational character state for ${promptNameFromCharacter(character)}, a ${agePresentation(facts, anchor.presentation)} and ${occupationEnglish(facts.occupation)}. ${sentence(anchor.portrait)} ${sentence(noncentralCastingTone(anchor))} ${sentence(`${framing} at ${anchor.setting}`)} ${sentence(anchor.gesture)} Complete layered Southern Song Linan clothing: ${anchor.wardrobe}. ${costumeConstruction(anchor.glamour, anchor.presentation, facts.occupation)} ${noncentralGrooming(anchor)} ${NATURAL_SKIN_SURFACE} Real skin, hair and textile response remain visible in a lived-in urban environment. ${movement} ${routeText(anchor.route)}`;
}

const roster = readJson('qa/character-roster.json');
const profileById = new Map();
for (const character of roster.named_characters) {
  const profileMarkdown = read(character.profile_path);
  const facts = parseTomlFrontMatter(profileMarkdown);
  const central = Boolean(CENTRAL_IDENTITY[character.id]);
  const supporting = central ? null : supportingLook(character.id);
  if (supporting && supporting.age !== facts.age_y0) {
    throw new Error(`Visual-anchor age mismatch for ${character.id}: ${supporting.age} versus ${facts.age_y0}`);
  }
  profileById.set(character.id, { character, facts, profileMarkdown });
  addRecord({
    prompt_id: `MJ-V2-CHR-${character.id}-ID-001`,
    target_key: `CHARACTER:${character.id}:IDENTITY-001`,
    family: 'character',
    asset_lane: central ? 'identity-anchor' : 'character-visual-anchor-exploration',
    target: { stable_id: character.id, name: character.name, asset_id: 'ID-001' },
    authority_refs: [sourceRef(character.profile_path, 'character-foundation-authority'), sourceRef('production/style/v2-urban-splendor-song-style-package.md', 'v2-style-authority')],
    facts_snapshot: { name: facts.name, aliases: facts.aliases, age_y0: facts.age_y0, occupation: facts.occupation, residence: facts.residence, identity_anchor_cn: extractIdentityAnchor(profileMarkdown), visual_anchor: supporting ? { portrait: supporting.portrait, wardrobe: supporting.wardrobe, gesture: supporting.gesture, setting: supporting.setting, presentation: supporting.presentation } : null },
    route: 'Day',
    technical: true,
    glamour_level: central ? 4 : supporting.glamour,
    ar: '3:4',
    stylize: central ? 82 : 100,
    chaos: central ? 1 : 2,
    positive: characterPrompt(character, facts, profileMarkdown),
    execution_status: central ? 'READY_FOR_V2_MASTER_REFERENCE_SELECTION' : 'READY_FOR_V2_VISUAL_ANCHOR_SELECTION',
    acceptance_checks: central ? [
      'Use this first-pass prompt to select one project-generated central-character master reference before any follow-on asset work.',
      'Age, occupation and stable visual anchors exactly match the character profile.',
      'Face remains individually recognizable, beautiful and natural with a high-end New Song historical-drama cast presence.',
      'The technical continuity lane is clear, front-facing and richly finished through collar, skin, hair and one profession-linked ornament.',
      'Record the approved local asset path, hash and rights decision before attaching the selected master image in a later Midjourney session.'
    ] : [
      'Confirms the stated age, occupation, role-specific wardrobe, occupational gesture and presentation candidate as a casting exploration.',
      'A human must select and approve the face, body and behavior candidate before it becomes a named identity asset.',
      'This record remains a non-Canon casting direction until the selected visual anchor is approved.'
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
      ar: '2:3',
      stylize: character.tier === 'L1' ? 165 : 145,
      chaos: 2,
      positive: characterHeroPrompt(character, facts, profileMarkdown),
      reference_binding: {
        mode: 'PROJECT_GENERATED_MASTER_REFERENCE_REQUIRED',
        status: 'AWAITING_USER_APPROVED_MASTER_REFERENCE',
        policy: 'After the user selects a project-generated ID-001 candidate and records its local asset metadata, attach that approved image in the Midjourney web UI before running this hero prompt. Keep the full text prompt intact and record the actual session value locally.'
      },
      depends_on: [`CHARACTER:${character.id}:IDENTITY-001 approved master-reference selection`],
      execution_status: 'BLOCKED_UNTIL_APPROVED_MASTER_REFERENCE',
      acceptance_checks: [
        'Run only after an approved project-generated ID-001 master reference is available for the named central character.',
        'Matches the locked age, occupation and facial identity anchors for the named central character.',
        'Reads as a premium New Song historical-romance key art with a complete, character-specific wardrobe system.',
        'Uses a real light source and a legible Linan environment; selected source remains subject to identity and rights review before continuity use.'
      ]
    });
  }
  if (!central) {
    const route = supporting.route;
    const isACharacter = /^A[123]$/.test(character.tier);
    addRecord({
      prompt_id: `MJ-V2-CHR-${character.id}-STATE-001`,
      target_key: `CHARACTER:${character.id}:STATE-001`,
      family: 'character',
      asset_lane: isACharacter ? 'supporting-hero-state' : 'supporting-occupation-state',
      target: { stable_id: character.id, name: character.name, asset_id: 'STATE-001' },
      authority_refs: [sourceRef(character.profile_path, 'character-foundation-authority')],
      facts_snapshot: { name: facts.name, aliases: facts.aliases, age_y0: facts.age_y0, occupation: facts.occupation, residence: facts.residence, visual_anchor: { portrait: supporting.portrait, wardrobe: supporting.wardrobe, gesture: supporting.gesture, setting: supporting.setting, presentation: supporting.presentation } },
      route,
      glamour_level: supporting.glamour,
      ar: isACharacter ? '2:3' : '3:4',
      stylize: isACharacter ? 185 : 160,
      chaos: 3,
      positive: supportingStatePrompt(character, facts),
      execution_status: 'READY_FOR_V2_VISUAL_ANCHOR_SELECTION',
      depends_on: [`CHARACTER:${character.id}:IDENTITY-001`],
      acceptance_checks: [
        'Uses the role-specific portrait candidate, palette and material, occupational gesture and professional setting.',
        'Keeps the character distinct from other named residents through three or more visible anchors.',
        'A human selects the identity candidate before the state becomes a named Canon continuity asset.'
      ]
    });
  }
}

const COSTUME_VALIDATION_SPECS = [
  {
    id: 'SHEN-HENG',
    characterId: 'CHR-L1-01',
    route: 'Day',
    glamourLevel: 4,
    stylize: 175,
    prompt: `Full-body front-facing costume validation portrait of a 20-year-old Chinese woman, a fragrance artisan with a quiet oval-heart face, a gently lifted outer eye line, warm brown almond eyes, natural straight brows, a refined natural nose, soft peach-coral lips, and subtle dry fragrance-powder traces on the right thumb and index finger. ${NATURAL_SKIN_SURFACE} Lightweight translucent base makeup, soft peach-brown eye tone, naturally separated lashes, softly warmed cheeks, muted coral-rose lips, black hair in a polished half-up high bun with a celadon hairpin, tiny pearl details and several fine loose strands beside the temples. She wears a matte milk-ivory crossed-collar inner robe, a pale mist-blue structured middle layer, a high-waisted long pleated skirt, a muted sage-grey woven sash, and a moon-white silk-gauze outer layer with wide sleeves. Silver-blue flowering branches and fine curling stems form slightly raised embroidery concentrated along the collar, cuffs, sash and lower hem; narrow silver-thread brocade echoes the same pattern at the sleeve edge, with large areas of plain luminous silk. Visible silk crepe weave, translucent gauze edge, subtle satin response at the sash, realistic cloth thickness, vertical weighted folds, complete white cloth shoes visible. She stands upright with relaxed shoulders and hands gently overlapping at the waist, the whole costume visible from hair to hem, centered on a plain warm-ivory studio backdrop with a small soft floor shadow, even diffused frontal light and gentle side light revealing fabric layers, 70mm full-body fashion reference photograph.`,
    acceptanceChecks: [
      'Reads as Shen Heng through the mist-blue, aged-ivory and sage palette, fragrance traces and celadon detail.',
      'Shows three legible garment layers, silver-blue local embroidery and working sleeve logic.',
      'Keeps the face, skin and hair naturally detailed under neutral studio light.'
    ]
  },
  {
    id: 'LIU-SHISI',
    characterId: 'CHR-L1-02',
    route: 'StageFestival',
    glamourLevel: 5,
    stylize: 235,
    prompt: `Full-body front-facing costume validation portrait of a 25-year-old Chinese woman, a performance-house singer and songwriter with a graceful slender oval face, horizontally extended luminous almond eyes, warm dark-brown irises, a refined straight nose, muted rose lips, and the right corner of her mouth resting a fraction higher before a smile. ${NATURAL_SKIN_SURFACE} Breathable peach-rose makeup, fine individually separated lashes, soft rose warmth across the cheeks, muted rose lips with visible texture, black hair in a sculpted high performer updo with one gilt filigree floral hairpin, small pearl sprigs and slender tassel earrings. She wears an old-rose crossed-collar inner robe, a smoky soft-celadon high-waisted pleated skirt, an aged-ivory silk-gauze outer robe with full flowing sleeves, and a deep peacock-ink brocade collar and cuff border. Raised flowering branches, small petals and curling vine embroidery in old gold, pale silver, ivory and dusty celadon threads concentrate at the collar, cuffs, waist sash and hem; selected flower centers hold tiny pearl beads, while broad sections of the outer robe remain plain and translucent. Matte silk, translucent gauze, soft satin and woven brocade remain visibly separate, with long controlled vertical drape and complete cloth shoes. She stands in a poised performance-ready stance, full figure visible from hair to hem, centered on a plain muted cinnabar-to-ivory studio gradient with a soft floor shadow, warm practical side light and clean frontal fill defining silk, pearl, gilt and natural skin, 70mm full-body costume reference photograph.`,
    acceptanceChecks: [
      'Reads as Liu Shisi through the old-rose, celadon, ivory and peacock-ink palette plus the integrated pearl-and-gilt ornament system.',
      'Shows the highest C10-level embroidery density while retaining a complete high collar, full sleeves and a weighted performance skirt.',
      'Keeps pearl, metal, silk and skin in one physically motivated light field.'
    ]
  },
  {
    id: 'PEI-JIUNIANG',
    characterId: 'CHR-L1-04',
    route: 'Day',
    glamourLevel: 4,
    stylize: 185,
    prompt: `Full-body front-facing costume validation portrait of a 31-year-old Chinese woman, a river courier and boat owner with a strong shoulder and forearm line from poles and ropes, a believable sun-warmed skin tone with subtle outdoor tonal variation, a healed mark at the left tiger-mouth, steady alert eyes, and a grounded stance with knees held in a slight deck-balance bend. ${NATURAL_SKIN_SURFACE} Clean restrained historical grooming, individually readable brows, natural lip texture, black hair in a polished practical half-up arrangement with a small jade-green hairpin and fine loose temple strands. She wears a deep-indigo matte-silk crossed-collar inner robe, a river-teal tightly woven structured middle layer, an aged-ivory high collar, a narrow strongly woven belt with a small dull-brass clasp, and compact river-teal outer panels that stay close to the body. Full sleeves gather into workable inner cuffs, the side panels stop above the ankles for wet timber movement, and fitted cloth boots remain fully visible. Water-ripple jacquard and restrained floral threadwork in river teal, aged ivory and muted brass concentrate at the collar, cuffs and belt, with a smaller matching edge at the outer panels; large areas of dense plain woven cloth show their own fiber texture. Realistic weave thickness, durable silk-wool folds, low-reflective brass, restrained jade response and a complete vertical silhouette. She stands with relaxed readiness, full figure visible from hair to boots, centered on a plain warm grey-ivory studio background with a small contact shadow, large diffused daylight from the front side and a quiet reflected fill, 70mm full-body costume reference photograph.`,
    acceptanceChecks: [
      'Reads as Pei Jiuniang through the indigo, river-teal, aged-ivory and dull-brass palette plus visible boat-work constraints.',
      'Shows high material refinement through dense weave, controlled jacquard and tailored water-ready construction.',
      'Preserves outdoor skin variation, the left-hand scar and the deck-balance stance.'
    ]
  }
];

for (const spec of COSTUME_VALIDATION_SPECS) {
  const profile = profileById.get(spec.characterId);
  if (!profile) throw new Error(`Missing character profile for costume validation ${spec.characterId}`);
  addRecord({
    prompt_id: `MJ-V2-COSTUME-VALIDATION-${spec.id}-001`,
    target_key: `COSTUME-VALIDATION:${spec.characterId}:001`,
    family: 'costume-validation',
    asset_lane: 'costume-validation-fullbody',
    target: { stable_id: spec.characterId, name: profile.facts.name, asset_id: 'COSTUME-VALIDATION-001' },
    authority_refs: [sourceRef(profile.character.profile_path, 'character-foundation-authority'), sourceRef('production/style/v2-costume-construction-standard.md', 'v2-costume-construction-authority')],
    facts_snapshot: { name: profile.facts.name, age_y0: profile.facts.age_y0, occupation: profile.facts.occupation, validation_role: 'first-round-costume-construction' },
    route: spec.route,
    raw: true,
    glamour_level: spec.glamourLevel,
    ar: '2:3',
    stylize: spec.stylize,
    chaos: 2,
    positive: spec.prompt,
    reference_binding: {
      mode: 'OPTIONAL_PROJECT_GENERATED_MASTER_REFERENCE',
      status: 'TEXT_ONLY_COSTUME_VALIDATION_READY',
      policy: 'Run this text-only costume validation first. After a project-generated identity reference is approved, attach that approved image in the Midjourney web UI and retain the full text for a continuity validation pass.'
    },
    execution_status: 'READY_FOR_USER_COSTUME_VALIDATION',
    acceptance_checks: spec.acceptanceChecks
  });
}

const LOCATIONS = [
  ['LOC-001', '鹤鸣巷', 0], ['LOC-002', '沈家香铺', 0], ['LOC-003', '香药街', 0],
  ['LOC-004', '御街', 1], ['LOC-005', '御街夜市', 1], ['LOC-006', '春台瓦舍', 1],
  ['LOC-007', '西湖画舫', 2], ['LOC-008', '西泠书坊与画铺', 2], ['LOC-009', '停云酒肆', 2],
  ['LOC-010', '钱塘码头', 3], ['LOC-011', '青鹞', 3], ['LOC-012', '船坊与水上茶摊', 3],
  ['LOC-013', '城务司', 4], ['LOC-014', '三仓', 4], ['LOC-015', '城门、桥闸与查验口', 4],
  ['LOC-016', '小济堂与寺院行堂', 5], ['LOC-017', '松风客舍', 6], ['LOC-018', '城南安置区', 6]
].map(([id, name, group]) => ({ id, name, group }));

const PROMPT_LOCATION_NAMES = {
  'LOC-001': 'Crane-Call Lane',
  'LOC-002': 'Shen Family Fragrance Shop',
  'LOC-003': 'Fragrance and Medicine Street',
  'LOC-004': 'Imperial Street',
  'LOC-005': 'Imperial Street Night Market',
  'LOC-006': 'Chun Tai Performance House',
  'LOC-007': 'West Lake Painted Boat',
  'LOC-008': 'West-Lake Bookshop and Painting Arcade',
  'LOC-009': 'Cloud-Stopping Tavern',
  'LOC-010': 'Qiantang Wharf',
  'LOC-011': 'Green Kite Boat',
  'LOC-012': 'Boat Yard and Water Tea Stalls',
  'LOC-013': 'City Affairs Office',
  'LOC-014': 'Three Granaries',
  'LOC-015': 'City Gate, Bridge Sluice and Inspection Crossing',
  'LOC-016': 'Little Relief Hall and Temple Service Court',
  'LOC-017': 'Pine-Wind Guesthouse',
  'LOC-018': 'South-City Resettlement Quarter'
};

const worldVisualRegistry = readJson('production/style/v2-world-asset-visual-registry.json');

function sceneCompositionProfile(profileId) {
  const profile = worldVisualRegistry.scene_composition_profiles?.[profileId];
  if (!profile?.prompt_block || !Array.isArray(profile.acceptance_checks) || profile.acceptance_checks.length === 0) {
    throw new Error(`Missing V2 scene composition profile ${profileId}`);
  }
  return profile;
}

function locationDesign(locationId) {
  const design = worldVisualRegistry.locations?.[locationId];
  if (!design?.master_description || !design.composition_profile_id || !Array.isArray(design.canonical_sources) || design.canonical_sources.length === 0) {
    throw new Error(`Missing V2 location visual binding for ${locationId}`);
  }
  sceneCompositionProfile(design.composition_profile_id);
  return design;
}

function propDesign(propCode) {
  const design = worldVisualRegistry.props?.[propCode];
  if (!design?.description || !Array.isArray(design.canonical_sources) || design.canonical_sources.length === 0) {
    throw new Error(`Missing V2 prop visual binding for ${propCode}`);
  }
  return design;
}

const LOCATION_TEXT_BINDINGS = [
  ['沈家香铺', 'LOC-002'], ['香铺', 'LOC-002'], ['香药街', 'LOC-003'],
  ['御街夜市', 'LOC-005'], ['夜市', 'LOC-005'], ['御街', 'LOC-004'],
  ['春台瓦舍', 'LOC-006'], ['春台', 'LOC-006'], ['瓦舍', 'LOC-006'],
  ['西湖', 'LOC-007'], ['断桥', 'LOC-007'], ['画舫', 'LOC-007'],
  ['书坊', 'LOC-008'], ['画铺', 'LOC-008'], ['酒肆', 'LOC-009'],
  ['钱塘码头', 'LOC-010'], ['码头', 'LOC-010'], ['青鹞', 'LOC-011'],
  ['船坊', 'LOC-012'], ['水上茶', 'LOC-012'], ['城务', 'LOC-013'],
  ['三仓', 'LOC-014'], ['仓', 'LOC-014'], ['城门', 'LOC-015'],
  ['桥闸', 'LOC-015'], ['查验', 'LOC-015'], ['小济堂', 'LOC-016'],
  ['寺院', 'LOC-016'], ['医棚', 'LOC-016'], ['客舍', 'LOC-017'],
  ['安置', 'LOC-018'], ['春信屋', 'LOC-018']
];

const MATERIAL_VISUAL_TERMS = {
  '纸灯': 'handmade paper lantern paper',
  '竹篾': 'split bamboo',
  '竹': 'bamboo',
  '丝': 'woven silk',
  '布': 'woven cloth',
  '绢': 'fine silk gauze',
  '木': 'weathered timber',
  '纸': 'handmade paper',
  '陶': 'glazed ceramic',
  '瓷': 'glazed ceramic',
  '铜': 'aged brass',
  '铁': 'forged iron',
  '麻': 'ramie fiber',
  '绳': 'coiled rope',
  '漆': 'lacquered wood',
  '水': 'river water'
};

function locationIdForText(text, fallback = 'LOC-001') {
  const value = String(text || '');
  const direct = value.match(/LOC-\d{3}/)?.[0];
  if (direct && LOCATIONS.some((location) => location.id === direct)) return direct;
  const binding = LOCATION_TEXT_BINDINGS.find(([term]) => value.includes(term));
  return binding ? binding[1] : fallback;
}

function locationContext(locationId) {
  const location = LOCATIONS.find((entry) => entry.id === locationId);
  if (!location) throw new Error(`Unknown location context ${locationId}`);
  return `${PROMPT_LOCATION_NAMES[locationId]}: ${locationDesign(locationId).master_description}`;
}

function locationsContext(locationIds, fallback = 'LOC-001') {
  const resolved = unique((locationIds || []).filter((id) => LOCATIONS.some((location) => location.id === id)));
  const ids = resolved.length ? resolved.slice(0, 2) : [fallback];
  return ids.map((locationId) => sentence(locationContext(locationId))).join(' ');
}

function materialVisualTerms(materials) {
  const terms = [];
  for (const item of materials || []) {
    const match = Object.entries(MATERIAL_VISUAL_TERMS).find(([key]) => String(item).includes(key));
    terms.push(match ? match[1] : 'locally used working material');
  }
  return unique(terms).join(', ');
}

function sceneLookForCharacter(characterId) {
  const profile = profileById.get(characterId);
  if (!profile) return characterName(characterId);
  const name = promptNameFromCharacter(profile.character);
  if (CENTRAL_LOOKS[characterId]) {
    return `${CENTRAL_IDENTITY[characterId]} Wardrobe: ${CENTRAL_LOOKS[characterId].identity}`;
  }
  const anchor = supportingLook(characterId);
  return `${name} has ${anchor.portrait} and wears ${anchor.wardrobe}`;
}

function sceneLooksForMembers(memberIds) {
  return (memberIds || []).map((memberId) => sentence(sceneLookForCharacter(memberId))).join(' ');
}

const LOCATION_GROUP_STATES = [
  [
    'after-rain reopening: thresholds and work surfaces are drying, practical queues form beneath eaves, and an old chest appears only as an unresolved object rather than a solved clue.',
    'price strain: smaller measured bundles, refill containers and cautious exchanges show pressure through abstract price marks and measured handling.',
    'merged reports: distinct sealed paper packets and handoffs gather at a shared work point while the lane remains passable.',
    'brief autumn calm: drier brick, restrained seasonal goods and slower normal commerce, with debt and daily exchange still visible.',
    'controlled entry during restriction: half-closed doors, high dry cargo routes and papers or meals passed across thresholds, with a clear observed access protocol.',
    'street spring-letter house: an open mutual-aid table, practical door lamps and correction slips with abstract marks.'
  ],
  [
    'ordinary performance and food-trade cycle: dressing, mending, listening routes and service queues all remain visible.',
    'song-message circulation: listening lines, revised rehearsal material and word-of-mouth clusters are shown through bodies, gesture and routes.',
    'divided response: separate entry, exit and table paths show audience differences while labor and service continue.',
    'osmanthus night-market season: a restrained festival layer of blossom parcels, warm local lamps and rich textile accents at a civic urban celebration scale.',
    'ban state: lowered covers, stored sleeves and repair labor reshape routes; a small working market and repair activity continue at a measured pace.',
    'public oral correction: performers, listeners and street routes stay connected, with source handoff visible through abstract paper marks.'
  ],
  [
    'daytime route sketching, tea service and ordinary sightseeing: water, berth and work paths create a useful working waterfront.',
    'rain-route condition: lowered canopy, wet gear, paper kept dry and delayed or moored passage made spatially clear.',
    'tide anomaly: changed waterline, tightened ropes, separated version proofs or delayed arrival show a careful material observation and a bounded route response.',
    'osmanthus gathering: restrained hospitality, refined tea and textile accents, a working lake-and-book trade environment with mobile berth activity.',
    'restricted berths: waiting people, luggage, cargo and clear routes show constraint through a disciplined physical crossing protocol.',
    'paper and tactile route maps used as partial aids at a shared worktable, with abstract labels and multiple observable route cues.'
  ],
  [
    'waiting-vessel and repair rhythm: berth assignment, weighed bundles, tools, rope and tide marks are physically legible.',
    'water-route verification: draft marks, hold checks, seals, measuring stations and witness work show a bounded procedure.',
    'dark-flood repair: wet piles, raised cargo, reinforced planks and tool handling show physical risk through a working repair route.',
    'autumn navigation recovery: cautious berth queues, repaired rope and markers, and limited cargo movement.',
    'sealed-water state: tied vessels, stop lines, idle cargo and local guard lamps, with a guarded crossing protocol.',
    'rescue-transfer support: shared loading and documented handoffs, practical repair and ration staging across a civilian work network.'
  ],
  [
    'ordinary intake and stock verification: bounded duty tables, separate inventories and clear queue logic.',
    'centralized dispatch: seals, shift plaques, count tables and rerouted queues show finite authority and constrained resources.',
    'account discrepancy: competing source bundles, dual verification and stalled movement reveal a layered civic conflict through material procedure.',
    'continued sealing: calm archive or warehouse restraint, visible fire-and-water tools and ongoing ordinary duty.',
    'emergency order: raised documents and sacks, local lamps, wet passage or firebreak work, a finite civic response with local practical light.',
    'public accountability: open review desk, grouped records and route-time chains made spatially visible through abstract record marks.'
  ],
  [
    'scattered cases and care workflow: diagnosis bench, wash point, porridge line, bedding or shelter routes remain legible across a dignified local care network.',
    'medicine scarcity: fewer bundles, rationed supplies and care requests visible through a grounded care workflow.',
    'medical split and water pressure: raised medicine, drainage or triage routes, privacy-respecting partitions and usable circulation.',
    'false recovery: cleaner paths and ordinary routines return but an unfinished observation, absence or watch route remains.',
    'winter illness and restriction: warm bowls, layered blankets, public kitchen and safe entry routes within a dignified care setting.',
    'public care and correction system: resident-amendable worktable, medical or missing-person route and collective work, with abstract notice surfaces.'
  ],
  [
    'new-resident intake: bedding, travel bundles, registration desk, privacy curtain and water point make the camp or inn a working place.',
    'supply pressure: rationed bundles, public kitchen and water-route details show scarcity through active community care work.',
    'water decline and triage overflow: raised luggage and medicine, drainage repair, safe-water and care lanes retain agency and privacy.',
    'false recovery: drier paths and regular cooking return while logged absences, drainage or watch details remain.',
    'winter restriction: sheltered circulation, meal handoff and care-aware bedding within a dignified shared shelter setting.',
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
  const composition = sceneCompositionProfile(design.composition_profile_id);
  const locationAcceptanceChecks = [
    'Matches the stated Canon facts and the specified V2 route.',
    ...composition.acceptance_checks,
    'Uses motivated light and physically differentiated material response.',
    'Contains no readable text, watermark, logo, fantasy styling or modern object.',
    'Passes the applicable identity, costume, location or continuity review before delivery.'
  ];
  const masterBase = `A human-height medium-wide environmental portrait of ${PROMPT_LOCATION_NAMES[location.id]} in Southern Song Linan. ${design.master_description} ${composition.prompt_block} Its architecture, work surfaces, entrances, circulation paths, local storage and occupation-related tools are spatially clear. Anonymous residents and workers carry the everyday activity.`;
  const masterPositive = `${masterBase} ${routeText(LOCATION_ROUTES[location.id][0])}`;
  addRecord({
    prompt_id: `MJ-V2-${location.id}-MASTER`,
    target_key: `LOCATION:${location.id}:MASTER`,
    family: 'location',
    asset_lane: 'location-master',
    target: { stable_id: location.id, name: location.name, asset_id: 'MASTER' },
    authority_refs: [sourceRef('canon/city/00-city-index.md', 'canonical-location-index'), sourceRef('canon/city/10-seasonal-location-state.md', 'seasonal-location-state'), ...design.canonical_sources.map((relativePath) => sourceRef(relativePath, 'canonical-location-detail'))],
    facts_snapshot: { location_id: location.id, name: location.name, state_group: location.group, composition_profile_id: design.composition_profile_id },
    route: LOCATION_ROUTES[location.id][0],
    glamour_level: location.id === 'LOC-006' ? 4 : 2,
    ar: '16:9',
    stylize: LOCATION_ROUTES[location.id][0] === 'StageFestival' ? 210 : 155,
    chaos: 3,
    positive: masterPositive,
    acceptance_checks: locationAcceptanceChecks,
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
      facts_snapshot: { location_id: location.id, name: location.name, seasonal_window: `E${String(stateIndex * 6 + 1).padStart(2, '0')}-E${String(stateIndex * 6 + 6).padStart(2, '0')}`, state_delta: LOCATION_GROUP_STATES[location.group][stateIndex], composition_profile_id: design.composition_profile_id },
      route,
      glamour_level: route === 'StageFestival' ? 4 : 2,
      ar: '16:9',
      stylize: route === 'StageFestival' ? 220 : 155,
      chaos: 3,
      positive: `${masterBase} Canon seasonal state: ${LOCATION_GROUP_STATES[location.group][stateIndex]} Keep the established architecture, work surfaces, entry and exit logic, and material hierarchy unchanged. ${routeText(route)}`,
      acceptance_checks: locationAcceptanceChecks,
      execution_status: 'READY_FOR_V2_LOCATION_CALIBRATION'
    });
  }
}

const CITY_ESTABLISHING_VIEWS = [
  ['GOLDEN-WATER-CAPITAL', 'Day', 'SCN-WATER-CAPITAL-ESTABLISHING', 'wide elevated panoramic establishing view of a prosperous Southern Song Linan water-capital at late afternoon: layered dark-tile roofs, canal mouths, curved stone bridges, working wharves, cargo boats, market awnings, pedestrian lanes and distant low hills across humid luminous air; warm sunlight reaches timber, plaster, water and woven market cloth while the complete city operates at multiple scales.'],
  ['BLUE-HOUR-LANTERN-CITY', 'NightWet', 'SCN-WATER-CAPITAL-ESTABLISHING', 'wide cinematic water-city establishing view at blue hour: dense Linan rooflines, busy canal banks, occupied balconies, river boats, bridge crossings and rows of handmade lanterns creating small amber pools that recede through deep civic streets; practical light reflects across lacquered timber and water while the blue-grey sky preserves the city silhouette.'],
  ['MORNING-LAKE-AND-MARKET', 'Day', 'SCN-WATER-CAPITAL-ESTABLISHING', 'high wide morning view from lake water toward an inhabited Linan market city: moored painted boats, curved stone bridges, tiered shop roofs, willow edges, fresh trade movement, food stalls and a distant civic rise, with gentle warm haze revealing water routes and active labor.']
];

for (const [assetId, route, compositionProfileId, subject] of CITY_ESTABLISHING_VIEWS) {
  const composition = sceneCompositionProfile(compositionProfileId);
  addRecord({
    prompt_id: `MJ-V2-CITY-${assetId}`,
    target_key: `CITY:LINAN:${assetId}`,
    family: 'city-establishing',
    asset_lane: 'water-city-establishing',
    target: { stable_id: 'CITY-LINAN', asset_id: assetId },
    authority_refs: [sourceRef('canon/city/00-city-index.md', 'city-establishing-authority'), sourceRef('production/style/v2-world-reference-atoms.md', 'water-city-reference-atom')],
    facts_snapshot: { city: 'Linan', asset_id: assetId, visual_role: 'water-city-establishing', composition_profile_id: compositionProfileId },
    route,
    glamour_level: 3,
    ar: '16:9',
    stylize: 235,
    chaos: 3,
    positive: `${subject} ${composition.prompt_block} ${routeText(route)}`,
    execution_status: 'READY_FOR_V2_CITY_ESTABLISHING_CALIBRATION',
    acceptance_checks: [
      'Shows a dense inhabited water-capital with legible water, bridge, market and pedestrian routes.',
      ...composition.acceptance_checks,
      'Uses the V2 material and motivated-light grammar at an establishing scale.',
      'Serves as visual geography rather than an exact cartographic map.'
    ]
  });
}

const CINEMATIC_MOTION_STUDIES = [
  ['CHR-L1-02', 'LOC-006', 'StageFestival', 'Liu Shisi enters the Chun Tai threshold with one sleeve gathered and one hand clearing a curtain edge; a gentle corridor breeze gives weighted lift to old-rose, celadon and aged-ivory silk, pearl sprigs and fine tassels catch warm practical stage light, and the backstage work route remains active behind her.'],
  ['CHR-L1-01', 'LOC-002', 'Day', 'Shen Heng pauses beside the fragrance-shop lattice with a small scent paper and a porcelain jar; a restrained window breeze moves the translucent mist-blue outer layer and a few hair strands, warm reflected daylight articulates her woven collar, jade detail, skin and glazed ceramic.'],
  ['CHR-L3-03', 'LOC-007', 'Day', 'He Lan Du stands at the practical canopy edge of a West Lake painted boat, one hand on a rope rail and one hand steadying layered river-indigo silk; water-borne air moves the full-sleeved outer layer, polished brass and deep teal weave catch a low real sun while crew work and berth traffic remain readable.']
];

for (const [characterId, locationId, route, action] of CINEMATIC_MOTION_STUDIES) {
  const profile = profileById.get(characterId);
  if (!profile) throw new Error(`Missing central profile for motion study ${characterId}`);
  addRecord({
    prompt_id: `MJ-V2-CHR-${characterId}-MOTION-001`,
    target_key: `CHARACTER:${characterId}:MOTION-001`,
    family: 'character',
    asset_lane: 'narrative-motion-study',
    target: { stable_id: characterId, name: profile.facts.name, asset_id: 'MOTION-001' },
    authority_refs: [sourceRef(profile.character.profile_path, 'character-foundation-authority'), ...locationDesign(locationId).canonical_sources.map((relativePath) => sourceRef(relativePath, 'motion-location-visual-authority'))],
    facts_snapshot: { name: profile.facts.name, age_y0: profile.facts.age_y0, location_id: locationId, visual_role: 'wind-and-gauze-motion' },
    route,
    glamour_level: route === 'StageFestival' ? 5 : 4,
    ar: '2:3',
    stylize: route === 'StageFestival' ? 245 : 210,
    chaos: 3,
    positive: `A premium live-action Chinese historical-romance motion still. ${sentence(sceneLookForCharacter(characterId))} ${sentence(locationContext(locationId))} ${action} The full character silhouette, physically motivated fabric movement and active Linan environment remain legible in one cinematic frame. ${routeText(route)}`,
    execution_status: 'READY_FOR_V2_MOTION_SELECTION',
    acceptance_checks: [
      'Preserves the named character identity, age, costume system and location logic.',
      'Uses a physically explained breeze or water movement with visible fabric weight and readable setting.',
      'Supports a controlled New Song emotional key-art or narrative transition selection.'
    ]
  });
}

// The eleven non-Shen central characters previously had only a starter identity
// prompt and hero still. The following post-reference foundation recipe remains
// intentionally dormant until a user-selected project-generated master render
// exists for each character; it must never substitute for the first-pass master
// reference-selection workflow above.
const CENTRAL_FOUNDATION_SPECS = {
  'CHR-L1-02': {
    locationId: 'LOC-006', route: 'StageFestival', accessory: 'gilt filigree hairpin with pearl sprigs', token: 'old-rose silk cue pouch',
    actions: ['straightening the sleeve edge before an entrance', 'steadying a pearl sprig at the temple', 'checking a folded cue folio at the side of the stage', 'marking a phrase pause with one fingertip', 'receiving a tea cup between rehearsal calls', 'listening across audience tables before she smiles', 'closing a contract folio after a decision', 'lifting a curtain edge for an entering performer', 'setting a small ornament aside after the performance'],
    kit: ['unmarked cue folio', 'small wooden rhythm clapper', 'silk sleeve weight', 'performance contract folio', 'pearl sprig', 'gilt hairpin', 'tea cup with lid', 'backstage lamp key', 'soft cloth for ornaments'],
    narrative: 'a singer holds a cue folio at the threshold of a working stage while curtains, mending hands and audience light make the professional world feel alive'
  },
  'CHR-L1-03': {
    locationId: 'LOC-008', route: 'Day', accessory: 'dark wood topknot pin', token: 'rolled map tube with measuring cord',
    actions: ['aligning an old map with a fresh field sketch', 'measuring a bridge span with a cord', 'brushing fine ink from a marked fingertip', 'checking a muddy canal edge against a drawing', 'holding a paper tube against a carved railing', 'revising a scaled route line', 'pausing above a sluice measurement', 'sorting map weights beside a worktable', 'carrying a rolled survey sheet through a bookshop arcade'],
    kit: ['rolled map tube', 'measuring cord', 'fine ink brush', 'stone ink dish', 'waxed paper sheet', 'small ruler', 'bridge-sluice sketch', 'wooden map weights', 'woven paper wrap'],
    narrative: 'a map artist compares a route drawing against a measured canal edge, with bookshop work and a living water-city moving through the background'
  },
  'CHR-L1-04': {
    locationId: 'LOC-010', route: 'Day', accessory: 'restrained jade-green boat hairpin', token: 'weathered river rope bracelet',
    actions: ['testing the tension of a mooring rope', 'reading a tide mark along a hull', 'bracing a cargo tag against wind', 'steadying a passenger at a plank crossing', 'checking a boat hook before departure', 'lifting a wet rope coil with a grounded stance', 'marking a berth time on a wax tablet', 'watching the river current from a landing', 'passing a sealed parcel across a boat rail'],
    kit: ['rope coil', 'boat hook', 'tide-mark cord', 'waterproof cargo tag', 'small wax tablet', 'brass berth token', 'folded river chart', 'oilcloth wrap', 'wooden tally stick'],
    narrative: 'a river-route owner reads tide and cargo evidence at a working landing while boats, ropes and porters create a full water-city rhythm'
  },
  'CHR-L1-05': {
    locationId: 'LOC-009', route: 'NightWet', accessory: 'dark wood hair ornament with a small brass clasp', token: 'water-road route token',
    actions: ['setting a tea tray down with one eye on the entrance', 'checking a rope mark on a courier parcel', 'pouring wine during a careful negotiation', 'guiding a guest toward a safer interior table', 'testing a lantern wick at the tavern rail', 'folding a route note beside a tea bowl', 'pausing at a wet threshold to listen', 'lifting a service cloth from a lacquered table', 'walking a covered balcony route after closing'],
    kit: ['route token', 'covered tea tray', 'small wine ewer', 'sealed courier parcel', 'lantern wick tool', 'rope sample', 'folded route note', 'brass cup', 'oilcloth packet'],
    narrative: 'a tavern keeper holds a covered route parcel beside warm lamps and a riverside balcony while the night city keeps moving below'
  },
  'CHR-L2-01': {
    locationId: 'LOC-002', route: 'Day', accessory: 'jade-and-wood hairpin', token: 'small fragrance-goods pouch',
    actions: ['weighing fragrant material on a brass scale', 'folding a paper packet with steady hands', 'checking a ceramic jar seal', 'arranging a customer parcel on the counter', 'warming a small scent dish in window light', 'tying a shop pouch to a sash', 'reading a ledger edge at the threshold', 'passing a wrapped order across the counter', 'returning tools to an ordered drawer'],
    kit: ['brass scale', 'small ceramic jar', 'scent dish', 'paper packet', 'soft brush', 'shop ledger', 'fragrance pouch', 'wooden scoop', 'cloth wrapping square'],
    narrative: 'a seasoned fragrance-shop keeper completes a precise parcel handoff amid ceramic jars, paper drawers and soft daylight from the lane'
  },
  'CHR-L2-02': {
    locationId: 'LOC-001', route: 'Day', accessory: 'small flower hairpin', token: 'woven market coin pouch',
    actions: ['balancing a hot bowl with both hands', 'counting small coins beside a serving cloth', 'scanning a lane while tying an apron edge', 'passing a bowl across a busy counter', 'lifting a basket of clean bowls', 'saving an oil-paper note from steam', 'turning toward a familiar market call', 'settling a loose sleeve before work', 'carrying a food tray into the afternoon lane'],
    kit: ['porcelain bowl', 'wooden spoon', 'woven coin pouch', 'bowl cloth', 'oil-paper note', 'food tray', 'small basket', 'scallion bundle', 'brass change dish'],
    narrative: 'a quick young market observer pauses with a serving tray in warm late afternoon as bowls, neighbors and market routes remain active behind her'
  },
  'CHR-L2-03': {
    locationId: 'LOC-016', route: 'Day', accessory: 'small polished jade hairpin', token: 'herbal sachet',
    actions: ['sorting medicine packets by texture', 'checking a water sample beside a case folder', 'lifting a pulse cloth from a care table', 'grinding dried herbs in a small mortar', 'recording a patient observation', 'carrying a warm bowl through a care lane', 'separating a clean medicine wrap', 'steadying a ceramic jar while listening', 'pausing at a relief-hall threshold'],
    kit: ['herbal sachet', 'small mortar', 'medicine packets', 'ceramic jar', 'pulse cloth', 'wooden scoop', 'case folder', 'warm bowl', 'soft medicine wrap'],
    narrative: 'a medical apprentice sorts practical medicine materials in a dignified relief hall, with patients, workers and bright care routes behind her'
  },
  'CHR-L2-04': {
    locationId: 'LOC-013', route: 'Day', accessory: 'tidy dark wood hairpiece', token: 'duty token on a woven belt',
    actions: ['aligning a civic ledger with a route notice', 'checking a seal beside a gate token', 'setting an arrival slip into a separate tray', 'holding a measured pause between two arguing residents', 'walking a city-office passage with a document roll', 'testing the order of papers at a desk', 'receiving a warehouse note at a doorway', 'marking a time on a wooden tally', 'closing a duty folder before a decision'],
    kit: ['duty token', 'civic ledger', 'sealed document', 'gate token', 'wooden tally', 'document roll', 'brass paper weight', 'route notice', 'small seal case'],
    narrative: 'a city clerk aligns papers and public routes at a light-filled office passage while civic traffic passes through the middle distance'
  },
  'CHR-L3-01': {
    locationId: 'LOC-013', route: 'NightWet', accessory: 'aged-metal topknot pin', token: 'precisely fitted dark belt token',
    actions: ['ordering documents into a fixed sequence', 'holding a lamp beside a city dispatch board', 'checking an arrival time against a warehouse count', 'placing a seal beside a folded order', 'listening before issuing a measured hand signal', 'walking an amber-lit civic corridor', 'opening a document case at a worktable', 'separating route reports into clear groups', 'pausing beside an open city gate ledger'],
    kit: ['document case', 'dark belt token', 'civic seal', 'arrival board', 'folded order', 'brass paper weight', 'time tally', 'route report bundle', 'covered lamp'],
    narrative: 'a city administrator organizes arrival reports beneath warm corridor lamps while ordered papers and civic movement recede toward blue-hour depth'
  },
  'CHR-L3-02': {
    locationId: 'LOC-009', route: 'NightWet', accessory: 'formal dark hairpiece with polished jade detail', token: 'merchant account pouch',
    actions: ['pouring tea before a negotiation', 'separating account tags by trade route', 'closing a lacquered ledger at a waterside table', 'testing a cargo sample between careful fingers', 'receiving a river note from a messenger', 'holding a silk sleeve clear of a tea service', 'watching a lantern reflection across a canal', 'setting a jade counter beside a contract case', 'walking a tavern balcony after the guests depart'],
    kit: ['merchant account pouch', 'lacquered ledger', 'jade counter', 'contract case', 'tea ewer', 'cargo sample', 'route tag', 'brass cup', 'covered river note'],
    narrative: 'a refined merchant host pours tea beside a waterside ledger while lantern reflections, occupied balconies and the moving canal create material social depth'
  },
  'CHR-L3-03': {
    locationId: 'LOC-007', route: 'Day', accessory: 'small bronze clasp at a maintained topknot', token: 'weathered leather wrist guard',
    actions: ['steadying a rope rail during a crossing', 'reading a water route from a folded chart', 'checking a bridge approach before a handoff', 'tightening a leather wrist guard', 'lifting a travel parcel to a boat deck', 'watching berth traffic from a painted-boat canopy', 'offering a covered cup across a table', 'securing a brass clasp before departure', 'walking a lakeside rail into low sunlight'],
    kit: ['leather wrist guard', 'folded water chart', 'travel parcel', 'bronze clasp', 'rope rail marker', 'covered cup', 'small brass compass weight', 'woven travel wrap', 'boat berth token'],
    narrative: 'a traveler-merchant steadies a rope rail on a painted West Lake boat while water-borne air moves his full silhouette and berth work remains visible'
  }
};

const FOUNDATION_EXPRESSION_SETS = {
  'EX-001': ['calm', 'natural happiness', 'comforting concern', 'careful intimacy', 'shame', 'sadness', 'alertness', 'resolve', 'quiet relief'],
  'EX-002': ['fear', 'contained anger', 'jealousy', 'guilt', 'disappointment', 'helplessness', 'hope', 'despair held back', 'acceptance']
};

const FOUNDATION_HAIR_STATES = ['daily half-up', 'work-secured', 'rain-protected', 'social braid or layered topknot', 'formal restrained updo', 'night low knot', 'winter wrapped style', 'care-work practical arrangement', 'renewed spring finish'];
const FOUNDATION_MAKEUP_STATES = ['barely-there daily base', 'workday satin-matte', 'rain-resilient finish', 'social visit glow', 'formal civic or performance finish', 'night lamp finish', 'winter dry-air finish', 'long-workday reset', 'post-work freshening'];
const FOUNDATION_GENERAL_ACTIONS = ['walking with a natural purpose', 'stopping to observe', 'turning back toward a sound', 'raising one hand to pause', 'passing an object', 'taking an object', 'sitting to work', 'standing from a worktable', 'leaving along a safe active route'];
const FOUNDATION_POSE_SETS = {
  'PS-001': ['neutral standing', 'side standing', 'natural seated work', 'controlled turn', 'leaning to observe', 'crouching to retrieve', 'looking back', 'crossing a threshold', 'resting posture'],
  'PS-002': ['contained', 'guarded', 'alert', 'decisive', 'tired', 'relieved', 'grieving while working', 'resistant', 'open to correction']
};
const FOUNDATION_CAMERA_FRAMES = ['eye close detail', 'full face', 'bust portrait', 'waist-up', 'three-quarter body', 'full body', 'side profile', 'back view', 'signature-hand detail'];
const FOUNDATION_COSTUME_STATES = [
  ['C01', 'daily city attire', 'clean use-ready layers, a complete sleeve line and a small character-specific ornament', 2],
  ['C02', 'professional work attire', 'fitted inner sleeves, a compact work sash and carefully maintained material at the hands', 2],
  ['C03', 'social visit attire', 'finer floral weave, a translucent outer layer and a restrained gift or calling detail', 3],
  ['C04', 'formal civic or performance attire', 'sculpted layering, visible hand-finished embroidery and a coordinated ornament system', 4],
  ['C05', 'lantern-evening attire', 'deepened dye values from the fixed palette, satin response and protected mobile layers', 3],
  ['C06', 'rain-ready attire', 'weather-protected outer silk, physically weighted hems and a polished compact silhouette', 2],
  ['C07', 'winter attire', 'credible woven warmth, textured sash layers and refined insulation at collar and sleeve', 2],
  ['C08', 'care-state attire', 'easy working sleeves, a fresh collar, a wrapped warm layer and dignified practical presentation', 2],
  ['C09', 'long-labor attire', 'natural handled folds, a maintained hairstyle and material signs of a full professional day', 2],
  ['C10', 'story-special attire', 'the richest coherent version of the fixed palette, a refined translucent layer, hand-finished embroidery and coordinated jewelry or fittings', 4]
];

function foundationGrooming(profile) {
  const presentation = CENTRAL_PRESENTATIONS[profile.character.id] || inferPresentation(profile.facts.name, profile.facts.occupation, profile.profileMarkdown);
  return presentation === 'woman'
    ? `Refined translucent historical makeup: sheer breathable base, soft peach-rose eye tone, naturally separated lashes, subtle warmth at the cheeks and softly stained rose lips. ${NATURAL_SKIN_SURFACE}`
    : `Clean high-end historical grooming: naturally shaped brows, realistic lip texture, individually readable hair and a refined, believable leading-cast finish. ${NATURAL_SKIN_SURFACE}`;
}

function foundationBase(profile) {
  const look = CENTRAL_LOOKS[profile.character.id];
  const presentation = CENTRAL_PRESENTATIONS[profile.character.id] || inferPresentation(profile.facts.name, profile.facts.occupation, profile.profileMarkdown);
  return `${CENTRAL_IDENTITY[profile.character.id]} Fixed wardrobe DNA: ${look.identity}. ${costumeConstruction(2, presentation, profile.facts.occupation)} ${foundationGrooming(profile)}`;
}

function foundationPersonalProps(spec) {
  return [spec.accessory, `secondary version of ${spec.accessory}`, spec.token, `small personal pouch carrying ${spec.token}`, 'coordinated waist fastening', 'well-kept cloth footwear', 'folded sleeve tie matching the fixed palette'];
}

function foundationRoute(spec, assetId) {
  if (assetId === 'C05' || assetId === 'C06' || assetId === 'NV-004' || assetId === 'NV-005') return 'NightWet';
  if ((assetId === 'C04' || assetId === 'C10' || assetId === 'NV-001') && spec.route === 'StageFestival') return 'StageFestival';
  return spec.route === 'StageFestival' && /^(AC|PS|NV)/.test(assetId) ? 'StageFestival' : 'Day';
}

function foundationSettings(kind, technical, assetId) {
  if (technical) return { raw: true, stylize: kind === 'foundation-identity' ? 100 : 88, chaos: 2 };
  if (kind === 'foundation-costume') return { raw: true, stylize: /C04|C10/.test(assetId) ? 180 : 155, chaos: 2 };
  if (kind === 'foundation-prop') return { raw: true, stylize: 105, chaos: 2 };
  if (kind === 'foundation-narrative') return { raw: false, stylize: 205, chaos: 3 };
  return { raw: false, stylize: 180, chaos: 3 };
}

function foundationTime(route) {
  return route === 'StageFestival' ? 'blue-hour-or-lantern-lit' : undefined;
}

function addFoundationTask(profile, spec, input) {
  const route = input.route || foundationRoute(spec, input.assetId);
  const settings = foundationSettings(input.kind, Boolean(input.technical), input.assetId);
  addRecord({
    prompt_id: `MJ-V2-FOUNDATION-${profile.character.id}-${input.assetId}-${input.tile.replace(/[^a-z0-9]+/gi, '-').replace(/^-|-$/g, '').toUpperCase()}`,
    target_key: `FOUNDATION:${profile.character.id}:${input.assetId}:${input.tile}`,
    family: 'central-character-package',
    asset_lane: input.kind,
    target: { stable_id: profile.character.id, name: profile.facts.name, asset_id: input.assetId, tile: input.tile },
    authority_refs: [sourceRef(profile.character.profile_path, 'character-foundation-authority'), ...locationDesign(spec.locationId).canonical_sources.map((relativePath) => sourceRef(relativePath, 'foundation-location-visual-authority'))],
    facts_snapshot: { name: profile.facts.name, aliases: profile.facts.aliases, age_y0: profile.facts.age_y0, occupation: profile.facts.occupation, foundation_delivery_asset: input.assetId, task_tile: input.tile, location_id: spec.locationId },
    route,
    time: foundationTime(route),
    technical: Boolean(input.technical),
    raw: settings.raw,
    glamour_level: input.glamour_level,
    ar: input.ar,
    stylize: settings.stylize,
    chaos: settings.chaos,
    positive: input.positive,
    execution_status: 'BLOCKED_UNTIL_APPROVED_MASTER_REFERENCE',
    assembly: input.assemblyGroup ? { assembly_group: `${profile.character.id}:${input.assetId}`, tile: input.tile, strategy: 'Generate each task independently; select the approved candidates and assemble any contact or comparison sheet locally.' } : null,
    acceptance_checks: [
      'Matches the locked central-character age, face anchor, fixed wardrobe DNA and professional identity.',
      'Keeps the selected candidate beautiful, individually recognizable and materially grounded in the V2 New Song world.',
      input.technical ? 'Technical continuity view keeps face, hair, collar, body geometry and professional hand detail legible.' : 'Narrative or state view keeps a full, physically motivated environment and complete costume silhouette legible.',
      'A human selection is required before this candidate becomes a Canon continuity asset.'
    ]
  });
}

const INCLUDE_POST_REFERENCE_FOUNDATION = process.env.LINAN_INCLUDE_POST_REFERENCE_FOUNDATION === '1';

if (INCLUDE_POST_REFERENCE_FOUNDATION) for (const [characterId, spec] of Object.entries(CENTRAL_FOUNDATION_SPECS)) {
  const profile = profileById.get(characterId);
  if (!profile || !CENTRAL_IDENTITY[characterId] || !CENTRAL_LOOKS[characterId]) throw new Error(`Missing central foundation authority for ${characterId}`);
  const base = foundationBase(profile);
  const place = sentence(locationContext(spec.locationId));
  const standardTechnical = `${base} Front-facing official continuity task with a clean warm-ivory background, level head and shoulders, clear collar line and natural eye-level lens.`;

  addFoundationTask(profile, spec, { assetId: 'ID-001', tile: 'front-neutral', kind: 'foundation-identity', technical: true, glamour_level: 2, ar: '3:4', positive: `${standardTechnical} Head-and-upper-torso front view, neutral composed expression, hands below the crop. ${routeText('Day', true)}` });
  for (const tile of ['front', 'left-three-quarter', 'left-profile', 'right-three-quarter', 'right-profile']) {
    addFoundationTask(profile, spec, { assetId: 'ID-002', tile, kind: 'foundation-identity-angle', technical: true, glamour_level: 2, ar: '3:4', assemblyGroup: true, positive: `${standardTechnical} ${sentence(`${tile} head view with the same light makeup or grooming, same hairstyle and same collar`) } ${routeText('Day', true)}` });
  }
  for (const tile of ['front-full-body', 'left-profile-full-body', 'back-full-body']) {
    addFoundationTask(profile, spec, { assetId: 'ID-003', tile, kind: 'foundation-turnaround', technical: true, glamour_level: 2, ar: '2:3', assemblyGroup: true, positive: `${base} ${sentence(`${tile} full-body continuity view from head to footwear, level natural stance and clear garment construction`) } ${routeText('Day', true)}` });
  }
  for (const tile of ['face-skin', 'hairline-and-strands', 'signature-hand-trace', 'collar-and-textile']) {
    addFoundationTask(profile, spec, { assetId: 'ID-004', tile, kind: 'foundation-detail', technical: true, glamour_level: 2, ar: '1:1', assemblyGroup: true, positive: `${base} ${sentence(`Single macro continuity detail of ${tile}, with fine natural skin or material response and clean light`) } ${routeText('Day', true)}` });
  }
  for (const [assetId, tiles] of Object.entries(FOUNDATION_EXPRESSION_SETS)) {
    for (const tile of tiles) {
      addFoundationTask(profile, spec, { assetId, tile, kind: 'foundation-expression', technical: true, glamour_level: 2, ar: '3:4', assemblyGroup: true, positive: `${standardTechnical} ${sentence(`Single restrained ${tile} expression; the face remains fully visible and naturally attractive`) } ${routeText('Day', true)}` });
    }
  }
  for (const tile of FOUNDATION_HAIR_STATES) {
    addFoundationTask(profile, spec, { assetId: 'HR-001', tile, kind: 'foundation-hair', technical: true, glamour_level: 2, ar: '3:4', assemblyGroup: true, positive: `${standardTechnical} ${sentence(`Single ${tile} hairstyle state, coordinated with ${spec.accessory} and readable individual strands`) } ${routeText('Day', true)}` });
  }
  for (const tile of FOUNDATION_MAKEUP_STATES) {
    addFoundationTask(profile, spec, { assetId: 'MK-001', tile, kind: 'foundation-makeup', technical: true, glamour_level: 2, ar: '3:4', assemblyGroup: true, positive: `${standardTechnical} ${sentence(`Single ${tile} historical grooming or makeup state, preserving true skin texture and fixed facial identity`) } ${routeText('Day', true)}` });
  }
  for (const [assetId, label, stateDetail, glamourLevel] of FOUNDATION_COSTUME_STATES) {
    const route = foundationRoute(spec, assetId);
    addFoundationTask(profile, spec, { assetId, tile: 'full-look', kind: 'foundation-costume', technical: false, glamour_level: glamourLevel, ar: '2:3', route, positive: `${base} ${sentence(`Front three-quarter full-body ${label} presentation at ${place} ${stateDetail}`)} Complete long silhouette, materially weighted drape, coordinated accessories and real light make the entire costume system readable. ${routeText(route)}` });
  }
  for (const tile of spec.actions) {
    addFoundationTask(profile, spec, { assetId: 'AC-001', tile, kind: 'foundation-occupational-action', technical: false, glamour_level: 3, ar: '2:3', assemblyGroup: true, positive: `${base} ${place} ${sentence(`Professional action: ${tile}`)} The full figure, working hands, one useful tool and the active local service route remain legible. ${routeText(spec.route)}` });
  }
  for (const tile of FOUNDATION_GENERAL_ACTIONS) {
    addFoundationTask(profile, spec, { assetId: 'AC-002', tile, kind: 'foundation-general-action', technical: false, glamour_level: 3, ar: '2:3', assemblyGroup: true, positive: `${base} ${place} ${sentence(`Natural motion study: ${tile}`)} Physically weighted fabric, a controlled hand gesture and a readable working background keep the character grounded in the city. ${routeText(spec.route)}` });
  }
  for (const [assetId, tiles] of Object.entries(FOUNDATION_POSE_SETS)) {
    for (const tile of tiles) {
      addFoundationTask(profile, spec, { assetId, tile, kind: 'foundation-pose', technical: false, glamour_level: 3, ar: '2:3', assemblyGroup: true, positive: `${base} ${place} ${sentence(`Single natural body pose: ${tile}`)} Full costume silhouette, graceful practical posture and the relevant environment remain readable. ${routeText(spec.route)}` });
    }
  }
  for (const tile of foundationPersonalProps(spec)) {
    addFoundationTask(profile, spec, { assetId: 'PR-001', tile, kind: 'foundation-prop', technical: true, glamour_level: 2, ar: '3:2', assemblyGroup: true, positive: `${sentence(`A single personal prop study for ${promptNameFromCharacter(profile.character)}: ${tile}`)} Refined Southern Song material detail on a clean work surface, with visible silk, wood, jade, pearl, brass or leather response as appropriate. ${routeText('Day', true)}` });
  }
  for (const tile of spec.kit) {
    addFoundationTask(profile, spec, { assetId: 'PR-002', tile, kind: 'foundation-prop', technical: true, glamour_level: 2, ar: '3:2', assemblyGroup: true, positive: `${sentence(`A single professional prop study for ${promptNameFromCharacter(profile.character)}: ${tile}`)} Useful Southern Song work material on a clean practical surface, with individual fibers, paper, wood, ceramic, metal or rope response clearly visible. ${routeText('Day', true)}` });
  }
  for (const tile of FOUNDATION_CAMERA_FRAMES) {
    addFoundationTask(profile, spec, { assetId: 'CAM-001', tile, kind: 'foundation-camera-frame', technical: true, glamour_level: 2, ar: '3:4', assemblyGroup: true, positive: `${standardTechnical} ${sentence(`Single ${tile} camera-framing continuity view with the fixed character identity and professional detail held in clear focus`) } ${routeText('Day', true)}` });
  }
  const narratives = [
    ['NV-001', 'hero', '2:3', spec.route, `Official character key art: ${spec.narrative}.`],
    ['NV-002', 'professional-work', '16:9', spec.route, `Professional work still: ${spec.actions[0]}, with ${spec.kit[0]} and ${spec.kit[1]} in the foreground.`],
    ['NV-003', 'day-city-movement', '16:9', 'Day', `Daylight city movement: ${FOUNDATION_GENERAL_ACTIONS[0]}, with a route from the work place toward a busy public threshold.`],
    ['NV-004', 'night-decision', '2:3', 'NightWet', `Night decision still: a covered light source, ${spec.kit[2]} and a held pause at a lantern-lit threshold.`],
    ['NV-005', 'lantern-evidence', '16:9', 'NightWet', `Lantern-lit decision moment: ${spec.actions[3]}, with ${spec.kit[3]} and a clear hand-to-object relation.`]
  ];
  for (const [assetId, tile, ar, route, detail] of narratives) {
    addFoundationTask(profile, spec, { assetId, tile, kind: 'foundation-narrative', technical: false, glamour_level: route === 'StageFestival' ? 5 : 4, ar, route, positive: `${base} ${place} ${sentence(detail)} A readable foreground task, active middle-ground circulation and receding inhabited architecture build a cinematic historical-romance story still. ${routeText(route)}` });
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
  const value = String(text || '');
  if (/春台|瓦舍|桂花|夜市|演出|灯会|曲牌|戏台|歌伎|表演/.test(value)) return 'StageFestival';
  if (/夜市|夜雨|雨夜|深夜|夜间|晚间|傍晚|暮色|蓝调|\bnight\b|\bdusk\b|\bevening\b/i.test(value)) return 'NightWet';
  return 'Day';
}

function routeForEpisode(episode) {
  const locationIds = episode.city_evidence?.location_ids || [];
  const text = `${episode.episode_id} ${episode.title || ''} ${episode.opening_state || ''} ${episode.profession_action?.action || ''} ${episode.city_evidence?.description || ''}`;
  if (locationIds.includes('LOC-006') && /曲|演|桂|台|夜雨|灯会|歌|节/.test(text)) return 'StageFestival';
  return routeForText(text);
}

function routeForStoryboard(scene, shot) {
  const sources = (shot.light?.physical_sources || []).join(' ');
  const context = `${scene.scene_binding?.weather_state || ''} ${sources}`;
  if (/春台|瓦舍|演出|曲牌|戏台|灯会/.test(context)) return 'StageFestival';
  if (/天光|日光|散射光|阴天光|午后|晨光/.test(sources)) return 'Day';
  if (/夜|油灯|灯笼|烛|炉火|夜雨|深蓝/.test(context)) return 'NightWet';
  return 'Day';
}

function characterName(id) {
  const profile = profileById.get(id);
  return profile ? promptNameFromCharacter(profile.character) : id;
}

function relationshipVisualMoment(snapshot, route) {
  const text = `${snapshot.space || ''} ${snapshot.object || ''} ${snapshot.observable_action || ''} ${snapshot.continuity_delta || ''}`;
  const object = /香|粉|匣|药/.test(text)
    ? 'a small fragrance case, sample dish or wrapped herbal packet'
    : /账|册|票|签|纸|信|稿|图/.test(text)
      ? 'separated paper records, a folded ledger or an unmarked route sheet'
      : /船|水|潮|码头|湖/.test(text)
        ? 'a rope rail, route chart or water-side parcel'
        : /茶|酒|食|碗/.test(text)
          ? 'a tea cup, serving tray or small shared table object'
          : /曲|台|演|灯/.test(text)
            ? 'a gathered sleeve, cue strip or small backstage tool'
            : 'one carefully handled shared work object';
  const staging = route === 'StageFestival'
    ? 'One figure gathers a full sleeve or steadies the cue object while the other keeps an attentive, measured distance amid working performance circulation.'
    : /船|水|潮|码头|湖/.test(text)
      ? 'One figure steadies the shared object against the water-side movement while the other reads the route and maintains a clear, deliberate distance.'
      : 'Separate hand positions, eye lines and a held pause make the relationship boundary readable while the practical activity continues.';
  return `A held relationship moment centers ${object}. ${staging}`;
}

for (const relation of relationshipSlots.relationships) {
  const snapshots = evidenceByRelation.get(relation.id) || [];
  for (const snapshot of snapshots) {
    const memberIds = relation.members || [relation.left, relation.right];
    const route = routeForText(`${snapshot.space} ${snapshot.observable_action}`);
    const locationId = locationIdForText(snapshot.space);
    const place = locationContext(locationId);
    const memberLooks = sceneLooksForMembers(memberIds);
    const staging = relation.members
      ? 'Every named participant has an individually readable silhouette, palette and working gesture across a shared foreground-to-background composition.'
      : 'The two figures maintain the registered distance through clear open staging, their shared object and their separate hand positions.';
    addRecord({
      prompt_id: `MJ-V2-${relation.id}-${snapshot.snapshot}`,
      target_key: `RELATIONSHIP:${relation.id}:${snapshot.snapshot}`,
      family: 'relationship',
      asset_lane: 'relationship-state-study',
      target: { stable_id: relation.id, asset_id: snapshot.snapshot, members: memberIds },
      authority_refs: [sourceRef('qa/relationship-slots.json', 'relationship-registry'), sourceRef('qa/relationship-evidence.json', 'relationship-evidence'), ...locationDesign(locationId).canonical_sources.map((relativePath) => sourceRef(relativePath, 'relationship-location-visual-authority'))],
      facts_snapshot: { relation_id: relation.id, kind: relation.kind, snapshot: snapshot.snapshot, episode_window: snapshot.episode_window, space: snapshot.space, location_id: locationId, object: snapshot.object, observable_action: snapshot.observable_action, continuity_delta: snapshot.continuity_delta },
      route,
      glamour_level: route === 'StageFestival' ? 4 : 3,
      ar: '16:9',
      stylize: route === 'StageFestival' ? 220 : 175,
      chaos: 3,
      positive: `A premium live-action Chinese historical-romance relationship scene at ${place} ${memberLooks} ${relationshipVisualMoment(snapshot, route)} ${staging} A readable foreground object, active middle-ground behavior and receding urban work depth carry the scene. ${routeText(route)}`,
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
    positive: `An uncast individual Chinese resident of Southern Song Linan for the ${slot.category} unit slot. Show one plausible ${profession} work context, a practical occupation gesture, a distinct casting face, tailored crossed-collar clothing, real skin texture and materially specific tools. Front-facing three-quarter identity-study composition with a clear professional silhouette. ${routeText('Day', true)}`,
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
  const isNight = /night|dusk|evening/.test(archetype.active_time);
  const route = isNight ? 'NightWet' : 'Day';
  const place = locationContext(locationId);
  const materials = materialVisualTerms(archetype.materials);
  addRecord({
    prompt_id: `MJ-V2-${archetype.id}-EXPLORATION-001`,
    target_key: `BACKGROUND:${archetype.id}:EXPLORATION-001`,
    family: 'background-archetype',
    asset_lane: 'ecosystem-exploration',
    target: { stable_id: archetype.id, asset_id: 'EXPLORATION-001' },
    authority_refs: [sourceRef('qa/background-usage.json', 'background-usage-registry'), ...locationDesign(locationId).canonical_sources.map((relativePath) => sourceRef(relativePath, 'background-location-visual-authority'))],
    facts_snapshot: { ...archetype, normalized_location_id: locationId },
    route,
    glamour_level: 2,
    ar: '2:3',
    stylize: 125,
    chaos: 5,
    positive: `An individually readable uncast ${archetype.age_band} Chinese ${archetype.occupation_family} resident working at ${place} Active during ${archetype.active_time}, the ${archetype.class_band} worker handles ${materials} with a precise occupational posture. A specific work zone, useful tool, layered depth and local circulation establish a flexible later scene composition. ${routeText(route)}`,
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

// Story facts remain Chinese Canon metadata.  Direct Midjourney text instead
// uses these hand-authored English visual beats so it reads as a shot direction,
// never as a block of story database prose or a source for accidental typography.
const EPISODE_VISUAL_BEATS = {
  'S1-E01': 'At a rain-washed fragrance-shop threshold, the heroine separates a tiny ash sample beside a worn fragrance case, a thin blade, a powder dish and blank paper fields; an older shopkeeper holds at the rear-room threshold.',
  'S1-E02': 'A low crate lies open beside a brass scale, grain dust, cargo tags and carefully separated fragrance packets; workers and civic staff hold a tense but orderly work route beyond the counter.',
  'S1-E03': 'During blue hour at a lantern-lit performance house, a singer compares two cue pauses and rearranges the ending of a song while audience tables, backstage runners and a nearby night market remain active.',
  'S1-E04': 'A mapmaker overlays an old route drawing, a fresh field sketch, wet mud lines and a measuring cord on a long worktable while a bridge-sluice passage and official records create depth behind.',
  'S1-E05': 'At an occupied wharf, a boat owner reads tide marks and hull depth beside a cargo tag, rope coil and working berth while porters cross the frame with deliberate water-route movement.',
  'S1-E06': 'Five separated evidence trays, each with a different material trace, sit around a central fragrance-work table as several professional routes converge through the same living city.',
  'S1-E07': 'A civic administrator compares arrival boards, grain sacks and price tallies beneath lanterns while an urgent food-release route moves through the performance district after rain.',
  'S1-E08': 'A mapmaker studies a missing picture frame, layered canal sketches and a marked waterway edge on a West Lake worktable, with boat traffic and painting-shop activity receding behind.',
  'S1-E09': 'A young medical apprentice sorts medicine packets, household meal notes and a water sample across a care-table while patients, attendants and a relief queue remain visible through soft daylight.',
  'S1-E10': 'A tavern keeper examines a half-volume archive beside paper fibers, page holes and an old seal while a civic corridor beyond carries travelers, clerks and restrained warm light.',
  'S1-E11': 'A city clerk compares synchronized order summaries at a long desk, with gate tokens, dock schedules and warehouse slips arranged as distinct physical sources.',
  'S1-E12': "At a rain-dark boat berth, a river-route worker holds a protected water letter beside a seal, wet rope and a survivor's covered handoff under warm local lamps.",
  'S1-E13': 'A fragrance artisan compares fish, tide marks, a ferry-time cord and a water-color sample along a sunlit canal edge where daily crossings keep moving.',
  'S1-E14': 'A merchant accountant recopies a warehouse page beside a berth chart, porter tally and a blank space in the ledger, each surface catching a different window reflection.',
  'S1-E15': 'A young market observer revisits households with a plain record board, a water jar and a bowl count while the care quarter holds a patient, dignified daily rhythm.',
  'S1-E16': 'A boat owner guides a rescue line across tide-swept water; a broken seal, damaged hull edge and witnesses at the wharf preserve the material consequence of the choice.',
  'S1-E17': 'A record keeper aligns an original warehouse slip, ink comparison and a porter’s load measurement at a busy granary threshold, making labor and documentation equally visible.',
  'S1-E18': 'A fragrance artisan gathers five clearly separated evidence groups on a civic table while medical, boat, warehouse and market paths overlap in a readable public interior.',
  'S1-E19': 'At an early-osmanthus street celebration, a young woman keeps flower bundles, household accounts and a wedding-gift list in separate graceful stacks while ordinary joy continues around her.',
  'S1-E20': 'At a guesthouse intake desk, a relief organizer records travel bundles and individual choices beside a privacy curtain, water point and varied newcomer groups.',
  'S1-E21': 'A mapmaker compares a formal academy notice, a civilian road sketch and a measuring cord at a bookshop arcade while pedestrian routes and official access points remain visible.',
  'S1-E22': 'At Chun Tai under lantern light, a singer shapes a new melody with a pipa, cue strips and copied verses as performers, listeners and backstage mending work sustain the city’s living sound.',
  'S1-E23': 'A fragrance artisan uses three differently colored paper tabs to separate original material, working inference and open questions beside a weathered manuscript and scent case.',
  'S1-E24': 'A lantern-lit supper corridor holds an elegant table, an empty place setting, a covered medical note and a city-record bundle; evening hospitality and public concern share the same frame.',
  'S1-E25': 'At a relief hall clinic, an apprentice aligns case folders, a water sample and a medicine ledger beside a raised drainage line and a functioning care route.',
  'S1-E26': 'A boat owner marks water-risk sections on a route board beside medicine bundles, rescue rope and a waiting craft, while the active wharf keeps a protected service lane open.',
  'S1-E27': 'A city clerk keeps an original order, a condensed summary and a field objection as three separate paper bundles while gate staff and residents negotiate a constrained civic crossing.',
  'S1-E28': 'At a smoke-lit granary edge, an accountant directs a human passage between stacked sacks and a damaged ledger, with controlled firelight on timber, ash and wet stone.',
  'S1-E29': 'A tavern keeper marks care-bed availability, symptom clusters and road access on a hand-drawn district sheet while relief workers maintain a dignified treatment route.',
  'S1-E30': 'In a snow-rain lantern corridor, a city clerk creates a local message handoff with rope markers, covered grain bundles and several listening residents at distinct thresholds.',
  'S1-E31': 'During heavy spring rain, a young woman compiles a missing-person list at a lane table while a damaged bridge-sluice route, muddy carts and neighbor search teams remain visible.',
  'S1-E32': 'At a rain-lit street junction, an umbrella artisan tests bamboo ribs, cloth touch-markers, a lantern and a sound cue with several residents across separate but linked corners.',
  'S1-E33': 'A young courier returns an incorrect lantern signal through floodwater, carrying a corrected route marker while three different helpers relay independent observations from bridges and relief lanes.',
  'S1-E34': 'At a public city-office review table, a clerk aligns the original order, revised summary, countersign time and gate-opening record while residents witness the accountable action.',
  'S1-E35': 'A merchant-system leader sends a true account bundle, water-level marker and evacuation route to several visible professional nodes: boat crews, porters, clinic workers and food-service hands.',
  'S1-E36': 'In a repaired spring-letter house, Shen Heng records a child’s direct willow observation beside a public correction ledger, care tools and the first calm green life returning to the lane.'
};

function episodeVisualBeat(episode) {
  const beat = EPISODE_VISUAL_BEATS[episode.episode_id];
  if (!beat) throw new Error(`Missing English visual beat for ${episode.episode_id}`);
  return beat;
}

function stageTemporalDetail(episode) {
  const source = `${episode.title || ''} ${episode.opening_state || ''} ${episode.city_evidence?.description || ''}`;
  return /夜|灯|宴|雨/.test(source)
    ? 'Blue-hour exterior depth and warm lantern pools shape the performance or festival space.'
    : 'Late-afternoon sunlight and early practical lamps shape the performance or festival space.';
}

const SHEN_COSTUMES = {
  C01: 'daily attire: matte milk-ivory crossed-collar inner layer, pale mist-blue structured middle layer, muted sage sash, fine vertical folds, a silver-blue collar jacquard and a polished celadon hairpin.',
  C02: 'work attire: fitted inner cuffs under a mist-blue woven middle layer, a protective fragrant-paper apron panel, a tool pouch, compact sash and a clean hand-working zone for scent samples.',
  C03: 'social visit attire: milk-ivory and mist-blue layers with a moon-white silk-gauze outer edge, fine floral jacquard at the collar and cuffs, a small gift case, restrained jade accent and a polished half-up coiffure.',
  C04: 'formal civic attire: aged-ivory inner silk, mist-blue pleated middle skirt, moon-white gauze outer layer, silver-blue floral jacquard and low-reflective silver thread concentrated at the collar, cuffs and hem, a sculpted formal updo and coordinated jade-and-pearl hairpins.',
  C05: 'night attire: deep blue-grey and mist-blue silk layers, a complete collar, narrow silver-blue woven edges, a compact luminous sash, protected walking movement and a dark wood hairpin responding to practical lamp light.',
  C06: 'rain attire: blue-grey dense woven rain layer over pale inner silk, protected collar, tied-back outer panels, physically wet sleeve and hem edges, rain-secured hair and a compact polished silhouette.',
  C07: 'winter attire: aged-ivory and blue-grey silk-cotton layers, a textured sash, woven warmth at the collar and sleeves, softly padded vertical folds and a modest silver-blue finishing detail.',
  C08: 'injury attire: intact ivory and blue-grey layers with a clean left-forearm bandage integrated into the sleeve structure, a fresh collar, a reduced hair ornament and right-hand fragrance-work ability readable.',
  C09: 'long-labor attire: compact ivory and mist-blue layers, natural handled folds, faint fragrance powder and paper dust, worked inner cuffs, a secure sash and hair kept orderly through a full day.',
  C10: 'story-special attire: deeper mist-blue and silver-grey structured layers within her fixed palette, a moon-white gauze outer layer, raised floral jacquard, narrow silver thread at the collar, cuffs and hem, a more sculpted coiffure and refined fragrance-artisan authority.'
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
  1: 'A well-kept professional finish: complete collar, clean layered fabric, a tidy hairstyle and one small useful personal detail.',
  2: 'A refined daily finish: tailored silk and ramie layers, visible woven pattern, a narrow embroidered edge, a polished hairpin and gentle light catching the cloth.',
  3: 'A social finish: richer dye depth, floral jacquard, a translucent outer layer, a coordinated jade or pearl detail and softly luminous material response.',
  4: 'A formal finish: sculpted layered silhouette, hand-finished embroidery, narrow silver thread, a coordinated hairpin-and-earring system and real light articulating silk, metal and skin.'
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
  'S1-PR-A01-material-clue-board': ['separated old incense chest, ash, grain dust, canal fragment and water-route tag, with clear material edges and unmarked paper dividers', 'Day'],
  'S1-PR-A02-old-case-privacy-board': ['protected old case page, oil-paper private letter, separated source envelope and route record, arranged with unmarked paper fields', 'NightWet'],
  'S1-PR-A03-supply-water-combined-report-board': ['false-bottom grain crate trace, warehouse bundle, tide-marked slip and separated sources, arranged as an unresolved material relationship', 'Day'],
  'S1-PR-A04-osmanthus-manuscript-board': ['fresh osmanthus, weathered personal manuscript, fragrance pouch and paper dividers, ordinary life beside incomplete evidence', 'Day'],
  'S1-PR-A05-lockdown-epidemic-map-board': ['abstract case-and-water-route map, medicine record, reed sample and separate historically grounded care tools, with blank label fields', 'NightWet'],
  'S1-PR-A06-spring-lantern-correction-board': ['practical lantern, tactile rope markers, small copper sound pieces, route tags and weather cover, an unmarked public-coordination kit', 'NightWet']
};

function shenNarrativeV2Spec(assetId) {
  const match = assetId.match(/^S1-NV-(E\d{2})([A-Z]?)-(.+)$/);
  if (!match) throw new Error(`Malformed Shen narrative asset id: ${assetId}`);
  const [, episodeCode, suffix, slug] = match;
  const episodeId = `S1-${episodeCode}`;
  const episode = seasonLedger.episodes.find((entry) => entry.episode_id === episodeId);
  if (!episode) throw new Error(`Missing season-ledger entry for ${assetId}`);
  const locationIds = episode.city_evidence?.location_ids || [];
  const route = routeForEpisode(episode);
  const place = locationsContext(locationIds, 'LOC-002');
  const focusObject = slug.replace(/-/g, ' ');
  return {
    tile: 'narrative',
    kind: 'seasonal-narrative',
    ar: '16:9',
    detail: `${place} ${episodeVisualBeat(episode)} Shen Heng works at a near evidence surface, carefully separating the ${focusObject} from neighboring materials with a scent paper, a small porcelain dish and deliberate hand positions. Her mist-blue, soft-celadon and aged-ivory fragrance-artisan layers carry a complete collar, floral weave and a small jade or silver personal detail appropriate to the route. ${route === 'StageFestival' ? stageTemporalDetail(episode) : ''}`,
    route,
    time: route === 'StageFestival' ? 'blue-hour-or-lantern-lit' : undefined,
    technical: false,
    authority_paths: ['story/season/season-causal-ledger.json', ...unique(locationIds.flatMap((locationId) => locationDesign(locationId).canonical_sources))]
  };
}

function shenTaskSpecs(assetId) {
  if (assetId.startsWith('ID-001')) return [{ tile: 'front-neutral', kind: 'identity', ar: '3:4', detail: 'front-facing neutral head-and-upper-torso identity render, level head, all facial features unobstructed and hands resting below the crop.', technical: true }];
  if (assetId.startsWith('ID-002')) return ['front', 'left-three-quarter', 'left-profile', 'right-three-quarter', 'right-profile'].map((tile) => ({ tile, kind: 'identity-angle', ar: '3:4', detail: `${tile} head view, same neutral expression, same makeup and same clean collar, individual task only.`, technical: true }));
  if (assetId.startsWith('ID-003')) return ['front-full-body', 'left-profile-full-body', 'back-full-body'].map((tile) => ({ tile, kind: 'turnaround', ar: '2:3', detail: `${tile} full body from head to footwear, neutral stance, consistent garment construction, individual task only.`, technical: true }));
  if (assetId.startsWith('ID-004')) return ['face-skin', 'hairline-and-strands', 'right-hand-professional-trace', 'collar-and-textile'].map((tile) => ({ tile, kind: 'detail', ar: '1:1', detail: `single macro continuity detail of ${tile} in a clean unmarked frame.`, technical: true }));
  for (const [prefix, tiles] of Object.entries(SHEN_SHEETS)) {
    if (assetId.startsWith(prefix)) return tiles.map((tile) => ({ tile, kind: prefix === 'MK-001' ? 'makeup-state' : prefix === 'HR-001' ? 'hair-state' : 'expression', ar: '3:4', detail: `${prefix === 'MK-001' ? 'same face, light historical makeup state' : prefix === 'HR-001' ? 'same face, same light makeup, hairstyle state' : 'single restrained facial expression'}: ${tile}. One independently framed continuity render.`, technical: true }));
  }
  for (const [prefix, tiles] of Object.entries(SHEN_ACTIONS)) {
    if (assetId.startsWith(prefix)) return tiles.map((tile) => ({ tile, kind: prefix === 'CAM-001' ? 'camera-framing' : 'pose-or-motion', ar: prefix === 'CAM-001' ? '3:4' : '2:3', detail: `${prefix === 'CAM-001' ? 'single camera-framing continuity view' : 'single natural body action or pose'}: ${tile}. One independently framed continuity render.`, technical: true }));
  }
  for (const [prefix, tiles] of Object.entries(SHEN_PROP_TILES)) {
    if (assetId.startsWith(prefix)) return tiles.map((tile) => ({ tile, kind: 'personal-prop', ar: '3:2', detail: `single object material study of Shen Heng's ${tile}; object-only frame on a clean work surface with blank, unmarked supporting paper where needed.`, technical: true }));
  }
  const costume = Object.entries(SHEN_COSTUMES).find(([prefix]) => assetId.startsWith(prefix));
  if (costume) return [{ tile: 'full-look', kind: 'costume', ar: '2:3', detail: `front-facing full-body historical wardrobe presentation. ${costume[1]} Natural poised stance, complete silhouette and clean construction visibility.`, technical: false, raw: true }];
  const appearanceKey = Object.keys(SHEN_APPEARANCE).find((key) => assetId.startsWith(key));
  const appearance = appearanceKey ? SHEN_APPEARANCE[appearanceKey] : null;
  if (appearance) return [{ tile: 'appearance', kind: 'seasonal-appearance', ar: '2:3', detail: `${appearance[0]}; ${appearance[1]}. Front three-quarter full-body continuity render.`, route: appearance[2], technical: false }];
  const evidenceKey = Object.keys(SHEN_EVIDENCE).find((key) => assetId.startsWith(key));
  const evidence = evidenceKey ? SHEN_EVIDENCE[evidenceKey] : null;
  if (evidence) return [{ tile: 'evidence', kind: 'seasonal-evidence', ar: '3:2', detail: `Top-down practical evidence arrangement: ${evidence[0]}. An object-focused work-surface composition with ample clear margin.`, route: evidence[1], technical: false }];
  if (assetId.startsWith('NV-001')) return [{ tile: 'narrative', kind: 'narrative-still', ar: '2:3', detail: 'spring official character portrait at a garden stone rail, holding an unmarked fragrance slip in an intimate cinematic character-still composition.', route: 'Day', technical: false }];
  if (assetId.startsWith('NV-002')) return [{ tile: 'narrative', kind: 'narrative-still', ar: '16:9', detail: 'fragrance-shop work still: bamboo tweezers, blank fragrance slip, window light, ceramic jars and scale, one clear decision moment.', route: 'Day', technical: false }];
  if (assetId.startsWith('NV-003')) return [{ tile: 'narrative', kind: 'narrative-still', ar: '16:9', detail: 'waterside daylight return, natural walking rhythm, fragrance pouch, bridge, willow, shopfront and water-depth perspective.', route: 'Day', technical: false }];
  if (assetId.startsWith('NV-004')) return [{ tile: 'narrative', kind: 'narrative-still', ar: '2:3', detail: 'rain-night clue still, a side-held oil-paper umbrella, warm local lamp against cool rain and physically motivated reflected highlights.', route: 'NightWet', technical: false }];
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
      time: task.time,
      technical,
      raw: task.raw ?? settings.raw,
      glamour_level: glamourLevel,
      ar: task.ar,
      stylize: settings.stylize,
      chaos: settings.chaos,
      positive: `${shenBase} ${costumeConstruction(glamourLevel, 'woman', shen.facts.occupation)} ${SHEN_GLAMOUR_FINISH[glamourLevel]} ${task.detail} ${routeText(route, technical)}`,
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
  const primaryId = episode.profession_action?.character_id || episode.episode_choice?.actor || '';
  const route = routeForEpisode(episode);
  const primaryLook = primaryId ? sceneLookForCharacter(primaryId) : '';
  const locationIds = episode.city_evidence?.location_ids || [];
  const place = locationsContext(locationIds, 'LOC-001');
  addRecord({
    prompt_id: `MJ-V2-${episode.episode_id}-PREMISE-001`,
    target_key: `EPISODE:${episode.episode_id}:PREMISE-001`,
    family: 'season-episode',
    asset_lane: 'episode-premise-study',
    target: { stable_id: episode.episode_id, asset_id: 'PREMISE-001' },
    authority_refs: [sourceRef('story/season/season-causal-ledger.json', 'season-causal-ledger'), ...unique(locationIds.flatMap((locationId) => locationDesign(locationId).canonical_sources)).map((relativePath) => sourceRef(relativePath, 'episode-location-visual-authority'))],
    facts_snapshot: { episode_id: episode.episode_id, title: episode.title, opening_state: episode.opening_state, city_evidence: episode.city_evidence?.description, profession_action: episode.profession_action?.action, episode_choice: episode.episode_choice?.action, location_ids: episode.city_evidence?.location_ids || [] },
    route,
    glamour_level: route === 'StageFestival' ? 4 : 3,
    ar: '16:9',
    stylize: route === 'StageFestival' ? 230 : 180,
    chaos: 3,
    time: route === 'StageFestival' ? 'blue-hour-or-lantern-lit' : undefined,
    positive: `A cinematic episode-premise image. ${place} ${sentence(primaryLook)} ${episodeVisualBeat(episode)} ${route === 'StageFestival' ? stageTemporalDetail(episode) : ''} A clear foreground task, active middle ground and receding inhabited architecture establish an episodic frame. ${routeText(route)}`,
    execution_status: 'BLOCKED_UNTIL_EPISODE_GATE',
    acceptance_checks: [
      'Uses only the ledger opening state, professional action and evidence for this episode.',
      'Does not claim a final scene or invent an unbound screenplay event.',
      'Requires Episode Gate before delivery or image generation for production use.'
    ]
  });
}

const storyboard = readJson('production/episodes/S1-E01/storyboard.json');

function storyboardFrame(shot) {
  const text = `${shot.camera?.scale || ''} ${shot.camera?.angle || ''} ${shot.camera?.focal_length || ''}`;
  if (/特写|大特/.test(text)) return 'an intimate close framing with the face, hands and one evidence surface clearly resolved';
  if (/近景/.test(text)) return 'a chest-up to waist-up dramatic framing with one foreground object';
  if (/中景/.test(text)) return 'a natural waist-to-mid-thigh framing with active foreground and middle ground';
  if (/全景|远景/.test(text)) return 'a medium-wide environmental framing with a legible foreground, working middle ground and receding city depth';
  return 'a natural cinematic environmental framing with a readable foreground task and active city depth';
}

function storyboardActionDirection(shot, route) {
  const text = `${shot.purpose || ''} ${shot.blocking?.action_path || ''} ${shot.blocking?.movement || ''} ${shot.blocking?.prop_handling || ''}`;
  const object = /匣|盒|香丸|香灰|香/.test(text)
    ? 'a worn fragrance case, a small ash sample and a separated examination tool'
    : /账|纸|信|券|册|签|竹片/.test(text)
      ? 'a folded ledger or paper record with a small physical marker'
      : /碗|食|茶|酒/.test(text)
        ? 'a bowl, tea vessel or serving tray'
        : /门|闩|阈|门槛/.test(text)
          ? 'a threshold, door bar or handoff at the entry'
          : /船|水|绳|桥/.test(text)
            ? 'a rope rail, water-side parcel or route marker'
            : 'one carefully handled working object';
  const action = /柜台|后仓|桌|案/.test(text)
    ? 'The primary performer crosses from a public work surface toward a more private rear task, keeping the object visible between the two zones.'
    : /门|阈|门槛/.test(text)
      ? 'The primary performer pauses at the threshold while a second figure holds the interior side of the frame, creating a clear line of attention and access.'
      : /递|交|接/.test(text)
        ? 'A precise handoff carries the object across a measured distance, with both sets of hands and the receiving surface clearly visible.'
        : 'A decisive hand movement, a held gaze and one nearby secondary figure make the immediate pressure readable.';
  const light = route === 'StageFestival'
    ? 'Warm practical lantern and candle light catches silk, timber and the object while blue-hour depth remains visible beyond the performance space.'
    : route === 'NightWet'
      ? 'A local lantern or oil lamp creates a warm pool across the object and faces, balanced by cool rain-softened exterior depth.'
      : 'Window-filtered daylight and pale reflected fill articulate skin, woven fabric, paper and wood.';
  return `The foreground task centers ${object}. ${action} ${light}`;
}

for (const scene of storyboard.scenes) {
  for (const shot of scene.shots) {
    const primaryId = shot.blocking?.primary_actor || '';
    const primaryLook = primaryId ? sceneLookForCharacter(primaryId) : '';
    const locationIds = scene.scene_binding?.location_ids || [];
    const place = locationsContext(locationIds, 'LOC-001');
    const route = routeForStoryboard(scene, shot);
    addRecord({
      prompt_id: `MJ-V2-${shot.shot_id}`,
      target_key: `SHOT:${shot.shot_id}`,
      family: 'episode-shot',
      asset_lane: 'draft-shot-visualization',
      target: { stable_id: shot.shot_id, scene_id: scene.scene_id, asset_id: shot.shot_id },
      authority_refs: [sourceRef('production/episodes/S1-E01/storyboard.json', 'episode-storyboard'), ...unique(locationIds.flatMap((locationId) => locationDesign(locationId).canonical_sources)).map((relativePath) => sourceRef(relativePath, 'storyboard-location-visual-authority'))],
      facts_snapshot: { scene_id: scene.scene_id, shot_id: shot.shot_id, scene_status: scene.status, purpose: shot.purpose, primary_actor: shot.blocking?.primary_actor || null, action_path: shot.blocking?.action_path || shot.blocking?.movement || '', prop_handling: shot.blocking?.prop_handling || '', camera: shot.camera, light: shot.light, temporal: shot.temporal },
      route,
      glamour_level: route === 'StageFestival' ? 3 : 2,
      ar: '16:9',
      stylize: route === 'StageFestival' ? 190 : 140,
      chaos: 3,
      time: route === 'StageFestival' ? 'blue-hour-or-lantern-lit' : undefined,
      positive: `A precise cinematic draft shot at ${place} ${primaryLook ? `${sentence(primaryLook)} ` : ''}${sentence(storyboardFrame(shot))} ${storyboardActionDirection(shot, route)} ${routeText(route)}`,
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
  ['DAY-CANAL', 'Day', '16:9', 'a dense Linan canal-market day: narrow waterway, loaded working boats, damp timber wharves, stacked trade parcels, food stalls, pedestrians and layered Song roofs; the water and labor routes carry a busy working-waterfront rhythm.', 'SCN-STREET-LEVEL-WATER-MARKET'],
  ['DAY-GOLDEN-TEA', 'Day', '16:9', 'a late-afternoon Linan tea-table social moment in a working market courtyard: one elegant believable young adult Chinese woman in historically grounded layered ivory and soft-celadon clothing, seated naturally with a small tea vessel, warm side-back sunlight catching real skin, silk and glazed ceramic, nearby people and market activity softly present behind her in an environmental mid-shot.'],
  ['DAY-TEXTILE-YARD', 'Day', '16:9', 'a busy Linan laundry and textile-work yard: several Chinese workers washing, lifting, folding and carrying long pale silk and woven cloth across wooden racks, low warm sunlight passing through moving fabric to reveal translucent fibers, wet hems, baskets, lacquered chests and active work routes; lived-in craft labor with a graceful material rhythm.'],
  ['DAY-FRAGRANCE-SHOP', 'Day', '16:9', 'the interior and threshold of a working Linan fragrance shop: incense chest, scale, jars, paper, racks and a clear street-facing counter, with ordinary trade and practical access.'],
  ['NIGHT-WET-LANE', 'NightWet', '16:9', 'a rain-wet Linan lane with occupied eaves, local lantern pools, oilcloth covers, people continuing practical work and physical reflections on stone; warm practical illumination and rain-softened blue-grey depth.'],
  ['NIGHT-LANTERN-CORRIDOR', 'NightWet', '16:9', 'an evening Linan covered corridor used for a small public gathering: dark cinnabar timber columns, softly glowing handmade paper lanterns and candle stands receding toward a real vanishing point, ivory curtains moving gently at the edges, warm light on silk and wood balanced by quiet blue-grey exterior depth, attendants and guests using the corridor naturally; refined urban hospitality scale.'],
  ['STAGE-BACKSTAGE', 'StageFestival', '16:9', 'a Chun Tai performance-house backstage: mending sleeves, cue passage, hairpin repair, small lamps and visible labor behind a refined but historically plausible ornament system.'],
  ['FESTIVAL-PUBLIC-ROUTE', 'StageFestival', '16:9', 'a public osmanthus festival route in Linan: layered grounded textiles, blossom parcels, warm lamps, market service, safe circulation and an urban merchant celebration scale.'],
  ['DAY-WATER-CAPITAL-PANORAMA', 'Day', '16:9', 'a broad late-afternoon panorama of Linan as a prosperous water-capital: rivers and canal mouths, bridges, boats, layered tiled roofs, market awnings, timber wharves, distant hills and a clear network of pedestrians and goods moving through humid golden air.'],
  ['DAY-WIND-GAUZE-EMOTION', 'Day', '2:3', 'an emotionally poised live-action Chinese historical-romance character moment beside a city corridor or lakeside rail: complete layered ivory, celadon and old-rose crossed-collar silk, a fine translucent outer layer responding to a light physical breeze, a few backlit hair strands, subtle pearl and gilt details, real sunlight shaping skin, textile and water with the inhabited Linan environment still readable.']
];

for (const [id, route, ar, subject, compositionProfileId] of CALIBRATIONS) {
  const composition = compositionProfileId ? sceneCompositionProfile(compositionProfileId) : null;
  addRecord({
    prompt_id: `MJ-V2-CAL-${id}`,
    target_key: `CALIBRATION:${id}`,
    family: 'style-calibration',
    asset_lane: 'style-calibration',
    target: { stable_id: 'VIS-LW-V2', asset_id: id },
    authority_refs: [sourceRef('production/style/v2-urban-splendor-song-style-package.md', 'v2-style-authority'), sourceRef('production/style/v2-visual-qa.md', 'v2-qa')],
    facts_snapshot: { calibration_id: id, route: ROUTE_KEY[route], composition_profile_id: compositionProfileId || null },
    route,
    glamour_level: route === 'StageFestival' ? 5 : 3,
    ar,
    stylize: route === 'StageFestival' ? 250 : 180,
    chaos: 5,
    positive: `${subject}${composition ? ` ${composition.prompt_block}` : ''} ${routeText(route)}`,
    execution_status: 'READY_FOR_V2_STYLE_CALIBRATION',
    acceptance_checks: [
      'Tests the route rather than an individual character identity.',
      ...(composition?.acceptance_checks || []),
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
    baseline_not_emitted_parameters: ['--draft'],
    prohibited_parameters: ['--oref', '--ow', '--cref', '--cw', '--q', '--quality', 'multi-prompt ::']
  },
  source_manifest: [
    sourceRef('production/style/v2-urban-splendor-song-style-package.md', 'v2-style-authority'),
    sourceRef('production/style/v2-scene-composition-standard.md', 'v2-scene-composition-standard'),
    sourceRef('production/style/v2-costume-construction-standard.md', 'v2-costume-construction-authority'),
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
    noncentral_character_visual_anchor_candidates: roster.named_characters.filter((character) => !/^L[123]$/.test(character.tier)).length,
    noncentral_character_occupation_states: catalog.filter((record) => record.family === 'character' && /supporting-(hero|occupation)-state/.test(record.asset_lane)).length,
    central_character_hero_key_art: roster.named_characters.filter((character) => /^L[123]$/.test(character.tier)).length,
    central_character_motion_studies: catalog.filter((record) => record.family === 'character' && record.asset_lane === 'narrative-motion-study').length,
    canonical_location_masters: LOCATIONS.length,
    canonical_location_season_states: LOCATIONS.length * 6,
    water_city_establishing_views: catalog.filter((record) => record.family === 'city-establishing').length,
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
    'No direct prompt leaks the internal VIS-LW-V2 contract label or uses Omni Reference, Character Reference, --oref, --q, --quality, --draft or multi-prompt syntax; Raw and --no are lane-specific rather than global requirements.',
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

const centralMasterRecords = catalog
  .filter((record) => record.family === 'character' && /^CHR-L[123]-/.test(record.target?.stable_id || '') && ['ID-001', 'HERO-001'].includes(record.target?.asset_id))
  .sort((left, right) => {
    const characterOrder = left.target.stable_id.localeCompare(right.target.stable_id, 'en');
    if (characterOrder !== 0) return characterOrder;
    return (left.target.asset_id === 'ID-001' ? 0 : 1) - (right.target.asset_id === 'ID-001' ? 0 : 1);
  });
const centralMasterLines = [
  '# 核心人物母版｜Midjourney 8.2 先行提示词',
  '',
  '> 此文件是当前唯一的人物首轮入口：先逐人运行 `ID-001`，由用户选择项目生成的核心母版图；`HERO-001` 必须等该角色的已选母版图回传并记录后再执行。',
  '',
  '## 第一阶段：只生成 ID-001',
  '',
  '每次只运行一位角色的 `ID-001`。它锁定年龄、脸部结构、清透淡妆、发丝、完整领口与职业小饰物；不使用外部图片、`--no` 或拼板任务。选定项目生成候选后，记录本地路径、SHA-256 和选择理由。',
  '',
  '## 第二阶段：等待已选母版',
  '',
  '把选中的项目生成图交回后，再在 MJ 网页端把该图作为 Image Prompt，并运行对应 `HERO-001` 以及后续三视图、表情、妆发、服装、动作、道具和剧情资产。下面的 HERO 条目是预写文本，当前状态为阻塞，不能替代已选的身份图。',
  ''
];
const centralIdentityRecords = centralMasterRecords.filter((record) => record.target.asset_id === 'ID-001');
const centralHeroRecords = centralMasterRecords.filter((record) => record.target.asset_id === 'HERO-001');
for (const record of centralIdentityRecords) {
  centralMasterLines.push(`## ${record.prompt_id}`, '', `- 角色：${record.target.name} · 资产：\`${record.target.asset_id}\` · 状态：\`${record.execution_status}\``, '', '```text', record.prompt.mj_text, '```', '');
}
centralMasterLines.push('## 已锁脸后：HERO-001', '', '以下文本保留为第二阶段，不应在未选定对应 `ID-001` 项目母版图时直接运行。', '');
for (const record of centralHeroRecords) {
  centralMasterLines.push(`## ${record.prompt_id}`, '', `- 角色：${record.target.name} · 资产：\`${record.target.asset_id}\` · 状态：\`${record.execution_status}\``, '', '```text', record.prompt.mj_text, '```', '');
}
write('production/midjourney/v2/core-master-reference.md', centralMasterLines.join('\n'));

const summaryLines = [
  '# 《临安春信》V2 Midjourney 8.2 全量资产提示词',
  '',
  `> Catalog: \`${mainCatalog.catalog_id}\` · ${catalog.length} resolved prompt records · generated ${GENERATED_ON}.`,
  '',
  'This is the V2-only source of active Midjourney prompts. It contains complete V8.2 parameter strings for every declared target in the coverage contract; it does not treat an unbound reference image or a range template as a production prompt.',
  '',
  'Every narrative prompt uses the active cinematic historical-romance visual grammar: motivated daylight or practical lantern light, physical silk/paper/wood/water response, readable working depth and controlled optical softness. Location, city-establishing and relevant calibration records also carry a resolved scene-composition profile that preserves Canon geography. Technical continuity tasks deliberately retain clean neutral presentation.',
  '',
  '## Start here: central master-reference selection',
  '',
  'Run only the twelve `ID-001` prompts in [core-master-reference](core-master-reference.md) first. Each is a text-only, front-facing master-reference selection task. The twelve `HERO-001` prompts are deliberately blocked until the user returns an approved project-generated master render; then attach that approved image manually in the Midjourney web UI and retain the supplied hero text.',
  '',
  '## Family counts',
  '',
  ...Object.entries(familyCounts).map(([family, count]) => `- ${family}: ${count}`),
  '',
  '## Copyable prompt files',
  '',
  '- [core-master-reference](core-master-reference.md) — current first-pass character workflow',
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
