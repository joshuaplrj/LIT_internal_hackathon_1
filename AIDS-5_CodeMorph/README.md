# AIDS-5: CodeMorph — Neural Program Synthesis and Transformation

## Overview

Build a system that **automatically translates** programs between languages, optimizes code, and fixes bugs using LLMs with verification loops.

## Tasks

### 1. Python ↔ C++ Translation

Translate functions while preserving semantics

### 2. Code Optimization

Generate optimized version (≥5× faster)

### 3. Bug Fixing

Generate patches that make all tests pass

## Constraints

- Programs up to 200 lines
- Must pass all test cases
- Can use LLMs as components
- Must build verification and correction loop
- Cannot simply prompt LLM and return output

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Input Code                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLM Generation                            │
│              (GPT-4 / CodeLlama / StarCoder)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Verification                              │
│         (Compilation + Test Execution + Analysis)           │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
              ┌──────────┐        ┌──────────┐
              │  PASS    │        │  FAIL    │
              └──────────┘        └──────────┘
                    │                   │
                    ▼                   ▼
              ┌──────────┐        ┌──────────┐
              │  Output  │        │ Correction│
              └──────────┘        │   Loop   │
                                  └──────────┘
```

## LLM-Based Translation

```python
import openai

class CodeTranslator:
    """LLM-based code translator with verification"""
    
    def __init__(self, model="gpt-4"):
        self.model = model
        self.max_retries = 3
    
    def translate(self, source_code, source_lang, target_lang, test_cases):
        """
        Translate code with verification loop
        """
        for attempt in range(self.max_retries):
            # Generate translation
            translated = self._generate_translation(
                source_code, source_lang, target_lang, attempt > 0
            )
            
            # Verify translation
            verification = self._verify_translation(
                translated, target_lang, test_cases
            )
            
            if verification['passed']:
                return {
                    'code': translated,
                    'attempts': attempt + 1,
                    'verification': verification
                }
            
            # Prepare feedback for next attempt
            feedback = verification['errors']
        
        return {
            'code': translated,
            'attempts': self.max_retries,
            'verification': verification,
            'success': False
        }
    
    def _generate_translation(self, source_code, source_lang, target_lang, with_feedback=False, feedback=None):
        """Generate translation using LLM"""
        prompt = f"""Translate the following {source_lang} code to {target_lang}.
        
{source_lang} code:
```{source_lang}
{source_code}
```

Requirements:
- Preserve exact semantics
- Handle all edge cases
- Use idiomatic {target_lang}
- Include necessary imports

"""
        if with_feedback and feedback:
            prompt += f"""
Previous attempt had errors:
{feedback}

Please fix these issues.
"""
        
        prompt += f"\n{target_lang} code:"
        
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        return self._extract_code(response.choices[0].message.content)
    
    def _verify_translation(self, code, language, test_cases):
        """Verify translation by running tests"""
        results = {
            'passed': True,
            'errors': [],
            'test_results': []
        }
        
        for i, test in enumerate(test_cases):
            try:
                result = self._run_test(code, language, test)
                results['test_results'].append(result)
                
                if not result['passed']:
                    results['passed'] = False
                    results['errors'].append(f"Test {i}: {result['error']}")
            except Exception as e:
                results['passed'] = False
                results['errors'].append(f"Test {i}: {str(e)}")
        
        return results
    
    def _run_test(self, code, language, test_case):
        """Run a single test case"""
        if language == 'python':
            return self._run_python_test(code, test_case)
        elif language == 'cpp':
            return self._run_cpp_test(code, test_case)
    
    def _run_python_test(self, code, test_case):
        """Execute Python test"""
        namespace = {}
        exec(code, namespace)
        
        func_name = test_case['function']
        inputs = test_case['input']
        expected = test_case['output']
        
        result = namespace[func_name](*inputs)
        
        return {
            'passed': result == expected,
            'actual': result,
            'expected': expected
        }
```

## Code Optimization

```python
class CodeOptimizer:
    """Optimize code for performance"""
    
    def __init__(self, model="gpt-4"):
        self.model = model
    
    def optimize(self, code, language, test_cases, target_speedup=5):
        """
        Optimize code while preserving correctness
        """
        # Measure baseline performance
        baseline_time = self._measure_performance(code, language, test_cases)
        
        for attempt in range(5):
            # Generate optimized version
            optimized = self._generate_optimization(code, language, attempt)
            
            # Verify correctness
            if not self._verify_correctness(optimized, language, test_cases):
                continue
            
            # Measure performance
            optimized_time = self._measure_performance(optimized, language, test_cases)
            speedup = baseline_time / optimized_time
            
            if speedup >= target_speedup:
                return {
                    'code': optimized,
                    'speedup': speedup,
                    'baseline_time': baseline_time,
                    'optimized_time': optimized_time
                }
        
        return {
            'code': optimized,
            'speedup': speedup,
            'baseline_time': baseline_time,
            'optimized_time': optimized_time,
            'target_met': False
        }
    
    def _generate_optimization(self, code, language, attempt):
        """Generate optimized code using LLM"""
        optimization_strategies = [
            "Use more efficient data structures",
            "Reduce algorithmic complexity",
            "Use vectorized operations",
            "Cache repeated computations",
            "Use parallel processing"
        ]
        
        strategy = optimization_strategies[attempt % len(optimization_strategies)]
        
        prompt = f"""Optimize the following {language} code for performance.
        
Strategy: {strategy}

Original code:
```{language}
{code}
```

Requirements:
- Must produce identical output
- Focus on {strategy}
- Explain what optimizations you made

Optimized code:
"""
        
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        
        return self._extract_code(response.choices[0].message.content)
    
    def _measure_performance(self, code, language, test_cases, iterations=100):
        """Measure code execution time"""
        import time
        
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            self._run_test(code, language, test_cases[0])
            end = time.perf_counter()
            times.append(end - start)
        
        return np.median(times)
