from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "characters/01-central-cast-12.md"

PEOPLE = [
    ("CHR-L1-01", "沈蘅", "", 22, "沈家香铺调香师、辨货人", "鹤鸣巷沈家香铺后院", "香铺调香、辨货与家业分成", 52, 24, "shen-heng", ["CHR-A2-03", "CHR-A1-02"], ["继承父亲记录", "允许被更正"]),
    ("CHR-L1-02", "柳十四", "柳望舒", 25, "春台瓦舍歌伎、曲作者", "春台后巷艺人合住院", "演出、作曲与艺人分成", 44, 24, "liu-shisi-liu-wangshu", ["CHR-A1-04", "CHR-B-009"], ["用掌声保护自己", "用本名承担讲述"]),
    ("CHR-L1-03", "周砚之", "", 24, "画师、抄图者、民间测绘人", "西泠书坊街一间狭小楼上", "抄图、装裱与委托测绘", 42, 24, "zhou-yanzhi", ["CHR-A2-07", "CHR-B-015"], ["把混乱画成秩序", "让普通人的路留在图上"]),
    ("CHR-L1-04", "裴九娘", "", 31, "水路信使、前镖师、青鹞船主", "青鹞与钱塘码头船户院落", "水路信使、护送与船运", 46, 24, "pei-jiuniang", ["CHR-A1-08", "CHR-B-019"], ["接下的信必须送到", "守住寄信人的秘密"]),
    ("CHR-L1-05", "顾行舟", "", 29, "停云酒肆掌柜、前镖师与边地护送人", "停云酒肆二楼", "酒肆经营、护送旧债与信息交换", 46, 24, "gu-xingzhou", ["CHR-A1-08", "CHR-B-020"], ["先替别人挡危险", "把选择还给对方"]),
    ("CHR-L2-01", "陆清和", "", 45, "沈家香铺实际掌柜", "鹤鸣巷沈家香铺", "香铺经营、账目与货品周转", 30, 16, "lu-qinghe", ["CHR-A1-01", "CHR-B-001"], ["先让家人活下来", "不再替女儿冻结选择"]),
    ("CHR-L2-02", "林阿沅", "", 18, "馄饨铺帮掌柜、街坊生活记录者", "沈三娘馄饨铺后院", "餐食、赊账记录与街坊照料", 28, 16, "lin-ayuan", ["CHR-A1-01", "CHR-B-010"], ["记住每个人的饭量", "先核验再传播"]),
    ("CHR-L2-03", "余青禾", "", 21, "小济堂医徒、病例记录者", "小济堂后院", "医馆抄方、诊疗协助与药材整理", 26, 16, "yu-qinghe", ["CHR-A1-03", "CHR-B-037"], ["证明自己先看见", "把错误留在病例上"]),
    ("CHR-L2-04", "高问", "", 38, "城务司执行吏、封锁与开路负责人", "城务司值房", "官俸、差役与程序执行", 24, 16, "gao-wen", ["CHR-A1-06", "CHR-B-035"], ["照章办事以求不坏", "承认规则正在伤人"]),
    ("CHR-L3-01", "宋惟敬", "", 47, "临安府转运与城务总协调", "临安府署后宅", "官俸、调度权与制度信用", 28, 12, "song-weijing", ["CHR-A1-06", "CHR-A1-08"], ["让一城服从一个判断", "拆掉自己垄断的判断"]),
    ("CHR-L3-02", "黎见山", "", 53, "汇川行大掌柜、粮运与借贷网络掌控者", "汇川行内宅", "粮运、借贷与商号利润", 24, 12, "li-jianshan", ["CHR-A1-07", "CHR-B-043"], ["让供应不断", "开仓并承认罪责"]),
    ("CHR-L3-03", "贺兰度", "", 34, "北归社激进组织者、北方旧族之后", "北归社学舍与流民安置点之间", "演说、组织与旧族人脉", 20, 12, "helan-du", ["CHR-A1-05", "CHR-B-046"], ["替失乡者记住故土", "先问每个人想去哪"]),
]


def source_sections() -> dict[str, str]:
    text = SOURCE.read_text(encoding="utf-8")
    chunks = re.split(r"(?m)^## CHR-", text)
    result: dict[str, str] = {}
    for chunk in chunks[1:]:
        first, _, body = chunk.partition("\n")
        stable_id = "CHR-" + first.split("｜", 1)[0].strip()
        result[stable_id] = body.strip()
    return result


