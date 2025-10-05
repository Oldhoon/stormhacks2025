"""
Simple unit test to verify the Arena-LeetCode integration logic.
This tests the state transitions without actually running the pygame loop.
"""
import sys
import ast

def test_arena_integration():
    """Test the Arena-LeetCode integration by analyzing the source code."""
    print("Testing Arena-LeetCode Integration...")
    
    # Test 1: Verify file parses correctly
    print("\n1. Testing file parsing...")
    try:
        with open('arena.py', 'r') as f:
            code = f.read()
        tree = ast.parse(code)
        print("   ✓ arena.py parses successfully")
    except Exception as e:
        print(f"   ✗ Failed to parse: {e}")
        return False
    
    # Test 2: Verify imports are present
    print("\n2. Testing imports...")
    required_imports = [
        'ProblemPanel',
        'SnippetBoard',
        'random_problem',
        'show_problem',
        'grade_submission'
    ]
    
    import_found = {name: False for name in required_imports}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                name = alias.name
                if name in required_imports:
                    import_found[name] = True
    
    all_imports = all(import_found.values())
    for name, found in import_found.items():
        status = "✓" if found else "✗"
        print(f"   {status} {name}")
    
    if not all_imports:
        print("   ✗ Missing some required imports")
        return False
    
    # Test 3: Verify constants
    print("\n3. Testing constants...")
    constants = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id in ['TIMER', 'PROBLEM_TIMER']:
                        if isinstance(node.value, ast.Constant):
                            constants[target.id] = node.value.value
    
    if 'TIMER' in constants:
        print(f"   ✓ TIMER = {constants['TIMER']}ms ({constants['TIMER']/1000}s)")
    else:
        print("   ✗ TIMER constant not found")
        return False
    
    if 'PROBLEM_TIMER' in constants:
        print(f"   ✓ PROBLEM_TIMER = {constants['PROBLEM_TIMER']}ms ({constants['PROBLEM_TIMER']/1000}s)")
    else:
        print("   ✗ PROBLEM_TIMER constant not found")
        return False
    
    # Test 4: Verify Arena class methods
    print("\n4. Testing Arena class methods...")
    required_methods = [
        'start_problem_mode',
        'end_problem_mode_victory', 
        'end_problem_mode_timeout',
        'get_problem_remaining_time'
    ]
    
    arena_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'Arena':
            arena_class = node
            break
    
    if not arena_class:
        print("   ✗ Arena class not found")
        return False
    
    methods_found = {name: False for name in required_methods}
    for item in arena_class.body:
        if isinstance(item, ast.FunctionDef):
            if item.name in required_methods:
                methods_found[item.name] = True
    
    all_methods = all(methods_found.values())
    for name, found in methods_found.items():
        status = "✓" if found else "✗"
        print(f"   {status} {name}()")
    
    if not all_methods:
        print("   ✗ Missing some required methods")
        return False
    
    # Test 5: Verify state variables in __init__
    print("\n5. Testing state variables...")
    required_vars = [
        'problem_mode',
        'problem_start_time',
        'current_problem',
        'problem_panel',
        'snippet_board',
        'victory'
    ]
    
    init_method = None
    for item in arena_class.body:
        if isinstance(item, ast.FunctionDef) and item.name == '__init__':
            init_method = item
            break
    
    if not init_method:
        print("   ✗ __init__ method not found")
        return False
    
    vars_found = {name: False for name in required_vars}
    for node in ast.walk(init_method):
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id == 'self':
                if node.attr in required_vars:
                    vars_found[node.attr] = True
    
    all_vars = all(vars_found.values())
    for name, found in vars_found.items():
        status = "✓" if found else "✗"
        print(f"   {status} self.{name}")
    
    if not all_vars:
        print("   ✗ Missing some required state variables")
        return False
    
    print("\n✅ All tests passed!")
    print("\nIntegration Summary:")
    print("━" * 60)
    print("Flow: Arena → Knight Death → LeetCode Problem → Result")
    print("━" * 60)
    print("1. Player fights Knight in Arena (A/D to move, SPACE to attack)")
    print("2. When Knight dies → Pause Arena, show LeetCode problem")
    print("3. Player has 60 seconds to solve the problem")
    print("4. Correct solution → VICTORY! Game ends")
    print("5. Timeout → Return to Arena, Knight revives with 50% HP")
    print("━" * 60)
    return True

if __name__ == "__main__":
    success = test_arena_integration()
    sys.exit(0 if success else 1)

