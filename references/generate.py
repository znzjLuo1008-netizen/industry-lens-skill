"""
IndustryLens 主生成入口
用法：
    python3 generate.py <行业名> [输出路径]

例如：
    python3 generate.py "智能驾驶"                  # 输出到 ./智能驾驶-百科.html
    python3 generate.py "生物医药" /tmp/bio.html     # 指定输出

流程：
1. 调用 DeepSeek 3 次（kw1-50 + kw51-100 + 公司）
2. 质量检查，不合格重试
3. 合并数据 + 填充 HTML 模板
4. 输出到目标路径
"""
import os, sys, json, argparse, time
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from api_call import call_deepseek, check_kw_quality, check_co_quality


def load_prompts():
    """从 prompt_templates.md 提取各 prompt（写死一份避免 markdown 解析复杂度）"""
    return {
        'kw_system': '''你是一位精通行业研究、擅长用通俗语言解释专业概念的顶级分析师。针对用户输入的行业，输出指定数量关键词信息卡片，严格JSON。

【⚠️ 每张卡片6件套必备】
1. term：关键词名称
2. rank + cat：排序号 + 分类(core/finance/tech/biz)
3. pro（专业释义）150-200字：三段式 ①精确定义(含英文/公式) ②2025-2026年最新数据(含具体数字/公司/市占率) ③产业链位置或商业影响。禁一句话概括。
4. ref：google(中文搜索词如"毛利率 行业平均 2025") + wiki(英文词如"Gross margin")
5. industryData（行业参考数据）35-70字：必须含数字+公司名+趋势。
6. ez（大白话）25-50字：生活化类比，可幽默调侃。

【硬性要求】
- 数据基于2025-2026年事实，禁编造
- cat分布均衡
- 只输出纯净JSON

【JSON Schema】
{"keywords":[{"rank":N,"cat":"...","term":"...","pro":"150-200字","ref":{"google":"...","wiki":"..."},"industryData":"35-70字","ez":"25-50字"}]}''',
        
        'co_system': '''你是一位精通行业研究的顶级分析师。针对用户输入的行业，输出该行业3家最具代表性的标杆公司的详细拆解，严格JSON。

【公司必备字段】
- name(中文名), enName(English), domain(官网域名)
- ecoNiche(生态位定位，30字内)
- tags(标签数组，3-5个)
- moatPro(护城河专业版100字+)：含技术壁垒/市占率/专利等具体数据
- moatEz(护城河大白话30字+)：生活化比喻
- lifecycle(0=初创 1=成长 2=成熟 3=转型 4=衰退)
- lifeLabel(对应文字)
- revenue(收入结构)：≥3条，pct加和100，含label/pct/color。若公司未上市无营收，可填研发投入/临床试验等支出结构

【硬性要求】
- 公司必须真实存在的行业头部
- 数据基于2025-2026年最新事实，禁编造
- 只输出纯净JSON

【JSON Schema】
{"companies":[{"name":"...","enName":"...","domain":"...","ecoNiche":"...","tags":[...],"moatPro":"...","moatEz":"...","lifecycle":2,"lifeLabel":"成熟期","revenue":[{"label":"...","pct":N,"color":"#XXXXXX"}]}]}''',

        'vc_system': '''你是一位精通行业研究的顶级分析师。针对用户输入的行业，输出该行业完整的【产业链上中下游】结构化拆解，严格JSON。

【产业链三层结构】
- upstream（上游）：原材料 / 核心零部件 / 基础设施 / 底层技术提供方
- midstream（中游）：行业主体 / 系统集成 / 制造加工 / 产品与服务研发
- downstream（下游）：终端应用场景 / 渠道 / 客户 / 最终消费者

【每一层要求】
- role：该层定位一句话（20-40字）
- desc：该层详细说明（80-140字，含代表品类、市场规模/增速、2025-2026数据）
- segments：3-5个核心细分环节，每个含 name / players(3-5家真实公司) / note(20-40字)
- marginLevel：该层综合毛利率 "high"(≥40%) / "mid"(20-40%) / "low"(≤20%)
- bargainPower：议价能力 "strong" / "medium" / "weak"

【全局字段】
- flowNote：50-80字，描述上→中→下的核心价值流动逻辑
- keyInsight：60-100字，点出该产业链当下的核心矛盾/机会/风险（2025-2026视角）

【硬性要求】
- 数据基于2025-2026年事实，公司必须真实存在
- 三层不重复，边界清晰
- 只输出纯净JSON

【JSON Schema】
{"valueChain":{"flowNote":"...","keyInsight":"...","upstream":{"role":"...","desc":"...","marginLevel":"...","bargainPower":"...","segments":[{"name":"...","players":["..."],"note":"..."}]},"midstream":{...},"downstream":{...}}}'''
    }


