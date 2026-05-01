import json
from typing import Any, Dict, List, Union

class DataCondenser:
    """[v22.0] High-Density Data Condenser
    Transforms raw JSON data into high-signal, low-token intelligence maps.
    """

    def __init__(self):
        self.exclude_keys = [
            'metadata', 'collected_at', 'ttl_policy_minutes', 'snippet', 
            'url', 'success_count', 'elapsed_seconds', 'run_at', 'link'
        ]

    def condense(self, data: Dict[str, Any]) -> str:
        """Main entry point: Cleans, Compresses, and Serializes data."""
        cleaned_data = self._clean_recursive(data)
        return self._serialize_optimized(cleaned_data)

    def _clean_recursive(self, obj: Any) -> Any:
        """Logic A & C: Metadata removal, null filtering, and strategic sampling."""
        if isinstance(obj, dict):
            # 1. Logic A: Exclude noise keys and empty values
            new_dict = {}
            for k, v in obj.items():
                if k in self.exclude_keys:
                    continue
                
                # Logic B: Compress trend/history arrays
                if (k == 'history_90d' or k == 'trend') and isinstance(v, list) and v:
                    new_dict[f"{k}_stat"] = self._compress_trend(v)
                    continue

                cleaned_v = self._clean_recursive(v)
                if cleaned_v not in [None, [], {}, ""]:
                    new_dict[k] = cleaned_v
            return new_dict

        elif isinstance(obj, list):
            if not obj:
                return []
            
            # Logic C: Strategic Sampling for social/news lists
            first_item = obj[0]
            if isinstance(first_item, dict) and any(k in first_item for k in ['points', 'score', 'comments']):
                # Sort by impact (points/score) and take top 5
                sorted_list = sorted(
                    obj, 
                    key=lambda x: x.get('points', x.get('score', x.get('comments', 0))), 
                    reverse=True
                )[:7] # Keep top 7 for slightly more context than 5
                return [self._clean_recursive(x) for x in sorted_list]
            
            return [self._clean_recursive(x) for x in obj]
        
        return obj

    def _compress_trend(self, trend: List[Union[int, float]]) -> str:
        """Logic B: Context Compression for time-series data."""
        if not trend:
            return "N/A"
        
        try:
            numeric_trend = [float(x) for x in trend if x is not None]
            if not numeric_trend:
                return "N/A"
            
            avg = sum(numeric_trend) / len(numeric_trend)
            hi = max(numeric_trend)
            lo = min(numeric_trend)
            last = numeric_trend[-1]
            last_3 = numeric_trend[-3:] if len(numeric_trend) >= 3 else numeric_trend
            
            return f"Last3:{last_3} | Avg:{avg:.1f} | Max:{hi} | Min:{lo}"
        except:
            return str(trend[-3:])

    def _serialize_optimized(self, data: Any, indent: int = 0) -> str:
        """Logic D: Serialization Optimization (Simplified Text Format)."""
        lines = []
        
        if isinstance(data, dict):
            for k, v in data.items():
                prefix = "  " * indent
                if isinstance(v, (dict, list)):
                    lines.append(f"{prefix}[{k}]")
                    lines.append(self._serialize_optimized(v, indent + 1))
                else:
                    lines.append(f"{prefix}{k}: {v}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                prefix = "  " * indent
                if isinstance(item, (dict, list)):
                    lines.append(f"{prefix}- Item {i+1}:")
                    lines.append(self._serialize_optimized(item, indent + 1))
                else:
                    lines.append(f"{prefix}- {item}")
        else:
            return str(data)

        return "\n".join([line for line in lines if line.strip()])

if __name__ == "__main__":
    # Quick Test
    test_data = {
        "metadata": {"version": "1.0"},
        "market": {
            "kospi": {"current": 2500, "trend": [2400, 2450, 2500]},
            "empty": None
        },
        "social": [
            {"title": "Good News", "points": 100, "snippet": "too long"},
            {"title": "Bad News", "points": 10, "url": "http://skip.me"}
        ]
    }
    condenser = DataCondenser()
    print(condenser.condense(test_data))
