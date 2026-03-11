#!/usr/bin/env python3
"""
请求追踪工具 - 记录用户请求和执行结果
格式：紧凑 JSON + 自动索引
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict, field

@dataclass
class UserRequest:
    """用户请求"""
    id: str                    # 唯一 ID: REQ-YYYYMMDD-HHMMSS
    timestamp: str             # 请求时间
    user_name: str             # 用户名称
    request_type: str          # 类型：search/create/analyze/fix/consult/other
    content: str               # 请求内容
    context: Dict = field(default_factory=dict)  # 上下文信息
    priority: str = "normal"   # high/normal/low
    
@dataclass
class Execution:
    """执行记录"""
    request_id: str            # 关联的请求 ID
    start_time: str            # 开始时间
    end_time: str              # 结束时间
    actions: List[str]         # 执行的动作
    results: List[str]         # 结果摘要
    files_created: List[str]   # 创建的文件
    files_modified: List[str]  # 修改的文件
    success: bool              # 是否成功
    metrics: Dict = field(default_factory=dict)  # 性能指标
    
@dataclass
class Reflection:
    """反思记录"""
    request_id: str            # 关联的请求 ID
    timestamp: str             # 反思时间
    what_went_well: List[str]  # 做得好的
    what_went_wrong: List[str] # 出问题的
    improvements: List[str]    # 改进建议
    unnecessary: List[str]     # 不必要的步骤
    lessons: List[str]         # 学到的经验

@dataclass
class RequestRecord:
    """完整请求记录"""
    request: UserRequest
    execution: Optional[Execution]
    reflection: Optional[Reflection]

class RequestTracker:
    """请求追踪器"""
    
    def __init__(self, memory_dir: str = None):
        if memory_dir is None:
            self.memory_dir = os.path.expanduser(r'~\.openclaw\workspace\memory')
        else:
            self.memory_dir = memory_dir
        
        self.requests_file = os.path.join(self.memory_dir, 'requests.jsonl')
        self._ensure_file()
    
    def _ensure_file(self):
        """确保文件存在"""
        os.makedirs(self.memory_dir, exist_ok=True)
        if not os.path.exists(self.requests_file):
            with open(self.requests_file, 'w', encoding='utf-8') as f:
                pass  # 创建空文件
    
    def _generate_id(self) -> str:
        """生成唯一 ID"""
        now = datetime.now()
        return f"REQ-{now.strftime('%Y%m%d-%H%M%S')}"
    
    def log_request(self, content: str, request_type: str = "other", 
                    context: Dict = None, priority: str = "normal") -> str:
        """记录用户请求"""
        request = UserRequest(
            id=self._generate_id(),
            timestamp=datetime.now().isoformat(),
            user_name="庆",
            request_type=request_type,
            content=content,
            context=context or {},
            priority=priority
        )
        
        record = RequestRecord(request=request, execution=None, reflection=None)
        self._write_record(record)
        
        print(f"[REQUEST] {request.id}: {content[:50]}...")
        return request.id
    
    def log_execution(self, request_id: str, actions: List[str], 
                      results: List[str], files_created: List[str] = None,
                      files_modified: List[str] = None, 
                      metrics: Dict = None, success: bool = True):
        """记录执行过程"""
        execution = Execution(
            request_id=request_id,
            start_time=datetime.now().isoformat(),
            end_time=datetime.now().isoformat(),
            actions=actions,
            results=results,
            files_created=files_created or [],
            files_modified=files_modified or [],
            metrics=metrics or {},
            success=success
        )
        
        # 更新记录
        records = self._read_all()
        for record in records:
            if record.request.id == request_id:
                record.execution = execution
                break
        
        self._write_all(records)
        print(f"[EXECUTION] {request_id}: {len(actions)} actions, success={success}")
    
    def log_reflection(self, request_id: str, 
                       what_went_well: List[str] = None,
                       what_went_wrong: List[str] = None,
                       improvements: List[str] = None,
                       unnecessary: List[str] = None,
                       lessons: List[str] = None):
        """记录反思"""
        reflection = Reflection(
            request_id=request_id,
            timestamp=datetime.now().isoformat(),
            what_went_well=what_went_well or [],
            what_went_wrong=what_went_wrong or [],
            improvements=improvements or [],
            unnecessary=unnecessary or [],
            lessons=lessons or []
        )
        
        # 更新记录
        records = self._read_all()
        for record in records:
            if record.request.id == request_id:
                record.reflection = reflection
                break
        
        self._write_all(records)
        print(f"[REFLECTION] {request_id}: {len(lessons or [])} lessons learned")
    
    def _write_record(self, record: RequestRecord):
        """写入单条记录"""
        with open(self.requests_file, 'a', encoding='utf-8') as f:
            data = asdict(record)
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    def _write_all(self, records: List[RequestRecord]):
        """写入所有记录"""
        with open(self.requests_file, 'w', encoding='utf-8') as f:
            for record in records:
                data = asdict(record)
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    def _read_all(self) -> List[RequestRecord]:
        """读取所有记录"""
        records = []
        with open(self.requests_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    record = RequestRecord(
                        request=UserRequest(**data['request']),
                        execution=Execution(**data['execution']) if data.get('execution') else None,
                        reflection=Reflection(**data['reflection']) if data.get('reflection') else None
                    )
                    records.append(record)
        return records
    
    def search(self, query: str) -> List[RequestRecord]:
        """搜索请求"""
        records = self._read_all()
        results = []
        query_lower = query.lower()
        
        for record in records:
            searchable = f"{record.request.content} {' '.join(record.execution.results if record.execution else [])}".lower()
            if query_lower in searchable:
                results.append(record)
        
        return results
    
    def get_by_date(self, date: str) -> List[RequestRecord]:
        """按日期获取请求"""
        records = self._read_all()
        return [r for r in records if r.request.timestamp.startswith(date)]
    
    def get_by_type(self, request_type: str) -> List[RequestRecord]:
        """按类型获取请求"""
        records = self._read_all()
        return [r for r in records if r.request.request_type == request_type]
    
    def summary(self) -> str:
        """生成摘要"""
        records = self._read_all()
        
        lines = [
            f"[REQUEST TRACKER] Summary",
            f"   Total requests: {len(records)}",
            f"",
            f"Recent requests:"
        ]
        
        # 最近 10 条
        recent = sorted(records, key=lambda r: r.request.timestamp, reverse=True)[:10]
        for record in recent:
            req = record.request
            status = "[OK]" if record.execution and record.execution.success else "[PENDING]"
            lines.append(f"   {status} [{req.timestamp[:10]}] {req.content[:50]}")
        
        return '\n'.join(lines)

# 命令行工具
if __name__ == '__main__':
    import sys
    
    tracker = RequestTracker()
    
    if len(sys.argv) < 2:
        print("Usage: request_tracker.py <command> [args]")
        print("Commands:")
        print("  summary              - 显示请求摘要")
        print("  search <query>       - 搜索请求")
        print("  date <YYYY-MM-DD>    - 按日期获取")
        print("  type <type>          - 按类型获取 (search/create/analyze/fix/consult)")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'summary':
        print(tracker.summary())
    
    elif cmd == 'search':
        query = ' '.join(sys.argv[2:])
        results = tracker.search(query)
        print(f"\n[SEARCH: {query}]")
        print(f"  Found: {len(results)} results")
        for r in results:
            print(f"  [{r.request.timestamp[:10]}] {r.request.content}")
    
    elif cmd == 'date':
        date = sys.argv[2]
        results = tracker.get_by_date(date)
        print(f"\n[DATE: {date}]")
        print(f"  Found: {len(results)} results")
        for r in results:
            print(f"  [{r.request.timestamp}] {r.request.content}")
    
    elif cmd == 'type':
        req_type = sys.argv[2]
        results = tracker.get_by_type(req_type)
        print(f"\n[TYPE: {req_type}]")
        print(f"  Found: {len(results)} results")
        for r in results:
            print(f"  [{r.request.timestamp[:10]}] {r.request.content}")
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
