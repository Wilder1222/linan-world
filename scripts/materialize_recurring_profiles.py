from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "characters/03-recurring-citizens-48.md"

AGE_OVERRIDES = {
    "B004": 10,  # source explicitly says 10 岁
    "B006": 57,  # “锁叔”，听力衰退且有长期门户经验
    "B007": 68,  # “独居煎饼老妇”
    "B019": 25,  # “年轻船工”，仍在攒半条自己的船
    "B025": 15,  # source explicitly says 15 岁
    "B032": 58,  # “仓场老吏”，已接近退役经验段
    "B034": 14,  # “递铺少年”
    "B041": 70,  # “蒋阿婆”，北来失乡老人
    "B042": 13,  # source explicitly says 13 岁
    "B047": 22,  # “激进青年”
    "B048": 62,  # “常伯”，前骡队赶车人、失乡老人
}


# The source table already defines each recurring citizen's life pressure and
# terminal echo.  This second layer makes those facts executable: a generator
# can render a distinct daily action, blind spot, choice, cost and recovery
# gesture instead of repeating one generic "street citizen" performance.
RECURRING_PRODUCTION_DETAILS = {
    "B001": {"daily_action": "称药、筛香、折纸包并用炭笔记下交货数", "daily_problem": "儿子的识字钱与香铺可能停工互相挤压", "protect": "儿子的识字机会和一份稳定工钱", "blind_spot": "总把自己的手腕疼和疲惫排在最后", "choice": "先把药材与灯号说明分成两包，再把损耗和责任写回账上", "cost": "主动承认错领会让香铺扣她工钱", "misread": "被同行看成多事、被家人看成不肯顾自己", "ending_action": "在雨棚下重新核对纸包折角，给下一班留下可摸出的区别"},
    "B002": {"daily_action": "削竹篾、浸软竹条、补篮底并试提承重", "daily_problem": "自家漏雨却不断有客人拿坏篮子来催修", "protect": "不靠卖掉摊位也能维持家的屋顶和手艺", "blind_spot": "把先替别人补好东西当成自己有用的证明", "choice": "拆下自家半片旧篾先做担架和灯架", "cost": "屋顶修缮继续拖延，同行还会说他亏本逞强", "misread": "被家人看成不会算账，被同行看成抢功", "ending_action": "收工时把最后一根竹篾插回工具筒，留下可继续修屋的长度"},
    "B003": {"daily_action": "穿针、压线、试袖口并用左手托住酸痛的右腕", "daily_problem": "手腕疼时仍要赶完戏服，否则下月没有房钱", "protect": "典当铺里那把旧银梳和自己的手艺署名", "blind_spot": "把忍痛当成不拖累别人的体面", "choice": "把旧布裁成触感不同的灯号条，并承认自己需要轮班", "cost": "失去一单急活和一部分收入，仍可能被说成娇气", "misread": "被后台当成慢，被亲近人当成不肯求助", "ending_action": "把线头按颜色收进小匣，给手腕缠好布再坐回针线前"},
    "B004": {"daily_action": "烧水、切葱、数碗并在灶台边记住谁少吃了一只馄饨", "daily_problem": "想证明自己能帮忙，却常被大人赶去看火", "protect": "自己被认真当成能做事的大孩子的机会", "blind_spot": "看见异常就急着说，没先确认第二遍", "choice": "在大人漏记时先回头核问，再指出独居老人未领饭", "cost": "错报一次会让掌柜少赚一顿饭，也让同伴不再立刻信他", "misread": "被大人当成爱炫耀，被同龄人当成告密", "ending_action": "把油纸上的名字折出一个小角，第二天再逐户核对"},
    "B005": {"daily_action": "压豆花、切板、收水并把当天豆渣分给邻户", "daily_problem": "女儿嫁妆逼近，但卖掉摊位会断掉全家生计", "protect": "女儿的体面和一块能传下去的豆腐板", "blind_spot": "把不卖摊位当成唯一的父亲责任", "choice": "把豆腐板改成浮水托盘，先救药包再谈嫁妆", "cost": "摊位被水泡坏，婚嫁计划必须延期", "misread": "被女儿看成固执，被邻户看成不肯出钱", "ending_action": "晾干豆腐板后重新刨平边缘，不把损坏说成英雄功勋"},
    "B006": {"daily_action": "摸锁簧、听回声、配钥匙并用手背确认门缝是否进水", "daily_problem": "听力下降后仍怕街坊把他当成无用老人", "protect": "门户安全和自己仍被需要的尊严", "blind_spot": "不肯让别人复述，容易把没听清当成听懂", "choice": "承认听漏一段口令，改用手势和锁痕核验再开仓", "cost": "失去一笔夜间代看门户的活，且要面对旁人怀疑", "misread": "被年轻人当成固执，被旧同伴当成衰了", "ending_action": "把新配的钥匙分成两串，用刻痕而不是耳朵记编号"},
    "B007": {"daily_action": "和面、摊饼、听油响并把卖剩的饼包给熟客", "daily_problem": "视力变差却不愿搬去侄家，独居账目越来越难记", "protect": "自己决定住在哪里、给谁送饼的自由", "blind_spot": "把接受照料误认成被赶走", "choice": "允许净圆替她抄账，同时主动登记自己几日未领饭", "cost": "失去独自掌账的体面，侄家仍可能催她搬走", "misread": "被侄家看成不知好歹，被邻里看成爱逞强", "ending_action": "用手摸饼边的焦痕，照旧给下一户留一块"},
    "B008": {"daily_action": "核酒钱、安排后厨席位并把欠账写在不同颜色的签上", "daily_problem": "权贵要求免费开席，祖楼的木梁又急需修", "protect": "祖上传下的楼和不被权贵拿走的账本", "blind_spot": "把拒绝白吃白拿看得比员工当日饭钱还重要", "choice": "开放后厨配餐但坚持逐笔记账，拒绝抹去欠账", "cost": "失去一桌权贵生意，楼的修缮继续拖延", "misread": "被客人看成小气，被伙计看成不识时务", "ending_action": "收摊后把湿掉的账页压平，先记今日损失再关门"},
    "B009": {"daily_action": "调颜料、糊纸面具、试戴并在背面刻下自己的小记号", "daily_problem": "后台活很多，却没人愿意把署名给一个小工", "protect": "成为署名画工的机会和弟弟安全回家的路", "blind_spot": "用抢先署名掩盖自己害怕再次被忽略", "choice": "把剩余颜料改成大字路标，并把功劳写给共同做工的人", "cost": "错过一次个人署名，弟弟也会埋怨她把颜料用掉", "misread": "被同行看成不争，被弟弟看成不顾家", "ending_action": "在路标背面留下自己的小记号，却不把它写到正面"},
    "B010": {"daily_action": "熬粥、分咸菜、记夜班人数并把锅底留给最后来的客人", "daily_problem": "弟弟欠债跑路，摊位租金和照料人情同时追来", "protect": "一个不靠弟弟也能站住的夜摊", "blind_spot": "把照顾所有人当成追回弟弟的替代", "choice": "把夜粥摊改成补给与失联询问点，却先留出本钱", "cost": "当天少卖一锅，弟弟的债主仍会来催", "misread": "被熟客看成不够大方，被亲人看成只会做生意", "ending_action": "把锅盖留一条缝，清点明日米量后才给自己盛粥"},
    "B011": {"daily_action": "绑高台、试木楔、用膝盖支撑梯脚并记录疼痛位置", "daily_problem": "膝伤让他怕自己只剩过去的杂技名声", "protect": "不靠冒险表演也能被需要的手艺", "blind_spot": "总想用一次高处动作证明自己还行", "choice": "负责挂灯却拒绝冒险翻梁，把危险位置交给稳手的人", "cost": "失去一次能让观众喝彩的机会，名声恢复更慢", "misread": "被旧友看成胆小，被孩子看成没本事", "ending_action": "下台先揉膝再收绳，不把安全说成退缩"},
    "B012": {"daily_action": "敲更、听巷声、在木牌上刻下时刻并避开醉汉", "daily_problem": "想让儿子别继承夜差，却知道自己听见的秘密越来越多", "protect": "儿子有选择职业的自由和街坊的夜间秩序", "blind_spot": "把沉默当作保护，可能让错误时刻继续流传", "choice": "用更点节奏公开消息先后，不替任何一方藏错", "cost": "失去一段安稳夜差，也可能得罪发错消息的人", "misread": "被官署看成多嘴，被家人看成把危险带回家", "ending_action": "敲完最后一更把木槌放远，等旁人复述后再记时"},
    "B013": {"daily_action": "量木、凿榫、试台脚并把多余竹料退回 B002", "daily_problem": "想娶季素娘，却不敢承认木作收入不稳", "protect": "自己的婚事选择和不靠谎话维持的手艺", "blind_spot": "用加班搭台逃避谈清收入与婚事", "choice": "先搭临时高台救人，再把真实欠款和婚期告诉季素娘", "cost": "婚期要延期，同行也会知道他手头紧", "misread": "被恋人看成不诚实，被同行看成没担当", "ending_action": "把榫头重新楔紧，回家前留下写明欠料的木牌"},
    "B014": {"daily_action": "磨墨、抄信、校地名并把废纸按可用面翻过来", "daily_problem": "出身贫寒，署名抄本的愿望总被文人一句话压回去", "protect": "自己能被看见的文字工作和 B019 的信任", "blind_spot": "过度替别人润色，可能掩掉原话里的迟疑", "choice": "把口述消息照原意抄下并标注不确定处，不替人补全", "cost": "失去一次体面抄工，读者可能觉得他不够聪明", "misread": "被文人看成粗拙，被熟人看成不肯帮忙", "ending_action": "把墨迹未干的纸压在镇纸下，等说话人亲自核名"},
    "B015": {"daily_action": "刻线、试版、清木屑并用旧布包住受伤手指", "daily_problem": "想买自己的刻刀套，旧伤却让每一次深刻都更慢", "protect": "能独立署名的刻版手艺和不被抹掉的版本来源", "blind_spot": "把版面整齐放在人的阅读困难之前", "choice": "设计带缺角的更正版，并公开旧版曾经从自己手里出过", "cost": "失去一笔旧版重刻收入，手伤恢复更慢", "misread": "被旧主顾看成砸招牌，被同行看成背叛行规", "ending_action": "把新刻刀套挂到墙上，先在废木上试一刀再开工"},
    "B016": {"daily_action": "刷浆、对齐纸边、压裱并检查潮气是否从背面返上来", "daily_problem": "想开自己的铺，却被婚事与工坊分成两处牵住", "protect": "只署自己名字的手艺和与邬木生的平等关系", "blind_spot": "把不署别人名当成保护自己，忽略共同劳动", "choice": "用旧布纸木条做耐雨地图板，并在背面写共同制作者", "cost": "暂时失去一单高价装裱，自己的开铺钱更少", "misread": "被师傅看成不守规矩，被恋人看成把名声放第一", "ending_action": "把地图板边角磨平，留出能让后来者继续修补的槽"},
    "B017": {"daily_action": "辨纸色、看印记、听买家问价并把夸大的来历写在心里", "daily_problem": "债务逼他夸大作品来历，进入收藏圈的愿望越来越像骗局", "protect": "翻身的机会和自己不被彻底揭穿的体面", "blind_spot": "把交易成功当成作品真实价值的证明", "choice": "主动公布错误旧图来源，先让买家知道自己曾经骗人", "cost": "失去一笔大买卖和一部分信用，债务仍在", "misread": "被同行看成软弱，被债主看成自毁", "ending_action": "把旧图卷好放回柜底，在新标签上写清来源等级"},
    "B018": {"daily_action": "编目录、核页码、按版本扎册并把弟弟的字帖藏在账册下", "daily_problem": "供弟弟读书，却从未被当成真正的读书人", "protect": "弟弟的读书机会和自己作为目录女工的判断权", "blind_spot": "把照料弟弟的责任变成不许别人帮忙", "choice": "负责版本目录并公开最新版，同时把自己的名字写进工作记录", "cost": "失去一次替别人隐名的工钱，弟弟会觉得她太张扬", "misread": "被文人看成越位，被家人看成争名", "ending_action": "给弟弟留一页空白纸，自己在目录末页写下日期"},
    "B019": {"daily_action": "缚缆、看潮、试舵并把船头偏差记在木片上", "daily_problem": "想买半条自己的船，急于证明胆量却怕被当成毛头小子", "protect": "成为能独当一面的船工的资格", "blind_spot": "把承认看错水势当成失去尊严", "choice": "在错误救援路线后主动回传更正，先让别人绕开危险", "cost": "失去一次掌舵机会和船帮信任，买船计划后延", "misread": "被少年看成不够勇，被师傅看成不稳", "ending_action": "把看错的水纹画在船板背面，下一次出航前先给新人看"},
    "B020": {"daily_action": "刨龙骨、试木纹、敲船腹并把旧钉按长短分格", "daily_problem": "想让儿子留岸学手艺，却被船坊欠料和洪水逼着出船", "protect": "儿子选择岸上生活的权利和船坊的手艺", "blind_spot": "把替儿子决定安全路线当成爱", "choice": "组织抢修青鹞但公开说明不是每条船都能保住", "cost": "失去几块最好的木料和一艘旧船的声誉", "misread": "被船户看成不够拼命，被儿子看成不信他", "ending_action": "把可用木料分三堆，最后一堆留给岸上学徒"},
    "B021": {"daily_action": "撑篙、认水色、系渡牌并在风变时先收短线", "daily_problem": "丧夫后独自撑渡，渡牌是收入也是唯一的安全感", "protect": "自己掌握渡船与不被替她决定的生活", "blind_spot": "害怕失去渡牌，容易把所有停渡都看成投降", "choice": "停高风险航段，同时公开一条可核验的安全短线", "cost": "失去半日渡钱，还要承受船户抱怨", "misread": "被客人看成胆小，被官署看成抗令", "ending_action": "收篙前把渡牌擦干，给下一班写明风向"},
    "B022": {"daily_action": "烧茶、稳船、收空杯并把湿草席压在舱门边", "daily_problem": "想让女儿上岸，却舍不得水上社群和一船熟客", "protect": "女儿的选择与水上人互相照料的关系", "blind_spot": "把替女儿挡风浪当成唯一的爱", "choice": "把茶船改成伤员中转船，同时让女儿决定是否留下", "cost": "茶摊货物损失，母女仍会因去留争执", "misread": "被女儿看成控制，被船户看成临阵改行", "ending_action": "把茶壶放到舱角，先清点伤员名字再煮下一壶"},
    "B023": {"daily_action": "分脚夫、称货重、排队次序并用手势提醒后排", "daily_problem": "想加入大行会，却常在工钱与兄弟情之间摇摆", "protect": "兄弟们不被当成可替换的力气和自己的入会机会", "blind_spot": "把维持队伍听话当成保护队伍", "choice": "用分组法建立连续搬运线，先公开每人负重和工钱", "cost": "失去行会推荐，亲友也会觉得他把账算得太细", "misread": "被兄弟看成冷硬，被行会看成不服管", "ending_action": "收工后把分组木牌归还，不把自己留在队伍最前面"},
    "B024": {"daily_action": "剖鱼、撒盐、翻晒架并用鼻子和指腹判断水味", "daily_problem": "旺季还没过就欠下盐钱，水味变化可能让整批鱼卖不出去", "protect": "一季收入和自己对水的经验不被嘲笑", "blind_spot": "太相信鼻子，容易把个人经验当成完整证据", "choice": "先记录水味变化，再找别的水边人交叉核验", "cost": "延迟出货，短期少赚一批钱", "misread": "被商贩看成故弄玄虚，被家人看成耽误旺季", "ending_action": "把一小撮盐封在纸里，注明日期而不是只说味道不对"},
    "B025": {"daily_action": "打绳结、试浮力、收缆并把每个结的用途讲给小伙伴", "daily_problem": "想跟大船远航，却只能守绳，父母把冒险都挡在岸上", "protect": "自己成为真正船工的可能和父母的信任", "blind_spot": "把急着出海当成证明长大的唯一办法", "choice": "用绳结标出淹水深浅，先承担留岸的工作", "cost": "错过一次远航名额，仍被同伴笑作小孩", "misread": "被同伴看成胆怯，被父母看成终于听话", "ending_action": "把最牢的结拆开重打，给下一个孩子说明为什么"},
    "B026": {"daily_action": "盘点米面、按锅次分库存并把剩菜改成下一顿小食", "daily_problem": "替亲弟还债，自己开小食肆的本钱总被挪走", "protect": "不靠亏空也能开张的小食肆梦想", "blind_spot": "把会算库存当成可以扛住所有人的理由", "choice": "按库存法公开可供几顿饭，并先留下后厨人的口粮", "cost": "失去一部分讨好客人的余量，亲弟会说她不肯帮", "misread": "被客人看成吝啬，被家人看成不讲情面", "ending_action": "关灶后在锅底写下余量，明早照数采购"},
    "B027": {"daily_action": "看门牌、问租期、记空屋并在酒席边收回旧欠条", "daily_problem": "多数信用已经失去，却还想靠一次大买卖翻身", "protect": "最后一点可交易的信用和自己不被赶出酒楼的体面", "blind_spot": "把知道空屋当成拥有解决方案", "choice": "交出熟悉的空屋名单，却不承诺每间都安全可住", "cost": "失去一次中介佣钱，旧债主仍能找到他", "misread": "被安置点看成投机，被酒楼看成泄密", "ending_action": "把空屋名单分成已核与未核两栏，不再用一张嘴包圆"},
    "B028": {"daily_action": "闻香、验袋、记到货日并在客舍墙上标出延误路线", "daily_problem": "货船延误使跨城信誉和账期同时逼近断裂", "protect": "不靠抬价也能守住的跨城信誉", "blind_spot": "把守约看得比解释风险更重要", "choice": "用外地价格和到货日证明短缺被放大，并承认自己也会亏", "cost": "失去一笔急售利润，违约风险仍由自己承担", "misread": "被客商看成拆台，被船户看成只会算价", "ending_action": "把香料袋封好，账上同时写成本、损失和未收款"},
    "B029": {"daily_action": "换床单、记入住行李、清点钥匙并在晒衣处分开湿布", "daily_problem": "想赎回妹妹长工契，却没有稳定的额外钱路", "protect": "妹妹能离开长工契的选择和客舍里每个人的下落", "blind_spot": "把记住别人行李当成替别人做决定", "choice": "用床铺与行李变化建立仍在客舍的人名单，并先征得同意", "cost": "失去一段能换钱的私密消息，赎契更慢", "misread": "被客人看成窥探，被妹妹看成只会等", "ending_action": "把钥匙按房号挂好，回头确认每个名字都有人认领"},
    "B030": {"daily_action": "验货、看风向、封车并把绳索分给不同工位", "daily_problem": "季风前必须回港，却担心被当外人而得不到信任", "protect": "货队安全与自己不被标签决定的信誉", "blind_spot": "过度强调货物和契约，忽视本地人的恐惧", "choice": "交出货车和绳索救援，同时按契约记录自己的损失", "cost": "损失货物和回港时间，仍可能被怀疑逐利", "misread": "被临安人看成算账冷漠，被同乡看成软弱", "ending_action": "在索赔单上先写救援使用记录，再签自己的名字"},
    "B031": {"daily_action": "抄时刻、盖印、分原稿与誊本并把错字圈出", "daily_problem": "想通过吏考升等，却怕留下越权记录", "protect": "原始记录不被重抄抹掉，也保住自己继续做事的资格", "blind_spot": "把留痕当成足以替自己说话，忽略当下要有人站出来", "choice": "保存原始时刻记录并在交卷前标出被要求改写的地方", "cost": "升等机会受损，可能被上司记恨", "misread": "被同僚看成不合群，被上司看成不懂规矩", "ending_action": "把原稿与誊本分层收好，给后来者说明差异"},
    "B032": {"daily_action": "看粮袋缝线、核到货数、在仓门上记潮痕并洗手", "daily_problem": "早知账目有问题却想平安熬到退役", "protect": "退役前不再牵连家人的平稳生活", "blind_spot": "把沉默当成不扩大损失，实际让假账继续有效", "choice": "在粮火后承认自己签过不实到货单，并交出原始记号", "cost": "失去退役安稳和名声，可能连累旧同僚", "misread": "被同僚看成临老反水，被家人看成自找麻烦", "ending_action": "把旧签押按日期排好，不再撕掉最难看的那张"},
    "B033": {"daily_action": "巡门、验腰牌、问路并把听令内容复述给下一班", "daily_problem": "想得到高问认可，却把听令当成最安全的职业方式", "protect": "家人的平安与自己不被军法惩罚的身份", "blind_spot": "把服从误认成不伤人的中立", "choice": "在高问违令后先停在原地，随后独自放行一批医者", "cost": "失去一次升迁机会，可能被同袍视为不可靠", "misread": "被上官看成叛逆，被街坊看成迟来的好人", "ending_action": "交班时把放行理由写清，不让下一班替自己背黑锅"},
    "B034": {"daily_action": "验印、折信、系递牌并在雨里选择不积水的巷线", "daily_problem": "想成为正式递夫，姐姐却怕他跑危险差事", "protect": "自己被信任的递送能力和姐姐的安心", "blind_spot": "把跑得快当成把事情做对", "choice": "绕开封锁送更正令，但先核验印记再出发", "cost": "失去一次正式递夫推荐，还会被姐姐骂冒险", "misread": "被官差看成越权，被姐姐看成不听话", "ending_action": "把递牌擦干后交回，不把秘密路线当成自己的功劳"},
    "B035": {"daily_action": "排军阵、看门宽、用手势引导人流并偷偷摸孩子牙包", "daily_problem": "想攒军饷给孩子治牙病，却怕服从曹肃也怕军法", "protect": "孩子治病的钱与不把城门变成敌人的底线", "blind_spot": "把站稳岗位当成唯一能保护家人的办法", "choice": "开门时把军阵改成引导人流，公开说明谁能先过", "cost": "违背旧操典，军饷和升迁都可能受损", "misread": "被同袍看成心软，被百姓看成仍是拦门的人", "ending_action": "收队后把引导手势教给下一班，自己才去看孩子"},
    "B036": {"daily_action": "搓洗泥水、辨衣角污痕、拧布并把军衣按队伍分开", "daily_problem": "想让丈夫别逞强，但浆洗收入又是家里不能少的钱", "protect": "丈夫回家和自己不被当作附属劳力的收入", "blind_spot": "把辨出行踪当成可以替丈夫承担危险", "choice": "从泥水位置指出某队去过被隐瞒的仓区，并保留衣物证据", "cost": "失去军营浆洗活，丈夫也可能被牵连", "misread": "被军营看成多嘴，被丈夫看成把家事带进公事", "ending_action": "把证物布条单独晾起，照常洗下一盆衣服"},
    "B037": {"daily_action": "碾药、筛粉、分包并把不同药材的气味记在纸角", "daily_problem": "想学会识药，却长期只被当作搬药的力气活", "protect": "成为识药人的机会和自己不被替代的手艺", "blind_spot": "太急于证明能识药，可能越过医工确认", "choice": "建立药包形状编码，同时把不确定的药名交给 B038 复核", "cost": "失去一次独立记功机会，仍被叫小工", "misread": "被老药工看成抢学，被病人看成不够快", "ending_action": "把药包按形状排齐，留下一个空位表示待核"},
    "B038": {"daily_action": "进针、敷膝、洗手并用眼睛休息的间隙摸针盒边", "daily_problem": "想保住手稳的名声，却开始害怕眼花", "protect": "病人信任与自己还能救人的手", "blind_spot": "把亲自下针当成不辜负名声，拖延交给年轻人", "choice": "主动把精细操作让给年轻人，转做分诊和复核", "cost": "失去一部分诊金和“最稳的手”名声", "misread": "被病人看成退缩，被同行看成老了", "ending_action": "把针盒交接表写完，给年轻人指出自己曾经犯过的错"},
    "B039": {"daily_action": "分粥、排队、看碗底并把熟人和陌生人分开登记", "daily_problem": "想让施粥公平，却怕寺院被挤垮", "protect": "不让施舍变成争抢的秩序和寺院继续救人的能力", "blind_spot": "把公平理解成一模一样，忽略老人、孩子和伤员的差异", "choice": "用分批领粮和特殊通道减少踩踏，并公开规则", "cost": "失去一部分熟客的好感，寺院仍要承担短缺", "misread": "被熟人看成不讲情，被外来人看成官府口气", "ending_action": "收队后把空碗叠好，记录哪条规则需要修正"},
    "B040": {"daily_action": "换药、煮水、记录病人睡眠并把自己的饭留到最后", "daily_problem": "想照顾病母又不愿离开公棚，身体已经先撑不住", "protect": "病母的照料与照料者也能喘气的权利", "blind_spot": "把不休息当成不抛下任何人的证明", "choice": "建立轮班表并承认自己需要离岗一刻钟", "cost": "错过一名病人的第一声求助，仍会被人责怪", "misread": "被病棚看成不够尽责，被家人看成不肯回家", "ending_action": "按轮班表坐下吃完半碗饭，再回去换药"},
    "B041": {"daily_action": "劈草、编席、摸结头并向来客重复几个北地地名", "daily_problem": "只想知道失散孙女是否活着，却不断被当成可怜符号", "protect": "孙女的名字和自己作为记得很多事情的人格尊严", "blind_spot": "把记住旧地当成能找回家人的保证", "choice": "把北地姓名和旧关系补入失联簿，同时接受别人不能立刻找到", "cost": "承认线索可能无结果，失去继续等一个奇迹的安慰", "misread": "被好心人看成不知足，被激进者看成不肯北归", "ending_action": "编完一张草席，把孙女名字写在席背而不是喊给人听"},
    "B042": {"daily_action": "排队领饭、收集旧牌、练写自己的名字并帮小孩辨认颜色", "daily_problem": "想有一张正式名牌，却总被当成谁家的附带孩子", "protect": "名字被正确登记的权利和不再被随手带走的安全", "blind_spot": "把跟熟人走当成唯一安全，可能漏掉无名孩子", "choice": "先逐一登记无名儿童，再决定自己跟谁走", "cost": "错过一顿熟人带来的饭，也可能短暂和照看她的人失散", "misread": "被大人看成不懂事，被同龄人看成爱管闲事", "ending_action": "把写有自己名字的牌挂在胸前，也替下一个孩子写一张"},
    "B043": {"daily_action": "抄账、核车数、复制运输页并把涂改处留在边上", "daily_problem": "想成为大掌柜，却把黎见山的成功当成唯一范本", "protect": "成为能看懂全链条的人和自己不被假账吞掉的前程", "blind_spot": "把数字改得漂亮当成帮团队渡过难关", "choice": "复制关键运输页并承认自己曾主动替数字找借口", "cost": "失去升任掌柜的机会，旧同僚也会断交", "misread": "被上司看成背叛，被书吏看成晚来的清白", "ending_action": "在新账页留出更正栏，不再把空白填成好看的数字"},
    "B044": {"daily_action": "验马、护账箱、看路面并用身体挡住货车转弯处", "daily_problem": "想退行开马店，却习惯把护货排在人命前面", "protect": "退行后的生活和自己能守住的信用", "blind_spot": "把货物完整当成对雇主负责的全部", "choice": "粮火中弃货救人，并公开失货数量与责任", "cost": "失去行内信用，开马店本钱被烧掉一部分", "misread": "被东家看成叛徒，被获救者看成理所当然", "ending_action": "把烧坏的缰绳挂在新马棚门口，提醒自己先看人"},
    "B045": {"daily_action": "看田水、修短堤、挑菜进城并在租契边标出欠租日", "daily_problem": "想保住租田，粮价高时又忍不住想多卖一点", "protect": "一块能继续耕种的田和不被债逼走的家", "blind_spot": "把多卖一担粮当成唯一翻身机会", "choice": "公开短堤修建中自己曾被征劳力的事实，并先保住下游田户", "cost": "少卖一批粮，租田仍可能被收回", "misread": "被买家看成不肯发财，被佃户看成不够仗义", "ending_action": "把租契重新压在灶边，第二天照旧下田"},
    "B046": {"daily_action": "分粥、抱孩子、查布包并把危险路线画在木板上", "daily_problem": "想让两个孩子在临安稳定，却不想被再次推回北归路", "protect": "孩子们的安稳和自己选择留下的权利", "blind_spot": "把保护孩子变成替所有北来人决定去留", "choice": "公开反对截粮，先带家属撤离危险点而不替别人宣誓", "cost": "失去施粥组织位置，激进派会说她背叛北人", "misread": "被贺兰度一派看成软弱，被官署看成不可靠", "ending_action": "把孩子的布包系紧，回头为另一个家庭指出安全路"},
    "B047": {"daily_action": "抄口号、组织人群、检查火把并在争执时抢先发言", "daily_problem": "想做一件让天下记住北方的事，却把愤怒越说越像命令", "protect": "北方人的记忆不被临安忘掉，以及自己被看见的价值", "blind_spot": "把共同记忆偷换成替所有人决定目的地", "choice": "截粮时放下火把，转身帮助转运伤者", "cost": "失去领袖位置，旧同伴会把他当叛徒", "misread": "被激进派看成软弱，被临安人看成仍不可信", "ending_action": "把火把浸灭后留在救援队末尾，不再站在口号最前面"},
    "B048": {"daily_action": "认牲口脚印、调车绳、看泥深并按旧路线避开低洼地", "daily_problem": "想把故乡地名教给下一代，却不相信自己还能回去", "protect": "故乡记忆和晚年仍能派上用场的身体经验", "blind_spot": "把回不去解释成只能向北，忽略别人已经选择留下", "choice": "组织牲口避开积水把物资送上高地，同时承认不替别人决定归处", "cost": "失去最后一趟能带他回北地的机会，身体也更差", "misread": "被青年看成拖后腿，被南方街坊看成只会讲旧事", "ending_action": "教孩子看泥印和地名，最后把缰绳交给年轻人"},
}