def generate_keywords(industry_name: str, batch: int, max_retries: int = 2) -> list:
    """生成一批关键词（50 条）"""
    prompts = load_prompts()
    
    if batch == 1:
        user = f'''请为「{industry_name}」行业生成 50 个关键词信息卡片，严格6件套格式。
要求：
- rank: 1-50
- 前30个为该行业最核心、最高频的入门概念
- 31-50个为重要的财务/商业概念
- cat分布：约25个core + 25个finance/biz
只返回 keywords 数组的JSON。'''
    else:
        user = f'''请为「{industry_name}」行业生成 50 个关键词信息卡片（rank 51-100），严格6件套格式。
要求：
- rank: 51-100
- 51-80为重要但稍专业的技术/术语概念
- 81-100为细分领域、长尾、政策法规、新兴趋势
- cat分布：约30个tech + 20个biz/core
- 不要重复1-50的概念
只返回 keywords 数组的JSON。'''
    
    for attempt in range(1, max_retries + 1):
        print(f'  ▶️  关键词 batch{batch} 第 {attempt} 次尝试...', flush=True)
        res = call_deepseek(prompts['kw_system'], user, max_tokens=16384)
        if '__error' in res:
            print(f'  ⚠️  错误: {res["__error"][:80]}', flush=True)
            time.sleep(3)
            continue
        kws = res.get('keywords', [])
        ok, stats = check_kw_quality(kws, expected_count=50)
        print(f'  📊  {stats}', flush=True)
        if ok:
            return kws
        print(f'  🔄 质量不达标，重试', flush=True)
    
    # 返回最后一次的结果（即便不达标也不阻塞）
    return res.get('keywords', []) if isinstance(res, dict) else []


def generate_companies(industry_name: str, max_retries: int = 2) -> list:
    """生成 3 家公司"""
    prompts = load_prompts()
    user = f'''请为「{industry_name}」行业输出3家最具代表性的标杆公司的详细拆解，严格JSON。
要求：
- 真实存在的该行业头部公司
- 含完整字段（见schema）
- moatPro 100字+
- revenue 至少3条，pct加和=100
只返回 companies 数组的JSON。'''
    
    for attempt in range(1, max_retries + 1):
        print(f'  ▶️  公司数据 第 {attempt} 次尝试...', flush=True)
        res = call_deepseek(prompts['co_system'], user, max_tokens=8192)
        if '__error' in res:
            time.sleep(3)
            continue
        cos = res.get('companies', [])
        ok, stats = check_co_quality(cos)
        print(f'  📊  {stats}', flush=True)
        if ok:
            return cos
    
    return res.get('companies', []) if isinstance(res, dict) else []


def check_vc_quality(vc: dict) -> tuple:
    """产业链数据质检"""
    if not vc or not isinstance(vc, dict):
        return False, '空对象'
    missing = []
    for layer in ['upstream', 'midstream', 'downstream']:
        l = vc.get(layer)
        if not l or not isinstance(l, dict):
            missing.append(layer)
            continue
        if not l.get('role') or not l.get('desc'):
            missing.append(f'{layer}.role/desc')
        segs = l.get('segments', [])
        if len(segs) < 3:
            missing.append(f'{layer}.segments<3')
        for s in segs:
            if not s.get('players') or len(s.get('players', [])) < 2:
                missing.append(f'{layer}.{s.get("name","?")}.players<2')
                break
    if missing:
        return False, f'缺项: {missing[:3]}'
    return True, f"3层完整, 细分 {sum(len(vc[x].get('segments',[])) for x in ['upstream','midstream','downstream'])} 个"


def generate_value_chain(industry_name: str, max_retries: int = 2) -> dict:
    """生成产业链上中下游数据"""
    prompts = load_prompts()
    user = f'''请为「{industry_name}」行业输出完整的产业链上中下游拆解，严格JSON。
要求：
- 三层 upstream / midstream / downstream，每层 3-5 个细分环节
- 每个环节 3-5 家真实代表公司
- 含 role / desc / segments / marginLevel / bargainPower
- flowNote 说明价值流动逻辑，keyInsight 点出核心矛盾
- 数据基于 2025-2026 年事实
只返回 valueChain 对象的JSON。'''
    
    res = {}
    for attempt in range(1, max_retries + 1):
        print(f'  ▶️  产业链数据 第 {attempt} 次尝试...', flush=True)
        res = call_deepseek(prompts['vc_system'], user, max_tokens=6000)
        if '__error' in res:
            time.sleep(3)
            continue
        vc = res.get('valueChain', {})
        ok, stats = check_vc_quality(vc)
        print(f'  📊  {stats}', flush=True)
        if ok:
            return vc
    
    return res.get('valueChain', {}) if isinstance(res, dict) else {}


