import json
from typing import List, Dict, Any, Optional

def read_json(file_path: str) -> Dict[str, List[str]]:
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def analyze(seeded_targets: Dict[str, List[str]], unseeded_targets: Dict[str, List[str]], prefix: Optional[str] = None) -> Dict[str, int]:
    # Filter targets by prefix if prefix is provided
    if prefix:
        seed_set = set(filter(lambda x: x.startswith(prefix), seeded_targets['seeded']))
        seeded_run_set = set(filter(lambda x: x.startswith(prefix), seeded_targets['lastSeen']))
        unseeded_run_set = set(filter(lambda x: x.startswith(prefix), unseeded_targets['lastSeen']))
    else:
        seed_set = set(seeded_targets['seeded'])
        seeded_run_set = set(seeded_targets['lastSeen'])
        unseeded_run_set = set(unseeded_targets['lastSeen'])

    # Remove seed_set items from seeded_run_set
    seeded_run_set = seeded_run_set - seed_set

    total_seeded_targets = seed_set | seeded_run_set

    # Calculate unique counts
    seed_unique = len(seed_set - seeded_run_set - unseeded_run_set)
    seeded_run_unique = len(seeded_run_set - seed_set - unseeded_run_set)
    unseeded_run_unique = len(unseeded_run_set - seed_set - seeded_run_set)

    # Calculate intersections
    seed_and_seeded_run = len(seed_set & seeded_run_set)
    seed_and_unseeded_run = len(seed_set & unseeded_run_set)
    seeded_run_and_unseeded_run = len(seeded_run_set & unseeded_run_set)
    all_three_intersection = len(seed_set & seeded_run_set & unseeded_run_set)

    return {
        "|Es|": len(total_seeded_targets),
        "|S|": len(seed_set),
        "|Eu|": len(unseeded_run_set),
        "|S \ Eu|": seed_unique,
        "Es \ (S ∪ Eu)": seeded_run_unique,
        "Eu \ Es": unseeded_run_unique,
        "S ∩ Eu": seed_and_unseeded_run,
        "Es ∩ Eu": seeded_run_and_unseeded_run,
    }

def calculate_averages(results: List[Dict[str, int]]) -> Dict[str, float]:
    if not results:
        return {}
    
    average_result = {key: 0.0 for key in results[0].keys()}
    num_results = len(results)
    
    for result in results:
        for key in result:
            average_result[key] += result[key]
    
    for key in average_result:
        average_result[key] /= num_results
    
    return average_result

def print_averages(sut_name: str, results: List[Dict[str, int]]) -> None:
    averages = calculate_averages(results)
    print(f"Averages for {sut_name}:")
    for key, value in averages.items():
        print(f"{key}: {value}")
    print("\n")

def process_sut(sut_name: str, seeded_paths: List[str], unseeded_paths: List[str], prefix: Optional[str] = None) -> List[Dict[str, int]]:
    results = []
    for seeded_path in seeded_paths:
        seeded_data = read_json(seeded_path)
        for unseeded_path in unseeded_paths:
            unseeded_data = read_json(unseeded_path)
            results.append(analyze(seeded_data, unseeded_data, prefix=prefix))
    return results

# Paths for each SUT
sut_paths: Dict[str, Dict[str, List[str]]] = {
    "genome-nexus": {
        "seeded": [
            'results/genome-nexus/seeded/run1/targets.json',
            'results/genome-nexus/seeded/run2/targets.json',
            'results/genome-nexus/seeded/run3/targets.json'
        ],
        "unseeded": [
            'results/genome-nexus/unseeded/run1/targets.json',
            'results/genome-nexus/unseeded/run2/targets.json',
            'results/genome-nexus/unseeded/run4/targets.json'
        ]
    },
    "scout-api": {
        "seeded": [
            'results/scout-api/seeded/run1/targets.json',
            'results/scout-api/seeded/run2/targets.json',
            'results/scout-api/seeded/run3/targets.json'
        ],
        "unseeded": [
            'results/scout-api/unseeded/run1/targets.json',
            'results/scout-api/unseeded/run2/targets.json',
            'results/scout-api/unseeded/run3/targets.json'
        ]
    },
    "catwatch": {
        "seeded": [
            'results/catwatch/seeded/run1/targets.json',
            'results/catwatch/seeded/run2/targets.json',
            'results/catwatch/seeded/run3/targets.json',
        ],
        "unseeded": [
            'results/catwatch/unseeded/run1/targets.json',
            'results/catwatch/unseeded/run2/targets.json',
            'results/catwatch/unseeded/run3/targets.json'
        ]
    }
}

# Process and print averages for each SUT
for sut_name, paths in sut_paths.items():
    results = process_sut(sut_name, paths['seeded'], paths['unseeded'])
    print_averages(sut_name, results)
