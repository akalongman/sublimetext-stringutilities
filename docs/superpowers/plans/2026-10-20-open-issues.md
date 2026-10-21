# Open Issues Batch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve issues #32, #50, #26 and #35 as the design describes, one commit per issue.

**Architecture:** The four case converters share one module-level toggle
function and one base command class, so #32's rules and #50's new command
live in one place. The menu becomes nested submenus without touching command
names. The package drops `.no-sublime-package` and keeps `docs/` out of the
release archive.

**Tech Stack:** Sublime Text plugin, Python 3.3 and 3.14 plugin hosts, JSON
menu files. Tests are plain Python scripts against fake `sublime` stubs,
run on local Python 3.14 and Docker `python:3.3` (3.3.7).

**Spec:** `docs/superpowers/specs/2026-10-20-open-issues-design.md`

## Global Constraints

- Python 3.3 and 3.14 compatible: no f-strings, no `secrets`, no standard library additions newer than 3.3 without a fallback.
- Keep every existing command name, command `args`, and the menu `id` values `context-convert` and `context-convert-end` exactly as they are.
- Every existing command produces the same output as before, except the case converter changes the spec's #32 section defines.
- One commit per issue, messages under 72 characters, each containing `closes #N`. No `Co-Authored-By` trailers, no mention of AI tools, no em or en dashes.
- Commit path-limited in one command: `git add <paths> && git commit -m "<title>" -- <paths>`. Never `git add -A`, `git add .` or `git commit -a`. Never disable commit signing. Check `git show --stat HEAD` after each commit.
- Do not push, tag, create releases or post issue comments. The release is a separate, confirmed step.
- Run every command from the repository root.
- Match the surrounding code: four-space indent, the existing `#Comment` line above each command's `run`, no type hints.
- Tests live in `tmp/tests/` (ignored by git) and are never committed. Test scripts are Python 3.3 compatible, set `sys.dont_write_bytecode = True` before importing the plugin, take two arguments (stubs directory, directory holding `stringutilities.py`), print one `PASS`/`FAIL` line per check and end with `failures: N`.

## Review Focus

1. Multi-cursor: each selection converts on its own; an unconvertible selection between two convertible ones stays as it is.
2. Quoted selection `"foo_bar"` (quotes included): unchanged, as today.
3. Non-ASCII identifiers: `élan_vital` and `ÉLAN_VITAL` both become `élanVital` under camelCase; `élanVital` becomes `élan_vital`.
4. Cursor without a selection: nothing changes.
5. Mixed separators: `foo-bar_baz` under camelCase <-> Underscores keeps today's `foo-barBaz`.

Each line has its test in Task 1, step 2.

---

### Task 1: Shared case toggle with the new detection rules (#32)

**Files:**
- Modify: `stringutilities.py:160-223` (the three converter classes)
- Create (ignored): `tmp/tests/stubs/{sublime,sublime_plugin,fakeview}.py`, `tmp/tests/{harness,batch_tests,encoding_tests,hex_tests}.py`, `tmp/tests/out-enc-py314.txt`, `tmp/tests/out-enc-py33.txt`, `tmp/tests/run_all.sh`
- Test (ignored): `tmp/tests/case_tests.py`

**Interfaces:**
- Consumes: nothing.
- Produces, in `stringutilities.py`, placed where the converter classes are now:
  - `split_case(name, separator)` returns `str`: today's `toUnderscores`/`toDash` regex pair with `separator` in place of `_`/`-`, lowercased.
  - `join_case(name, separator, pascal)` returns `str`: spec rule 6.
  - `toggle_case(text, separator, pascal)` returns the converted `str`, or `None` when the selection is to be left alone.
  - `class CaseToggleCommand(sublime_plugin.TextCommand)` with class attributes `separator = '_'` and `pascal = False`, and `run(self, edit)` that replaces each non-empty selection with `toggle_case(...)` unless it returns `None`.
  - `ConvertCamelUnderscoresCommand`, `ConvertCamelDashCommand`, `ConvertPascalUnderscoresCommand` become subclasses that only set `separator` and `pascal` and keep their `#Convert ...` comment. The old `toUnderscores`, `toCamelCase`, `toDash` and `toPascalCase` methods go away (nothing else calls them).

- [ ] **Step 1: Copy the earlier test kit into `tmp/tests/`**

Copy the `.py` files from `/tmp/claude-1000/-home-longman-projects-akalongman-sublimetext-stringutilities/58e0ecf3-53c5-4835-ac93-4cfba9bdc42b/scratchpad/py314-probe/stubs/` into `tmp/tests/stubs/`, and `harness.py`, `batch_tests.py`, `encoding_tests.py`, `hex_tests.py`, `out-enc-py314.txt` and `out-enc-py33.txt` from `py314-probe/` into `tmp/tests/`. Do not copy `__pycache__`.

