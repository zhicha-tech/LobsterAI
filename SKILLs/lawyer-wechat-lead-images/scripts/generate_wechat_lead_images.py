#!/usr/bin/env python3
import argparse
import base64
import datetime as dt
import json
import os
import re
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib import error, request
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


# 配置文件路径
LAWCLAW_CONFIG_PATH = Path.home() / ".lawclaw.json"

DEFAULT_DISCLAIMER = "本文仅作普法交流，不构成个案法律意见。"
ANGLE_POOL = [
    "事件速读",
    "关键法律风险",
    "企业常见误区",
    "3步应对方案",
    "证据留存清单",
    "沟通与谈判策略",
    "管理动作排期",
    "案例拆解",
    "老板高频问答",
    "咨询引导",
    "应急动作",
    "合规升级",
]

TEMPLATE_LIBRARY = {
    "事件速读": {
        "subhead": "先看事实，再判断风险等级",
        "bullets": [
            "先把时间线梳理清楚：发生了什么、谁参与、影响范围",
            "区分管理问题与法律问题，避免混为一谈",
            "第一时间保留原始记录，避免后续证据断层",
        ],
        "cta": "私信“速读清单”，领取事件初判模板。",
    },
    "关键法律风险": {
        "subhead": "风险不只在结果，更在处理过程",
        "bullets": [
            "程序瑕疵可能比实体问题更先触发争议",
            "关键通知、沟通、审批都要形成书面留痕",
            "涉及人事与赔付时，先核对法律边界再行动",
        ],
        "cta": "私信“风险图谱”，领取企业风险排查表。",
    },
    "企业常见误区": {
        "subhead": "这三类误区最容易把小事拖成纠纷",
        "bullets": [
            "只追求“快处理”，忽略后续可举证性",
            "口头沟通过多，关键节点缺少书面确认",
            "规则未提前公示，事后执行阻力大",
        ],
        "cta": "私信“避坑”，领取常见误区对照表。",
    },
    "3步应对方案": {
        "subhead": "用可执行动作替代情绪化应对",
        "bullets": [
            "第1步：明确目标，先稳秩序再处理个案",
            "第2步：建立证据台账，责任人+时间点+材料",
            "第3步：同步对外口径，防止二次风险扩散",
        ],
        "cta": "私信“3步模板”，领取标准动作SOP。",
    },
    "证据留存清单": {
        "subhead": "没有证据链，很多正确动作也难被证明",
        "bullets": [
            "保留制度文件、告知记录、沟通纪要",
            "关键时间点保存截图、邮件、签收材料",
            "分类归档，做到“随时可调取、可复核”",
        ],
        "cta": "私信“证据”，领取证据清单模板。",
    },
    "沟通与谈判策略": {
        "subhead": "沟通目标是降冲突，不是比谁声音大",
        "bullets": [
            "先确认诉求，再给可选方案而非单一结论",
            "对争议点采用“事实-规则-方案”表达",
            "关键谈判内容形成会后确认，减少反复",
        ],
        "cta": "私信“谈判”，领取高频沟通话术包。",
    },
    "管理动作排期": {
        "subhead": "把复杂问题拆成24小时、72小时、7天动作",
        "bullets": [
            "24小时：完成信息收集与风险分级",
            "72小时：完成关键沟通与文件补齐",
            "7天内：完成流程复盘与制度加固",
        ],
        "cta": "私信“排期”，领取应急排期甘特表。",
    },
    "案例拆解": {
        "subhead": "同类案件中，输赢常在细节执行",
        "bullets": [
            "先看起因：制度、流程还是沟通断点",
            "再看转折点：哪一步动作改变了结果",
            "最后看可复制点：你公司能立刻执行什么",
        ],
        "cta": "私信“案例”，领取可复用案例拆解表。",
    },
    "老板高频问答": {
        "subhead": "高频问题提前准备，决策更稳",
        "bullets": [
            "能不能立刻处理？先看程序与证据完整度",
            "要不要给补偿？先判断法律义务与谈判空间",
            "如何避免连锁反应？统一口径+流程前置",
        ],
        "cta": "私信“问答”，领取老板高频问题清单。",
    },
    "咨询引导": {
        "subhead": "把问题带来，我帮你做场景化拆解",
        "bullets": [
            "提交行业、人员规模、当前争议点",
            "我给出风险优先级与处理顺序建议",
            "可提供文书模板与沟通话术示例",
        ],
        "cta": "私信我“诊断”，领取一次场景初诊建议。",
    },
}

EXECUTION_TOPIC_KEYWORDS = [
    "执行",
    "被执行",
    "终本",
    "限高",
    "财产保全",
    "回款",
]

