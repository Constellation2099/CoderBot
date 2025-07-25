# main.py

import os
import time
from datetime import datetime
from generator import generate_code, generate_test_cases
from executor import run_code
from evaluator import evaluate_output
from debugger import debug_code

os.makedirs("logs", exist_ok=True)
os.makedirs("output", exist_ok=True)

# Configuration constants
MAX_ATTEMPTS = 50  # Hard limit to prevent infinite loops
MAX_EXECUTION_TIME = 300  # 5 minutes in seconds
MAX_DUPLICATE_ERRORS = 2  # Stop if same error repeats this many times

def is_output_based_task(task_description):
    """
    Check if the task is output-based (suitable for automated testing)
    Returns True if task seems to have predictable outputs
    """
    task_lower = task_description.lower()
    
    # Keywords that strongly indicate non-output-based tasks
    non_output_keywords = [
        'create file', 'write file', 'save file', 'file in', 'write to file',
        'read file', 'open file', 'delete file', 'modify file', 'edit file',
        'directory', 'folder', 'path', 'mkdir', 'rmdir',
        'database', 'sql', 'insert into', 'create table', 'drop table',
        'machine learning', 'train model', 'save model', 'load model',
        'neural network', 'deep learning', 'tensorflow', 'pytorch',
        'plot', 'graph', 'chart', 'visualization', 'matplotlib', 'pyplot',
        'gui', 'interface', 'tkinter', 'pyqt', 'kivy', 'streamlit',
        'api', 'rest api', 'flask', 'django', 'fastapi',
        'server', 'client', 'socket', 'network', 'http',
        'thread', 'process', 'multiprocessing', 'async',
        'install', 'pip install', 'download', 'upload', 'request',
        'email', 'notification', 'send message',
        'web scraping', 'scrape', 'beautiful soup', 'selenium',
        'image processing', 'opencv', 'pillow', 'image',
        'audio', 'video', 'media', 'pygame'
    ]
    
    # Check for non-output keywords first (highest priority)
    for keyword in non_output_keywords:
        if keyword in task_lower:
            return False
    
    # Keywords that indicate output-based tasks
    output_keywords = [
        'return', 'output', 'print', 'display', 'show',
        'calculate', 'compute', 'find', 'determine', 'get',
        'sum', 'add', 'subtract', 'multiply', 'divide',
        'average', 'mean', 'median', 'mode',
        'maximum', 'minimum', 'max', 'min', 'largest', 'smallest',
        'sort', 'arrange', 'order', 'reverse', 'flip',
        'count', 'search', 'lookup', 'index',
        'convert', 'transform', 'change', 'format',
        'check', 'validate', 'verify', 'test', 'is',
        'compare', 'match', 'equal', 'different',
        'parse', 'extract', 'split', 'join',
        'palindrome', 'anagram', 'substring',
        'factorial', 'fibonacci', 'prime', 'perfect',
        'even', 'odd', 'positive', 'negative',
        'length', 'size', 'contains', 'startswith', 'endswith'
    ]
    
    # Check for output keywords
    for keyword in output_keywords:
        if keyword in task_lower:
            return True
    
    # Additional checks for mathematical expressions
    math_indicators = ['formula', 'equation', 'algorithm', 'logic', 'condition']
    for indicator in math_indicators:
        if indicator in task_lower:
            return True
    
    # Default to False for ambiguous cases to be safe
    return False

def get_task_category(task_description):
    """
    Categorize the task to provide specific warnings
    """
    task_lower = task_description.lower()
    
    if any(word in task_lower for word in ['file', 'directory', 'folder', 'path']):
        return "file_operations"
    elif any(word in task_lower for word in ['database', 'sql', 'table']):
        return "database"
    elif any(word in task_lower for word in ['machine learning', 'model', 'neural', 'tensorflow', 'pytorch']):
        return "machine_learning"
    elif any(word in task_lower for word in ['gui', 'interface', 'tkinter', 'window']):
        return "gui"
    elif any(word in task_lower for word in ['api', 'server', 'client', 'flask', 'django']):
        return "web_api"
    elif any(word in task_lower for word in ['plot', 'graph', 'chart', 'matplotlib']):
        return "visualization"
    elif any(word in task_lower for word in ['scrape', 'scraping', 'selenium', 'requests']):
        return "web_scraping"
    elif any(word in task_lower for word in ['thread', 'process', 'async', 'concurrent']):
        return "concurrency"
    else:
        return "general"

