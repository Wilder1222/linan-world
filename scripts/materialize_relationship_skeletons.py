from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLOTS = ROOT / "qa/relationship-slots.json"
EVIDENCE_PATH = ROOT / "qa/relationship-evidence.json"

DIMENSIONS = ("亲近", "信任", "亏欠", "依赖", "敬意", "怨恨", "共同秘密")
SNAPSHOTS = ("Y0-OPEN", "ARC1-END", "ARC2-END", "ARC3-END", "ARC4-END", "ARC5-END", "ARC6-END", "Y+1")
SNAPSHOT_WINDOWS = {
    "Y0-OPEN": "E01-E06",
    "ARC1-END": "E01-E06",
    "ARC2-END": "E07-E12",
    "ARC3-END": "E13-E18",
    "ARC4-END": "E19-E24",
    "ARC5-END": "E25-E30",
    "ARC6-END": "E31-E36",
    "Y+1": "灾后一年",
}
SNAPSHOT_PHASES = {
    "Y0-OPEN": "建立关系基线",
    "ARC1-END": "第一次日常回报",
    "ARC2-END": "误读与边界受压",
    "ARC3-END": "职业复核改变判断",
    "ARC4-END": "短暂回到普通生活",
    "ARC5-END": "不可逆代价落到具体的人",
    "ARC6-END": "公共协作与责任公开",
    "Y+1": "带着旧账回访新边界",
}

SNAPSHOT_COST_EFFECTS = {
    "Y0-OPEN": "双方第一次把边界说出来，失去继续假装轻松相处的余地",
    "ARC1-END": "日常选择被关系改变，至少一人承担一次可见的时间、收入或名声损失",
    "ARC2-END": "误读使一项信息、身体或署名边界受损，不能靠一句解释撤回",
    "ARC3-END": "职业复核迫使双方承认对方有独立判断，旧有的照料、服从或占有位置失效",
    "ARC4-END": "短暂普通生活让双方延迟一次核验或救援，亲近与进度不能同时保全",
    "ARC5-END": "代价落到具体的人、资源或前途，关系无法靠道歉恢复原状",
    "ARC6-END": "公共协作要求共同署名、公开或受审，任何一方都不能替另一方洗白",
    "Y+1": "灾后回访只确认新的边界，继续来往不等于旧伤自动消失",
}