def render(person: tuple, source: str) -> str:
    stable_id, name, alias, age, occupation, residence, income, pov, coverage, slug, relation_people, spine = person
    aliases = f'["{alias}"]' if alias else "[]"
    relation_lines = "\n".join(
        f"- REL-NC-{stable_id[-2:]}-{index:02d} `{other}`：跨生活圈关系，首要证据待 Season Gate 绑定具体母集。"
        for index, other in enumerate(relation_people, start=1)
    )
    states = [
        ("Y-13", f"{name}在十三年前的生活位置已形成当前职业与债务；源稿记录为：{spine[0]}。"),
        ("Y0-OPEN", f"面对春信重新出现，{name}的当季目标是：{spine[0]}。"),
        ("ARC1-END", f"{name}第一次把个人经验转成可被他人复核的行为，仍保留错误可能。"),
        ("ARC2-END", f"{name}在秩序、收入或关系压力下作出一次不完美选择，并承担可见损失。"),
        ("ARC3-END", f"{name}承认原有判断不足，开始让另一个生活圈纠正自己。"),
        ("ARC4-END", f"{name}短暂看见可以回到普通生活，但不再把安稳当作免除责任的理由。"),
        ("ARC5-END", f"{name}失去一件具体的珍贵之物，且没有用一次道歉或胜利恢复原状。"),
        ("ARC6-END", f"{name}在终局选择：{spine[1]}；职业能力产生公共回响，但旧账仍保留。"),
        ("ENDING", f"结局画面：{name}回到自己的工作场所，用一个日常动作承认损失仍在，并继续做能做的事。"),
        ("Y+1", f"一年后，{name}仍保留这次选择带来的新边界；关系可以改善，但不被写成自动和解。"),
    ]
    state_text = "\n\n".join(f"### {state}\n{detail}" for state, detail in states)
    return f'''+++
id = "{stable_id}"
tier = "{stable_id.split("-")[1]}"
name = "{name}"
aliases = {aliases}
age_y0 = {age}
occupation = "{occupation}"
residence = "{residence}"
economic_source = "{income}"
pov_budget = {pov}
minimum_episode_coverage = {coverage}
status = "FOUNDATION-DRAFT"
+++

# {stable_id}｜{name}

> 本档案是 Character Foundation 的独立权威源；实际母集与微短章绑定在 Season/Episode Gate 前保持 RESERVED。

## 角色定位

{name}是临安城市系统中的一名主动选择者，不是主角递线索的工具人。其不可替代责任是把“{spine[0]}”与“{spine[1]}”之间的矛盾变成可观察的行动。

## 身份与外在

- 年龄与职业：{age}岁；{occupation}。
- 居所与经济来源：{residence}；{income}。
- 稳定外观锚点、职业痕迹、四季服装和随身物以 Canon 源稿为基础，必须在后续 Character Asset 版本中保持不变。
- 职业流程：先处理手边的实际物件，再判断是否需要对外说话；常见错误是把自己的生活经验当成他人的唯一答案。

## 内在与行为

- 公开面具：源稿已记录的社会形象；镜头中不以单一情绪标签替代行为。
- 隐藏经历与矛盾：{spine[0]}与“害怕失去掌控/被误解”的现实恐惧同时成立。
- 行为指纹：先看与职业相关的物件，再看人；压力升高时保留一个重复的职业动作；亲近并不自动等于同意。
- 能力边界：只能使用档案中已展示的职业知识；不能突然获得血统、神秘力量、全知信息或未经训练的武力。
- 不依赖台词的关心动作：在对方不知道时完成一次具体照料，但把选择权留回对方。

## 现实与关系

- 一日作息必须包含工作、吃饭、清洁、休息、照料和一段不服务主线的个人时间。
- 主要收入、债务和照料责任必须在每集状态账本中连续更新。

## 非中央关系

{relation_lines}

每条关系必须在正式 REL 档案中补足表面行为、自觉动机、未承认动机、情感债务与八个快照；本档案不复制关系数值。

## 坚守七问

1. 最想保护什么：{spine[0]}。
2. 这种坚守为什么形成：来自职业训练、家庭经历和 Y-13 的具体后果，而非抽象口号。
3. 在保护它时伤害过谁：最亲近或最依赖自己的人会先承担代价。
4. 两件都正确的事冲突时选择什么：先公开风险与代价，再作可复核、可撤回的选择。
5. 为此具体放弃什么：{spine[1]}以外的一项收入、名声、关系安全或政治机会。
6. 谁会因此误解、怨恨或离开：至少一名亲近者和一名非中央关系对象保留异议。
7. 即使没有回报，是否仍承认这个选择属于自己：是；结局不将正确选择兑换成奖励。

## 状态与选择链

{state_text}

## 待集成人同步

- 关系数值、实际母集、微短章 ID、镜头绑定和 AIGC 资产均由下游 Gate 写入。
- 本档案当前只锁定人物事实、行为边界、状态责任和生产禁忌。

## Canon 来源摘录（只读）

{source}
'''


def main() -> int:
    sections = source_sections()
    for person in PEOPLE:
        stable_id = person[0]
        path = ROOT / f"characters/central/chr-{person[0].lower().replace('chr-', '')}-{person[9]}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(person, sections.get(stable_id, "")), encoding="utf-8")
        print(path.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
