# Open issues batch: design

Date: 2026-10-20. Covers GitHub issues #35, #50, #32, #26 and #13.

## Intent

StringUtilities has about 21K installs through Package Control, and the
maintainer does not use Sublime Text day to day. The changes therefore have
to be judged on behalf of users the maintainer never sees: does a change help
them, can it break a setup they already have, and how much upkeep does it add.

The goal of this batch is an empty issue tracker. Three issues get small,
low-risk changes, one gets a narrow behavior fix plus an explanation, and one
is closed in favor of an existing package.

Success looks like this:

- every open issue is resolved by a commit or closed with an explanation;
- no existing command name, command argument, menu `id` or command palette
  caption changes;
- every existing command produces the same output as before, except for the
  case converter changes the #32 section defines;
- the plugin keeps working on both plugin hosts, Python 3.3 and Python 3.14
  (see "Compatibility" in the README).

## Goals

1. #35: install as a zipped `.sublime-package` instead of an unpacked folder.
2. #50: add a PascalCase <-> Dash converter.
3. #32: make the case converters recognize separated text that does not start
   with a lowercase letter, and close the acronym question with an
   explanation.
4. #26: group the right-click submenu into nested submenus.
5. #13: close in favor of the Insert Nums package.

## Non-goals

- Preserving acronyms when joining (`a_LL_pointer` stays `aLlPointer`).
- Converting selections that hold several identifiers or whitespace
  (`foo_bar baz_qux`); today's output for those stays as it is.
- Changing how segments after the first are capitalized; `foo_barBaz` keeps
  becoming `fooBarbaz`.
- Renaming captions, unifying menu and palette captions, or fixing other
  stale README content beyond what is listed here.
- Committing a test suite or adding CI. Tests live in the ignored `tmp/`
  directory, as in the previous fix rounds (designer's call; a committed
  suite is a possible follow-up).
