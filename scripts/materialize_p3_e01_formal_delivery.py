from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EPISODE_ID = "S1-E01"
EPISODE_DIR = ROOT / "production/episodes/S1-E01"
CARD_PATH = EPISODE_DIR / "episode-production-cards.json"
FORMAL_PATH = EPISODE_DIR / "episode-formal-delivery.json"
SCRIPT_PATH = EPISODE_DIR / "script-scenes.json"
STORYBOARD_PATH = EPISODE_DIR / "storyboard.json"
CONTINUITY_PATH = EPISODE_DIR / "continuity-ledger.json"

C = {
    "沈蘅": "CHR-L1-01",
    "陆清和": "CHR-L2-01",
    "林阿沅": "CHR-L2-02",
    "顾行舟": "CHR-L1-05",
    "胡六婆": "CHR-B-007",
    "孙锁叔": "CHR-B-006",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def line(speaker: str, text: str, intent: str, pace: str = "中慢") -> dict:
    return {
        "speaker_id": C[speaker],
        "speaker": speaker,
        "text": text,
        "intent": intent,
        "pace": pace,
    }


def beat(action: str, subtext: str, dialogue: list[dict]) -> dict:
    return {"action": action, "subtext": subtext, "dialogue": dialogue}


SCENES = {
    "S1-E01-M01": {
        "scene_title": "雨后开市，旧匣不肯安静",
        "location_ids": ["LOC-001", "LOC-002"],
        "scene_spec_ref": "canon/city/03-he-ming-lane-and-shen-shop.md",
        "participants": [C["沈蘅"], C["陆清和"]],
        "beats": [
            beat("沈蘅擦去旧匣上的雨水；陆清和把香铺前堂的湿帕叠成四角。", "两个人都在做开门的事，谁也不先碰亡父留下的名字。", [
                line("陆清和", "先把门槛擦干。客人要进来。", "把日常放在调查之前"),
                line("沈蘅", "匣子里进了水。铜扣却是干的。", "把异常藏进生活观察", "慢"),
            ]),
            beat("沈蘅打开旧匣，香丸与内壁黏住；陆清和伸手要拿走。", "陆清和害怕的不是香丸，而是女儿又把死者带回家。", [
                line("陆清和", "这东西，烧了。", "下结论以终止风险", "低"),
                line("沈蘅", "你还没看它是什么。", "要求保留核验权"),
                line("陆清和", "我看过你爹留下的东西。看得够多了。", "把十三年前的代价压回现在", "低"),
            ]),
        ],
        "choice": "沈蘅不烧香丸，先把它连同旧匣移到后仓并记下出入。",
        "exit_state": "母女从共同开铺转为各自守着一件东西；后仓第一次成为需要记录的空间。",
        "blocking": {"zones": ["前堂柜台", "后仓门槛"], "movement": "沈蘅由柜台到后仓；陆清和停在门槛内侧。", "contact": "无新触碰；陆清和伸手取匣后收回。", "prop_handling": "旧匣由沈蘅双手托住，香丸不脱离匣底。", "axis": "柜台—后仓门槛轴"},
        "light_sources": ["雨后檐下天光", "前堂一盏未完全拨亮的油灯"],
    },
    "S1-E01-M02": {
        "scene_title": "铜扣内侧的新胶痕",
        "location_ids": ["LOC-002"],
        "scene_spec_ref": "canon/city/03-he-ming-lane-and-shen-shop.md",
        "participants": [C["沈蘅"], C["陆清和"], C["孙锁叔"]],
        "beats": [
            beat("陆清和拿竹片刮铜扣内侧，动作比平日更整齐；孙锁叔只看锁，不碰香丸。", "她先确认门和钱匣，再允许自己听女儿说完。", [
                line("孙锁叔", "铜扣换过。换扣的人，没动里面。", "限定自己的证词范围"),
                line("沈蘅", "什么时候换的？", "把时间钉进物件", "慢"),
                line("孙锁叔", "我只记得雨前。年月，不敢替它说。", "拒绝把模糊记忆说满"),
            ]),
            beat("沈蘅用镊尖挑出半透明胶丝；陆清和把后仓门再合上一寸。", "胶痕让‘亡父遗物’变成‘近半年有人进过匣子’。", [
                line("沈蘅", "胶还软过。不是十三年前。", "提出可复核的局部事实"),
                line("陆清和", "你要查，先查进门的人。别先查死人。", "把调查对象拉回活人", "低"),
                line("沈蘅", "我只查东西。", "保护自己不被情绪带走"),
                line("陆清和", "东西最后，都要落到活人身上。", "提醒代价", "低"),
            ]),
        ],
        "choice": "沈蘅把胶痕留在纸上，不把孙锁叔的模糊时间写成确定日期。",
        "exit_state": "胶痕成为第一条当代证据；陆清和将后仓门纳入日常锁闭。",
        "blocking": {"zones": ["后仓案桌", "门闩"], "movement": "孙锁叔靠近案桌后退回门边；陆清和负责门闩。", "contact": "沈蘅与孙锁叔不碰手；陆清和只碰门闩。", "prop_handling": "胶丝落在白纸中央，竹片与镊子分置两侧。", "axis": "案桌—门闩轴"},
        "light_sources": ["后仓窄窗散射天光", "案桌小油灯"],
    },
    "S1-E01-M03": {
        "scene_title": "阿沅把闲话带进门",
        "location_ids": ["LOC-001", "LOC-002"],
        "scene_spec_ref": "canon/city/03-he-ming-lane-and-shen-shop.md",
        "participants": [C["林阿沅"], C["沈蘅"], C["陆清和"]],
        "beats": [
            beat("林阿沅端来一篮刚收的碗，先把碗口朝同一方向，再看后仓门。", "她想帮忙，却怕自己又被当作说得太快。", [
                line("林阿沅", "我不是来偷听的。我是来还碗——顺便看一眼。", "用轻话试探是否被接纳"),
                line("陆清和", "看一眼也要说清楚，看见什么。", "给她进入记录的门槛", "低"),
                line("林阿沅", "我看见门最近总是早关一刻。人没变，门先变了。", "提供生活观察"),
            ]),
            beat("沈蘅把纸推到阿沅面前，问她近半年谁来过后仓。", "沈蘅第一次把市井观察当作可用信道，而不是热闹。", [
                line("沈蘅", "别猜是谁。先写你亲眼见过的。", "设定证据边界"),
                line("林阿沅", "那我先写‘亲见’。不知道的，留空。", "接受方法并承担记录责任"),
            ]),
        ],
        "choice": "林阿沅主动回访街坊与修匣者，不把传闻直接递成结论。",
        "exit_state": "阿沅获得临时记录权；沈蘅的调查开始离开香铺内部。",
        "blocking": {"zones": ["前堂碗架", "后仓门外"], "movement": "阿沅从门口到碗架，再停在后仓门外；沈蘅不让路也不挡路。", "contact": "沈蘅递纸，不触碰阿沅手。", "prop_handling": "油纸记录夹在碗篮下，不遮住碗数。", "axis": "碗架—后仓门外轴"},
        "light_sources": ["巷口雨后天光", "前堂反射光"],
    },
    "S1-E01-M04": {
        "scene_title": "停云酒肆的两句药价",
        "location_ids": ["LOC-009"],
        "scene_spec_ref": "canon/city/05-west-lake-and-xiling-circle.md",
        "participants": [C["顾行舟"], C["沈蘅"]],
        "beats": [
            beat("顾行舟先把客人桌边的短刀推回桌内，再把两张酒账分开。", "他的关心先表现为减少危险；他不解释自己为什么注意到。", [
                line("顾行舟", "两条路来的客人，都说白芷贵了。", "交付可核验的第二信道", "低"),
                line("沈蘅", "你信他们？", "测试信息来源", "慢"),
                line("顾行舟", "我信他们都说过。信不信原因，得再问。", "区分听见与判断"),
            ]),
            beat("沈蘅看向他手边的酒账；顾行舟把一张空白纸放到她够得到的位置。", "他提供工具而不是答案。", [
                line("顾行舟", "我只把路告诉你。走哪条，你自己定。", "明确不代替选择"),
                line("沈蘅", "那就别替我把门关上。", "建立边界", "低"),
            ]),
        ],
        "choice": "顾行舟提供北客药价信息，不替沈蘅决定是否继续查。",
        "exit_state": "两人建立‘提供事实但不代选’的初始边界；白芷价格进入并列疑报。",
        "blocking": {"zones": ["酒肆柜台", "临窗桌"], "movement": "顾行舟始终可见门口；沈蘅站在柜台外侧，不进入他的安全位。", "contact": "无触碰；顾行舟只移动刀与纸。", "prop_handling": "酒账与空白纸平行放置，刀尖朝内。", "axis": "柜台—门口轴"},
        "light_sources": ["酒肆门口阴天光", "柜台暖油灯"],
    },
    "S1-E01-M05": {
        "scene_title": "切样、留灰、标未核",
        "location_ids": ["LOC-002"],
        "scene_spec_ref": "canon/city/03-he-ming-lane-and-shen-shop.md",
        "participants": [C["沈蘅"], C["陆清和"]],
        "beats": [
            beat("沈蘅把香丸切成两半，一半放入灰纸，一半留在匣底；陆清和站在炉边不看她。", "物件被分开，母女却都不愿先承认这意味着什么。", [
                line("沈蘅", "灰里有新黏合物，矿粉也不对。", "报告局部事实"),
                line("陆清和", "不对到什么程度？", "逼她把专业话说清楚", "低"),
                line("沈蘅", "只够写‘不相容’，还不够写‘是谁’。", "主动限制结论", "慢"),
            ]),
            beat("她在纸角写下‘未核’，把笔停在最后一横。", "沈蘅第一次用职业规则保护自己不去证明父亲。", [
                line("陆清和", "这两个字，能护住谁？", "追问记录的现实后果"),
                line("沈蘅", "至少不让它先伤到别人。", "把谨慎变成选择"),
            ]),
        ],
        "choice": "沈蘅保留切样与灰样，并把判断标为‘未核’。",
        "exit_state": "香丸从一件遗物变成两份可追踪样本；‘未核’成为本集的工作规则。",
        "blocking": {"zones": ["案桌", "炉边"], "movement": "沈蘅围案桌半圈；陆清和保持炉边位置，只用听觉参与。", "contact": "无人物触碰。", "prop_handling": "切样、灰样、原匣三点分置，纸签朝外。", "axis": "案桌—炉边轴"},
        "light_sources": ["案桌油灯", "炉火低光"],
    },
    "S1-E01-M06": {
        "scene_title": "两条生活消息，不合成一个答案",
        "location_ids": ["LOC-002"],
        "scene_spec_ref": "canon/city/03-he-ming-lane-and-shen-shop.md",
        "participants": [C["陆清和"], C["沈蘅"], C["林阿沅"], C["顾行舟"]],
        "beats": [
            beat("陆清和把阿沅的饭量纸与顾行舟的酒账并排压在账本下。", "她把家庭账本变成临时的城市账本，却拒绝替它命名。", [
                line("陆清和", "一家的饭少了，是家事。两路客都说药贵，还是不是？", "让信息保持分栏"),
                line("沈蘅", "现在只够写两条疑报。", "不合并未核信息", "慢"),
                line("林阿沅", "那我再去问三家。问到他们自己愿意说。", "主动承担回访"),
            ]),
            beat("顾行舟站在门边，听见‘疑报’后没有靠近案桌。", "他理解她的规则，也理解自己被留在门边。", [
                line("顾行舟", "两条路的客人，明早还会走。要问，得趁今晚。", "提出时间压力"),
                line("沈蘅", "先问，不先信。", "给行动定边界"),
            ]),
        ],
        "choice": "四人把生活观察并列为疑报，不升级为预言或疫讯。",
        "exit_state": "调查获得横向核验的方向；时限从‘以后’变成‘今晚与明早’。",
        "blocking": {"zones": ["账桌", "门边", "炉边"], "movement": "陆清和在桌与炉之间；顾行舟留门边；阿沅靠近纸但不拿走。", "contact": "无触碰；纸张由陆清和推动。", "prop_handling": "饭量纸与酒账不重叠，中央留‘疑报’空位。", "axis": "账桌—门边轴"},
        "light_sources": ["桌面油灯", "门外雨后冷光"],
    },
    "S1-E01-M07": {
        "scene_title": "碗里的空处",
        "location_ids": ["LOC-001"],
        "scene_spec_ref": "canon/city/03-he-ming-lane-and-shen-shop.md",
        "participants": [C["林阿沅"], C["胡六婆"]],
        "beats": [
            beat("阿沅给熟客添汤，发现张家连续四日只要半碗；她没有马上问病。", "她第一次忍住把观察说成答案。", [
                line("林阿沅", "今日还是半碗？", "用生活问题替代诊断", "快后放慢"),
                line("胡六婆", "半碗也能暖肚子。你别把碗看得比人还懂。", "保护尊严并回避解释", "低"),
                line("林阿沅", "我不是看碗。我是怕有人没来。", "承认真正担心的是失联"),
            ]),
            beat("她把‘四日半碗、未问病因’写在油纸背面，抬头看门口。", "生活记录第一次产生了等待与责任。", [
                line("林阿沅", "我先去问下一家。问到你愿意说为止。", "把观察变成回访行动"),
            ]),
        ],
        "choice": "阿沅记录饭量和赊账变化，并把未确认部分留空。",
        "exit_state": "阿沅从‘会看见’进入‘会回访’，生活基线不再只是闲话。",
        "blocking": {"zones": ["馄饨摊案板", "街口座位"], "movement": "阿沅边添汤边记，最后从摊位走向街口。", "contact": "只与碗、勺、油纸接触。", "prop_handling": "油纸折角标记待回访，不写诊断词。", "axis": "案板—街口轴"},
        "light_sources": ["街巷雨后散射光", "食担小灯"],
    },
    "S1-E01-M08": {
        "scene_title": "灯可以留，路不能替人走",
        "location_ids": ["LOC-009"],
        "scene_spec_ref": "canon/city/05-west-lake-and-xiling-circle.md",
        "participants": [C["顾行舟"], C["沈蘅"]],
        "beats": [
            beat("顾行舟把防风灯挂到门钩上，先试灯钩，再把路线纸放下。", "照顾先于表白；他差一点把安全安排变成命令。", [
                line("顾行舟", "灯借你。明早还我。", "用借口隐藏关心", "低"),
                line("沈蘅", "我没说要走这条路。", "指出被安排的感觉", "低"),
                line("顾行舟", "所以我把路放这儿，没把你带过去。", "退回选择权"),
            ]),
            beat("沈蘅把灯往里挪一寸，仍不取下；顾行舟退到门侧。", "第一次接受善意，同时保留边界。", [
                line("沈蘅", "灯我留着。决定我自己做。", "明确接受与拒绝的边界", "慢"),
                line("顾行舟", "好。", "不追加解释，练习站开"),
            ]),
        ],
        "choice": "顾行舟只提供灯与路线，不替沈蘅决定；沈蘅接受灯但不接受安排。",
        "exit_state": "关系靠近一寸，选择权也被明确写回各自手中。",
        "blocking": {"zones": ["酒肆后门", "灯钩", "门侧阴影"], "movement": "顾行舟挂灯后退到门侧；沈蘅靠近灯钩但不跨出门。", "contact": "无人物触碰；灯钩由顾行舟操作。", "prop_handling": "防风灯固定后不得在本集再换位置。", "axis": "灯钩—门侧轴"},
        "light_sources": ["防风灯（主光源）", "酒肆后门冷雨光"],
    },
    "S1-E01-M09": {
        "scene_title": "不是父亲留下的预言",
        "location_ids": ["LOC-002"],
        "scene_spec_ref": "canon/city/03-he-ming-lane-and-shen-shop.md",
        "participants": [C["沈蘅"], C["陆清和"]],
        "beats": [
            beat("沈蘅把十三年前旧灰与新胶痕放在同一张纸上，先看物再看母亲。", "她不愿承认自己最想要的是父亲仍然正确。", [
                line("沈蘅", "它不是十三年前留下来的。", "用职业事实切断预言解释", "慢"),
                line("陆清和", "那你高兴了吗？", "刺中女儿的私愿", "低"),
                line("沈蘅", "我只知道有人刚把它放进去。", "拒绝把事实变成情绪答案"),
            ]),
            beat("陆清和把旧匣盖回，却没有扣上铜扣。", "盖住不等于结束；母亲开始允许问题留在家里。", [
                line("陆清和", "你爹若错过，怎么办？", "提前提出父亲不完美的可能"),
                line("沈蘅", "那就把错的地方也记下来。", "第一次说出与父亲不同的原则"),
            ]),
        ],
        "choice": "沈蘅把香丸改写为当代疑报，不把亡父当作答案来源。",
        "exit_state": "核心问题从‘父亲预言’改为‘谁投递、为何让她发现’。",
        "blocking": {"zones": ["案桌两侧"], "movement": "沈蘅绕桌取纸；陆清和只移动匣盖，不跨过桌中线。", "contact": "无人物触碰。", "prop_handling": "旧灰与新胶痕并置，匣盖合上但铜扣保持打开。", "axis": "案桌中线轴"},
        "light_sources": ["案桌油灯", "后仓窄窗微光"],
    },
    "S1-E01-M10": {
        "scene_title": "后仓今晚上锁",
        "location_ids": ["LOC-002"],
        "scene_spec_ref": "canon/city/03-he-ming-lane-and-shen-shop.md",
        "participants": [C["陆清和"], C["沈蘅"]],
        "beats": [
            beat("陆清和锁钱匣、封后仓门、把钥匙放在自己掌心；沈蘅没有伸手要。", "生活秩序开始承担证据保护的功能，也制造母女的不信任。", [
                line("陆清和", "后仓今晚我锁。", "先控制可见风险", "低"),
                line("沈蘅", "你不信我？", "把制度动作听成关系判断"),
                line("陆清和", "我信你会做对的事。", "承认女儿的坚持", "低"),
                line("陆清和", "我不信做对的事，不会伤人。", "把生活代价说出来", "低"),
            ]),
        ],
        "choice": "陆清和把后仓钥匙收回，沈蘅接受出入记录而不抢回权限。",
        "exit_state": "调查获得制度化边界；母女从争论意图转向争论谁承担后果。",
        "blocking": {"zones": ["钱匣", "后仓门"], "movement": "陆清和完成一条锁匣—锁门的生活路线；沈蘅停在门外。", "contact": "无人物触碰。", "prop_handling": "钥匙在陆清和右手；后仓门锁闭。", "axis": "钱匣—门闩轴"},
        "light_sources": ["门内油灯", "门外雨光被门缝切断"],
    },
    "S1-E01-M11": {
        "scene_title": "有人少吃，也有人不再来",
        "location_ids": ["LOC-001"],
        "scene_spec_ref": "canon/city/03-he-ming-lane-and-shen-shop.md",
        "participants": [C["林阿沅"], C["胡六婆"]],
        "beats": [
            beat("阿沅到胡六婆门口，不敲门，先把油纸塞在门槛下。", "她尊重不愿说话的人，却也不允许‘没来’被写成‘没事’。", [
                line("林阿沅", "胡婆婆，我把半碗记上了。你不想说，就摇一下门。", "给对方选择回应方式"),
                line("胡六婆", "记饭就记饭，别记人。", "保护隐私", "低"),
                line("林阿沅", "那我记‘有人在门里’。别的，留空。", "在隐私与失联之间留证", "慢"),
            ]),
        ],
        "choice": "阿沅记录具体生活变化，同时不把未回应的人写成已安全。",
        "exit_state": "失联风险第一次落到一扇具体的门；阿沅获得下一章关系回报的行动依据。",
        "blocking": {"zones": ["门槛", "巷口"], "movement": "阿沅从门槛退到巷口，回头一次，不再敲第二次。", "contact": "只接触门槛和油纸。", "prop_handling": "油纸留在门内侧可见位置。", "axis": "门槛—巷口轴"},
        "light_sources": ["巷口阴天光", "门内未点灯的暗部"],
    },
    "S1-E01-M12": {
        "scene_title": "把选择权放回桌上",
        "location_ids": ["LOC-009", "LOC-002"],
        "scene_spec_ref": "canon/city/05-west-lake-and-xiling-circle.md",
        "participants": [C["顾行舟"], C["沈蘅"]],
        "beats": [
            beat("顾行舟把两名北客的原话和时刻写在纸上，纸边不写姓名；沈蘅检查他是否替人下结论。", "顾行舟主动把保护对象的隐私写进方法，沈蘅仍在防备被代替。", [
                line("顾行舟", "他们说白芷贵，不等于他们知道为什么。", "把事实和推断分开"),
                line("沈蘅", "你这次没替他们说完。", "确认边界被尊重", "慢"),
                line("顾行舟", "我学得慢。你可以再提醒。", "承认关系中的亏欠"),
            ]),
            beat("沈蘅把纸推回给他，让他自己决定是否保留姓名空栏。", "边界不靠宣言，而靠谁把纸推回谁面前。", [
                line("沈蘅", "名字空着。时刻留下。", "建立共同记录规则"),
                line("顾行舟", "好。", "接受协商后的限制"),
            ]),
        ],
        "choice": "顾行舟提供可核验原话而不代替判断；沈蘅保留隐私边界。",
        "exit_state": "两人的关系从被照顾转向共同制定记录规则；母女裂缝仍未解决。",
        "blocking": {"zones": ["酒肆后门", "香铺案桌"], "movement": "顾行舟将纸放在门边；沈蘅取纸回到案桌，两人不并肩。", "contact": "无人物触碰。", "prop_handling": "纸张折角标记来源保护等级。", "axis": "门边—案桌轴"},
        "light_sources": ["酒肆门口雨光", "香铺案桌油灯"],
    },
    "S1-E01-M13": {
        "scene_title": "留下香丸，留下未核",
        "location_ids": ["LOC-002"],
        "scene_spec_ref": "canon/city/03-he-ming-lane-and-shen-shop.md",
        "participants": [C["沈蘅"], C["陆清和"]],
        "beats": [
            beat("沈蘅把香丸、灰样、胶痕纸分成三列，给每列留出空白。", "她提出方案，不是为了证明父亲，而是为了让错误有回头路。", [
                line("沈蘅", "香丸留下，灰样分开，所有纸都写‘未核’。", "提出可执行方案", "慢"),
                line("陆清和", "你要把它留在家里？", "确认生活风险", "低"),
                line("沈蘅", "留在可看见的地方。不是供起来。", "拒绝把遗物神圣化"),
            ]),
        ],
        "choice": "沈蘅保留香丸并公开写下‘未核’，不借亡父名义给城里下结论。",
        "exit_state": "调查从家事转为公共责任；但母女裂缝正式成立。",
        "blocking": {"zones": ["案桌三列"], "movement": "沈蘅从左至右摆放三列；陆清和站在桌尾，不动手。", "contact": "无人物触碰。", "prop_handling": "香丸居中、灰样左、胶痕纸右；空白栏必须可见。", "axis": "案桌横向轴"},
        "light_sources": ["案桌油灯主光", "炉火边缘光"],
    },
    "S1-E01-M14": {
        "scene_title": "十三年的账",
        "location_ids": ["LOC-002"],
        "scene_spec_ref": "canon/city/03-he-ming-lane-and-shen-shop.md",
        "participants": [C["陆清和"], C["沈蘅"]],
        "beats": [
            beat("陆清和打开旧账箱，一张张放下停业单、罚银、药费和鞋钱；每放一张就把箱盖推远一点。", "她不是控诉亡夫，而是让女儿看见正确选择由谁付账。", [
                line("陆清和", "你爹死后，第一个月，铺子关了十九日。", "把抽象代价变成日期", "低"),
                line("陆清和", "第二个月，门口每天有人骂。", "把名声代价放到门口", "低"),
                line("陆清和", "第三个月，你夜里发热。我没有钱同时买药和交货款。", "把母女生活放入选择账单", "低"),
                line("沈蘅", "我不知道。", "承认自己只看见父亲一边", "极慢"),
            ]),
            beat("沈蘅没有去碰账单，只把香丸旁边的空白纸推给母亲。", "她不求母亲批准，只承认母亲一直在支付。", [
                line("沈蘅", "这次我先把会付账的人写下来。", "把方法改成共同承担", "慢"),
                line("陆清和", "写。写全。", "不阻止，但不替她承担", "低"),
            ]),
        ],
        "choice": "陆清和让沈蘅先看清代价；沈蘅放弃‘只要正确就够了’的轻易判断。",
        "exit_state": "母女仍有裂缝，但争执从‘查不查’转为‘谁付账’。",
        "blocking": {"zones": ["旧账箱", "案桌三列"], "movement": "陆清和沿桌边放账；沈蘅保持一臂距离，只移动空白纸。", "contact": "无人物触碰；账单不交到对方手里。", "prop_handling": "账单按月份排列，鞋钱最后落下。", "axis": "账箱—案桌轴"},
        "light_sources": ["旧账箱旁低油灯", "案桌冷暖混合光"],
    },
    "S1-E01-M15": {
        "scene_title": "亲见、转闻、未核",
        "location_ids": ["LOC-001", "LOC-002"],
        "scene_spec_ref": "canon/city/03-he-ming-lane-and-shen-shop.md",
        "participants": [C["林阿沅"], C["沈蘅"], C["陆清和"]],
        "beats": [
            beat("阿沅把油纸上的饭量、门声和空位抄成三栏；沈蘅不替她改词。", "普通人的记录被允许保留粗糙，而不是被专业语言吞掉。", [
                line("林阿沅", "这栏写‘亲见’，这栏写‘听说’，中间这栏……", "寻找可以诚实表达的不确定词"),
                line("沈蘅", "写‘未核’。不知道，不丢人。", "把不确定性制度化", "低"),
                line("陆清和", "纸够不够？", "用生活动作表达支持但不表态", "低"),
                line("林阿沅", "够。只要别把空白也算成答案。", "把方法变成自己的坚持"),
            ]),
        ],
        "choice": "阿沅按来源等级记录，沈蘅公开‘未核’规则。",
        "exit_state": "春信的最小记录格式出现：亲见、转闻、未核；信息可以被后来者纠正。",
        "blocking": {"zones": ["案桌", "门边纸架"], "movement": "阿沅从桌左写到桌右；沈蘅站在对面；陆清和在后方整理纸。", "contact": "沈蘅不拿笔，只推纸；陆清和只补纸。", "prop_handling": "三栏纸张固定在木夹板上。", "axis": "纸架—案桌轴"},
        "light_sources": ["案桌油灯", "门边天光"],
    },
    "S1-E01-M16": {
        "scene_title": "有人故意让她拆穿",
        "location_ids": ["LOC-002"],
        "scene_spec_ref": "canon/city/03-he-ming-lane-and-shen-shop.md",
        "participants": [C["顾行舟"], C["沈蘅"]],
        "beats": [
            beat("顾行舟用纸纤维、胶痕软硬和刀口方向复核香丸曾被重新封入；沈蘅在纸上补时刻。", "真相不是‘谁’，而是投递者知道她会按职业方法拆穿伪装。", [
                line("顾行舟", "这不是藏得好。是故意让你发现。", "提出行为层重义", "低"),
                line("沈蘅", "如果故意让我发现，他就知道我会拆。", "把对手能力写进问题", "慢"),
                line("顾行舟", "也可能只知道你不会烧。", "保留替代解释", "低"),
            ]),
            beat("顾行舟伸手想按住纸角，停住；沈蘅自己压平纸边。", "他学会不替她固定证据，也不替她固定结论。", [
                line("沈蘅", "别替我压。纸会记住手。", "把物证与边界同时说清", "低"),
                line("顾行舟", "那我记在旁边。", "接受协作方式", "低"),
            ]),
        ],
        "choice": "顾行舟确认投递者利用职业核验习惯，沈蘅记录为疑点而非身份判断。",
        "exit_state": "调查对象从‘亡父遗言’转为‘懂得沈蘅方法的人’；关系协作更具体。",
        "blocking": {"zones": ["案桌两侧"], "movement": "顾行舟靠近桌边后停下；沈蘅压平纸角。", "contact": "禁止顾行舟触碰沈蘅手；只允许物件接触。", "prop_handling": "纸角由沈蘅压住，顾行舟的手停在纸外。", "axis": "案桌横向轴"},
        "light_sources": ["案桌油灯主光", "门缝冷光"],
    },
    "S1-E01-M17": {
        "scene_title": "不写无春，只写未核",
        "location_ids": ["LOC-002"],
        "scene_spec_ref": "canon/city/03-he-ming-lane-and-shen-shop.md",
        "participants": [C["沈蘅"], C["陆清和"]],
        "beats": [
            beat("沈蘅提笔，先写下地点、时刻、来源，再停在‘结论’一栏。", "她可以用父亲的名义让一座城紧张，却选择不这样做。", [
                line("沈蘅", "今岁无春，不能写。", "拒绝把一句话扩大成城市判断", "慢"),
                line("陆清和", "那你写什么？", "逼她完成而不是只克制", "低"),
                line("沈蘅", "香丸新封，来源未核。", "用事实替代解释", "低"),
            ]),
            beat("她把笔放下，等墨干；陆清和没有替她盖纸。", "选择没有掌声，只有一张不够漂亮但可纠正的纸。", [
                line("陆清和", "做对的事，常常看起来不像做了什么。", "承认她的选择但不美化代价", "低"),
                line("沈蘅", "那就让它先不像答案。", "接受不确定的孤独", "低"),
            ]),
        ],
        "choice": "沈蘅公开写下‘未核’，不使用‘无春’替城市下结论。",
        "exit_state": "第一集的价值选择完成：春信先记录事实，再等待合报。",
        "blocking": {"zones": ["案桌正面", "陆清和身后"], "movement": "沈蘅坐定写字；陆清和在她身后停住，不越过肩线。", "contact": "无触碰。", "prop_handling": "墨迹自然晾干，纸不折叠。", "axis": "案桌正面轴"},
        "light_sources": ["案桌油灯稳定主光"],
    },
    "S1-E01-M18": {
        "scene_title": "故意留下的胶痕",
        "location_ids": ["LOC-002"],
        "scene_spec_ref": "canon/city/03-he-ming-lane-and-shen-shop.md",
        "participants": [C["陆清和"], C["沈蘅"]],
        "beats": [
            beat("陆清和重新检查铜扣，把一小片近半年才会变色的胶留在灯下；沈蘅没有立即拿笔。", "母亲先发现：这不是藏匿失败，而是投递者留下的邀请。", [
                line("陆清和", "这胶痕，故意留在你看得见的地方。", "把尾钩从物件推到人", "低"),
                line("沈蘅", "他知道我会拆。", "承认对手已经预判她", "慢"),
                line("陆清和", "那他也知道，你会记。", "把女儿的选择推向明天", "低"),
            ]),
            beat("沈蘅在‘未核’下面补写‘待查：近半年入匣者’，陆清和把铜扣扣上。", "匣子终于合上，但问题从家内移向城市。", [
                line("沈蘅", "明早先查进门的人。", "把尾钩转成下一集行动", "慢"),
                line("陆清和", "明早先吃饭。", "用生活把英雄拉回人间", "低"),
            ]),
        ],
        "choice": "母女共同留下‘近半年入匣者’这一追问，香丸状态与未核记录保持连续。",
        "exit_state": "E01 在生活动作中闭环；下一集由入匣者、香材与粮运异常接续。",
        "blocking": {"zones": ["案桌", "后仓门"], "movement": "陆清和从灯下到门边扣匣；沈蘅留在案桌完成补记。", "contact": "无人物触碰。", "prop_handling": "铜扣扣上但不加锁；未核纸留在案桌中央。", "axis": "案桌—后仓门轴"},
        "light_sources": ["案桌油灯", "灯下局部反光"],
    },
}


def build_story_scene(card: dict, data: dict) -> dict:
    return {
        "scene_id": f"SCN-{card['chapter_id']}",
        "chapter_id": card["chapter_id"],
        "episode_id": EPISODE_ID,
        "format": "2-3 minute microchapter scene",
        "status": "DRAFT-EPISODE-GATE",
        "duration_seconds": card["duration_seconds"],
        "scene_spec_ref": data["scene_spec_ref"],
        "location_ids": data["location_ids"],
        "participants": data["participants"],
        "dramatic_question": card["relationship_delta_sheet"]["unresolved_question"],
        "objective": card["story_card"]["scene_goal"],
        "obstacle": card["story_card"]["obstacle"],
        "entry_state": card["character_state_sheet"]["entry_state"],
        "beats": data["beats"],
        "choice": data["choice"],
        "exit_state": data["exit_state"],
        "causes_next": card["story_card"]["next_chase"],
        "continuity_refs": [card["chapter_id"], *data["location_ids"]],
        "dialogue_boundary": "对白为正式剧本第一版；不改写 Character DNA，不引入镜头指令或未锁定事实。",
    }


def build_storyboard(card: dict, data: dict, scene: dict) -> dict:
    focus = scene["participants"][0]
    return {
        "scene_id": scene["scene_id"],
        "chapter_id": scene["chapter_id"],
        "status": "DRAFT-EPISODE-GATE",
        "scene_binding": {
            "scene_spec_ref": data["scene_spec_ref"],
            "location_ids": data["location_ids"],
            "weather_state": "惊蛰雷雨后；保持与 Season Ledger 一致",
            "axis": data["blocking"]["axis"],
            "zones": data["blocking"]["zones"],
        },
        "shots": [
            {
                "shot_id": f"{scene['chapter_id']}-S01",
                "purpose": "建立空间与当章生活压力",
                "attention_order": ["location", "focus_character", "unresolved_object_or_action"],
                "blocking": data["blocking"],
                "camera": {
                    "scale": "wide-to-medium",
                    "position": f"{data['blocking']['zones'][0]}边缘，朝向{data['blocking']['zones'][-1]}",
                    "height": "人物胸口至视线高度",
                    "angle": "水平，略带空间侧向",
                    "focal_length": "28mm 等效",
                    "perspective_intent": "先让观众读懂生活空间、入口出口与关键物件的相对位置",
                    "focus_target": "人物工作路径与未解决物件",
                    "depth": "深景深，保留前中后景关系",
                    "anchor": data["blocking"]["zones"][0],
                    "movement": "slow observational drift",
                    "axis_side": "preserve",
                },
                "composition": {"foreground": "章内生活物件", "midground": "人物工作路径", "background": "入口或出口", "negative_space": "为尾钩对象留出可见位置"},
                "light": {"physical_sources": data["light_sources"], "treatment": "不改变地理光源，仅保持雨后湿材质反应"},
                "temporal": {"start": "人物进入日常动作", "event": "生活动作露出异常", "end": "观众知道要追什么"},
                "stable_end_state": "空间轴、人物相对位置与关键物件位置可复用",
            },
            {
                "shot_id": f"{scene['chapter_id']}-S02",
                "purpose": "让目标与阻力通过动作而非旁白可见",
                "attention_order": ["focus_character", "counteraction", "prop_or_record"],
                "blocking": {"primary_actor": focus, "action_path": data["blocking"]["movement"], "contact": data["blocking"]["contact"], "prop_handling": data["blocking"]["prop_handling"]},
                "camera": {
                    "scale": "medium two-shot or medium single",
                    "position": f"{data['blocking']['zones'][0]}与{data['blocking']['zones'][-1]}之间的安全线外",
                    "height": "人物胸口高度",
                    "angle": "平视三分之四角度",
                    "focal_length": "50mm 等效",
                    "perspective_intent": "压缩但不抹平人物之间的关系距离，让阻力在同一空间内可见",
                    "focus_target": "主行动者、对抗动作与被处理的物件",
                    "depth": "中景深，保持对方反应可读",
                    "anchor": data["blocking"]["zones"][0],
                    "movement": "locked with one motivated pan",
                    "axis_side": "preserve",
                },
                "composition": {"foreground": "hands and working surface", "midground": "performer", "background": "relationship counter-position", "negative_space": "retain eyeline toward next chase"},
                "light": {"physical_sources": data["light_sources"], "treatment": "让手部、纸面和材质读清，不用风格光替代动机"},
                "temporal": {"start": "目标被提出", "event": "对方或环境施加阻力", "end": "角色作出一项局部选择"},
                "stable_end_state": "动作完成后保留关系距离与道具握持状态",
            },
            {
                "shot_id": f"{scene['chapter_id']}-S03",
                "purpose": "落尾钩并把问题交给下一章",
                "attention_order": ["evidence_or_relationship_delta", "reaction", "tail_hook"],
                "blocking": {"primary_actor": focus, "end_position": data["blocking"]["zones"][-1], "contact": data["blocking"]["contact"], "prop_handling": data["blocking"]["prop_handling"]},
                "camera": {
                    "scale": "close detail to restrained reaction",
                    "position": f"{data['blocking']['zones'][-1]}侧的可见边界，不越过人物安全距离",
                    "height": "手部或桌面略高处，随后回到眼线高度",
                    "angle": "轻微斜侧，不改变既有轴线",
                    "focal_length": "85mm 等效",
                    "perspective_intent": "把证据、关系反应与尾钩压进同一注意顺序，不制造风格化惊吓",
                    "focus_target": "evidence_or_relationship_delta 与克制反应",
                    "depth": "浅至中景深，尾钩对象清晰且保留必要环境线索",
                    "anchor": data["blocking"]["zones"][-1],
                    "movement": "no decorative move; end on observable hold",
                    "axis_side": "preserve",
                },
                "composition": {"foreground": "evidence or hand", "midground": "reaction", "background": "unresolved exit", "negative_space": "tail hook direction"},
                "light": {"physical_sources": data["light_sources"], "treatment": "保持光线连续，尾钩不靠闪白或突发风格变化"},
                "temporal": {"start": "局部选择已完成", "event": "反应或新事实出现", "end": "下一追问可直接接入"},
                "stable_end_state": scene["exit_state"],
            },
        ],
        "director_boundary": "镜头设计只实现已锁定戏剧目的；不新增对白、角色知识或城市地理。",
    }


def build_continuity(card: dict, data: dict, scene: dict) -> dict:
    return {
        "chapter_id": scene["chapter_id"],
        "scene_id": scene["scene_id"],
        "status": "DRAFT-EPISODE-GATE",
        "characters": {
            character_id: {
                "entry": "沿用 v6 Character DNA 与上一章状态",
                "exit": scene["exit_state"],
                "knowledge_added": card["character_state_sheet"]["knowledge_after"],
                "knowledge_forbidden": "不得提前知道后续集的投递者身份、无春结论或未提供的水粮药因果。",
            }
            for character_id in scene["participants"]
        },
        "appearance": {"wardrobe": "E01 春季工作状态；细节由 v6 Costume Standard 锁定", "hair_and_ornament": "沿用角色资产版本，不在本章新增", "injury": "无新增伤口"},
        "props": {"continuity_refs": ["story/season/season-causal-ledger.json", "story/season/short-chapter-hook-map.json"], "state_after": data["choice"], "must_remain": data["blocking"]["prop_handling"]},
        "space_and_time": {"location_ids": data["location_ids"], "weather": "惊蛰雷雨后", "time": "精确钟点待 Episode Gate 逐场确认", "axis": data["blocking"]["axis"]},
        "relationship": {"delta": card["relationship_delta_sheet"]["episode_delta"], "boundary": card["relationship_delta_sheet"]["chapter_boundary"]},
        "handoff": scene["causes_next"],
    }


def main() -> int:
    packet = json.loads(CARD_PATH.read_text(encoding="utf-8"))
    cards = {card["chapter_id"]: card for card in packet["cards"]}
    if set(cards) != set(SCENES):
        raise SystemExit("scene data must cover exactly the 18 E01 production cards")
    scenes = [build_story_scene(cards[chapter_id], SCENES[chapter_id]) for chapter_id in sorted(SCENES)]
    storyboards = [build_storyboard(cards[scene["chapter_id"]], SCENES[scene["chapter_id"]], scene) for scene in scenes]
    continuity = [build_continuity(cards[scene["chapter_id"]], SCENES[scene["chapter_id"]], scene) for scene in scenes]
    source_manifest = [
        {"path": "production/episodes/S1-E01/episode-production-cards.json", "sha256": sha256(CARD_PATH)},
        {"path": "story/season/short-chapter-hook-map.json", "sha256": sha256(ROOT / "story/season/short-chapter-hook-map.json")},
        {"path": "production/ai/v6-character-asset-bible/01-character-bible/12-central-character-master-cards.md", "sha256": sha256(ROOT / "production/ai/v6-character-asset-bible/01-character-bible/12-central-character-master-cards.md")},
        {"path": "production/ai/v6-character-asset-bible/10-episode-gate/episode-delivery-gate.md", "sha256": sha256(ROOT / "production/ai/v6-character-asset-bible/10-episode-gate/episode-delivery-gate.md")},
    ]
    formal = {
        "schema_version": 1,
        "status": "P3-03-DRAFT",
        "scope": "P3-03 S1-E01 formal script, storyboard and continuity preflight",
        "episode_id": EPISODE_ID,
        "episode_gate_status": "OPEN",
        "source_manifest": source_manifest,
        "script_scene_total": len(scenes),
        "storyboard_scene_total": len(storyboards),
        "continuity_scene_total": len(continuity),
        "script_scenes": scenes,
        "storyboard": storyboards,
        "continuity_ledger": continuity,
        "qa_policy": {"dimensions": 10, "threshold": 90, "status": "PENDING-EPISODE-GATE"},
        "execution_policy": "DESIGN-ONLY; no provider calls, media claims, or final render receipts.",
        "deferred_boundary": {"aigc_generation": "DEFERRED-UNTIL-EPISODE-GATE-APPROVAL", "u_unique_identity": "DEFERRED-UNTIL-EPISODE-GATE", "bg_bindings": "DEFERRED-UNTIL-EPISODE-GATE"},
        "next_gate": "Episode Gate preflight audit, then human review of dialogue, blocking, storyboard and ten QA dimensions.",
    }
    EPISODE_DIR.mkdir(parents=True, exist_ok=True)
    FORMAL_PATH.write_text(json.dumps(formal, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SCRIPT_PATH.write_text(json.dumps({"schema_version": 1, "status": "P3-03-DRAFT", "episode_id": EPISODE_ID, "scenes": scenes}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    STORYBOARD_PATH.write_text(json.dumps({"schema_version": 1, "status": "P3-03-DRAFT", "episode_id": EPISODE_ID, "scenes": storyboards}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CONTINUITY_PATH.write_text(json.dumps({"schema_version": 1, "status": "P3-03-DRAFT", "episode_id": EPISODE_ID, "scenes": continuity}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"materialized {EPISODE_ID} formal scenes={len(scenes)} storyboard_scenes={len(storyboards)} continuity_scenes={len(continuity)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