EXECUTION_CLIENT_PACK = [
    {
        "angle": "执行立案",
        "headline": "判决生效后对方还不还钱，执行申请怎么一次做对？",
        "subhead": "材料完整度和请求清晰度，直接影响执行推进效率",
        "bullets": [
            "生效文书、身份信息、送达材料先做完整清单",
            "执行请求分开列明：本金、利息、迟延履行金",
            "已知财产线索同步提交，避免执行空转",
        ],
        "cta": "私信“执行立案”，{lawyer_name}发你《执行申请材料清单》。",
        "caption": "很多人赢了官司却卡在执行第一步。你的问题可能不是“打不赢”，而是“执行申请没打到关键点”。",
        "hashtags": ["#执行程序", "#判决后回款", "#律师咨询"],
    },
    {
        "angle": "财产线索",
        "headline": "明知对方有房有车，却查不到可执行财产，问题通常出在哪？",
        "subhead": "线索不是“知道就行”，要可核验、可落地、可追踪",
        "bullets": [
            "资产线索按类型拆分：不动产、车辆、股权、应收账款",
            "线索来源写清时间和证据载体，提升法院采信度",
            "每轮查控结果做台账，便于申请下一步措施",
        ],
        "cta": "私信“财产线索”，{lawyer_name}发你《执行线索提交模板》。",
        "caption": "你以为是法院“查不到”，很多时候是线索提交方式不专业，导致有效信息没有形成执行抓手。",
        "hashtags": ["#财产线索", "#执行实务", "#回款管理"],
    },
    {
        "angle": "终本恢复",
        "headline": "案件被“终本”就彻底没机会了？恢复执行的关键是什么？",
        "subhead": "终本不等于结束，补充新线索后可申请恢复执行",
        "bullets": [
            "先核对终本理由，判断是线索不足还是措施已穷尽",
            "补充新财产线索后，尽快递交恢复执行申请",
            "同步跟踪被执行人经营变化和新增资产路径",
        ],
        "cta": "私信“终本恢复”，{lawyer_name}发你《恢复执行申请要点》。",
        "caption": "不少当事人把“终本”当成终局，错过了恢复执行窗口。专业动作是把案件重新拉回执行轨道。",
        "hashtags": ["#终本案件", "#恢复执行", "#执行策略"],
    },
    {
        "angle": "转移财产",
        "headline": "怀疑对方在转移财产，执行阶段怎么固定证据更有效？",
        "subhead": "先固证再行动，避免关键事实后续无法证明",
        "bullets": [
            "先固定交易时间、对象、金额等核心信息",
            "把可疑转移路径整理成时间线，便于法院审查",
            "必要时同步申请追加措施，防止继续转移",
        ],
        "cta": "私信“固证”，{lawyer_name}发你《转移财产证据清单》。",
        "caption": "执行最怕“看见风险却没有证据”。越早把证据链搭起来，后续措施越有力度。",
        "hashtags": ["#转移财产", "#证据固定", "#执行维权"],
    },
    {
        "angle": "限高落地",
        "headline": "被执行人被限高后仍高消费，如何推动法院采取更强措施？",
        "subhead": "执行措施能否升级，取决于证据是否形成闭环",
        "bullets": [
            "高消费线索保留原始载体：时间、地点、消费记录",
            "线索与被执行人身份建立对应关系，避免证据脱节",
            "及时提交书面申请，推动执行措施升级",
        ],
        "cta": "私信“限高执行”，{lawyer_name}发你《高消费线索提交样例》。",
        "caption": "很多客户不是没有线索，而是线索不成体系，导致执行措施无法进一步推进。",
        "hashtags": ["#限高令", "#执行措施", "#法院执行"],
    },
    {
        "angle": "和解违约",
        "headline": "执行和解签了又违约，还能继续强制执行吗？",
        "subhead": "看协议条款和履行节点，决定下一步程序路径",
        "bullets": [
            "先核对和解协议是否约定恢复执行条件",
            "违约事实和催告记录要形成书面证据",
            "选择恢复执行还是另行主张，按成本与效率判断",
        ],
        "cta": "私信“和解违约”，{lawyer_name}发你《执行和解避坑清单》。",
        "caption": "执行和解不是“签完就稳了”。条款设计和违约留痕，才决定你后续是否被动。",
        "hashtags": ["#执行和解", "#违约处理", "#执行律师"],
    },
    {
        "angle": "追加责任",
        "headline": "公司账户没钱就执行不动？能否追加股东或实控人？",
        "subhead": "不是所有案件都能追加，关键在证据标准是否满足",
        "bullets": [
            "先判断追加路径：未实缴、抽逃出资或人格混同",
            "证据重点放在资金流、财务混用和控制关系",
            "程序上把执行申请与追加请求配合推进",
        ],
        "cta": "私信“追加被执行人”，{lawyer_name}发你《追加责任判断表》。",
        "caption": "很多应收款回不来，不是没有权利，而是没有按可被法院采纳的方式举证。",
        "hashtags": ["#追加被执行人", "#股东责任", "#商事执行"],
    },
    {
        "angle": "保全衔接",
        "headline": "只拿到胜诉判决还不够：保全与执行如何衔接提高回款效率？",
        "subhead": "执行效率高低，往往在诉讼阶段就已决定",
        "bullets": [
            "诉前/诉中保全信息要提前为执行预留接口",
            "保全到期节点和执行申请时间要衔接好",
            "回款目标倒推执行节奏，减少程序空档期",
        ],
        "cta": "私信“保全执行”，{lawyer_name}发你《回款路径规划图》。",
        "caption": "真正专业的执行策略，不是判决后才开始，而是从保全阶段就布局回款路径。",
        "hashtags": ["#财产保全", "#执行衔接", "#回款效率"],
    },
    {
        "angle": "执行异议",
        "headline": "执行中突然出现案外人异议，回款会不会被卡死？",
        "subhead": "先分清异议类型，再决定反制和应对节奏",
        "bullets": [
            "识别异议性质：执行行为异议还是实体权利争议",
            "针对异议核心点准备反证，避免程序拖延",
            "同步评估和解窗口与继续执行的成本收益",
        ],
        "cta": "私信“执行异议”，{lawyer_name}发你《异议应对清单》。",
        "caption": "遇到异议并不可怕，可怕的是没有预案。执行节奏一旦被打乱，回款周期会明显拉长。",
        "hashtags": ["#执行异议", "#案外人异议", "#执行风险"],
    },
    {
        "angle": "咨询转化",
        "headline": "你的执行案卡在哪一步？先做一次“回款路径体检”",
        "subhead": "把复杂执行问题拆成清晰动作，先找最影响回款的关键点",
        "bullets": [
            "提交案件阶段：立案/执行中/终本/和解",
            "提交已掌握财产线索与当前卡点",
            "我给你一份可执行的下一步动作建议",
        ],
        "cta": "私信“执行体检”，预约与{lawyer_name}一对一评估。",
        "caption": "如果你已经催了很久仍没回款，说明问题大概率出在执行路径设计。找对路径，比盲目催更重要。",
        "hashtags": ["#执行咨询", "#回款路径", "#律师获客"],
    },
]