def parse_rows() -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    section_residence = "临安市井生活圈"
    section_map = {
        "A": "鹤鸣巷与香药街",
        "B": "春台瓦舍与夜市",
        "C": "西泠书坊街",
        "D": "钱塘码头与漕运",
        "E": "停云酒肆、客舍与商旅",
        "F": "城务司、临安府与军伍",
        "G": "医馆、寺院与流民救济",
        "H": "汇川行、北归社与城外仓运",
    }
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^##\s+([A-H])\.", line)
        if heading:
            section_residence = section_map[heading.group(1)]
            continue
        match = re.match(r"^\|\s*(B\d{3})\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$", line)
        if not match:
            continue
        short_id, name, occupation, wish_pressure, relations, echo = match.groups()
        rows[short_id] = {
            "name": name, "occupation": occupation, "wish_pressure": wish_pressure,
            "relations": relations, "echo": echo, "ecosystem": section_residence,
        }
    return rows


def age_for(short_id: str) -> int:
    if short_id in AGE_OVERRIDES:
        return AGE_OVERRIDES[short_id]
    return 22 + ((int(short_id[1:]) * 7) % 31)


def age_basis(short_id: str) -> str:
    if short_id in AGE_OVERRIDES:
        return "基于名册称谓、明示年龄或职业/家庭阶段的生产推定；Character Foundation 人工审读确认。"
    return "按生活圈职业与家庭阶段生成的生产推定；Character Foundation 人工审读确认。"