```

## Bug Fixing

```python
class BugFixer:
    """Automated bug fixing"""
    
    def __init__(self, model="gpt-4"):
        self.model = model
    
    def fix_bugs(self, buggy_code, language, failing_tests, passing_tests):
        """
        Fix bugs in code
        """
        for attempt in range(5):
            # Generate fix
            fixed = self._generate_fix(
                buggy_code, language, failing_tests, attempt
            )
            
            # Verify: failing tests now pass
            failing_now_pass = self._run_tests(fixed, language, failing_tests)
            
            # Verify: passing tests still pass
            still_passing = self._run_tests(fixed, language, passing_tests)
            
            if failing_now_pass['all_passed'] and still_passing['all_passed']:
                return {
                    'code': fixed,
                    'success': True,
                    'attempts': attempt + 1
                }
        
        return {
            'code': fixed,
            'success': False,
            'attempts': 5
        }
    
    def _generate_fix(self, code, language, failing_tests, attempt):
        """Generate bug fix using LLM"""
        test_info = "\n".join([
            f"Input: {t['input']}, Expected: {t['output']}, Got: {t['actual']}"
            for t in failing_tests
        ])
        
        prompt = f"""Fix the bug in the following {language} code.

Buggy code:
```{language}
{code}
```

Failing tests:
{test_info}

The bug causes incorrect output for these test cases. 
Analyze the code, identify the bug, and provide the fixed version.

Fixed code:
"""
        
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        return self._extract_code(response.choices[0].message.content)
```

## Search-Based Correction

```python
class SearchBasedCorrection:
    """Use search algorithms to find correct translations"""
    
    def __init__(self, llm, verifier, beam_width=5):
        self.llm = llm
        self.verifier = verifier
        self.beam_width = beam_width
    
    def beam_search(self, source_code, source_lang, target_lang, test_cases, max_depth=10):
        """
        Beam search for correct translation
        """
        # Initial candidates
        candidates = self._generate_candidates(source_code, source_lang, target_lang, n=self.beam_width)
        
        for depth in range(max_depth):
            scored_candidates = []
            
            for candidate in candidates:
                # Verify
                result = self.verifier.verify(candidate, target_lang, test_cases)
                
                if result['all_passed']:
                    return {'code': candidate, 'depth': depth, 'success': True}
                
                # Score based on number of passing tests
                score = result['pass_rate']
                scored_candidates.append((candidate, score, result['errors']))
            
            # Select top-k
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            top_candidates = scored_candidates[:self.beam_width]
            
            # Generate variations
            candidates = []
            for candidate, score, errors in top_candidates:
                variations = self._generate_variations(candidate, errors, target_lang)
                candidates.extend(variations)
        
        # Return best found
        best = max(scored_candidates, key=lambda x: x[1])
        return {'code': best[0], 'depth': max_depth, 'success': False, 'score': best[1]}
    
    def _generate_variations(self, code, errors, language):
        """Generate variations of code to fix errors"""
        prompt = f"""The following {language} code has errors:

```{language}
{code}
```

Errors:
{errors}

Generate 3 variations that might fix these errors:
"""
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return self._extract_multiple_codes(response.choices[0].message.content)
```

## Deliverables

1. **System Architecture**: How components combine
2. **Implementation**: Complete system
3. **Results**: On benchmark (100 translations, 50 optimizations, 50 bug fixes)
4. **Error Analysis**: What types are hardest

## Project Structure

```
AIDS-5_CodeMorph/
├── README.md
├── translation/
│   ├── translator.py
│   └── language_pairs.py
├── optimization/
│   └── optimizer.py
├── bugfix/
│   └── fixer.py
├── verification/
│   ├── runner.py
│   └── test_executor.py
├── search/
│   └── beam_search.py
├── benchmarks/
│   ├── translation/
│   ├── optimization/
│   └── bugfix/
├── run_benchmark.py
└── solution_template.py
```

## Tips

1. Verification is key - never trust LLM output blindly
2. Test-driven generation improves success rate
3. Beam search finds solutions that single generation misses
4. Error messages guide the correction loop
5. Multiple attempts with different strategies help