Write `tmp/tests/run_all.sh` (bash, `set -u`):
- `REPO` is two directories above the script.
- For every `tmp/tests/*_tests.py`: run `TZ=UTC python3 -I <suite> "$REPO/tmp/tests/stubs" "$REPO"` and `docker run --rm -e TZ=UTC -v "$REPO:/repo:ro" python:3.3 python -E -s /repo/tmp/tests/<suite> /repo/tmp/tests/stubs /repo`, and print the suite, the Python version and every `FAIL` line and the `failures:` line.
- Run `harness.py` the same two ways and `diff` the output against `out-enc-py314.txt` and `out-enc-py33.txt`.
- Strict compile: `python3 -I -W error -c` compiling `stringutilities.py`.
- Exit 1 if any run printed a `FAIL` line, a `failures:` count above 0, or an `IMPORT ERROR`, if a baseline diff is non-empty, or if the compile failed. Gate on `grep -c` counts.

Run: `bash tmp/tests/run_all.sh`
Expected: every suite `failures: 0` on both versions, both baseline diffs empty, exit 0. This proves the kit works against the current code before anything changes.

- [ ] **Step 2: Write `tmp/tests/case_tests.py`**

Same shape as `batch_tests.py` (`check(name, fn)`, `same(cmd, text, expected)` driving `getattr(su, cmd)(view).run(None)` on a `fakeview.View`). Never compute the expected value in the test; every expectation is a literal.

One `same` check per row of the spec's worked-examples table for `camel _`, `Pascal _` and `camel -`, using the "After" column ("same" means the "Today" value; "unchanged" means the input itself). The rows written in words are literal strings: `'    def __init__(self):'`, `'    _private_name'`, `'foo_bar\n'` (expected `'fooBar\n'`), `'  margin-top: 1px;'`.

Review Focus checks:
- `multi-cursor`: `View('foo_bar $x MAX_VALUE', [Region(11, 20), Region(8, 10), Region(0, 7)])` (descending, because the fake view does not shift offsets) under `ConvertCamelUnderscoresCommand` gives `'fooBar $x maxValue'`.
- `quoted`: `'"foo_bar"'` under `ConvertCamelUnderscoresCommand` stays `'"foo_bar"'`.
- `non-ASCII`: `'élan_vital'` gives `'élanVital'`, `'ÉLAN_VITAL'` gives `'élanVital'`, `'élanVital'` gives `'élan_vital'`, all under `ConvertCamelUnderscoresCommand`. Write the non-ASCII literals as `\u` escapes.
- `cursor only`: `View('foo_bar', [Region(3, 3)])` under each of the three commands stays `'foo_bar'`.
- `mixed separators`: `'foo-bar_baz'` under `ConvertCamelUnderscoresCommand` gives `'foo-barBaz'`.

- [ ] **Step 3: Run it against the current code and see the intended changes fail**

Run: `bash tmp/tests/run_all.sh`
Expected: `case_tests.py` fails on both versions for exactly the rows whose "After" differs from "Today" (`MAX_VALUE`, `Foo_bar`, `_private_name`, `_privateName`, `1st_place`, Pascal `MAX_VALUE`, `Foo_Bar`, `_private_name`, dash `Foo-bar`, `--flag-name`, `--fooBar`, `ÉLAN_VITAL`, and `multi-cursor`, whose `MAX_VALUE` region is left alone today) and passes every other row. A failure in any other row is a test bug: fix the test, not the plugin.

- [ ] **Step 4: Implement the shared toggle in `stringutilities.py`**

`toggle_case` follows the spec's rules 1 to 5. The non-identifier path must be today's code exactly:

```
if not every char is alnum or separator:          # rule 1, today's behavior
    if separator in text and text[0].islower(): return join_case(text, ...)
    if text[0] is lower (camel) / upper (pascal):  return split_case(text, ...)
    return None
if text starts with separator:                    # rule 2
    set aside leading and trailing separator runs; None if nothing is left
if separator in core: join                        # rule 3
elif core[0] is lower (camel) / upper (pascal): split   # rule 4
else: None                                        # rule 5
put the set-aside runs back
```

`join_case` for camelCase lowercases the first segment entirely when `segment.isupper()`, otherwise only its first character; every later segment uses `str.capitalize()`. For PascalCase every segment uses `str.capitalize()`.

- [ ] **Step 5: Run everything**

Run: `bash tmp/tests/run_all.sh`
Expected: exit 0. `case_tests.py`, `batch_tests.py` (its `#41` case converter rows included), `encoding_tests.py` and `hex_tests.py` report `failures: 0` on Python 3.14 and 3.3, both harness diffs are empty, and the strict compile is clean.

