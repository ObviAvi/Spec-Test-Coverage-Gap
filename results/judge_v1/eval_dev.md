# STCG judge evaluation: `judge_v1` on `dev`

- tasks: 138, judged: 138, judged by all judges: 138
- errors per judge: {'claude': 0, 'gpt61': 0}

## Targets (ensemble, all tasks)

- recall on overspecified: 81% (target >= 70%)
- false-flag rate on fine: 3% (target <= 15%)
- **MET**

## Detection

| scorer | group | recall | false-flag rate |
|---|---|---|---|
| claude | all | 83% (62/75, CI 73%-90%) | 3% (2/63, CI 1%-11%) |
| claude | source:agent_consensus | - | 3% (2/63, CI 1%-11%) |
| claude | source:openai_excluded | 89% (40/45, CI 77%-95%) | - |
| claude | source:pro_narrow_original | 73% (22/30, CI 56%-86%) | - |
| gpt61 | all | 88% (66/75, CI 79%-94%) | 17% (11/63, CI 10%-29%) |
| gpt61 | source:agent_consensus | - | 17% (11/63, CI 10%-29%) |
| gpt61 | source:openai_excluded | 89% (40/45, CI 77%-95%) | - |
| gpt61 | source:pro_narrow_original | 87% (26/30, CI 70%-95%) | - |
| ensemble | all | 81% (61/75, CI 71%-89%) | 3% (2/63, CI 1%-11%) |
| ensemble | source:agent_consensus | - | 3% (2/63, CI 1%-11%) |
| ensemble | source:openai_excluded | 87% (39/45, CI 74%-94%) | - |
| ensemble | source:pro_narrow_original | 73% (22/30, CI 56%-86%) | - |
| ensemble_certain_only | all | 85% (61/72, CI 75%-91%) | 4% (2/56, CI 1%-12%) |
| ensemble_certain_only | source:agent_consensus | - | 4% (2/56, CI 1%-12%) |
| ensemble_certain_only | source:openai_excluded | 87% (39/45, CI 74%-94%) | - |
| ensemble_certain_only | source:pro_narrow_original | 81% (22/27, CI 63%-92%) | - |

## Inter-judge agreement

- Fleiss' kappa on the flag (tasks judged by all): 0.783
- uncertain (spread >= 2): 7% (10/138, CI 4%-13%)

| pair | n | Cohen's kappa | agree |
|---|---|---|---|
| claude~gpt61 | 138 | 0.784 | 89% |

## Missed overspecified tasks (14)

- `full/django__django-13199` [openai_excluded] scores={'claude': 2, 'gpt61': 3} final=2
  - claude: Every reasonable fix adds a `samesite` argument to delete_cookie, mirroring set_cookie, and has messages and sessions pass SESSION_COOKIE_SAMESITE when deleting, which is exactly what the graded assertions check.
  - gpt61: A correct fix that canonicalizes SameSite values to 'Lax' would fail the test requiring exactly 'lax'. Alternatively, preserving the session cookie's HttpOnly attribute during deletion would fail the exact session-header comparisons despite preserving SameSite correctly.
- `full/django__django-16786` [openai_excluded] scores={'claude': 2, 'gpt61': 2} final=2
  - claude: The tests only check that FilteredRelation conditions referencing fields across joins (directly, through another filtered relation, or self-referencing) return the correct rows, which is what a correct fix for the reported missing JOIN would do.
  - gpt61: The tests reasonably generalize the reported JOIN-resolution bug to direct F references, chained filtered relations, and self-references, asserting only that the public queries return the matching book.
- `full/pydata__xarray-4994` [openai_excluded] scores={'claude': 2, 'gpt61': 1} final=1
  - claude: The graded test only checks that `da.time.dt.date` matches pandas' `DatetimeIndex.date` (object array of `datetime.date`), which is exactly what the issue requests and suggests implementing.
  - gpt61: The graded date-field access case directly checks the missing `.dt.date` functionality requested in the issue; no shown graded assertion imposes an additional implementation choice.
- `full/scikit-learn__scikit-learn-13253` [openai_excluded] scores={'claude': 2, 'gpt61': 1} final=1
  - claude: The graded test checks only that each column's `categories_` dtype is preserved (int, object, float) and that the transform output is correct, which is exactly what the specification's per-column dtype preservation describes.
  - gpt61: The graded assertions directly check the requested preservation of integer, object-string, and floating-point column dtypes in categories_, while retaining the existing one-hot encoding behavior.