# Concrete Foundation evidence anchors. Exact scene IDs remain RESERVED until
# Season/Episode Gate, but each relation already has a space, object, observable
# action, dialogue intent, cost and continuity handle that can be staged.
RELATION_CONTEXT = {
    "REL-001": {
        "spaces": ["沈家香铺后门", "香铺后仓", "西湖雨棚", "断桥灯棚"],
        "objects": ["防风灯", "原始记录", "半卷旧案", "疫图与更正簿"],
        "actions": ["挂灯后把选择权让回", "让对方先看完整记录", "只交出一半证据后站开", "在风险公开后不再拉住对方"],
        "dialogues": ["借的，明早还。", "先写你亲眼看见的。", "这页我还不能交给你。", "你去哪？"],
        "cost": "保护逐步变成控制，最终造成信任与身体边界的不可逆损伤。",
        "continuity": "灯钩、半卷旧案页码、疫图折痕和双方站位距离必须连续。",
    },
    "REL-002": {
        "spaces": ["春台瓦舍后台", "书坊窗边", "西湖画舫", "封城后的书坊"],
        "objects": ["未完成曲稿", "失画残片", "测绘图", "独立署名印"],
        "actions": ["共享半成品但保留删改权", "未经许可画下对方后主动撕掉", "把失败稿交给对方复核", "在公共图上保留双方独立署名"],
        "dialogues": ["这句我可以改，但不是替你改。", "你看见我，先问过我了吗？", "失败也要留下。", "署名不是谢礼，是责任。"],
        "cost": "艺术合作不断触及被观看、被拥有和署名控制，带来契约与前程损失。",
        "continuity": "曲稿折角、画稿墨色、署名位置和两人保持的工作距离必须连续。",
    },
    "REL-003": {
        "spaces": ["御街夜市", "鹤鸣巷街口", "春信屋公共桌"],
        "objects": ["曲词纸条", "油纸饭量记录", "更正簿"],
        "actions": ["争执后一起回访街坊", "把彼此最不信的证据并排放下", "公开承认对方的生活判断", "共同撤下一张错报"],
        "dialogues": ["你先别替我解释。", "人的重复也是证据。", "我羡慕你能让人开口。", "这张错了，一起改。"],
        "cost": "羡慕与嫉妒被说破，双方各自失去一段安全的自我形象。",
        "continuity": "曲词、油纸、街坊姓名和共同改字的笔迹必须连续。",
    },
    "REL-004": {
        "spaces": ["钱塘码头", "青鹞船舱", "旧船帮修船棚"],
        "objects": ["吃水绳结", "船钉", "旧水路记录"],
        "actions": ["并肩搬货却拒绝替对方解释", "递工具而不接管舵位", "在旧船帮面前各自说出责任", "让对方独自承担公开后的后果"],
        "dialogues": ["我救你，不等于替你说话。", "这条船你自己定。", "十三年前我也选择过沉默。", "这次账上写两个人的名字。"],
        "cost": "救命恩与旧案责任同时存在，船、名声和旧同袍信任被重新定价。",
        "continuity": "吃水刻线、船钉缺口、旧记录水渍和两人的站位必须连续。",
    },
    "REL-005": {
        "spaces": ["沈家香铺后院", "灶房", "旧账箱前"],
        "objects": ["香匣", "停业单", "灯芯与账簿"],
        "actions": ["关门后仍把热水留在桌上", "逐张放下账单而不哭诉", "把香匣推给女儿后收回手", "在公开风险前交回决定权"],
        "dialogues": ["做对的事，账会落到人头上。", "你先把这些名字看完。", "香匣给你，但不是让你替我活。", "回来吃饭，决定你自己做。"],
        "cost": "母亲放弃控制与丈夫名声的最后维护，家业与母女安全感都受损。",
        "continuity": "香匣铜扣、账单顺序、灯芯长度和母女之间的桌距必须连续。",
    },
    "REL-006": {
        "spaces": ["沈家旧仓", "春信屋档案桌", "公开更正墙"],
        "objects": ["父亲旧记录", "香丸切样", "公开错误簿"],
        "actions": ["把父亲的事实与推断分栏", "保留一条对父亲不利的原句", "公开错误而不撤回爱", "允许后来者在父亲记录旁贴更正"],
        "dialogues": ["好是真的，错也是真的。", "我不替他补上没有的证据。", "这条错误由我公开。", "你可以纠正他，也可以纠正我。"],
        "cost": "沈蘅舍弃完美父亲的心理支撑，换来更可信却更孤独的继承方式。",
        "continuity": "原记录纸边、香丸切面、错误簿页码和公开墙位置必须连续。",
    },
    "REL-007": {
        "spaces": ["沈家账房", "后院火盆旁", "旧铺门口"],
        "objects": ["停业单", "罚银票", "亡夫旧印"],
        "actions": ["整理账箱而不替亡夫辩护", "把罚银票按月份排开", "在女儿面前承认爱与怨同时存在", "封存旧印但保留记录"],
        "dialogues": ["我还爱他，不等于我替他解释。", "第三个月，你的鞋钱也在这里。", "这笔账不能用想念抵。", "门可以再开，旧账不会消失。"],
        "cost": "陆清和放弃替亡夫保留体面的最后幻想，家庭名声与生计继续承受后果。",
        "continuity": "账箱锁、票据顺序、旧印印泥和火盆灰必须连续。",
    },
    "REL-008": {
        "spaces": ["鹤鸣巷馄饨铺", "公共灶", "失联名册桌"],
        "objects": ["热汤碗", "油纸名册", "赊账簿"],
        "actions": ["先端稳热汤再询问女儿", "把赊账簿交给阿沅核对", "允许女儿先去逐户确认", "在门口等候而不追出去"],
        "dialogues": ["先吃一口，再说你看见什么。", "账簿给你，不代表我不担心。", "你先确认，我不替你宣布。", "回来时门还开着。"],
        "cost": "沈三娘放弃以照料换服从，阿沅也失去永远被保护的女儿位置。",
        "continuity": "碗沿葱花、名册折角、灶火和门闩状态必须连续。",
    },
    "REL-009": {
        "spaces": ["汇川行账房", "商会席", "复制真账的内室"],
        "objects": ["算盘", "真账与副本", "养父送的旧砚"],
        "actions": ["黎见山亲自教她查账", "黎令仪复制关键页而不撕原账", "探望养父却不替证词辩护", "在公开场合各自留下名字"],
        "dialogues": ["你教我的，我用来查你。", "对你好是真的，做错也是真的。", "我来看你，不是来求情。", "账上不能因为亲人换一种算术。"],
        "cost": "养父女同时失去商号、信任和旧家庭叙事，却保留真实养育之恩。",
        "continuity": "算盘珠位、真账页码、旧砚裂纹和探望门槛必须连续。",
    },
    "REL-010": {
        "spaces": ["小济堂药柜", "病例桌", "药柜钥匙交接处"],
        "objects": ["病例簿", "药包批号", "药柜钥匙"],
        "actions": ["师父压下病例，学生留下原判", "共同复核药包而不争署名", "交出钥匙让学生独立核验", "公开写下前判有误"],
        "dialogues": ["样本少，不等于可以不记。", "前判有误，我来署名。", "钥匙给你，责任也一起给你。", "你不必先证明自己才救人。"],
        "cost": "余仲仁失去权威的安全感，余青禾失去荐书与被认可的顺路。",
        "continuity": "病例页码、药包批号、钥匙绳结和药柜格位必须连续。",
    },
    "REL-011": {
        "spaces": ["书坊画室", "排水渠边", "民用图刻印房"],
        "objects": ["磨墨砚", "失败稿", "独立落印"],
        "actions": ["老师改图却保留学生原稿", "学生把失败版带回重测", "老师在民用图旁落自己的印", "双方公开承认署名边界"],
        "dialogues": ["图不是我的脸，别替我说话。", "失败稿也要留着。", "你可以离开师门，不必删掉来路。", "这方印是我承担，不是你的奖赏。"],
        "cost": "师徒各自放弃控制与归属，画院机会和师门权威不再能同时保全。",
        "continuity": "墨色浓淡、失败稿折痕、刻印位置和画室桌面必须连续。",
    },
    "REL-012": {
        "spaces": ["城门值房", "封锁门轴", "风险记录桌"],
        "objects": ["腰牌", "门轴木楔", "风险记录"],
        "actions": ["高问按章办手续，顾行舟找出出口", "两人分别记录自己造成的风险", "危机中一人写例外一人签名", "接受被救者质询而不互相洗白"],
        "dialogues": ["我按章办过，所以我知道章会伤人。", "出口我找到了，签不签你自己定。", "这次例外写我的名字。", "救命不是撤销旧账。"],
        "cost": "同袍默契与制度责任冲突，高问的官身和顾的旧身份同时被重新审视。",
        "continuity": "腰牌挂位、门轴磨痕、签字墨色和风险记录页必须连续。",
    },
    "REL-013": {
        "spaces": ["城门验门处", "旧军械库", "回传更正的值房"],
        "objects": ["旧军令", "验门木签", "更正回传条"],
        "actions": ["曹肃认出顾却不替他撤销命令", "两人核验旧军令缺页", "曹肃回传一次更正并留下姓名", "完整解释旧事而不求谅解"],
        "dialogues": ["我替你传回更正，不替你洗白。", "当年我看见了，却没有追问。", "这条回传算我的。", "你可以不原谅，但要知道完整经过。"],
        "cost": "旧同袍的沉默被公开，曹肃失去安全的中立位置与顾的单纯信任。",
        "continuity": "木签刻痕、军令缺页、回传条折法和验门时刻必须连续。",
    },
    "REL-014": {
        "spaces": ["城务司值房", "城门点卯处", "非常令签押桌"],
        "objects": ["值房薄", "例外令", "签押笔"],
        "actions": ["高问发令，曹肃逐条点卯", "部下受伤后上级不删记录", "一人写例外条件一人决定签名", "开门后共同接受追责"],
        "dialogues": ["例外不是没有规则，是把规则写出来。", "我签，是因为我看见条件。", "名字留下，门才算真的开。", "服从不能替代判断。"],
        "cost": "上下级共同失去‘只是奉命’的心理保护，官职与部下信任都受损。",
        "continuity": "点卯顺序、令签编号、签押笔和门开时刻必须连续。",
    },
    "REL-015": {
        "spaces": ["城务司文书房", "摘要分发桌", "撤回封锁令的值房"],
        "objects": ["印泥", "签押链", "删报原稿"],
        "actions": ["章允中按要求删报却保留底稿", "宋惟敬追问摘要是否一致", "章把完整签押链摆回桌面", "宋亲手划掉自己签过的封锁建议"],
        "dialogues": ["我盖过章，所以我知道少了哪一页。", "责任不能只写在我一个人名下。", "这份删报原稿还在。", "撤回，是我自己的签。"],
        "cost": "程序忠诚与集中责任冲突，章失去安全的可靠形象，宋失去官位与制度自信。",
        "continuity": "印泥干湿、签押顺序、删报纸张和撤令墨迹必须连续。",
    },
    "REL-016": {
        "spaces": ["北归社登记处", "城南安置区公共灶", "撤离路口"],
        "objects": ["姓名册", "去向牌", "分粥木勺"],
        "actions": ["贺兰度动员，许含章先问每个人姓名", "共同分粥却因去向争执", "许把拒绝北归的人写入册中", "撤离时互相照料但不替对方求情"],
        "dialogues": ["先告诉我你叫什么，不是你属于谁。", "我想回北方，但她不一定想。", "我帮你走，不替你解释。", "理想可以留下，人不能被借走。"],
        "cost": "北归理想失去代表性垄断，许含章与贺兰度的政治机会和亲密关系都受损。",
        "continuity": "姓名册页码、去向牌颜色、木勺缺口和登记时刻必须连续。",
    },
    "REL-G01": {
        "spaces": ["五信共桌", "临安各职业节点", "万家春灯总棚"],
        "objects": ["来源标记纸", "不同版本地图", "错灯与更正灯"],
        "actions": ["五人把不同观察并排而不抢命名权", "争论后保留各自来源", "普通节点回传错报并允许撤灯", "共同公开错误链而不推出唯一领袖"],
        "dialogues": ["先写谁看见，再写你怎么想。", "不同信不是互相抵消。", "这盏灯错了，撤下来。", "没有人替全城最后判断。"],
        "cost": "协作群放弃统一口径的速度与个人正确感，换来可纠错但更慢的公共系统。",
        "continuity": "来源标记颜色、地图版本、错灯位置和撤灯时刻必须连续。",
    },
}