BUSINESS_DIRECTIONS = [
    ("execution", "执行回款"),
    ("labor", "劳动用工"),
    ("contract", "合同纠纷"),
    ("corporate", "企业合规"),
    ("debt", "债务清收"),
    ("custom", "自定义方向"),
]

DEFAULT_TOPIC_BY_DIRECTION = {
    "execution": "执行领域的高频问题",
    "labor": "劳动用工高频争议",
    "contract": "合同纠纷高频问题",
    "corporate": "企业合规高频风险",
    "debt": "债务清收高频问题",
}

LEAD_QUESTION_BANK = {
    "execution": [
        "判决生效后对方拖着不还钱，我现在第一步该做什么？",
        "我知道对方有资产，但法院查不到，线索该怎么提才有效？",
        "案件被终本后还有机会追回吗？",
        "怀疑对方转移财产，怎样固定证据才不白做？",
        "对方被限高后仍高消费，如何推动执行措施升级？",
        "执行和解后对方又违约，能否直接恢复执行？",
        "公司没钱就没办法了吗？能否追加股东责任？",
        "保全和执行怎么衔接，回款效率最高？",
        "执行中被提异议，如何避免回款节奏被拖垮？",
        "执行案长期没进展，律师介入能先做哪些关键动作？",
    ],
    "labor": [
        "员工拒签调岗通知，企业怎么做才不被动？",
        "员工长期旷工，直接解除会不会被判违法？",
        "N+1怎么算才不出错？有哪些常见赔付坑？",
        "竞业限制约定了却无法执行，问题常出在哪？",
        "试用期不合格辞退，证据要准备到什么程度？",
        "员工主张加班费，企业如何应对举证责任？",
        "口头约定薪酬被反悔，企业如何留痕更安全？",
        "员工突然仲裁，企业应诉顺序怎么排最稳？",
        "社保补缴争议频发，企业如何降低连锁风险？",
        "劳动争议反复发生，制度该怎样做合规升级？",
    ],
    "contract": [
        "对方逾期不付款，先发函还是先起诉更划算？",
        "合同没约定违约金，现在还能主张损失吗？",
        "电子合同/聊天记录能不能当有效证据？",
        "签了补充协议却更被动，条款问题出在哪？",
        "对方先违约，我方能否立即解除合同？",
        "货款纠纷中，如何证明已交付并被对方验收？",
        "被要求承担高额违约责任，如何合法抗辩？",
        "合同相对方是空壳公司，怎么提前防风险？",
        "诉前保全怎么做，才能提高后续回款率？",
        "合同纠纷久拖不决，律师介入先抓哪三个点？",
    ],
    "corporate": [
        "公司股东之间僵局，如何避免经营被拖垮？",
        "实际控制人与公司账户混用，会有什么法律后果？",
        "公司章程写了很多条款，为什么打官司还是吃亏？",
        "高管离职带走客户资源，企业能否追责？",
        "关联交易被质疑，如何做证据与流程防火墙？",
        "企业被举报合规问题，内部调查如何开展？",
        "新业务上线前，哪些法律红线必须先排查？",
        "融资合作谈到最后翻车，常见法律漏洞有哪些？",
        "公司印章和授权管理混乱，怎么快速止损？",
        "合规体系怎么搭才不是“只做文件不落地”？",
    ],
    "debt": [
        "客户欠款长期不回，催收第一步该怎么做？",
        "没有完整合同，还能不能把钱要回来？",
        "欠条、对账单、转账记录怎么组合最有力？",
        "债务人失联后，律师通常怎么追踪财产线索？",
        "先谈和解还是直接诉讼，怎么判断成本更低？",
        "申请保全会不会打草惊蛇？",
        "拿到判决后回款慢，执行阶段如何提效？",
        "多笔账龄混在一起，如何制定分层回款策略？",
        "债权转让后，通知不到位会带来哪些风险？",
        "应收账款管理混乱，企业如何建立长效机制？",
    ],
}


def load_json(path: Path) -> Dict[str, Any]:
    # Accept both UTF-8 and UTF-8 with BOM from different editors/shells.
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def load_lawclaw_config() -> Dict[str, Any]:
    """从 ~/.lawclaw.json 加载 lawyerWechatLead 配置"""
    if not LAWCLAW_CONFIG_PATH.exists():
        raise FileNotFoundError(f"配置文件不存在: {LAWCLAW_CONFIG_PATH}")

    config = load_json(LAWCLAW_CONFIG_PATH)
    lawyer_wechat_lead = config.get("lawyerWechatLead", {})

    if not lawyer_wechat_lead:
        raise ValueError("配置文件中未找到 lawyerWechatLead 配置")

    return lawyer_wechat_lead


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^\w\-]+", "-", value.strip(), flags=re.UNICODE)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned[:40] if cleaned else "campaign"


def get_api_key(model_cfg: Dict[str, Any]) -> Optional[str]:
    """从配置中获取 API key"""
    # 直接从配置中读取 api_key
    api_key = model_cfg.get("api_key", "")
    if api_key:
        return api_key
    # 兼容旧配置：如果配置了 api_key_env，尝试从环境变量读取
    env_name = model_cfg.get("api_key_env", "")
    if env_name:
        return os.environ.get(env_name)
    return None