- `full/sympy__sympy-12906` [openai_excluded] scores={'claude': 2, 'gpt61': 2} final=2
  - claude: The graded test checks only properties inherent to a canonical form: idempotence on the issue's own example and related inputs, orientation invariance, and Numbers on the right per existing convention. It pins no specific output form, so any correct canonicalization passes.
  - gpt61: The tests directly check the reported idempotence failure on related inputs and add reversal consistency and numeric-right placement checks supported by existing canonicalization conventions, without requiring one exact symbolic result.
- `full/sympy__sympy-16334` [openai_excluded] scores={'claude': 3, 'gpt61': 2} final=2
  - claude: The tests also require symbolic 0**0 (two distinct zero=True symbols) to report is_positive True and is_negative False. A fix that only returns False for a zero base with a real nonzero exponent, as the issue describes, leaves this case as None and fails.
  - gpt61: The tests reproduce the requested `(p**q).is_positive is False` behavior and add only its sign consequences, a related nonzero even exponent, and standard power-sign boundary and regression checks.
- `pro/instance_element-hq__element-web-71fe08ea0f159ccb707904d87f0a4aef205a167c-vnan` [pro_narrow_original] scores={'claude': 1, 'gpt61': 1} final=1
  - claude: Every asserted string is either given verbatim in the requirements ("Profile picture" for MemberAvatar's aria-label) or follows from the mandated 'avatar' to 'profile picture' substitution in the EncryptionEvent sentence and the two setting labels, so every correct fix passes.
  - gpt61: The graded changes directly check the requested terminology replacement in EncryptionEvent and settings, and the explicitly required “Profile picture” accessibility label supplied by MemberAvatar.
- `pro/instance_element-hq__element-web-7c63d52500e145d6fff6de41dd717f61ab88d02f-vnan` [pro_narrow_original] scores={'claude': 2, 'gpt61': 1} final=1
  - claude: The tests check that the specified class `mx_WysiwygComposer_Editor_content_placeholder` is present on the content textbox when the composer is empty with a placeholder, and that it toggles off and back on with input. All of this is stated in the requirements, and the class name ties it to the content element.
  - gpt61: The graded assertions directly check the explicitly required CSS-class state: present when empty, absent after input, and present again after clearing, in both composer modes.
- `pro/instance_future-architect__vuls-83bcca6e669ba2e4102f26c4a2b52f78c7861f1a` [pro_narrow_original] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The spec explicitly names every method, its signature, the empty-slice semantics, the dedup rule, the allowed orderings (both sorted and host-order give the tested results), and IPv6 bracket preservation, so the tested behaviors follow directly from it.
  - gpt61: A correct parseListenPorts implementation can initialize PortScanSuccessOn to []string{}, consistent with the empty-slice requirement, but every parser fixture implicitly demands nil. The whole-struct comparison therefore rejects a correct fix based on an unspecified pre-scan internal representation.
- `pro/instance_internetarchive__openlibrary-e1e502986a3b003899a8347ac8a7ff7b08cbfc39-v08d8e8889ec945ab821fb156c04c7d2e2810debb` [pro_narrow_original] scores={'claude': 2, 'gpt61': 3} final=2
  - claude: The graded assertions follow the spec directly: stars, then a single space, then ' | '-delimited segments, with an optional fourth segment of default `json.dumps` extra fields, which `from_markdown` parses into the `authors` attribute.
  - gpt61: A correct fix could emit compact JSON such as '{"authors":[{"name":"Author 1"}]}' while preserving every field and using the required TOC segment delimiters. The final to_markdown assertion rejects that valid choice by requiring spaces inside the JSON.
- `pro/instance_navidrome__navidrome-3982ba725883e71d4e3e618c61d5140eeb8d850a` [pro_narrow_original] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The tests call the spec-named package-level functions `Backup`, `Restore` and `Prune` and use `Db()` as a `*sql.DB`. Repositories receive a plain `*dbx.DB` built in the test helper, which any fix that removes the read/write abstraction would accept.
  - gpt61: The tests require individual repository constructors to accept *dbx.DB, an implementation detail the specification does not prescribe. A correct refactor that instead passes the unified *sql.DB directly into those constructors would fail to compile against the test helper and its calls.
- `pro/instance_navidrome__navidrome-e12a14a87d392ac70ee4cc8079e3c3e0103dbcb2` [pro_narrow_original] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The tests check the Channels() method named in the Interface, the 'stereo'→2 mapping stated in the Requirements, and a map key "channels" that follows the existing "bitrate"/"duration" convention and the "channels" DB column, so every reasonable fix passes.
  - gpt61: The FFmpeg tests require channel extraction specifically inside the unexported extractMetadata helper. A correct implementation that parses channels and augments the metadata map in the normal FFmpeg entry point, after calling that helper, would fail these tests despite providing the required metadata.
- `pro/instance_qutebrowser__qutebrowser-2e961080a85d660148937ee8f0f6b3445a8f2c01-v363c8a7e5ccdf6968fc7ab84a2053ac78036691d` [pro_narrow_original] scores={'claude': 2, 'gpt61': 1} final=1
  - claude: The graded assertion checks only that `--disable-accelerated-2d-canvas` appears in `qt_args` output exactly as the spec's always/never/auto (Qt6 and Chromium<111) rules dictate, through the public entry point.
  - gpt61: The graded assertions directly check the specified flag presence for always, never, and the Qt/Chromium-dependent auto mode through the normal argument-building entry point.
- `pro/instance_qutebrowser__qutebrowser-85b867fe8d4378c8e371f055c70452f546055854-v2ef375ac784985212b1805e1d0431dc8f1b3c171` [pro_narrow_original] scores={'claude': 2, 'gpt61': 1} final=1
  - claude: The graded tests check only valid parsing, including negatives, and that all failures surface as ValueError, including overflow. All of this is explicitly required by the spec; the exact-message test is not graded.
  - gpt61: Every reasonable correct fix passes: the QPoint equality assertions directly check the specified integer-coordinate parsing, while the property tests check the specified robustness and ValueError handling without constraining message wording or implementation.

## False flags on fine tasks (2)

- `verified/django__django-11299` [agent_consensus] scores={'claude': 4, 'gpt61': 4} final=4
  - claude: The graded test calls Query.build_where directly and asserts that the internal lookup nodes' lhs/rhs are SimpleCol instances, including an F('id') rhs not mentioned in the spec. A fix that corrects the constraint SQL elsewhere (e.g., converting Cols in CheckConstraint._get_check_sql or stripping aliases at compile time) would produce correct SQL but fail these isinstance checks.
  - gpt61: A correct fix could remove column qualification specifically during CheckConstraint SQL generation without changing generic Query.build_where(). The graded test would reject it because it directly inspects that query builder's intermediate tree and requires SimpleCol instances.
- `verified/scikit-learn__scikit-learn-14983` [agent_consensus] scores={'claude': 3, 'gpt61': 3} final=3
  - claude: The test requires the repr to list parameters alphabetically (`n_repeats=6, n_splits=2, random_state=None`), but the spec's expected output lists n_splits before n_repeats. A fix that produces exactly the spec's format fails.
  - gpt61: A correct fix that follows the specification's illustrated parameter order—n_splits, n_repeats, random_state—would fail because the tests require n_repeats before n_splits.

## Uncertain tasks (reported separately) (10)

- `verified/django__django-14311` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The test asserts that get_child_arguments returns `-m <full dotted module name>` for a non-package module, which is exactly the behavior the issue requests; any spec-based fix (using __spec__.name, falling back to parent only for __main__) passes.
  - gpt61: A correct fix that uses sys.argv[0] to distinguish a package's __main__.py from an ordinary module file would fail because the test supplies a package-entry filename while substituting a different, non-package __main__ module. Real execution of the tested module would put main_module.py in sys.argv[0], so this failure does not demonstrate the reported bug.
- `verified/sphinx-doc__sphinx-11445` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The tests assert that ``:mod:`foo` `` is not treated as docinfo, so the prolog is inserted at the top with the existing generated blank line. That follows directly from the bug report and the existing behavior of `prepend_prolog`.
  - gpt61: A correct fix could recognize the role-containing heading and surround the inserted prolog with harmless blank-line padding. Both graded tests would reject that fix because they require an exact intermediate StringList layout and provenance, rather than checking that the heading renders and appears in the toctree.
- `verified/sphinx-doc__sphinx-10673` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The test asserts that the toctree keeps the entries `(None, 'genindex')`, `(None, 'modindex')` and `(None, 'search')` instead of dropping them with a warning; any fix that includes these names following the existing (title, docname) entry convention passes.
  - gpt61: A correct fix could populate generated-page titles when recognizing these special toctree entries, producing working links without warnings. The test would reject it because it requires the internal app.env.tocs entries to retain exactly (None, 'genindex'), (None, 'modindex'), and (None, 'search').
- `verified/sphinx-doc__sphinx-7757` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The bug lives in signature_from_str, which the directive uses to parse arglists. The test checks the spec's exact example, asserting `b.default == '0'`, using the existing string-default convention, so any reasonable fix passes.
  - gpt61: A correct fix could preserve positional-only defaults in the Python directive's parsing/rendering path while leaving `inspect.signature_from_str` unchanged. The graded test instead requires that helper itself to return specific intermediate default values, so that fix would fail despite producing the required documentation.
- `verified/pydata__xarray-2905` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The spec pinpoints the `getattr(data, 'values', data)` line in the shared `as_compatible_data` helper. Any fix there that stops unwrapping `.values` from arbitrary objects makes the test's assertion pass: the Variable stores the CustomWithValuesAttr object itself, which `_data.item()` returns.
  - gpt61: A correct fix could prevent coercion specifically during object-dtype assignment while retaining existing constructor behavior. The test bypasses assignment and instead requires direct scalar `Variable` construction to preserve the custom object in `_data`, so that fix could fail.
- `verified/sphinx-doc__sphinx-8120` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: Any correct fix must make the user's sphinx.po override the built-in 'sphinx' catalog that backs the existing `app.translator`, so both the gettext assertion and the 'QUICK SEARCH' HTML check follow directly from the issue's expected behaviour.
  - gpt61: A correct fix could load the project-local system catalog at the beginning of the build and produce all the requested translated output. It would nevertheless fail because the test requires app.translator to expose the override immediately after application construction, before app.build() runs.
- `verified/sympy__sympy-15345` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The assertion checks Max and Min (its direct twin) printed with Mathematica brackets, using the printer's existing ", " separator convention and natural x, y, z ordering, so any reasonable fix passes.
  - gpt61: The assertion additionally requires fixing Min printing, a separate function absent from the issue. A reasonable Max-only printer fix would resolve the reported defect and related Max inputs but fail because Min(y,z) still prints with parentheses.
- `pro/instance_future-architect__vuls-83bcca6e669ba2e4102f26c4a2b52f78c7861f1a` [pro_narrow_original] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The spec explicitly names every method, its signature, the empty-slice semantics, the dedup rule, the allowed orderings (both sorted and host-order give the tested results), and IPv6 bracket preservation, so the tested behaviors follow directly from it.
  - gpt61: A correct parseListenPorts implementation can initialize PortScanSuccessOn to []string{}, consistent with the empty-slice requirement, but every parser fixture implicitly demands nil. The whole-struct comparison therefore rejects a correct fix based on an unspecified pre-scan internal representation.
- `pro/instance_navidrome__navidrome-3982ba725883e71d4e3e618c61d5140eeb8d850a` [pro_narrow_original] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The tests call the spec-named package-level functions `Backup`, `Restore` and `Prune` and use `Db()` as a `*sql.DB`. Repositories receive a plain `*dbx.DB` built in the test helper, which any fix that removes the read/write abstraction would accept.
  - gpt61: The tests require individual repository constructors to accept *dbx.DB, an implementation detail the specification does not prescribe. A correct refactor that instead passes the unified *sql.DB directly into those constructors would fail to compile against the test helper and its calls.
- `pro/instance_navidrome__navidrome-e12a14a87d392ac70ee4cc8079e3c3e0103dbcb2` [pro_narrow_original] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The tests check the Channels() method named in the Interface, the 'stereo'→2 mapping stated in the Requirements, and a map key "channels" that follows the existing "bitrate"/"duration" convention and the "channels" DB column, so every reasonable fix passes.
  - gpt61: The FFmpeg tests require channel extraction specifically inside the unexported extractMetadata helper. A correct implementation that parses channels and augments the metadata map in the normal FFmpeg entry point, after calling that helper, would fail these tests despite providing the required metadata.