def normalize_error(error_message):
    """
    Normalize error messages to detect duplicates more effectively
    """
    if not error_message:
        return ""
    
    # Remove line numbers and file paths which change between attempts
    import re
    normalized = re.sub(r'line \d+', 'line X', error_message)
    normalized = re.sub(r'File "[^"]*"', 'File "X"', normalized)
    normalized = re.sub(r'tmp\w+\.py', 'tmpX.py', normalized)
    
    # Keep only the core error type and message
    lines = normalized.split('\n')
    core_error = []
    for line in lines:
        if line.strip() and not line.startswith('  File '):
            core_error.append(line.strip())
    
    return '\n'.join(core_error)

def solve_task(task_description, test_cases):
    log_lines = [
        f"Task: {task_description}", 
        "Language: Python", 
        f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "Test Cases:"
    ]
    for i, (inp, exp) in enumerate(test_cases, 1):
        log_lines.append(f"[{i}] Input: {inp} | Expected Output: {exp}")
    log_lines.append("")
    
    final_code = None
    feedback_summary = ""
    error_history = {}  # Track error occurrences
    start_time = time.time()
    
    print(f"🔄 Auto-retry enabled (max {MAX_ATTEMPTS} attempts, {MAX_EXECUTION_TIME//60} min timeout)")
    print(f"⏰ Will stop if same error repeats {MAX_DUPLICATE_ERRORS} times")
    print("=" * 60)
    
    for attempt in range(1, MAX_ATTEMPTS + 1):
        # Check time constraint
        elapsed_time = time.time() - start_time
        if elapsed_time > MAX_EXECUTION_TIME:
            termination_reason = f"⏰ Time limit exceeded ({MAX_EXECUTION_TIME//60} minutes)"
            log_lines.append(f"\n{termination_reason}")
            print(f"\n{termination_reason}")
            break
        
        log_lines.append(f"[Attempt {attempt}] Generating code...")
        print(f"\n[Attempt {attempt}] Generating code... ⏱️  {elapsed_time:.1f}s elapsed")
        
        code = generate_code(task_description, "python") if attempt == 1 else debug_code(task_description, feedback_summary, "python")
        log_lines.append("[Generated Code]\n" + code)
        print("[Generated Code]\n", code)
        
        all_passed = True
        feedback_summary = ""
        current_attempt_errors = []
        
        for idx, (input_data, expected_output) in enumerate(test_cases, 1):
            output, error = run_code(code, input_data)
            if error:
                normalized_error = normalize_error(error)
                current_attempt_errors.append(normalized_error)
                
                # Track error frequency
                if normalized_error in error_history:
                    error_history[normalized_error] += 1
                else:
                    error_history[normalized_error] = 1
                
                feedback_summary += f"Test Case {idx}: Execution Error:\n{error}\n"
                log_lines.append(f"[Test Case {idx}] Execution Error:\n{error}")
                print(f"[Test Case {idx}] Execution Error:\n{error}")
                all_passed = False
                break
            else:
                passed = evaluate_output(output, expected_output)
                result_mark = "✅" if passed else "❌"
                log_lines.append(f"[Test Case {idx}] {result_mark} Output: {output} | Expected: {expected_output}")
                print(f"[Test Case {idx}] {result_mark} Output: {output} | Expected: {expected_output}")
                if not passed:
                    feedback_summary += f"Test Case {idx}: Expected '{expected_output}' but got '{output}'\n"
                    all_passed = False
                    break
        
        # Check for repeated errors
        if current_attempt_errors:
            repeated_errors = [err for err in current_attempt_errors if error_history.get(err, 0) >= MAX_DUPLICATE_ERRORS]
            if repeated_errors:
                termination_reason = f"🔄 Stopping: Same error repeated {MAX_DUPLICATE_ERRORS} times"
                log_lines.append(f"\n{termination_reason}")
                log_lines.append(f"Repeated error pattern:\n{repeated_errors[0]}")
                print(f"\n{termination_reason}")
                print("🔍 Error pattern detected - the AI seems stuck on this approach")
                break
        
        if all_passed:
            final_code = code
            success_message = f"🎉 Success in attempt {attempt}! All test cases passed."
            elapsed_final = time.time() - start_time
            log_lines.append(f"\n{success_message}")
            log_lines.append(f"Total time: {elapsed_final:.1f} seconds")
            print(f"\n{success_message}")
            print(f"⏱️  Total time: {elapsed_final:.1f} seconds")
            break
    
    # Final results
    elapsed_total = time.time() - start_time
    
    if final_code:
        log_lines.append("\nFinal Working Code:\n" + final_code)
        print("\n" + "="*50)
        print("🏆 FINAL WORKING CODE")
        print("="*50)
        print(final_code)
        print("="*50)
        
        with open("output/final_code.txt", "w", encoding="utf-8") as f:
            f.write(final_code)
    else:
        failure_message = f"❌ Failed to solve the task after {attempt} attempts"
        log_lines.append(f"\n{failure_message}")
        log_lines.append(f"Total execution time: {elapsed_total:.1f} seconds")
        print(f"\n{failure_message}")
        print(f"⏱️  Total execution time: {elapsed_total:.1f} seconds")
        
        # Show error summary
        if error_history:
            print(f"\n📊 Error Summary:")
            for error, count in sorted(error_history.items(), key=lambda x: x[1], reverse=True):
                print(f"   • Occurred {count} times: {error.split(':')[-1].strip()}")
    
    # Save detailed log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/attempt_{timestamp}.txt"
    with open(log_filename, "w", encoding="utf-8") as log_file:
        log_file.write("\n".join(log_lines))
    
    print(f"\n📝 Detailed log saved to: {log_filename}")
    return final_code