- [ ] **Step 6: Commit**

```bash
git add stringutilities.py && git commit -m "Treat any identifier with separators as separated text (closes #32)" -- stringutilities.py
```

---

### Task 2: PascalCase <-> Dash converter (#50)

**Files:**
- Modify: `stringutilities.py` (after `ConvertPascalUnderscoresCommand`), `Context.sublime-menu`, `Default.sublime-commands`, `README.md:10`
- Test (ignored): `tmp/tests/case_tests.py`

**Interfaces:**
- Consumes: `CaseToggleCommand` from Task 1.
- Produces: `class ConvertPascalDashCommand(CaseToggleCommand)` with `separator = '-'` and `pascal = True`; command name `convert_pascal_dash`. Task 3 places its menu entry.

- [ ] **Step 1: Add the Pascal `-` rows to `case_tests.py`**

One `same` check on `ConvertPascalDashCommand` per `Pascal -` row of the spec table: `my-component-name` gives `MyComponentName`, `MyComponent` gives `my-component`, `HTTPServer` gives `http-server`, `--main-color` gives `--MainColor`. Add `MAX-VALUE` giving `MaxValue` and a `cursor only` check as in Task 1.

- [ ] **Step 2: Run it and see the new rows fail**

Run: `bash tmp/tests/run_all.sh`
Expected: only the new rows fail, with `AttributeError` for `ConvertPascalDashCommand`, on both versions.

- [ ] **Step 3: Add the command, menu entry, palette entry and README lines**

- `ConvertPascalDashCommand` with the comment `#Convert PascalCase to dash and vice versa`.
- `Context.sublime-menu`: `{"caption": "Convert PascalCase <-> Dash", "command": "convert_pascal_dash"}` directly after the "Convert PascalCase <-> Underscores" entry.
- `Default.sublime-commands`: `{"caption": "String Utilities: Convert PascalCase <-> Dash", "command": "convert_pascal_dash"}` directly after the "Convert PascalCase <-> Underscores" entry.
- `README.md`: replace the line `* Convert Camel Case <-> Underscores` with these four lines:

```
* Convert camelCase <-> Underscores
* Convert camelCase <-> Dash
* Convert PascalCase <-> Underscores
* Convert PascalCase <-> Dash
```

- [ ] **Step 4: Run everything**

Run: `bash tmp/tests/run_all.sh` and `python3 -I -c 'import json, sys; [json.load(open(f)) for f in sys.argv[1:]]' Context.sublime-menu Default.sublime-commands`
Expected: exit 0 for the suite runner; the JSON check prints nothing and exits 0.

- [ ] **Step 5: Commit**

```bash
git add stringutilities.py Context.sublime-menu Default.sublime-commands README.md && git commit -m "Add PascalCase <-> Dash converter (closes #50)" -- stringutilities.py Context.sublime-menu Default.sublime-commands README.md
```

---

### Task 3: Nested context menu (#26)

**Files:**
- Modify: `Context.sublime-menu`
- Create (ignored): `tmp/tests/baseline/Context.sublime-menu`
- Test (ignored): `tmp/tests/menu_tests.py`

**Interfaces:**
- Consumes: the `convert_pascal_dash` menu entry from Task 2.
- Produces: nothing later tasks use.

- [ ] **Step 1: Save the pre-batch menu and write `tmp/tests/menu_tests.py`**

Run: `mkdir -p tmp/tests/baseline && git show f05d5ad:Context.sublime-menu > tmp/tests/baseline/Context.sublime-menu`

`menu_tests.py` reads the files from the repo directory (second argument) and the baseline from `tmp/tests/baseline/`. Checks:
- `parses`: `Context.sublime-menu` and `Default.sublime-commands` load with `json.load`.
- `commands resolve`: every `command` in both files matches a class in `stringutilities.py` when underscores are removed and compared case-insensitively against the class name minus a trailing `Command` (`convert_md5` matches `ConvertMd5Command`, `convert_spaces_to_non_breaking` matches `ConvertSpacesToNonBreaking`).
- `ids`: the top level is exactly three items: a separator with `"id": "context-convert-end"`, the "String Utilities" item with `"id": "context-convert"`, and a separator with `"id": "context-convert-end"`.
- `groups`: the children of "String Utilities" are exactly ten submenus captioned, in order, `Whitespace`, `Case`, `Quotes`, `Encode / Decode`, `Color`, `Hash`, `Date and Time`, `Password`, `Network`, `JSON and PHP`.
- `group contents`: per group, the sequence of `command` values (separators skipped) equals the spec's #26 list, and the separator count is 5 for `Encode / Decode`, 1 for `Password`, 0 elsewhere. Write the expected command lists as literals.
- `nothing lost`: the sorted list of `(caption, command, json.dumps(args, sort_keys=True))` for every command entry at any depth in the new menu equals the same list from the baseline plus these five: `("Convert PascalCase <-> Dash", "convert_pascal_dash")`, `("Calculate SHA224", "convert_sha224")`, `("Calculate SHA256", "convert_sha256")`, `("Calculate SHA384", "convert_sha384")`, `("Calculate SHA512", "convert_sha512")`, all without `args`.