def post_json(url: str, payload: Dict[str, Any], headers: Dict[str, str], timeout: int) -> Dict[str, Any]:
    req = request.Request(
        url=url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"HTTP {exc.code} calling {url}: {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Network error calling {url}: {exc}") from exc


def url_with_query_key(url: str, key_name: str, key_value: str) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query[key_name] = key_value
    new_query = urlencode(query)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))


def extract_first_image_bytes(resp: Dict[str, Any]) -> Optional[bytes]:
    # OpenAI-compatible shape: {"data":[{"b64_json":"..."}]}
    data = resp.get("data")
    if isinstance(data, list) and data:
        item = data[0]
        if isinstance(item, dict) and item.get("b64_json"):
            return base64.b64decode(item["b64_json"])

    # Gemini generateContent shape: {"candidates":[{"content":{"parts":[{"inlineData":{"data":"..."}}]}}]}
    candidates = resp.get("candidates")
    if isinstance(candidates, list):
        for cand in candidates:
            content = cand.get("content") if isinstance(cand, dict) else None
            parts = content.get("parts") if isinstance(content, dict) else None
            if not isinstance(parts, list):
                continue
            for part in parts:
                if not isinstance(part, dict):
                    continue
                inline_data = part.get("inlineData") or part.get("inline_data")
                if isinstance(inline_data, dict) and inline_data.get("data"):
                    return base64.b64decode(inline_data["data"])
    return None


def render_one_image_openai_compatible(
    url: str, model: str, prompt: str, size: str, api_key: str, timeout: int
) -> bytes:
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "n": 1,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    resp = post_json(url, payload, headers, timeout=timeout)
    b = extract_first_image_bytes(resp)
    if b:
        return b

    # fallback url field if provider returns url instead of b64
    data = resp.get("data") or []
    if isinstance(data, list) and data:
        item = data[0]
        if isinstance(item, dict) and item.get("url"):
            with request.urlopen(item["url"], timeout=timeout) as resp_img:
                return resp_img.read()
    raise RuntimeError("openai-compatible image response does not contain image bytes")


def render_one_image_gemini_generate_content(
    endpoint: str, model: str, prompt: str, size: str, api_key: str, timeout: int,
    aspect_ratio: str = "3:4", image_size: str = "2K"
) -> bytes:
    # New API format with imageConfig support (yunwu-image-gen)
    # aspect_ratio: "1:1", "16:9", "9:16", "4:3", "3:4"
    # image_size: "1K", "2K", "4K"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": prompt
                    }
                ],
            }
        ],
        "responseModalities": ["TEXT", "IMAGE"],
        "imageConfig": {
            "aspectRatio": aspect_ratio,
            "imageSize": image_size
        }
    }

    # Try common auth styles in sequence for proxy compatibility.
    attempts = [
        (endpoint, {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}),
        (endpoint, {"Content-Type": "application/json", "x-goog-api-key": api_key}),
        (url_with_query_key(endpoint, "key", api_key), {"Content-Type": "application/json"}),
        (url_with_query_key(endpoint, "api_key", api_key), {"Content-Type": "application/json"}),
    ]
    last_error: Optional[Exception] = None
    for try_url, headers in attempts:
        try:
            resp = post_json(try_url, payload, headers, timeout=timeout)
            b = extract_first_image_bytes(resp)
            if b:
                return b
            last_error = RuntimeError("gemini response received but no inline image data found")
        except Exception as exc:
            last_error = exc
            continue
    raise RuntimeError(f"all gemini auth methods failed: {last_error}")


def extract_json_block(text: str) -> Any:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def safe_get_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    return []


def is_execution_topic(topic: str) -> bool:
    return any(keyword in topic for keyword in EXECUTION_TOPIC_KEYWORDS)


def fill_template_vars(value: str, topic: str, lawyer_name: str) -> str:
    return value.replace("{topic}", topic).replace("{lawyer_name}", lawyer_name)


def clone_config(config: Dict[str, Any]) -> Dict[str, Any]:
    return json.loads(json.dumps(config, ensure_ascii=False))


