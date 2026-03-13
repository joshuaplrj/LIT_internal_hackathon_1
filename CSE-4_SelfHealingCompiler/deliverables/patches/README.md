# CSE-4: Self-Healing Compiler - Patches

## Patch Files

Place your patch files in this directory. Each patch should be in unified diff format.

### Naming Convention
- `bug_01_type_inference.patch`
- `bug_02_memory_deallocation.patch`
- `bug_03_deadlock.patch`
- etc.

### Patch Format
```diff
--- a/path/to/file.py
+++ b/path/to/file.py
@@ -line,count +line,count @@
 context line
-old buggy code
+new fixed code
 context line
```

## Verification

After applying all patches, the compiler should pass the regression test suite:
```bash
python run_tests.py --suite regression
```

Expected: 200/200 tests passing