- [ ] **Step 2: Run it and see the structure checks fail**

Run: `bash tmp/tests/run_all.sh`
Expected: `menu_tests.py` passes `parses`, `commands resolve` and `ids`, and fails `groups`, `group contents` and `nothing lost` (the four SHA entries are missing) on both versions. Every other suite still passes.

- [ ] **Step 3: Rewrite `Context.sublime-menu` into the ten submenus**

Groups, order, captions and separators exactly as the spec's #26 section lists them. Keep each existing entry's `caption`, `command` and `args` byte for byte (password `length` values stay strings). Group submenus get no `id`. Keep the file's existing four-space JSON formatting and key order (`args`, `caption`, `command`, `children`, `id` in alphabetical order, as now).

- [ ] **Step 4: Run everything**

Run: `bash tmp/tests/run_all.sh`
Expected: exit 0, `menu_tests.py` at `failures: 0` on both versions.

- [ ] **Step 5: Commit**

```bash
git add Context.sublime-menu && git commit -m "Group the context menu into submenus (closes #26)" -- Context.sublime-menu
```

---

### Task 4: Install as a zipped package (#35)

**Files:**
- Delete: `.no-sublime-package`
- Create: `.gitattributes`
- Modify: `README.md` (remove the "Libraries" section)
- Test (ignored): `tmp/tests/zip_import_check.py` (not named `*_tests.py`, so the runner does not pick it up)

**Interfaces:**
- Consumes: the final `stringutilities.py`, menu and palette from Tasks 1 to 3.
- Produces: nothing.

- [ ] **Step 1: Confirm the plugin reads nothing from its own directory**

Run: `grep -nE '__file__|os\.path|open\(|load_resource|packages_path|find_resources' stringutilities.py`
Expected: no output. Any match stops the task: report it instead of continuing.

- [ ] **Step 2: Write `tmp/tests/zip_import_check.py`**

Takes the stubs directory and a zip path. Puts the stubs first on `sys.path`, then the zip, imports `stringutilities`, asserts `stringutilities.__file__` lies inside the zip, and runs `ConvertCamelUnderscoresCommand` on `'MAX_VALUE'` expecting `'maxValue'`. Prints `PASS`/`FAIL` lines and `failures: N`.

- [ ] **Step 3: Make the change**

- `git rm -q .no-sublime-package`
- `.gitattributes` with the single line `/docs export-ignore`
- `README.md`: delete the `## Libraries ##` heading, the `dateutil` line under it and the blank line that follows, keeping the `[0]: ...` link definition at the end.

- [ ] **Step 4: Commit**

```bash
git add .gitattributes README.md && git commit -m "Install as a zipped package (closes #35)" -- .no-sublime-package .gitattributes README.md
```

- [ ] **Step 5: Check the release archive**

Run: `git archive HEAD | tar -t`
Expected: no `docs/` entry and no `.no-sublime-package`; `stringutilities.py`, `Context.sublime-menu`, `Default.sublime-commands`, `.gitattributes`, `README.md`, `LICENSE` present.

Run: `mkdir -p tmp/pkg && git archive --format=zip -o tmp/pkg/StringUtilities.sublime-package HEAD && python3 -I tmp/tests/zip_import_check.py tmp/tests/stubs tmp/pkg/StringUtilities.sublime-package && docker run --rm -v "$PWD:/repo:ro" python:3.3 python -E -s /repo/tmp/tests/zip_import_check.py /repo/tmp/tests/stubs /repo/tmp/pkg/StringUtilities.sublime-package`
Expected: `failures: 0` on both versions.

If either check fails, fix the commit with `git commit --amend` (the commit is unpushed) and rerun both checks.

- [ ] **Step 6: Final run**

Run: `bash tmp/tests/run_all.sh && git log --format='%h %G? %s' f05d5ad..HEAD && git status --short`
Expected: exit 0; the plan commit followed by four commits, each signed (`G`), in the order #32, #50, #26, #35; clean working tree.

---

## After the plan

Tagging 1.9.0, the GitHub release, and the closing comments for #32 and #13
(wording in the spec) are a separate step, confirmed before anything is
published.