- A renumbering command (#13).

## Anti-goals

These would count as failure even if the feature technically works:

- an existing key binding, macro or menu override stops working;
- a Package Control user stops receiving updates after the #35 change;
- a converter silently produces worse output for input that converts
  correctly today.

## Constraints

- Python 3.3 and 3.14 compatibility: no f-strings, no `secrets`, no
  standard library additions newer than 3.3 without a fallback.
- Keep the existing command names, `args`, and the menu `id` values
  `context-convert` and `context-convert-end` exactly as they are. Other
  packages and user overrides may reference them.
- One commit per issue. Commits for #35, #50 and #26 say `closes #N`; the
  #32 commit says `closes #32` and its closing comment is posted with the
  release.

## #35: install as a zipped package

Delete `.no-sublime-package`.

Why it is safe:

- The plugin reads no files from its own directory (its only I/O is the
  network access in the two IP commands) and bundles no libraries, so it
  works from inside a zip. The README's `dateutil` credit is stale; no such code is
  in the repository.
- Package Control handles the move from an unpacked folder to a zip. In both
  3.4.1 and 4.2.8, `install_package` checks for
  `Packages/StringUtilities/package-metadata.json`; when that file exists and
  the new release has no `.no-sublime-package`, it backs the folder up,
  deletes it and installs the zip. If the delete fails (for example a Windows
  file lock), it schedules the reinstall for the next start.
- Users who installed with `git clone` have no `package-metadata.json`, so
  Package Control leaves their folder alone. They update with git, and the
  folder keeps working.
- Files a user added or edited inside the unpacked folder are already lost
  on every upgrade today: for an unpacked package, Package Control (3.4.1
  and 4.2.8) backs the folder up and then removes every file the new release
  did not overwrite. The move adds no new loss. Afterwards
  `Packages/StringUtilities/` becomes Sublime Text's override location for
  the zip, and Package Control leaves a folder without
  `package-metadata.json` in place, so overrides placed there survive
  upgrades.

Also in this commit (designer's calls):

- Add `.gitattributes` with `/docs export-ignore`, so specs and plans do not
  ship inside the package. Package Control downloads GitHub tag archives,
  which honor `export-ignore`.
- Remove the stale "Libraries" section (the `dateutil` credit) from the
  README.

## #32 and #50: case converter rules

There are four converters after this batch:

| Command | Separator | Joined form |
|---|---|---|
| `convert_camel_underscores` | `_` | camelCase |
| `convert_camel_dash` | `-` | camelCase |
| `convert_pascal_underscores` | `_` | PascalCase |
| `convert_pascal_dash` (new, #50) | `-` | PascalCase |

Each one toggles a non-empty selection. Today the direction depends on the
first character: text that does not start with a lowercase letter is never
treated as separated text. So `MAX_VALUE` does nothing under camelCase,
`Foo_Bar` becomes `foo__bar` under PascalCase, and `_private_name` is skipped
everywhere.

New rules, the same for all four commands:

1. The new rules apply only to an identifier: a selection in which every
   character is a letter, a digit or the command's separator (Unicode-aware,
   as `str.isalnum()` decides), and which contains at least one letter, so
   a number such as `1_000_000` is not joined (owner's call during the
   build). Every other selection keeps today's behavior
   exactly, including today's first-character check. That covers
   indentation, a whole line, quotes, `$`, several words and a trailing
   newline (designer's call; the anti-goals require it, because a whole-line
   selection starts with indentation).
2. If the identifier starts with the separator, its leading and trailing
   runs of the separator are set aside, the rest is converted by rules 3 to
   6, and the runs are put back unchanged. If nothing is left, the selection
   is unchanged. An identifier that does not start with the separator keeps
   its trailing separators in the conversion, as today, so `foo_bar_` still
   becomes `fooBar` (designer's call; today every input that starts with the
   separator is left unchanged, so this rule changes nothing that converts
   today).
3. If the text contains the separator, join it into the joined form,
   whatever its first character is, with one exception (owner's call during
   the build, after reviews found regressions). Text that starts with an
   uppercase letter keeps today's behavior when a segment has an inner case
   boundary, meaning one the splitting logic would split at (`UserProfile_id`,
   `HTTPServer_x`), or when its only separators are a trailing run
   (`Class_`). Today's behavior is a split under PascalCase and no change
   under camelCase. Joining such text would lose its word boundaries or its
   suffix.
4. Otherwise, if its first character is lowercase (camelCase commands) or
   uppercase (PascalCase commands), split it into the separated form with the
   existing splitting logic.
5. Otherwise leave the selection unchanged.
6. Joining into PascalCase is unchanged: every segment is capitalized.
   Joining into camelCase capitalizes every segment after the first, as
   today. The first segment is lowercased entirely when it is all uppercase,
   and otherwise only its first character is lowercased (designer's call).
   For input that converts today the first character is already lowercase,
   so its output does not change.
7. A result equal to the selection is not written back, so the file is not
   marked as modified (owner's call during the build).

Worked examples. Rows marked "same" are regression checks; the rest are the
intended changes. These rows are the test cases.

| Command | Input | Today | After |
|---|---|---|---|
| camel `_` | `foo_bar` | `fooBar` | same |
| camel `_` | `fooBar` | `foo_bar` | same |
| camel `_` | `a_LL_pointer` | `aLlPointer` | same |
| camel `_` | `getHTTPResponse` | `get_http_response` | same |
| camel `_` | `fooBar_baz` | `fooBarBaz` | same |
| camel `_` | `foo_barBaz` | `fooBarbaz` | same |
| camel `_` | `__init__` | unchanged | same |
| camel `_` | `foo_bar_` | `fooBar` | same |
| camel `_` | `fooBar_` | `fooBar` | same |
| camel `_` | `class_` | `class` | same |
| camel `_` | `def __init__(self):` with four leading spaces | unchanged | same |
| camel `_` | `_private_name` with four leading spaces | unchanged | same |
| camel `_` | `$_SERVER` | unchanged | same |
| camel `_` | `foo_bar` followed by a newline | `fooBar` and the newline | same |
| camel `_` | `1_000_000` | unchanged | same |
| camel `_` | `HTTPServer_x` | unchanged | same |
| camel `_` | `FooBar_baz` | unchanged | same |
| camel `_` | `UserProfile_id` | unchanged | same |
| camel `_` | `Class_` | unchanged | same |
| camel `_` | `MAX_` | unchanged | same |
| camel `_` | `MAX_VALUE` | unchanged | `maxValue` |
| camel `_` | `MAX_VALUE_` | unchanged | `maxValue` |
| camel `_` | `Foo_bar` | unchanged | `fooBar` |
| camel `_` | `_private_name` | unchanged | `_privateName` |
| camel `_` | `_privateName` | unchanged | `_private_name` |
| camel `_` | `1st_place` | unchanged | `1stPlace` |
| Pascal `_` | `foo_bar` | `FooBar` | same |
| Pascal `_` | `FooBar` | `foo_bar` | same |
| Pascal `_` | `a_LL_pointer` | `ALlPointer` | same |
| Pascal `_` | `HTTPServer` | `http_server` | same |
| Pascal `_` | `foo_bar_` | `FooBar` | same |
| Pascal `_` | `Hello_world foo` | `hello_world foo` | same |
| Pascal `_` | `1_000_000` | unchanged | same |
| Pascal `_` | `UserProfile_id` | `user_profile_id` | same |
| Pascal `_` | `FooBar_baz` | `foo_bar_baz` | same |
| Pascal `_` | `FooBar_` | `foo_bar_` | same |
| Pascal `_` | `TestCase_setUp` | `test_case_set_up` | same |
| Pascal `_` | `HTTPServer_x` | `http_server_x` | same |
| Pascal `_` | `Class_` | `class_` | same |
| Pascal `_` | `MAX_` | `max_` | same |
| Pascal `_` | `MAX_VALUE` | `max_value` | `MaxValue` |
| Pascal `_` | `MAX_VALUE_` | `max_value_` | `MaxValue` |
| Pascal `_` | `Foo_Bar` | `foo__bar` | `FooBar` |
| Pascal `_` | `_private_name` | unchanged | `_PrivateName` |
| camel `-` | `foo-bar` | `fooBar` | same |
| camel `-` | `fooBar` | `foo-bar` | same |
| camel `-` | `foo-` | `foo` | same |
| camel `-` | `margin-top: 1px;` with two leading spaces | unchanged | same |
| camel `-` | `foo_bar-baz` | `foo_barBaz` | same |
| camel `-` | `Foo-bar` | unchanged | `fooBar` |
| camel `-` | `--flag-name` | unchanged | `--flagName` |
| camel `-` | `--fooBar` | unchanged | `--foo-bar` |
| Pascal `-` | `my-component-name` | (new) | `MyComponentName` |
| Pascal `-` | `MyComponent` | (new) | `my-component` |
| Pascal `-` | `HTTPServer` | (new) | `http-server` |
| Pascal `-` | `--main-color` | (new) | `--MainColor` |
| Pascal `-` | `MAX-VALUE` | (new) | `MaxValue` |
| Pascal `-` | `UserProfile-id` | (new) | `user-profile-id` |
| Pascal `-` | `HTTPServer-x` | (new) | `http-server-x` |
| Pascal `-` | `Class-` | (new) | `class-` |

The new command (#50) is `ConvertPascalDashCommand`, command name
`convert_pascal_dash`. It appears:

- in the Case submenu as "Convert PascalCase <-> Dash", after
  "Convert PascalCase <-> Underscores";
- in `Default.sublime-commands` as
  "String Utilities: Convert PascalCase <-> Dash", after the PascalCase <->
  Underscores entry;
- in the README feature list. Replace the single "Convert Camel Case <->
  Underscores" line with one line per converter (four lines).

Closing comment for #32, posted with the release: the converters now treat
an identifier containing the separator as separated text whatever its first
letter (`MAX_VALUE` becomes `maxValue` or `MaxValue`), except capitalized
text with an inner case boundary or only a trailing separator, which keeps
its old behavior. Acronyms are not kept when joining (`a_LL_pointer` becomes
`aLlPointer`, as lodash and the Google style guide do), and a round trip
cannot restore them in either direction.

## #26: nested menus

The "String Utilities" submenu becomes a list of ten submenus (group names
and order are the designer's call). Captions inside the groups stay as they
are today. The top-level item keeps `"id": "context-convert"` and both
separators keep `"id": "context-convert-end"`.

1. **Whitespace:** Convert Tabs to Spaces; Convert Spaces to Tabs; Convert
   Spaces to &nbsp; (Non-breaking space)
2. **Case:** Convert camelCase <-> Underscores; Convert camelCase <-> Dash;
   Convert PascalCase <-> Underscores; Convert PascalCase <-> Dash (new)
3. **Quotes:** Expand Selection To Whole String; Convert Single Quotes To
   Double; Convert Double Quotes To Single
4. **Encode / Decode:** Convert Chars to HTML Entities; Convert HTML Entities
   to Chars; separator; Encode as URL Notation; Decode from URL Notation;
   separator; Convert To Unicode Notation; Convert From Unicode Notation;
   separator; Convert To Base64; Convert From Base64; separator; Convert To
   Hex; Convert From Hex; separator; Decode HeidiSQL password
5. **Color:** Convert HTML Color Hex To RGB; Convert HTML Color RGB To Hex
6. **Hash:** Calculate MD5; Calculate SHA1; Calculate SHA224; Calculate
   SHA256; Calculate SHA384; Calculate SHA512. The last four exist as
   commands and palette entries but were never in the menu (designer's call
   to add them).
7. **Date and Time:** Convert Unixtime <-> Datetime; Insert Current Datetime
8. **Password:** the seven "Generate Password (N char)" entries, a separator,
   then the seven "Generate Password with spec symbols (N char)" entries,
   with their existing `args`
9. **Network:** Insert Internal IP; Insert External IP
10. **JSON and PHP:** Pretify JSON String; Convert PHP Object to Array

## #13: close

Close with a comment. The issue has no description. If it meant "put a cursor
on several numbers and renumber them", Insert Nums (Package Control name
"Insert Nums", maintained under the SublimeText GitHub organization, last
updated September 2025) already does that across multiple selections.

## Verification

- Tests call each command's `run()` through the fake `sublime` stubs and
  fake view used in the earlier fix rounds. They must not reimplement the
  direction logic, or they cannot fail on it.
- The #32 and #50 tests are written first and are seen failing on the
  current code (for #50, because the command does not exist).
- Run every suite on Python 3.3.7 (Docker image `python:3.3`) and on the
  local Python 3.14. The earlier harness outputs for all other commands must
  still match their baselines.
- Menu and palette checks: both files parse as JSON; every `command` in
  either file resolves to a command class in `stringutilities.py`; the new
  menu holds every caption, command and `args` of the old menu exactly once,
  plus the five additions (Pascal <-> Dash and the four SHA entries); the
  `id` values are unchanged.
- #35: no runtime code reads files relative to the package. Whether to also
  import the plugin from a zip as an extra check is left to the builder.

## Release (separate, confirmed step)

Tagging 1.9.0, creating the GitHub release, and posting the #32 and #13
comments are outward-facing and are confirmed separately after the build.

## Left to the builder

- How the four converters share logic, for example a base class with
  separator and target attributes (the pattern
  `GeneratePasswordSpecSymbolsCommand` already uses) or module-level helpers.
- Test file layout under `tmp/`.
- Commit order.
