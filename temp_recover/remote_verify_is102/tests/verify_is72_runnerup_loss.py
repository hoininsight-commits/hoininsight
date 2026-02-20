from src.issuesignal.decision_tree import DecisionTree

def test_runnerup_loss():
    # 1. Success Path
    results_ok = {"DA": True, "HF": True, "WN": True, "AM": True, "QF": True}
    path_ok = DecisionTree.create_path(results_ok)
    assert all(n['status'] == 'PASS' for n in path_ok)
    
    # 2. Failure at 'Why-Now' (Step 3)
    results_wn_fail = {"DA": True, "HF": True, "WN": False, "AM": True, "QF": True}
    path_fail = DecisionTree.create_path(results_wn_fail)
    
    # Check nodes
    assert path_fail[0]['status'] == 'PASS' # 데이터 수집
    assert path_fail[1]['status'] == 'PASS' # 팩트 체크
    assert path_fail[2]['status'] == 'FAIL' # 시점 분석 (최초 실패)
    assert path_fail[3]['status'] == 'PENDING' # 주인공 매칭 (이후는 PENDING)
    assert path_fail[4]['status'] == 'PENDING' # 품질 하한선 (이후는 PENDING)
    
    # 3. First Fail Logic
    tree = DecisionTree()
    for n in path_fail:
        tree.update_node(n['name'], n['status'])
    
    assert tree.get_first_fail_node() == "시점 분석"

if __name__ == "__main__":
    test_runnerup_loss()
    print("[VERIFY] verify_is72_runnerup_loss.py passed!")
