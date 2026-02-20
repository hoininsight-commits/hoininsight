from src.issuesignal.decision_tree import DecisionTree

def test_tree_structure():
    tree = DecisionTree()
    data = tree.get_tree_data()
    
    # 1. Check Node Count (Spec R7: 5 nodes)
    assert len(data) == 5, f"Expected 5 nodes, got {len(data)}"
    
    # 2. Check Order and Labels (Spec R1 & R7)
    expected_names = ["데이터 수집", "팩트 체크", "시점 분석", "주인공 매칭", "품질 하한선"]
    actual_names = [node['name'] for node in data]
    assert actual_names == expected_names, f"Expected {expected_names}, got {actual_names}"
    
    # 3. Check Initial Status
    for node in data:
        assert node['status'] == 'PENDING'

if __name__ == "__main__":
    test_tree_structure()
    print("[VERIFY] verify_is72_tree_structure.py passed!")
