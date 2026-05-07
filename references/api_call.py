"""
DeepSeek API 调用封装 — 为 IndustryLens 使用
关键点：
- 用 curl -k 避免 SSL 证书校验失败
- 用临时文件传 --data @file.json 避免 shell 截断
- 带重试，超时 420s（大请求需要时间）

用法：
    from api_call import call_deepseek
    result = call_deepseek(system="...", user="...")
"""
import os, json, time, tempfile, subprocess


DEFAULT_API_KEY = ''  # 禁止硬编码。通过环境变量 DS_KEY 或 api_key 参数传入
API_URL = 'https://api.deepseek.com/v1/chat/completions'


def call_deepseek(system: str, user: str, max_tokens: int = 16384,
                  temperature: float = 0.5, max_retries: int = 3,
                  api_key: str = None) -> dict:
    """
    调用 DeepSeek，返回解析后的 JSON（JSON schema 由 prompt 指定）。
    失败返回 {'__error': 'xxx'}。
    """
    api_key = api_key or os.environ.get('DS_KEY') or DEFAULT_API_KEY
    if not api_key:
        return {'__error': '请设置 DeepSeek API Key：export DS_KEY=sk-xxx 或 api_key 参数传入'}
    
    body = json.dumps({
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': user}
        ],
        'temperature': temperature,
        'max_tokens': max_tokens,
        'response_format': {'type': 'json_object'}
    }, ensure_ascii=False)
    
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    tmp.write(body)
    tmp.close()
    
    try:
        for attempt in range(1, max_retries + 1):
            try:
                result = subprocess.run([
                    'curl', '-s', '-k', '--max-time', '420',
                    '-X', 'POST',
                    '-H', f'Authorization: Bearer {api_key}',
                    '-H', 'Content-Type: application/json',
                    '--data', f'@{tmp.name}',
                    API_URL
                ], capture_output=True, text=True, timeout=450)
                
                if result.returncode != 0:
                    if attempt < max_retries:
                        time.sleep(3 * attempt)
                        continue
                    return {'__error': f'curl_fail: {result.stderr[:200]}'}
                
                data = json.loads(result.stdout)
                content = data['choices'][0]['message']['content']
                return json.loads(content)
                
            except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError) as e:
                if attempt < max_retries:
                    time.sleep(3 * attempt)
                else:
                    return {'__error': f'{type(e).__name__}: {str(e)[:200]}'}
        
        return {'__error': 'max_retries_exhausted'}
    finally:
        try: os.unlink(tmp.name)
        except: pass


def check_kw_quality(kws: list, expected_count: int = 50) -> tuple:
    """检查关键词批次质量，返回 (is_ok, stats_str)"""
    if not kws or len(kws) < expected_count * 0.8:
        return False, f'count={len(kws)}'
    
    pro_lens = [len(k.get('pro', '')) for k in kws]
    id_lens = [len(k.get('industryData', '')) for k in kws]
    ez_lens = [len(k.get('ez', '')) for k in kws]
    has_ref = sum(1 for k in kws if k.get('ref') and k['ref'].get('google'))
    
    avg_pro = sum(pro_lens) / len(pro_lens)
    avg_id = sum(id_lens) / len(id_lens)
    avg_ez = sum(ez_lens) / len(ez_lens)
    good_pro = sum(1 for l in pro_lens if l >= 130)  # 升级到 130 字基准
    good_id = sum(1 for l in id_lens if l >= 35)
    good_ez = sum(1 for l in ez_lens if l >= 22)
    threshold = int(len(kws) * 0.7)
    
    ok = (avg_pro >= 130 and avg_id >= 35 and avg_ez >= 22
          and good_pro >= threshold and good_id >= threshold and good_ez >= threshold
          and has_ref >= threshold)
    stats = f'kw={len(kws)} pro={avg_pro:.0f}(g{good_pro}) id={avg_id:.0f}(g{good_id}) ez={avg_ez:.0f}(g{good_ez}) ref={has_ref}'
    return ok, stats


def check_co_quality(cos: list) -> tuple:
    """检查公司数据质量"""
    if not cos or len(cos) < 3:
        return False, f'cos={len(cos)}'
    moat_lens = [len(c.get('moatPro', '')) for c in cos]
    avg_moat = sum(moat_lens) / len(moat_lens) if moat_lens else 0
    has_rev = sum(1 for c in cos if isinstance(c.get('revenue'), list) and len(c['revenue']) >= 3)
    ok = avg_moat >= 80 and has_rev == len(cos)
    return ok, f'cos={len(cos)} moat={avg_moat:.0f} rev={has_rev}'


if __name__ == '__main__':
    # 简单测试
    r = call_deepseek(
        system='你是一位行业研究员，返回 JSON。',
        user='请用 JSON 返回 {"test":"ok"}'
    )
    print(r)
