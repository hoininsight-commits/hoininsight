import json
from src.utils.data_condenser import DataCondenser
from pathlib import Path

def prepare():
    condenser = DataCondenser()
    raw_dir = Path('data/raw/20260501/2/')
    all_data = {}
    
    # 1. 모든 로우 데이터 로드
    for f in raw_dir.glob('*.json'):
        if f.name == 'collection_status.json': continue
        try:
            all_data[f.stem] = json.loads(f.read_text())
        except:
            continue
            
    # 2. 데이터 고농축 압축
    condensed_text = condenser.condense(all_data)
    
    # 3. 파일 저장
    Path('condensed_data_for_user.txt').write_text(condensed_text, encoding='utf-8')
    print(f"✅ Condensed data saved (Size: {len(condensed_text)} chars)")

if __name__ == "__main__":
    prepare()
