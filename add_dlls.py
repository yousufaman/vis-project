import os
import glob

dll_code = """import os
if os.name == 'nt' and hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(r"C:\\VTK-build\\bin")
    os.add_dll_directory(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "build", "bin")))
"""

for py in ['task5_controlled_benchmark.py', 'task6_accuracy_benchmark.py', 'task7a_demo_topology.py', 'task7b_scalability_study.py']:
    path = os.path.join('c:\\Users\\pc\\Downloads\\VTK Project\\python', py)
    with open(path, 'r') as f:
        code = f.read()
    if 'add_dll_directory' not in code:
        new_code = dll_code + '\n' + code
        with open(path, 'w') as f:
            f.write(new_code)
        print(f'Updated {py}')