# Foundation-level relationship semantics. Episode production will add exact
# scene/shot evidence later; these notes prevent the relation files from being
# empty seven-dimensional placeholders.
RELATION_NOTES = {
    "REL-001": ("爱情从保护变成知情权：两人都想救对方，却不能替对方决定风险。", "顾行舟留灯、移开危险物；沈蘅接受一部分照料但保留记录。", "保护与求证。", "顾行舟想成为不可替代的人，沈蘅想证明自己不会重演父亲。", "旧案隐瞒、半卷信息和疫图用途造成的未偿债务。", "共同劳动、部分告知、边界动作和最终站开"),
    "REL-002": ("艺术相爱相惜，却不把对方固定成自己的作品或观众。", "柳十四改词、周砚之改图，彼此保留未完成稿。", "欣赏与成全。", "柳十四怕被定型，周砚之怕无人承认自己的创作。", "彼此曾把对方的表达误读成不真诚或消费。", "共享半成品、拒绝署名控制和保留失败版本"),
    "REL-003": ("女性友谊允许羡慕、嫉妒和反对同时存在，仍不把人交给标签。", "柳十四带沈蘅看夜临安，沈蘅替她核验传播链。", "互相补足。", "沈蘅羡慕人群接住柳十四，柳十四羡慕沈蘅可以沉默。", "两人曾轻视对方的职业知识和生活方式。", "争执后回访街坊、共享原始记录和共同更正"),
    "REL-004": ("生死旧交不等于无条件站队：救命恩可以与职责争执并存。", "裴九娘替顾行舟担责，顾行舟仍不替她处理船帮。", "不让旧友独自承担。", "双方都怕承认当年离开是自己选择。", "十三年前的船路误解和一次未归还的救命债。", "并肩搬货、递工具、拒绝替对方做决定"),
    "REL-005": ("母女之间的爱必须学会把账本和选择权交回女儿。", "陆清和关门、拨灯、翻账；沈蘅把灯和香匣重新摆正。", "让家人活下来。", "陆清和想锁住失去丈夫的恐惧，沈蘅想被当成大人。", "沈怀川留下的债、母亲的隐瞒和女儿重新打开旧伤。", "共同做饭、翻账、交回香匣和收回控制的手"),
    "REL-006": ("女儿不需要完美父亲，才能爱一个真实且犯过错的人。", "沈蘅翻旧记录、重做香丸、公开父亲错误判断。", "求证父亲留下的事实。", "想证明自己的成长没有建立在一个错误的人身上。", "父亲未能解释的旧案与女儿替他承担的流言。", "只信有来源的记录、保留好与错并列"),
    "REL-007": ("夫妻旧案不因死亡而清零：爱、怨、思念和生活账同时成立。", "陆清和整理账箱、拨灯、在女儿面前逐张放下停业单。", "保护家业和女儿。", "希望亡夫仍能被理解，又恨他把代价留下。", "药钱、罚银、流言和未完成的解释。", "旧物、账箱、停业单与不再替亡夫解释"),
    "REL-008": ("控制式养育要通过具体放手转为互相交代风险。", "沈三娘留饭、收账、关门；阿沅记录饭量和缺席名册。", "保护女儿。", "沈三娘怕不再被需要，阿沅怕永远只是孩子。", "母亲安排的安全席位与女儿反复越过的边界。", "热饭、失联名册、交账簿和让女儿先确认"),
    "REL-009": ("恩情不能购买道德判断：养父的好与账目的罪责可以同时为真。", "黎见山教账、改货路；黎令仪复制真账并保留探望。", "保护家业和养父。", "黎令仪怕爱削弱证词，黎见山怕失去唯一懂他的人。", "养育、教育、商号机会与被控制的人生。", "算盘、真账、复制件和不替选择辩护"),
    "REL-010": ("师徒关系在资历压制、职业嫉妒和放手困难中重新定义专业诚实。", "余仲仁压病例、补批号、交药柜钥匙；余青禾留下前判有误。", "不让年轻判断误人。", "师父怕被替代，学生怕永远得不到承认。", "多年教养与被压下的病例。", "拣药、病例簿、复核意见和药柜钥匙"),
    "REL-011": ("师徒成全不是把学生写进师父名下，而是让公共作品保留独立署名。", "程野老改图、骂图、最后在民用图旁落印；周砚之保留旧版。", "把画艺传下去。", "老师怕被时代淘汰，学生怕离开等于背叛。", "多年授艺与被扣住的署名。", "磨墨、失败稿、民用图落印和独立署名"),
    "REL-012": ("制度与同袍之间，救命恩不能抹掉执行命令造成的伤害。", "高问办手续、顾行舟找出口；两人分别留下风险记录。", "把人救出并保住制度。", "双方都怕承认曾经选择服从或逃避。", "旧案中互相救过，也互相让对方担责。", "腰牌、门轴、风险记录和接受质询"),
    "REL-013": ("旧同袍的默契包含羞愧：传回更正不等于替对方洗白。", "曹肃认出顾行舟、替他保密并回传一次更正。", "不让旧友死在错误命令里。", "曹肃怕承认自己也曾看见而不说。", "军中旧事和一次没有追问的救命。", "验门、军令、回传更正和完整解释"),
    "REL-014": ("上下级关系要在守门与开门之间证明例外也能被追责。", "高问发令、曹肃执行；危机中一人写例外，一人决定是否签名。", "让门按规则开合。", "高问怕失去官身，曹肃怕部下替自己受罚。", "共同执行过伤人的封锁。", "点卯、值房薄、例外条件和留下名字"),
    "REL-015": ("程序忠诚从服从权威转为保留完整签押链，最终允许权威撤回自己。", "章允中盖章、删报、重抄；宋惟敬要求快速集中调度。", "让城市及时行动。", "宋惟敬想承担所有判断，章允中想被看作可靠。", "被重用的荣誉与选择性呈报造成的伤害。", "印泥、签押链、被删报表和亲手撤回"),
    "REL-016": ("共同理想必须允许被代表者拒绝领袖替自己命名。", "贺兰度动员、许含章登记姓名和去向，两人共同照料又公开争执。", "护住失乡者。", "贺兰度想成为北方代表，许含章怕温和最终被遗忘。", "彼此爱护、借用地下水路和未能阻止的截粮。", "姓名册、去向询问、共同分粥和拒绝求情"),
    "REL-G01": ("五信协作群不是统一意见，而是允许彼此反对、保留来源并共同纠错。", "五类职业节点提交不同观察，争论是否合报。", "减少城市误判。", "每个人都想证明自己的信类最重要。", "Y-13 旧规失败留下的共同羞愧与互不信任。", "共享桌面、不同版本、来源标记和撤下错灯"),
}


