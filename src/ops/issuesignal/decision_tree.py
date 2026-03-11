from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class DecisionNode:
    name: str # 한글 단계명
    status: str # 'PASS', 'FAIL', 'PENDING'
    description: str = ""

class DecisionTree:
    """
    IS-72: Operator Decision Tree Engine
    후보별 의사결정 경로를 추적하고 트리 데이터를 생성합니다.
    """
    
    NODES_MAP = [
        ("DA", "데이터 수집"),
        ("HF", "팩트 체크"),
        ("WN", "시점 분석"),
        ("AM", "주인공 매칭"),
        ("QF", "품질 하한선")
    ]

    def __init__(self):
        self.path: List[DecisionNode] = []
        self._init_tree()

    def _init_tree(self):
        for id, name in self.NODES_MAP:
            self.path.append(DecisionNode(name=name, status='PENDING'))

    def update_node(self, node_name_ko: str, status: str, description: str = ""):
        """특정 노드의 상태를 업데이트합니다."""
        for node in self.path:
            if node.name == node_name_ko:
                node.status = status
                node.description = description
                break

    def get_tree_data(self) -> List[Dict[str, Any]]:
        """대시보드 렌더링을 위한 사전 형태로 변환합니다."""
        return [
            {
                "name": node.name,
                "status": node.status,
                "description": node.description
            } for node in self.path
        ]

    def get_first_fail_node(self) -> Optional[str]:
        """최초로 실패한 노드의 이름을 반환합니다."""
        for node in self.path:
            if node.status == 'FAIL':
                return node.name
        return None

    @staticmethod
    def create_path(results: Dict[str, bool]) -> List[Dict[str, Any]]:
        """간소화된 결과 맵으로부터 트리 데이터를 생성합니다."""
        tree = DecisionTree()
        for id, name in DecisionTree.NODES_MAP:
            status = 'PASS' if results.get(id, False) else 'FAIL'
            tree.update_node(name, status)
            if status == 'FAIL': break # 첫 실패 이후는 PENDING 유지
        return tree.get_tree_data()