def ask_text(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value if value else default


def ask_yes_no(prompt: str, default_yes: bool = True) -> bool:
    default_text = "Y/n" if default_yes else "y/N"
    while True:
        value = input(f"{prompt} ({default_text}): ").strip().lower()
        if not value:
            return default_yes
        if value in {"y", "yes"}:
            return True
        if value in {"n", "no"}:
            return False
        print("请输入 y 或 n。")


def ask_int(prompt: str, default: int, min_value: int, max_value: int) -> int:
    while True:
        raw = ask_text(prompt, str(default))
        try:
            value = int(raw)
        except ValueError:
            print("请输入数字。")
            continue
        if value < min_value or value > max_value:
            print(f"请输入 {min_value} 到 {max_value} 之间的数字。")
            continue
        return value


def choose_business_direction() -> str:
    print("\n[第2步] 选择生成宣传图的业务方向")
    for idx, (_, label) in enumerate(BUSINESS_DIRECTIONS, start=1):
        print(f"{idx}. {label}")
    max_idx = len(BUSINESS_DIRECTIONS)
    selected = ask_int("请输入序号", 1, 1, max_idx)
    key, _ = BUSINESS_DIRECTIONS[selected - 1]
    if key == "custom":
        return ask_text("请输入自定义业务方向", "民商事高频问题")
    return DEFAULT_TOPIC_BY_DIRECTION.get(key, "法律服务高频问题")


def get_default_lead_questions(topic: str, count: int) -> List[str]:
    direction_key = "execution" if is_execution_topic(topic) else ""
    if not direction_key:
        for key, default_topic in DEFAULT_TOPIC_BY_DIRECTION.items():
            if key == "execution":
                continue
            if default_topic[:2] in topic or default_topic.replace("高频问题", "") in topic:
                direction_key = key
                break
    bank = LEAD_QUESTION_BANK.get(direction_key, [])
    if not bank:
        bank = [
            f"{topic}里最容易踩坑的第一步是什么？",
            f"遇到“{topic}”时，先保留哪些证据最关键？",
            f"{topic}处理中，常见错误动作有哪些？",
            f"{topic}如何做风险分级并安排处理顺序？",
            f"{topic}里企业/个人最容易忽略的法律边界是什么？",
            f"如何把{topic}问题从“被动应对”变成“主动管理”？",
            f"{topic}发生后，沟通策略怎么做才更稳？",
            f"{topic}有没有3步可落地的处理模型？",
            f"{topic}如果已经拖了很久，如何尽快止损？",
            f"{topic}需要律师介入时，先准备哪些材料效率最高？",
        ]
    if count <= len(bank):
        return bank[:count]
    result = list(bank)
    while len(result) < count:
        result.append(f"{topic}场景问题 {len(result) + 1}：下一步该如何处理？")
    return result


def review_and_edit_questions(questions: List[str]) -> List[str]:
    while True:
        print("\n[第4步] 引流问题清单（可确认或调整）")
        for i, q in enumerate(questions, start=1):
            print(f"{i:02d}. {q}")
        action = input("输入 C 确认，输入 E 编辑: ").strip().lower()
        if action in {"c", "confirm", ""}:
            return questions
        if action not in {"e", "edit"}:
            print("请输入 C 或 E。")
            continue

        indexes_raw = input("输入要修改的问题序号（逗号分隔，例如 2,5）: ").strip()
        if not indexes_raw:
            continue
        changed = False
        for token in indexes_raw.split(","):
            token = token.strip()
            if not token.isdigit():
                continue
            idx = int(token)
            if idx < 1 or idx > len(questions):
                continue
            new_text = input(f"请输入第{idx}条新问题（留空保留原文）: ").strip()
            if new_text:
                questions[idx - 1] = new_text
                changed = True
        if not changed:
            print("没有有效修改，保持原清单。")


def build_cards_from_question_checklist(
    questions: List[str], topic: str, config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    lawyer = config.get("lawyer", {})
    lawyer_name = str(lawyer.get("name", "某律师"))
    wechat = str(lawyer.get("wechat", "")).strip()
    phone = str(lawyer.get("phone", "")).strip()
    contact_hint = f"微信：{wechat}" if wechat else (f"电话：{phone}" if phone else "私信咨询")
    cards: List[Dict[str, Any]] = []
    for idx, question in enumerate(questions, start=1):
        cards.append(
            {
                "angle": f"高频问题{idx:02d}",
                "headline": question,
                "subhead": f"这正是{topic}中的典型卡点，处理顺序决定结果。",
                "bullets": [
                    "先判断案件阶段与目标：立案/执行中/和解/终本",
                    "锁定当前卡点：证据缺口、程序节点、沟通策略",
                    "给出下一步动作：材料清单+时序安排+风险预案",
                ],
                "cta": f"私信“问题{idx:02d}”，{lawyer_name}给你对应处理清单。",
                "caption": (
                    f"如果你也在问“{question}”，说明你已经进入关键决策点。\n"
                    f"{lawyer_name}可基于你的案件阶段，给出可落地的下一步方案。"
                ),
                "hashtags": ["#律师咨询", "#高频法律问题", "#精准获客"],
                "image_prompt": "",
                "disclaimer": DEFAULT_DISCLAIMER,
            }
        )
    return normalize_cards(cards, topic, len(questions), config)


def run_wizard(config: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    runtime_cfg = clone_config(config)
    lawyer = runtime_cfg.setdefault("lawyer", {})

    while True:
        print("\n[第1步] 填写并确认律师信息")
        lawyer["name"] = ask_text("律师姓名", str(lawyer.get("name", "XXX律师")))
        lawyer["title"] = ask_text("律师头衔", str(lawyer.get("title", "执业律师")))
        lawyer["firm"] = ask_text("执业单位/律所", str(lawyer.get("firm", "某某律师事务所")))
        lawyer["wechat"] = ask_text("微信号", str(lawyer.get("wechat", "")))
        lawyer["phone"] = ask_text("电话", str(lawyer.get("phone", "")))
        focus_default = ", ".join(safe_get_list(lawyer.get("focus_areas", [])))
        focus_text = ask_text("核心业务领域（逗号分隔）", focus_default or "执行,劳动用工,合同纠纷")
        lawyer["focus_areas"] = [x.strip() for x in focus_text.split(",") if x.strip()]

        print("\n已录入信息：")
        print(f"- 姓名: {lawyer.get('name', '')}")
        print(f"- 头衔: {lawyer.get('title', '')}")
        print(f"- 单位: {lawyer.get('firm', '')}")
        print(f"- 联系方式: 微信 {lawyer.get('wechat', '')} / 电话 {lawyer.get('phone', '')}")
        print(f"- 业务领域: {', '.join(safe_get_list(lawyer.get('focus_areas', [])))}")
        if ask_yes_no("确认以上信息", True):
            break

    selected_topic = choose_business_direction()
    selected_topic = ask_text("\n[第3步] 可调整本次宣传业务方向", selected_topic)
    selected_count = ask_int("生成图片张数", args.count, 1, 20)
    question_list = get_default_lead_questions(selected_topic, selected_count)
    question_list = review_and_edit_questions(question_list)
    cards = build_cards_from_question_checklist(question_list, selected_topic, runtime_cfg)

    if ask_yes_no("是否把本次律师信息写回配置文件", True):
        # 读取完整配置并更新 lawyerWechatLead 部分
        full_config = load_json(LAWCLAW_CONFIG_PATH)
        full_config["lawyerWechatLead"] = runtime_cfg
        LAWCLAW_CONFIG_PATH.write_text(json.dumps(full_config, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[OK] 已更新配置文件: {LAWCLAW_CONFIG_PATH}")

    return {
        "config": runtime_cfg,
        "topic": selected_topic,
        "count": selected_count,
        "cards": cards,
    }


def compose_lawyer_signature(config: Dict[str, Any]) -> str:
    lawyer = config.get("lawyer", {})
    name = lawyer.get("name", "某律师")
    title = lawyer.get("title", "执业律师")
    firm = lawyer.get("firm", "某律师事务所")
    focus = "、".join(safe_get_list(lawyer.get("focus_areas", []))) or "民商事争议与企业合规"
    return f"{name} | {title} | {firm} | 业务方向：{focus}"


def normalize_cards(raw_cards: List[Dict[str, Any]], topic: str, count: int, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    lawyer = config.get("lawyer", {})
    compliance = config.get("compliance", {})
    disclaimer = compliance.get("global_disclaimer") or DEFAULT_DISCLAIMER
    name = lawyer.get("name", "某律师")
    wechat = lawyer.get("wechat", "")
    phone = lawyer.get("phone", "")
    contact_hint = f"微信：{wechat}" if wechat else (f"电话：{phone}" if phone else "私信咨询")

    cards: List[Dict[str, Any]] = []
    for i in range(count):
        source = raw_cards[i] if i < len(raw_cards) else {}
        angle = source.get("angle") or ANGLE_POOL[i % len(ANGLE_POOL)]
        headline = source.get("headline") or f"{angle}：{topic}"
        subhead = source.get("subhead") or "把复杂问题拆成可执行动作。"
        bullets = safe_get_list(source.get("bullets"))[:5]
        if not bullets:
            bullets = [
                "先识别风险等级，再决定处理节奏",
                "用证据链替代情绪化沟通",
                "关键动作形成书面留痕",
            ]
        cta = source.get("cta") or f"需要结合你单位情况评估，联系{name}。"
        caption = source.get("caption") or (
            f"{headline}\n\n"
            f"这类问题的关键不在“快”，而在“稳、准、可落地”。\n"
            f"如需我按你的场景给出执行清单，可留言或{contact_hint}。"
        )
        hashtags = safe_get_list(source.get("hashtags"))
        if not hashtags:
            hashtags = ["#劳动用工", "#企业合规", "#法律风险"]
        image_prompt = source.get("image_prompt", "")
        cards.append(
            {
                "index": i + 1,
                "angle": angle,
                "headline": headline,
                "subhead": subhead,
                "bullets": bullets,
                "cta": cta,
                "caption": caption,
                "hashtags": hashtags,
                "image_prompt": image_prompt,
                "disclaimer": source.get("disclaimer") or disclaimer,
            }
        )
    return cards


def template_cards(topic: str, count: int, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    raw: List[Dict[str, Any]] = []
    lawyer_name = str(config.get("lawyer", {}).get("name", "某律师"))
    use_execution_pack = is_execution_topic(topic)
    for i in range(count):
        if use_execution_pack:
            plan = EXECUTION_CLIENT_PACK[i % len(EXECUTION_CLIENT_PACK)]
            angle = plan.get("angle", f"执行场景{i + 1}")
            headline = fill_template_vars(
                str(plan.get("headline", f"{angle}：{topic}")), topic, lawyer_name
            )
            subhead = fill_template_vars(
                str(plan.get("subhead", "聚焦执行卡点，输出可落地动作")), topic, lawyer_name
            )
            bullets = [
                fill_template_vars(str(b), topic, lawyer_name)
                for b in safe_get_list(plan.get("bullets"))
            ] or [
                "先确认案件卡点，再决定下一步执行动作",
                "把线索转成可核验的证据材料",
                "每一步都形成书面留痕，避免程序空转",
            ]
            cta = fill_template_vars(
                str(plan.get("cta", "私信“执行方案”，领取执行动作清单。")),
                topic,
                lawyer_name,
            )
            caption = fill_template_vars(
                str(
                    plan.get(
                        "caption",
                        f"{headline}\n\n执行问题核心在路径设计，不在反复催促。",
                    )
                ),
                topic,
                lawyer_name,
            )
            hashtags = [
                fill_template_vars(str(tag), topic, lawyer_name)
                for tag in safe_get_list(plan.get("hashtags"))
            ] or ["#执行案件", "#回款管理", "#律师咨询"]
        else:
            angle = ANGLE_POOL[i % len(ANGLE_POOL)]
            plan = TEMPLATE_LIBRARY.get(angle, {})
            headline = f"{angle}：{topic}"
            subhead = plan.get("subhead", "律师视角，聚焦获客转化与实操建议")
            bullets = plan.get(
                "bullets",
                [
                    "问题先分类：紧急、重要、可延后",
                    "每个动作都要有责任人与截止时间",
                    "关键沟通尽量书面化，避免口头争议",
                ],
            )
            cta = plan.get("cta", "想拿到你行业的专属处理模板，私信我“模板”。")
            caption = (
                f"{angle}这一步做对，能明显降低{topic}带来的连锁风险。\n"
                "我整理了一套企业可直接落地的动作清单，留言即可领取。"
            )
            hashtags = ["#法律咨询", "#企业管理", "#风险防控"]

        raw.append(
            {
                "angle": angle,
                "headline": headline,
                "subhead": subhead,
                "bullets": bullets,
                "cta": cta,
                "caption": caption,
                "hashtags": hashtags,
            }
        )
    return normalize_cards(raw, topic, count, config)


def llm_cards(topic: str, count: int, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    models = config.get("models", {})
    text_cfg = models.get("text", {})
    if not text_cfg.get("enabled", False):
        raise RuntimeError("text model disabled")

    base_url = str(text_cfg.get("base_url", "")).rstrip("/")
    model = text_cfg.get("model", "")
    timeout = int(text_cfg.get("timeout_sec", 60))
    if not base_url or not model:
        raise RuntimeError("text model base_url/model missing")

    api_key = get_api_key(text_cfg)
    if not api_key:
        raise RuntimeError(f"text model API key missing in env: {text_cfg.get('api_key_env', '')}")

    lawyer = config.get("lawyer", {})
    compliance = config.get("compliance", {})
    brand = config.get("brand", {})

    system_prompt = textwrap.dedent(
        """
        你是律师行业获客内容策划。目标是为朋友圈生成可转化的法律营销海报脚本。
        必须输出严格 JSON，对象结构为:
        {
          "cards": [
            {
              "angle": "...",
              "headline": "...",
              "subhead": "...",
              "bullets": ["...", "...", "..."],
              "cta": "...",
              "caption": "...",
              "hashtags": ["#...", "#...", "#..."],
              "image_prompt": "...",
              "disclaimer": "..."
            }
          ]
        }
        约束:
        - 使用简体中文
        - cards 数量必须等于请求值
        - 每张卡片强调一个角度，避免重复
        - 禁止承诺结果、禁止绝对化词汇
        - 语气专业、克制、可执行
        """
    ).strip()

    user_prompt = textwrap.dedent(
        f"""
        主题: {topic}
        数量: {count}
        律师信息: {json.dumps(lawyer, ensure_ascii=False)}
        品牌风格: {json.dumps(brand, ensure_ascii=False)}
        合规要求: {json.dumps(compliance, ensure_ascii=False)}
        输出仅 JSON，不要 Markdown。
        """
    ).strip()

    payload = {
        "model": model,
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    url = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    resp = post_json(url, payload, headers, timeout=timeout)
    choices = resp.get("choices", [])
    if not choices:
        raise RuntimeError("text model returned no choices")
    content = choices[0].get("message", {}).get("content", "")
    parsed = extract_json_block(content)
    if not isinstance(parsed, dict) or not isinstance(parsed.get("cards"), list):
        raise RuntimeError("text model output missing cards list")
    raw_cards = parsed["cards"]
    return normalize_cards(raw_cards, topic, count, config)


def build_image_prompt(card: Dict[str, Any], config: Dict[str, Any], topic: str, reference_image: str) -> str:
    brand = config.get("brand", {})
    lawyer_sig = compose_lawyer_signature(config)
    primary = brand.get("primary_color", "#B30000")
    secondary = brand.get("secondary_color", "#111111")
    visual_style = brand.get(
        "visual_style",
        "clean legal poster for WeChat Moments, Chinese typography blocks, high contrast, editorial layout",
    )
    logo_hint = brand.get("logo_hint", "place a small legal badge at top-right")
    design_tone = brand.get("design_tone", "premium, professional, business, trust-building")
    background_style = brand.get(
        "background_style",
        "light neutral gradient background with subtle paper texture and clean geometric overlays",
    )
    typography_hint = brand.get(
        "typography_hint",
        "strong Chinese headline hierarchy, high legibility, generous line spacing, no tiny text",
    )
    layout_hint = brand.get(
        "layout_hint",
        "12-column editorial grid, clear top headline zone, middle bullet info zone, bottom CTA zone",
    )
    avoid_style = brand.get(
        "avoid_style",
        "no cartoon illustration, no flashy neon colors, no clutter, no meme style, no low-resolution artifacts",
    )
    bullets = "；".join(card.get("bullets", []))
    ref_note = f"Reference style image: {reference_image}." if reference_image else ""

    extra = card.get("image_prompt", "")
    return (
        f"{visual_style}. "
        f"Overall visual tone: {design_tone}. "
        f"Design one vertical WeChat Moments poster (3:4). "
        f"Apply layout system: {layout_hint}. "
        f"Background direction: {background_style}. "
        f"Typography direction: {typography_hint}. "
        f"Topic: {topic}. "
        f"Main headline text in Chinese: {card.get('headline', '')}. "
        f"Subheading: {card.get('subhead', '')}. "
        f"Bullet points: {bullets}. "
        f"CTA line: {card.get('cta', '')}. "
        f"Include signature line: {lawyer_sig}. "
        f"Use color palette primary {primary} and secondary {secondary}. "
        f"Use restrained accents only; keep most area neutral for premium corporate look. "
        f"Add subtle depth with soft shadow and translucent panels; do not over-decorate. "
        f"{logo_hint}. "
        f"Add disclaimer text at bottom: {card.get('disclaimer', DEFAULT_DISCLAIMER)}. "
        f"Keep layout legible, leave generous margins, avoid tiny text. "
        f"Negative constraints: {avoid_style}. "
        f"{ref_note} "
        f"{extra}"
    ).strip()


def image_cards(cards: List[Dict[str, Any]], topic: str, config: Dict[str, Any], out_dir: Path, reference_image: str) -> None:
    image_cfg = config.get("models", {}).get("image", {})
    if not image_cfg.get("enabled", False):
        print("[INFO] image model disabled; skip rendering")
        return

    base_url = str(image_cfg.get("base_url", "")).rstrip("/")
    model = image_cfg.get("model", "")
    timeout = int(image_cfg.get("timeout_sec", 120))
    size = image_cfg.get("size", "1024x1536")
    provider = str(image_cfg.get("provider", "openai_compatible")).strip().lower()
    endpoint = str(image_cfg.get("endpoint", "")).strip()
    # New API config for yunwu-image-gen
    aspect_ratio = image_cfg.get("aspect_ratio", "3:4")
    image_size = image_cfg.get("image_size", "2K")
    if not base_url or not model:
        if not endpoint or not model:
            raise RuntimeError("image model config missing: provide base_url+model or endpoint+model")

    api_key = get_api_key(image_cfg)
    if not api_key:
        raise RuntimeError(f"image model API key missing in env: {image_cfg.get('api_key_env', '')}")

    image_dir = out_dir / "images"
    ensure_dir(image_dir)
    url = endpoint or f"{base_url}/images/generations"

    for card in cards:
        prompt = build_image_prompt(card, config, topic, reference_image)
        if provider == "gemini_generate_content":
            raw = render_one_image_gemini_generate_content(url, model, prompt, size, api_key, timeout, aspect_ratio, image_size)
        else:
            raw = render_one_image_openai_compatible(url, model, prompt, size, api_key, timeout)
        file_name = f"{card['index']:02d}.png"
        file_path = image_dir / file_name
        file_path.write_bytes(raw)
        card["image_file"] = str(file_path)
        card["final_prompt"] = prompt
        print(f"[OK] rendered card {card['index']}: {file_path}")


def write_outputs(cards: List[Dict[str, Any]], out_dir: Path, topic: str) -> None:
    ensure_dir(out_dir)
    cards_path = out_dir / "cards.json"
    cards_path.write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")

    posts_lines = [f"# 朋友圈获客内容包：{topic}", ""]
    prompt_lines = []
    for card in cards:
        tags = " ".join(card.get("hashtags", []))
        posts_lines.extend(
            [
                f"## 第{card['index']}张｜{card.get('angle', '')}",
                card.get("caption", "").strip(),
                "",
                f"CTA：{card.get('cta', '').strip()}",
                f"话题：{tags}",
                f"免责声明：{card.get('disclaimer', DEFAULT_DISCLAIMER)}",
                "",
            ]
        )
        prompt_lines.extend(
            [
                f"[CARD {card['index']:02d}] {card.get('headline', '')}",
                card.get("final_prompt", card.get("image_prompt", "")),
                "",
            ]
        )

    (out_dir / "posts.md").write_text("\n".join(posts_lines).strip() + "\n", encoding="utf-8")
    (out_dir / "prompts.txt").write_text("\n".join(prompt_lines).strip() + "\n", encoding="utf-8")
    print(f"[OK] saved {cards_path}")
    print(f"[OK] saved {out_dir / 'posts.md'}")
    print(f"[OK] saved {out_dir / 'prompts.txt'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate WeChat Moments legal lead-gen cards and optional rendered images."
    )
    parser.add_argument("--topic", default="", help="Legal topic or social-news event")
    parser.add_argument("--count", type=int, default=1, help="Number of cards (default: 1)")
    parser.add_argument("--outdir", default="output", help="Output root dir (default: output)")
    parser.add_argument("--dry-run", action="store_true", help="Generate copy and prompts only")
    parser.add_argument("--skip-text-model", action="store_true", help="Force template mode")
    parser.add_argument("--wizard", action="store_true", help="Run step-by-step interactive wizard before generation")
    parser.add_argument("--reference-image", default="", help="Optional local image path for style reference")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.count < 1:
        raise SystemExit("--count must be >= 1")
    if args.count > 20:
        raise SystemExit("--count must be <= 20")

    # 从 ~/.lawclaw.json 加载配置
    try:
        config = load_lawclaw_config()
    except FileNotFoundError as e:
        raise SystemExit(str(e))
    except ValueError as e:
        raise SystemExit(str(e))

    topic = args.topic.strip()
    count = args.count
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    cards: List[Dict[str, Any]]
    if args.wizard:
        wizard_result = run_wizard(config, args)
        config = wizard_result["config"]
        topic = str(wizard_result["topic"])
        count = int(wizard_result["count"])
        cards = wizard_result["cards"]
        print("[INFO] using wizard-confirmed question checklist")
    else:
        if not topic:
            raise SystemExit("--topic is required unless --wizard is used")
        if args.skip_text_model:
            cards = template_cards(topic, count, config)
            print("[INFO] using template cards (skip-text-model)")
        else:
            try:
                cards = llm_cards(topic, count, config)
                print("[OK] generated cards via text model")
            except Exception as exc:
                print(f"[WARN] text model failed, fallback to template: {exc}")
                cards = template_cards(topic, count, config)

    campaign_name = f"{timestamp}-{slugify(topic)}"
    out_dir = Path(args.outdir).resolve() / campaign_name
    ensure_dir(out_dir)

    for card in cards:
        card["final_prompt"] = build_image_prompt(card, config, topic, args.reference_image)

    write_outputs(cards, out_dir, topic)

    if args.dry_run:
        print("[INFO] dry-run enabled; image rendering skipped")
        return

    try:
        image_cards(cards, topic, config, out_dir, args.reference_image)
        (out_dir / "cards.json").write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[OK] updated {out_dir / 'cards.json'} with rendered image paths")
    except Exception as exc:
        print(f"[WARN] image rendering failed: {exc}")


if __name__ == "__main__":
    main()