def render(short_id: str, data: dict[str, str], roster_record: dict) -> str:
    stable_id = roster_record["id"]
    # The source table uses `primary / alias`; Canon stores the primary name
    # in `name` and the alias separately for stable identity matching.
    name = data["name"].split("/")[0].strip()
    aliases = roster_record.get("aliases", [])
    alias_text = "[" + ", ".join(f'"{alias}"' for alias in aliases) + "]"
    relations = [part.strip() for part in data["relations"].replace("；", "；").split("；") if part.strip()]
    details = RECURRING_PRODUCTION_DETAILS.get(short_id, {})
    if not details:
        raise ValueError(f"missing production details for {short_id}")
    relation_lines = "\n".join(
        f"- REL-B-{short_id[1:]}-{index:02d}：{item}；该关系会在日常选择中形成具体互助或摩擦，双方仍保留自己的工作压力和未偿还债务。"
        for index, item in enumerate(relations[:2], 1)
    )
    if len(relations) < 2:
        relation_lines += "\n- REL-B-{0}-02：跨生活圈邻里关系，具体事件由 Season Gate 绑定。".format(short_id[1:])
    residence = f"{data['ecosystem']}工作圈；具体摊位、住处与班次由 Season Gate 绑定"
    return f'''+++
id = "{stable_id}"
tier = "B"
name = "{name}"
aliases = {alias_text}
age_y0 = {age_for(short_id)}
occupation = "{data["occupation"]}"
residence = "{residence}"
economic_source = "{data["occupation"]}的日常收入与临时活计"
pov_budget = {roster_record["pov_budget"]}
minimum_episode_coverage = 2
status = "FOUNDATION-LOCKED"
+++

# {stable_id}｜{name}

> B 级人物先锁定可持续的生活状态，实际母集、微短章和回访由下游 Gate 绑定。

## 基础状态

- 职业 / 身份：{data["occupation"]}。
- 年龄依据：{age_basis(short_id)}
- 小愿望与现实压力：{data["wish_pressure"]}。
- 关系底稿：{data["relations"]}。
- 生活圈：{data["ecosystem"]}；首次日常应在该生活圈内完成一个完整劳动流程，不能只以主线信息开场。
- 常态行为：{details['daily_action']}；先完成眼前的劳动，再决定是否介入别人的事。
- 日常阻力：{details['daily_problem']}；错误来自时间压力、信息缺口或生计压力，不来自愚蠢。
- 行为资产：危机中的能力必须由此前展示的工具、身体记忆或职业流程产生；不突然获得主角权限。

## 坚守七问

1. 最想保护什么：{details['protect']}。
2. 这种坚守为什么形成：它来自“{data['occupation']}”的重复劳动，也来自“{data['wish_pressure']}”中的现实压力。
3. 在保护它时伤害过谁：{details['blind_spot']}会让亲近者、同行或同一生活圈的人先承担后果。
4. 两件都正确的事冲突时选择什么：{details['choice']}。
5. 为此具体放弃什么：{details['cost']}。
6. 谁会误解或离开：{details['misread']}。
7. 没有回报是否仍承认选择属于自己：是；职业回响不等于人生奖励。

## 非中央关系

{relation_lines}

## 终局职业回响

{data["echo"]}。该能力必须先在早期日常状态中出现一次，并在终局承担可见的具体任务；任务可能成功、失败或只减少一部分损失。

## 四个 Foundation 状态

### Y0-OPEN
目标：{details['protect']}；动作：{details['daily_action']}；阻力：{details['daily_problem']}；误判：{details['blind_spot']}；余波：小愿望暂时没有解决，但人物留下了可回访的工具、账目或身体记忆；不以主线事件开场。

### 首次日常
目标：完成一次“{data['occupation']}”流程；可拍动作：{details['daily_action']}；现场小麻烦：{details['daily_problem']}；选择：先解决眼前的具体人或物，再决定是否说出观察；代价：{details['cost']}；移交：该工具、记录或身体经验以后可被自己或同圈人物调用。

### 终局职业回响
目标：把既有职业能力转成公共协作；动作：{data["echo"]}；选择：{details['choice']}；不可逆代价：{details['cost']}；关系余波：{details['misread']}；职业能力进入公共协作，但旧债、损失和误解不自动清零。

### ENDING
回到自己的工作现场：{details['ending_action']}；未解决问题：{details['cost']}；人物不获得自动奖励，最终镜头不把人物封成“群众英雄”。

## 待集成人同步

- 第二次 POV、母集覆盖、回访和 AIGC 资产由 Season/Episode/Final Gate 写入。
- 年龄为职业状态与原有名册的生产推定，需在 Character Foundation 人工审读中确认。
'''


def main() -> int:
    rows = parse_rows()
    roster = __import__("json").loads((ROOT / "qa/character-roster.json").read_text(encoding="utf-8"))
    by_short = {item["id"].replace("CHR-B-", "B"): item for item in roster["named_characters"] if item["tier"] == "B"}
    for short_id, data in sorted(rows.items()):
        record = by_short.get(short_id)
        if record is None:
            continue
        path = ROOT / record["profile_path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(short_id, data, record), encoding="utf-8")
        print(path.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
