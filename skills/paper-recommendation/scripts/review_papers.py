#!/usr/bin/env python3
"""
 Jarvis Research Skill - Script 2: Paper Review with Sub-agents

 Spawns sub-agents to read and review papers in parallel.

 Usage:
   python3 review_papers.py --papers '<json>' [--json]

 Input:
   JSON with paper list (from fetch_papers.py)

 Output:
   JSON with sub-agent reviews and scores
"""

import json
import argparse
import sys
from datetime import datetime

# Sub-agent task template for paper review
SUBAGENT_TASK_TEMPLATE = """请完整阅读这篇论文并给出评分：

论文信息：
- 标题: {title}
- 作者: {authors}
- 摘要: {summary}
- arXiv: {url}

请执行以下任务：
1. 完整阅读论文（通过 arXiv HTML 页面获取完整内容）
2. 提取：机构、完整摘要、核心贡献、主要结论、实验结果
3. 评估论文质量（1-5分）
4. 给出推荐建议（yes/no）

回复 JSON 格式：
{{"review": {{
    "id": "{paper_id}",
    "score": 5,
    "contribution": "一句话核心贡献",
    "conclusion": "一句话主要结论",
    "experiments": "实验设置和关键发现",
    "recommended": "yes"
}}}}"""

def generate_subagent_tasks(papers):
    """Generate sub-agent tasks for each paper."""
    tasks = []
    for p in papers:
        task = SUBAGENT_TASK_TEMPLATE.format(
            paper_id=p['id'],
            title=p['title'],
            authors=', '.join(p.get('authors', [])),
            summary=p.get('summary', '')[:500],
            url=p.get('url', '')
        )
        tasks.append({
            'paper_id': p['id'],
            'task': task,
            'label': f"review-{p['id']}"
        })
    return tasks


def main():
    parser = argparse.ArgumentParser(description='Spawn sub-agents to review papers')
    parser.add_argument('--papers', type=str, help='Papers JSON string')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    
    args = parser.parse_args()
    
    # Get papers from stdin or args
    if args.papers:
        papers = json.loads(args.papers).get('papers', [])
    else:
        papers_data = sys.stdin.read()
        papers = json.loads(papers_data).get('papers', [])
    
    if not papers:
        result = {'error': 'No papers provided', 'papers': []}
        if args.json:
            print(json.dumps(result, indent=2))
        return result
    
    # Generate sub-agent tasks
    tasks = generate_subagent_tasks(papers)
    
    result = {
        'papers': papers,
        'subagent_tasks': tasks,
        'count': len(tasks),
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'instructions': """使用 sessions_spawn 开子代理阅读每篇论文：

for task in tasks:
    clawdbot sessions spawn --task "<task>" --label "<label>"

子代理返回后，收集评分并决定最终推荐。"""
    }
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"生成 {len(tasks)} 个子代理任务")
        print("\n使用方法：")
        print(result['instructions'])
    
    return result


if __name__ == '__main__':
    main()
