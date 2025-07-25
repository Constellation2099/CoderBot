# executor.py

import subprocess
import tempfile
import os
import re

def install_package(package_name):
    """Install the given package using pip."""
    try:
        print(f"📦 Installing missing package: {package_name}...")
        result = subprocess.run(
            ["pip", "install", package_name],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"✅ Successfully installed: {package_name}")
            return True
        else:
            print(f"❌ Failed to install {package_name}: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout while installing {package_name}")
        return False
    except Exception as e:
        print(f"❌ Error installing {package_name}: {e}")
        return False

def run_code(code: str, input_data: str = "") -> tuple[str, str]:
    """
    Execute Python code with given input data.
    Returns a tuple: (stdout, stderr)
    
    Features:
    - Automatic package installation for missing modules
    - 10-second execution timeout
    - Temporary file cleanup
    - Error handling and normalization
    """
    temp_file = None
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        result = subprocess.run(
            ['python', temp_file],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=10  
        )
        
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        
        if stderr and "ModuleNotFoundError" in stderr:
            module_match = re.search(r"No module named ['\"]([^'\"]+)['\"]", stderr)
            if module_match:
                missing_module = module_match.group(1)
                
                if install_package(missing_module):
                    print("🔄 Retrying code execution with installed package...")
                    
                    retry_result = subprocess.run(
                        ['python', temp_file],
                        input=input_data,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    return retry_result.stdout.strip(), retry_result.stderr.strip()
                else:
                    return "", f"Failed to install required package '{missing_module}'"
        
        return stdout, stderr
        
    except subprocess.TimeoutExpired:
        return "", "⏰ Code execution timed out (10 seconds limit)"
    
    except FileNotFoundError:
        return "", "❌ Python interpreter not found. Please ensure Python is installed and in PATH."
    
    except Exception as e:
        return "", f"❌ Execution failed: {str(e)}"
    
    finally:
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass  

def test_python_environment():
    """
    Test if Python environment is working correctly.
    Returns True if everything is working, False otherwise.
    """
    try:
        result = subprocess.run(
            ['python', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"🐍 Python environment: {version}")
            return True
        else:
            print("❌ Python not found or not working properly")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Python environment: {e}")
        return False

if __name__ == "__main__":
    print("Testing executor.py...")
    
    if test_python_environment():
        print("✅ Python environment OK")
    
    test_code = 'print("Hello, World!")'
    output, error = run_code(test_code)
    
    if not error and output == "Hello, World!":
        print("✅ Code execution test passed")
    else:
        print(f"❌ Code execution test failed: {error}")
    
    test_code_input = '''
name = input()
print(f"Hello, {name}!")
'''
    output, error = run_code(test_code_input, "Alice")
    
    if not error and output == "Hello, Alice!":
        print("✅ Input handling test passed")
    else:
        print(f"❌ Input handling test failed: {error}")
    
    print("Executor testing complete!")
