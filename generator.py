# generator.py

import google.generativeai as genai
from utils import strip_code_fence

genai.configure(api_key="")
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def generate_code(task_prompt: str, language: str) -> str:
    try:
        prompt = (
            f"Write complete, executable {language.capitalize()} code to solve the following task.\n"
            f"Use standard input/output with separate input() calls for multiple values.\n"
            f"Keep the solution as SIMPLE as possible - avoid complex parsing unless necessary.\n"
            f"For basic operations with multiple numbers, use separate input() statements for each number.\n"
            f"Only use input().split() or map() if the task explicitly mentions space-separated input.\n"
            f"For simple print statements, output EXACTLY what is requested - no modifications.\n"
            f"No explanations, no markdown.\n\n"
            f"Task: {task_prompt.strip()}"
        )
        response = model.generate_content(prompt)
        raw_code = response.text.strip()
        return strip_code_fence(raw_code)
    except Exception as e:
        print("Gemini API error:", e)
        return {
            "python": '''
def main():
    print("Gemini API call failed.")
if __name__ == "__main__":
    main()
''',
            "java": '''
public class Solution {
    public static void main(String[] args) {
        System.out.println("Gemini API call failed.");
    }
}
'''
        }.get(language.lower(), "// Gemini API call failed.")

def generate_test_cases(task_description: str, num_cases: int = 3) -> list:
    """
    Generate test cases automatically based on task description using Gemini AI
    Returns list of (input, expected_output) tuples
    """
    
    # First, check for common patterns and use predefined realistic test cases
    task_lower = task_description.lower().strip()
    
    # Handle simple print statements - extract exactly what should be printed
    if task_lower.startswith('print ') and len(task_lower.split()) <= 6:
        # Extract the text after "print "
        text_to_print = task_description[6:].strip()  # Remove "print " prefix
        
        # Remove quotes if they exist, but preserve the exact content
        if (text_to_print.startswith('"') and text_to_print.endswith('"')) or \
           (text_to_print.startswith("'") and text_to_print.endswith("'")):
            text_to_print = text_to_print[1:-1]
        
        # Return exactly what the user asked for - no modifications
        return [
            ("", text_to_print),  # No input, exact output as requested
            ("", text_to_print),
            ("", text_to_print)
        ]
    
    # Predefined test cases for common problems (using separate input lines)
    if any(word in task_lower for word in ['palindrome']):
        if any(word in task_lower for word in ['ignore case', 'ignore spaces', 'ignore punctuation', 'alphanumeric']):
            # Complex palindrome
            return [
                ("Racecar", "True"),
                ("A man a plan a canal Panama", "True"),
                ("hello", "False")
            ]
        else:
            # Simple palindrome (exact matching)
            return [
                ("racecar", "True"),
                ("hello", "False"),
                ("madam", "True")
            ]
    
    elif any(word in task_lower for word in ['add', 'sum', 'plus']) and 'two' in task_lower:
        return [
            ("5\n3", "8"),      # Separate lines for simple input
            ("0\n0", "0"),      
            ("-2\n7", "5")
        ]
    
    elif any(word in task_lower for word in ['multiply', 'product']) and 'two' in task_lower:
        return [
            ("4\n5", "20"),     # Separate lines for simple input
            ("0\n10", "0"),     
            ("-3\n2", "-6")
        ]
    
    elif any(word in task_lower for word in ['subtract', 'difference']) and 'two' in task_lower:
        return [
            ("10\n3", "7"),     # Separate lines for simple input
            ("0\n5", "-5"),     
            ("-2\n-7", "5")
        ]
    
    elif any(word in task_lower for word in ['divide', 'division']) and 'two' in task_lower:
        return [
            ("10\n2", "5"),     # Separate lines for simple input
            ("15\n3", "5"),     
            ("7\n2", "3")       # Integer division
        ]
    
    elif any(word in task_lower for word in ['reverse']) and 'string' in task_lower:
        return [
            ("hello", "olleh"),
            ("python", "nohtyp"),
            ("a", "a")
        ]
    
    elif any(word in task_lower for word in ['factorial']):
        return [
            ("5", "120"),
            ("0", "1"),
            ("3", "6")
        ]
    
    elif any(word in task_lower for word in ['fibonacci']):
        return [
            ("0", "0"),
            ("1", "1"),
            ("5", "5")
        ]
    
    elif any(word in task_lower for word in ['maximum', 'max', 'largest']) and any(word in task_lower for word in ['list', 'array', 'numbers']):
        return [
            ("1\n2\n3\n4\n5", "5"),    # Multiple separate inputs
            ("-1\n-5\n-2", "-1"),
            ("10", "10")
        ]
    
    elif any(word in task_lower for word in ['minimum', 'min', 'smallest']) and any(word in task_lower for word in ['list', 'array', 'numbers']):
        return [
            ("1\n2\n3\n4\n5", "1"),    # Multiple separate inputs
            ("-1\n-5\n-2", "-5"),
            ("10", "10")
        ]
    
    elif any(word in task_lower for word in ['even', 'odd']):
        return [
            ("4", "True" if 'even' in task_lower else "False"),
            ("7", "False" if 'even' in task_lower else "True"),
            ("0", "True" if 'even' in task_lower else "False")
        ]
    
    elif any(word in task_lower for word in ['prime']):
        return [
            ("7", "True"),
            ("4", "False"),
            ("2", "True")
        ]
    
    elif any(word in task_lower for word in ['count']) and any(word in task_lower for word in ['character', 'letter', 'vowel']):
        return [
            ("hello\nl", "2"),          # String then character to count
            ("python\nn", "1"),
            ("aaa\na", "3")
        ]
    
    elif any(word in task_lower for word in ['area']) and 'rectangle' in task_lower:
        return [
            ("5\n3", "15"),     # length and width on separate lines
            ("10\n2", "20"),
            ("7\n7", "49")
        ]
    
    elif any(word in task_lower for word in ['power', 'exponent']) and 'two' in task_lower:
        return [
            ("2\n3", "8"),      # base and exponent on separate lines  
            ("5\n2", "25"),
            ("10\n0", "1")
        ]
    
    # If no predefined pattern matches, use AI generation with better prompting
    try:
        prompt = f"""
Generate {num_cases} test cases for this programming task: "{task_description}"

CRITICAL RULES:
- For simple print statements, use EXACTLY what the user requested - do not modify capitalization, punctuation, or format
- If user says "print hello world", the expected output should be exactly "hello world"
- Do not add punctuation, capitalization, or formatting unless explicitly requested
- Be LITERAL, not "helpful"
- Use SEPARATE INPUT LINES for multiple values (not space-separated)
- Keep test cases SIMPLE and matching the complexity of the task

Required format for single input:
Input: [value]
Output: [expected_output]

Required format for multiple inputs:
Input: [value1]
[value2]
[value3]
Output: [expected_output]

Required format for no input (like print statements):
Input: 
Output: [exact_expected_output]

Examples of GOOD test cases:

Task: "print hello world"
Input: 
Output: hello world

Task: "multiply two numbers"
Input: 4
5
Output: 20

Task: "check if number is even"
Input: 4
Output: True

Generate {num_cases} test cases for the given task using these exact formatting rules:
"""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Parse the response to extract test cases with multi-line input support
        test_cases = []
        lines = response_text.split('\n')
        
        i = 0
        while i < len(lines) and len(test_cases) < num_cases:
            line = lines[i].strip()
            
            if line.startswith('Input:'):
                # Extract first input line
                input_first = line.replace('Input:', '').strip()
                input_parts = [input_first] if input_first else []
                i += 1
                
                # Collect additional input lines until we hit "Output:"
                while i < len(lines) and not lines[i].strip().startswith('Output:'):
                    next_line = lines[i].strip()
                    if next_line and not next_line.startswith('Input:'):
                        input_parts.append(next_line)
                    i += 1
                
                # Get the output line
                if i < len(lines) and lines[i].strip().startswith('Output:'):
                    output_val = lines[i].strip().replace('Output:', '').strip()
                    
                    # Join input parts with newlines for multi-line input, or empty string if no input
                    input_val = '\n'.join(input_parts) if input_parts else ""
                    test_cases.append((input_val, output_val))
                    i += 1
                else:
                    i += 1
            else:
                i += 1
        
        # If we got good test cases from AI, use them
        if len(test_cases) >= 2:
            return test_cases[:num_cases]
        
    except Exception as e:
        print(f"⚠️ AI test case generation failed: {e}")
    
    # Final fallback - very generic test cases
    print("⚠️ Using generic fallback test cases")
    return [
        ("", "output1"),
        ("", "output2"),
        ("", "output3")
    ][:num_cases]