if __name__ == "__main__":
    print("Python Code Problem Solver")
    print("=" * 40)
    print("🤖 This system works best with computational problems that produce verifiable outputs")
    print("=" * 40)
    
    print("\nEnter the task/problem description:")
    task = input("> ").strip()
    
    if not task:
        print("❌ No task provided. Exiting.")
        exit()
    
    # Check if task is suitable for output-based testing
    if not is_output_based_task(task):
        task_category = get_task_category(task)
        
        print(f"\n⚠️  {'='*60}")
        print("❌ UNSUITABLE TASK DETECTED")
        print(f"{'='*60}")
        
        category_messages = {
            "file_operations": "📁 File Operations: This system cannot verify file creation, modification, or deletion.",
            "database": "🗄️  Database Operations: Database interactions cannot be automatically tested here.",
            "machine_learning": "🤖 Machine Learning: Model training and ML tasks are not suitable for this system.",
            "gui": "🖥️  GUI Applications: Graphical interfaces cannot be tested through console output.",
            "web_api": "🌐 Web/API Development: Server/client applications require different testing approaches.",
            "visualization": "📊 Data Visualization: Plots and charts cannot be verified through text output.",
            "web_scraping": "🕷️  Web Scraping: External web requests are not suitable for this testing environment.",
            "concurrency": "⚡ Concurrency: Multi-threading and async operations are complex to test automatically.",
            "general": "❓ Non-Computational Task: This task doesn't seem to produce verifiable outputs."
        }
        
        print(f"\n{category_messages.get(task_category, category_messages['general'])}")
        print(f"\n💡 Try a problem that has a displayable output instead.")
        print(f"{'='*60}")
        
        continue_choice = input("\n🤔 Do you want to continue anyway? (y/N): ").strip().lower()
        if continue_choice not in ['y', 'yes']:
            print("\n✅ Good choice! Please try again with a computational problem.")
            print("💡 Tip: Focus on problems that take input and produce calculable output.")
            exit()
        else:
            print("\n⚠️  Proceeding anyway... Results may be unpredictable.")
    else:
        print("\n✅ Task appears suitable for automated testing!")
    
    print(f"\n{'='*50}")
    print("TEST CASE SETUP")
    print(f"{'='*50}")
    
    print("\nHow would you like to provide test cases?")
    print("1. 📝 Enter test cases manually")
    print("2. 🤖 Generate test cases automatically")
    
    choice = input("\nChoose option (1 or 2): ").strip()
    
    test_cases = []
    
    if choice == "2":
        print("\n🤖 Generating test cases automatically...")
        try:
            test_cases = generate_test_cases(task)
            if test_cases:
                print(f"✅ Generated {len(test_cases)} test cases:")
                for i, (inp, exp) in enumerate(test_cases, 1):
                    print(f"[{i}] Input: {inp} | Expected: {exp}")
            else:
                print("❌ Failed to generate test cases. Falling back to manual entry.")
                choice = "1"
        except Exception as e:
            print(f"❌ Error generating test cases: {e}")
            print("🔄 Falling back to manual entry...")
            choice = "1"
    
    if choice == "1" or not test_cases:
        print("\n📝 Enter test cases manually:")
        print("💡 Tip: Provide input and expected output pairs. Leave input empty when done.")
        test_cases = []
        case_num = 1
        
        while True:
            print(f"\n--- Test Case {case_num} ---")
            user_input = input("Input: ").strip()
            if not user_input:
                if len(test_cases) == 0:
                    print("⚠️  You need at least one test case!")
                    continue
                else:
                    break
            expected_output = input("Expected Output: ").strip()
            test_cases.append((user_input, expected_output))
            case_num += 1
    
    if not test_cases:
        print("❌ No test cases provided! Exiting.")
        exit()
    
    print(f"\n{'='*50}")
    print("🚀 STARTING AUTOMATED PROBLEM SOLVING")
    print(f"{'='*50}")
    
    solve_task(task, test_cases)