def build_html(industry_name: str, keywords: list, companies: list, industry_desc: str = '', value_chain: dict = None) -> str:
    """拼装 HTML"""
    template_path = SCRIPT_DIR / 'html_template.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    industry_obj = {'name': industry_name, 'desc': industry_desc or ''}
    vc = value_chain or {}
    
    # 替换占位符
    html = html.replace('{{INDUSTRY_NAME}}', industry_name)
    html = html.replace('{{INDUSTRY_DESC}}', industry_desc or industry_name + ' 行业的关键词百科与标杆公司拆解')
    html = html.replace('{{INDUSTRY_JSON}}', json.dumps(industry_obj, ensure_ascii=False))
    html = html.replace('{{KEYWORDS_JSON}}', json.dumps(keywords, ensure_ascii=False))
    html = html.replace('{{COMPANIES_JSON}}', json.dumps(companies, ensure_ascii=False))
    html = html.replace('{{VALUE_CHAIN_JSON}}', json.dumps(vc, ensure_ascii=False))
    
    return html


def generate_industry_page(industry_name: str, output_path: str = None, preloaded_source: str = None, skip_value_chain: bool = False):
    """
    主入口：生成完整行业百科 HTML
    
    :param industry_name: 行业名称
    :param output_path: 输出文件路径（可选，默认 ./{行业名}-百科.html）
    :param preloaded_source: 已有数据源路径（可选，如果提供则优先从该文件读取，跳过 API 调用）
    :param skip_value_chain: 若 True 则不生成产业链上中下游（加速测试用）
    """
    print(f'🚀 开始生成「{industry_name}」行业百科')
    
    # Try preloaded source first
    keywords, companies, desc = [], [], ''
    value_chain = {}
    if preloaded_source and os.path.exists(preloaded_source):
        try:
            # Assume JS file with window.XXX = {...}
            import re
            with open(preloaded_source, encoding='utf-8') as f:
                content = f.read()
            m = re.search(r'=\s*(\{.*\});', content, re.DOTALL)
            if m:
                data = json.loads(m.group(1))
                # Try match by ind_name
                for ind_id, payload in data.items():
                    if payload.get('industry', {}).get('name') == industry_name:
                        keywords = payload.get('keywords', [])
                        companies = payload.get('companies', [])
                        desc = payload.get('industry', {}).get('desc', '')
                        value_chain = payload.get('valueChain', {})
                        print(f'  ✨ 从 preloaded 中找到「{industry_name}」: {len(keywords)} 词 + {len(companies)} 公司' + (' + 产业链' if value_chain else ''))
                        break
        except Exception as e:
            print(f'  ⚠️  preloaded 读取失败: {e}')
    
    if not keywords:
        # Call API
        kws1 = generate_keywords(industry_name, 1)
        kws2 = generate_keywords(industry_name, 2)
        keywords = kws1 + kws2
        # 修正 rank
        for i, k in enumerate(keywords):
            k['rank'] = i + 1
        companies = generate_companies(industry_name)
    
    # 产业链：独立调用（preloaded 没有或不完整时补调）
    if not skip_value_chain and (not value_chain or 'upstream' not in value_chain):
        value_chain = generate_value_chain(industry_name)
    
    if not keywords or not companies:
        print(f'❌ 生成失败：关键词 {len(keywords)} 条 + 公司 {len(companies)} 个')
        return None
    
    # Build HTML
    html = build_html(industry_name, keywords, companies, desc, value_chain)
    
    # Write
    if not output_path:
        output_path = f'./{industry_name}-百科.html'
    output_path = os.path.abspath(output_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    size_kb = os.path.getsize(output_path) / 1024
    print(f'✅ 完成: {output_path} ({size_kb:.0f} KB)')
    print(f'   关键词: {len(keywords)} 条')
    print(f'   公司: {len(companies)} 家')
    if value_chain and 'upstream' in value_chain:
        seg_count = sum(len(value_chain[x].get('segments', [])) for x in ['upstream','midstream','downstream'] if x in value_chain)
        print(f'   产业链: 3 层 / {seg_count} 个细分环节')
    
    return output_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('industry', help='行业名称')
    parser.add_argument('output', nargs='?', help='输出路径（可选）')
    parser.add_argument('--preloaded', help='从已有数据源读取（可选）', default=None)
    parser.add_argument('--skip-value-chain', action='store_true', help='不生成产业链上中下游')
    args = parser.parse_args()
    
    generate_industry_page(args.industry, args.output, args.preloaded, args.skip_value_chain)