def safe_slug(text: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", text.lower()).strip("-")


def build_evidence(relation: dict) -> list[dict]:
    relation_id = relation["id"]
    context = RELATION_CONTEXT.get(relation_id)
    if not context:
        raise KeyError(f"missing relationship evidence context: {relation_id}")
    base_cost = context["cost"].rstrip("。；")
    records: list[dict] = []
    for index, snapshot in enumerate(SNAPSHOTS):
        records.append(
            {
                "evidence_id": f"{relation_id}-EV-{index + 1:02d}",
                "relation_id": relation_id,
                "snapshot": snapshot,
                "episode_window": SNAPSHOT_WINDOWS[snapshot],
                "scene_id": None,
                "scene_status": "RESERVED-UNTIL-SEASON-GATE",
                "space": context["spaces"][index % len(context["spaces"])],
                "object": context["objects"][index % len(context["objects"])],
                "phase": SNAPSHOT_PHASES[snapshot],
                "observable_action": f"{SNAPSHOT_PHASES[snapshot]}：{context['actions'][index % len(context['actions'])]}。",
                "dialogue_intent": context["dialogues"][index % len(context["dialogues"])],
                "irreversible_cost": f"{base_cost}；阶段落点：{SNAPSHOT_COST_EFFECTS[snapshot]}。",
                "continuity_delta": f"{SNAPSHOT_PHASES[snapshot]}需保持：{context['continuity']}",
            }
        )
    return records


def render(relation: dict, evidence: list[dict]) -> str:
    relation_id = relation["id"]
    left = relation["left"]
    right = relation["right"]
    kind = relation["kind"]
    members = relation.get("members", [])
    thesis, surface, conscious, unconscious, debt, evidence_seed = RELATION_NOTES.get(
        relation_id,
        ("关系必须由选择和代价推进。", "双方通过职业劳动与物件交接呈现关系。", "保护具体的人或共同目标。", "自尊、恐惧和被需要的欲望同时存在。", "过去的恩、怨、隐瞒、承诺和现实损失不会清零。", "站位、物件交接、称谓变化和公开/隐瞒行为"),
    )
    member_text = "、".join(members) if members else "非群组双人关系"
    dimension_blocks = []
    for dimension in DIMENSIONS:
        dimension_action = {
            "亲近": "共享劳动、让路或保留一件只给对方看的物件",
            "信任": "交出原始记录、承认不知道或允许对方拒绝",
            "亏欠": "把具体的时间、收入、名誉或安全损失写回关系账",
            "依赖": "在职业盲区出现时请对方补位，但不把补位变成服从",
            "敬意": "公开承认对方的能力和独立判断",
            "怨恨": "保留一次没有被道歉抹平的伤害及其边界",
            "共同秘密": "共同决定哪些姓名、地点或旧账暂不公开，并记录理由",
        }[dimension]
        dimension_blocks.append(
            f"### {dimension}\n"
            f"- 可观察证据：引用 `{relation_id}-EV-01` 至 `{relation_id}-EV-08`；{evidence_seed}，并通过{dimension_action}留下痕迹。\n"
            f"- 冲突问题：双方对‘谁有权决定、谁承担代价、谁可以先知道’的判断不一致。\n"
            f"- 发展要求：每个 ARC 至少出现一次具体动作或选择改变该维度；禁止只用旁白宣布关系变化。\n"
            f"- 当前状态：FOUNDATION-EVIDENCE，待 Episode/Character Final 绑定最终场次与镜头。"
        )
    snapshots = []
    for item in evidence:
        snapshot = item["snapshot"]
        snapshots.append(
            f"### {snapshot}\n"
            f"- 关系位置：{kind}；成员/对象：{member_text}。\n"
            f"- Foundation 证据 ID：`{item['evidence_id']}`；阶段：{item['phase']}；候选集窗：{item['episode_window']}；场次 ID：RESERVED。\n"
            f"- 空间：{item['space']}；物件：{item['object']}。\n"
            f"- 可观察动作：{item['observable_action']}；对白意图：{item['dialogue_intent']}\n"
            f"- 进入状态：双方带着各自的现实目标和未偿还债务进入该阶段。\n"
            f"- 不可逆代价：{item['irreversible_cost']}\n"
            f"- 连续性变化：{item['continuity_delta']}\n"
            f"- 离开状态：至少一项七维状态发生可追溯变化；Season/Episode Gate 回填 scene_id、dialogue_id、shot_ids。"
        )
    return f'''---
id: {relation_id}
left: {left}
right: {right}
kind: {kind}
status: FOUNDATION-EVIDENCE
---

# {relation_id}｜{left} × {right}｜{kind}

## 关系命题

{thesis}
关系必须改变人物行动，不承担主线的关系不进入生产稿。

## 双方动机与选择冲突

- {left}：保留自己的目标、秘密和拒绝权；不得被写成只为关系服务。
- {right}：保留自己的目标、秘密和拒绝权；不得被写成只为关系服务。
- 主要冲突：保护/控制、忠诚/诚实、恩情/责任、理想/具体的人之间至少形成一轮不可同时满足的选择。
- 关系回报：不是自动和解，而是学会在旧账仍在时重新协作或重新设定边界。
- 表面行为：{surface}
- 自觉动机：{conscious}
- 未承认动机：{unconscious}
- 情感债务：{debt}

## 七维状态

{chr(10).join(dimension_blocks)}

## 八个快照

{chr(10).join(snapshots)}

## 生产绑定清单

- 最少一场生活活动：把关系放入宋代具体空间（夜市、瓦舍、游船、茶坊、相扑、灯会、修船或看诊等）。
- 最少一次幽默/尴尬：幽默必须改变距离、误解或选择，不作为无关插科。
- 最少一次边界动作：递回物件、让路、站开、拒绝触碰或公开承认欠债。
- 最少一次不可逆代价：关系变化必须带来时间、名誉、收入、资格或安全上的损失。
- 下游待回填：scene_id、dialogue_id、shot_ids、asset_ids、continuity_delta。
'''


def main() -> int:
    data = json.loads(SLOTS.read_text(encoding="utf-8"))
    target = ROOT / "characters/relations/core"
    target.mkdir(parents=True, exist_ok=True)
    evidence_registry = {
        "schema_version": 1,
        "status": "FOUNDATION-EVIDENCE",
        "snapshot_windows": SNAPSHOT_WINDOWS,
        "scene_binding_policy": "scene_id remains RESERVED until Season Gate; candidate evidence is production-bound and traceable.",
        "relationships": [],
    }
    for relation in data.get("relationships", []):
        evidence = build_evidence(relation)
        evidence_registry["relationships"].append(
            {"relation_id": relation["id"], "snapshots": evidence}
        )
        path = target / f"{relation['id'].lower()}.md"
        path.write_text(render(relation, evidence), encoding="utf-8")
        print(path.relative_to(ROOT).as_posix())
    EVIDENCE_PATH.write_text(
        json.dumps(evidence_registry, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(EVIDENCE_PATH.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
