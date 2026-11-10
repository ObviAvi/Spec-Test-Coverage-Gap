# STCG judge evaluation: `judge_v1_gold` on `dev`

- tasks: 138, judged: 138, judged by all judges: 138
- errors per judge: {'claude': 0, 'gpt61': 0}

## Targets (ensemble, all tasks)

- recall on overspecified: 87% (target >= 70%)
- false-flag rate on fine: 5% (target <= 15%)
- **MET**

## Detection

| scorer | group | recall | false-flag rate |
|---|---|---|---|
| claude | all | 87% (65/75, CI 77%-93%) | 5% (3/63, CI 2%-13%) |
| claude | source:agent_consensus | - | 5% (3/63, CI 2%-13%) |
| claude | source:openai_excluded | 91% (41/45, CI 79%-96%) | - |
| claude | source:pro_narrow_original | 80% (24/30, CI 63%-90%) | - |
| gpt61 | all | 88% (66/75, CI 79%-94%) | 17% (11/63, CI 10%-29%) |
| gpt61 | source:agent_consensus | - | 17% (11/63, CI 10%-29%) |
| gpt61 | source:openai_excluded | 91% (41/45, CI 79%-96%) | - |
| gpt61 | source:pro_narrow_original | 83% (25/30, CI 66%-93%) | - |
| ensemble | all | 87% (65/75, CI 77%-93%) | 5% (3/63, CI 2%-13%) |
| ensemble | source:agent_consensus | - | 5% (3/63, CI 2%-13%) |
| ensemble | source:openai_excluded | 91% (41/45, CI 79%-96%) | - |
| ensemble | source:pro_narrow_original | 80% (24/30, CI 63%-90%) | - |
| ensemble_certain_only | all | 88% (65/74, CI 78%-93%) | 5% (3/59, CI 2%-14%) |
| ensemble_certain_only | source:agent_consensus | - | 5% (3/59, CI 2%-14%) |
| ensemble_certain_only | source:openai_excluded | 91% (41/45, CI 79%-96%) | - |
| ensemble_certain_only | source:pro_narrow_original | 83% (24/29, CI 65%-92%) | - |

## Inter-judge agreement

- Fleiss' kappa on the flag (tasks judged by all): 0.869
- uncertain (spread >= 2): 4% (5/138, CI 2%-8%)

| pair | n | Cohen's kappa | agree |
|---|---|---|---|
| claude~gpt61 | 138 | 0.870 | 93% |

## Missed overspecified tasks (10)

- `full/django__django-16786` [openai_excluded] scores={'claude': 2, 'gpt61': 2} final=2
  - claude: All three tests assert only queryset results for FilteredRelation conditions whose F() references need a JOIN, which is exactly the bug described ('the JOIN not actually getting added') applied to closely related inputs.
  - gpt61: Every reasonable general fix should make these FilteredRelation queries resolve the JOINs needed by their F expressions and return the expected matching book, including when one filtered annotation references another.
- `full/pydata__xarray-4994` [openai_excluded] scores={'claude': 1, 'gpt61': 1} final=1
  - claude: The graded test `test_field_access[date]` checks that `da.time.dt.date` matches pandas' `DatetimeIndex.date`, which is exactly what the issue requests and the suggested one-line code provides.
  - gpt61: The graded date-field access case checks the public `.dt.date` functionality explicitly requested by the issue; no graded requirement shown rejects a reasonable alternative implementation.
- `full/scikit-learn__scikit-learn-13253` [openai_excluded] scores={'claude': 2, 'gpt61': 1} final=1
  - claude: The graded assertion that `categories_` dtypes are [int, object, float] for a mixed DataFrame is exactly the per-column dtype preservation the issue requests, so any fix that encodes column by column while keeping each column's dtype passes.
  - gpt61: The graded assertion that mixed DataFrame columns retain integer, object, and float category dtypes directly checks the requested per-column dtype preservation; the output assertions retain existing one-hot encoding behavior.
- `full/sympy__sympy-12906` [openai_excluded] scores={'claude': 2, 'gpt61': 2} final=2
  - claude: The graded test checks only idempotence (the issue itself), invariance under `.reversed`, and Number-on-rhs, all inherent to a 'canonical' form and to the existing rules, so any reasonable fix choosing any consistent normal form passes.
  - gpt61: The tests check the reported idempotence property on related inputs, together with existing canonicalization conventions: agreement under reversal, numeric operands on the right, and preservation of unevaluated relations. They do not require the official fix's particular symbolic ordering.
- `pro/instance_element-hq__element-web-71fe08ea0f159ccb707904d87f0a4aef205a167c-vnan` [pro_narrow_original] scores={'claude': 2, 'gpt61': 1} final=1
  - claude: Every graded assertion checks a string the requirements spell out or that results from a direct 'avatar'→'profile picture' substitution, including MemberAvatar's aria-label 'Profile picture', so every reasonable fix passes.
  - gpt61: The graded changes directly check the requested “avatar” → “profile picture” text substitutions and the explicitly specified “Profile picture” accessible label for member images.
- `pro/instance_element-hq__element-web-7c63d52500e145d6fff6de41dd717f61ab88d02f-vnan` [pro_narrow_original] scores={'claude': 2, 'gpt61': 1} final=1
  - claude: The tests check that the textbox carries the specified class `mx_WysiwygComposer_Editor_content_placeholder` when the composer is empty and has a placeholder, and that the class toggles off and back on with input. The spec states all of this explicitly, so every reasonable fix passes.
  - gpt61: The graded assertions directly match the specified CSS-class transitions for an empty composer, entered content, and cleared content in both required composer modes.
- `pro/instance_future-architect__vuls-83bcca6e669ba2e4102f26c4a2b52f78c7861f1a` [pro_narrow_original] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The spec spells out exact method signatures, last-colon parsing with brackets kept, wildcard expansion, deduplication, and non-nil return slices. Every ordering it allows (sorted or host-IP order) yields the asserted lists, so reasonable implementations pass.
  - gpt61: A correct parser that initializes PortScanSuccessOn to []string{} fails because the parser tests require nil before scanning. A correct wildcard matcher that validates addresses against ServerInfo.IPv4Addrs also fails because the wildcard fixtures provide no host addresses but expect matches.
- `pro/instance_navidrome__navidrome-e12a14a87d392ac70ee4cc8079e3c3e0103dbcb2` [pro_narrow_original] scores={'claude': 2, 'gpt61': 2} final=2
  - claude: The tests assert stereo maps to 2 under the conventional lowercase key "channels", read via Channels() and from both parsers, which follows directly from the spec's requirements and the existing "bitrate"/"duration" key pattern.
  - gpt61: The assertions check the specified stereo-to-2 conversion through FFmpeg, TagLib, and Channels(); string-slice storage follows the existing metadata convention, and the FFmpeg formats are ordinary related inputs.
- `pro/instance_qutebrowser__qutebrowser-2e961080a85d660148937ee8f0f6b3445a8f2c01-v363c8a7e5ccdf6968fc7ab84a2053ac78036691d` [pro_narrow_original] scores={'claude': 2, 'gpt61': 1} final=1
  - claude: The tests only check whether `--disable-accelerated-2d-canvas` appears in `qt_args` output for always/never/auto across Qt 5.15, 6.5 and 6.6, which matches the spec's stated rule (Qt 6 and Chromium < 111) exactly.
  - gpt61: Every reasonable correct fix passes because the graded assertions check precisely the specified flag presence for always, never, and auto across representative Qt/Chromium versions.
- `pro/instance_qutebrowser__qutebrowser-85b867fe8d4378c8e371f055c70452f546055854-v2ef375ac784985212b1805e1d0431dc8f1b3c171` [pro_narrow_original] scores={'claude': 2, 'gpt61': 1} final=1
  - claude: The graded tests check only correct parsing of valid 'x,y' strings and that every other input yields either a result or a ValueError (including overflow), all of which the requirements state explicitly; the exact-message checks are in the ungraded test_invalid.
  - gpt61: Every reasonable correct fix passes: the QPoint equality assertions directly check the specified coordinate conversion, and the hypothesis tests check the specified handling of malformed input and integer overflow without prescribing message wording.

## False flags on fine tasks (3)

- `verified/pydata__xarray-2905` [agent_consensus] scores={'claude': 3, 'gpt61': 4} final=3
  - claude: The graded test checks the `Variable` constructor (`Variable(dims=(), data=obj_with_values)`) rather than `__setitem__`/`.loc`. A correct fix that stops the coercion only in the `__setitem__` assignment path, without changing `as_compatible_data` for construction, would resolve the reported issue but fail the test.
  - gpt61: A correct fix could prevent coercion specifically during object-dtype assignment while leaving Variable construction unchanged. The graded test instead constructs a scalar Variable directly and inspects its private storage, so that fix would fail despite resolving the specified assignment bug.
- `verified/django__django-11299` [agent_consensus] scores={'claude': 3, 'gpt61': 4} final=3
  - claude: The test inspects the internal expression tree returned by `Query.build_where` and requires SimpleCol nodes there. A correct fix that removes table qualification at the CheckConstraint/SQL-generation level (e.g., converting Cols in `_get_check_sql` or compiling without aliases) would produce correct SQL but fail these isinstance assertions.
  - gpt61: A correct fix could remove table qualification specifically during CheckConstraint SQL compilation without changing Query.build_where(). It would still fail the test's assertions that nested lookup operands must already be SimpleCol instances.
- `verified/scikit-learn__scikit-learn-14983` [agent_consensus] scores={'claude': 3, 'gpt61': 3} final=3
  - claude: The test requires the parameters in alphabetical order, 'n_repeats=6, n_splits=2, random_state=None', as produced by the existing _build_repr helper. A fix that matches the spec's stated expected output order (n_splits, n_repeats, random_state) fails.
  - gpt61: A reasonable fix that preserves the specification's displayed order, n_splits before n_repeats, would fail both tests. The tests instead require n_repeats before n_splits through exact string equality.

## Uncertain tasks (reported separately) (5)

- `verified/django__django-14311` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The test asserts that `-m` receives the full dotted module name ('utils_tests.test_module.main_module') when `__main__.__spec__` names a non-package module, which is exactly what the spec says should replace the incorrect parent name, so any reasonable spec-based fix passes.
  - gpt61: A correct fix could use the launched script's filename to distinguish package execution from ordinary module execution. The test patches `__main__` to `main_module` but leaves `sys.argv[0]` pointing at the package's `__main__.py`, so that fix fails this internal argument-construction test despite handling real launches correctly.
- `verified/sphinx-doc__sphinx-11445` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The tests call the existing `prepend_prolog` function, which is the source of the bug. They check that a role-prefixed heading is not treated as docinfo, so the prolog is inserted before it with the existing '<generated>' blank-line layout, and every reasonable fix to the docinfo detection produces exactly this output.
  - gpt61: The tests require prepend_prolog itself to produce an exact intermediate StringList, including separator placement and source metadata. A correct input-preprocessing fix that protects initial role headings before calling this helper would restore rendering and toctree inclusion but fail both direct helper tests.
- `verified/sphinx-doc__sphinx-10673` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: Every reasonable fix must stop dropping the genindex/modindex/search entries in toctree parsing and keep them as `(None, name)` per the existing untitled-entry convention, which is what the entries assertion checks.
  - gpt61: A correct fix could resolve generated-page default titles while parsing the directive instead of preserving None until later resolution. The test would reject that fix because it requires exact unresolved tuples inside app.env.tocs['index'], although the resulting links and warning-free build could be identical.
- `verified/sphinx-doc__sphinx-7757` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The test runs the issue's exact signature through the existing parser `signature_from_str`, where the defaults are dropped. It asserts the stringified defaults `'0'` and `'1'`, which follows the existing convention for regular args, so every reasonable fix passes.
  - gpt61: A correct fix in the Python directive's signature-processing/rendering path could restore positional-only defaults while leaving `signature_from_str` unchanged. The graded test would reject it because it directly requires the lower-level utility to return `sig.parameters['b'].default == '0'`.
- `pro/instance_future-architect__vuls-83bcca6e669ba2e4102f26c4a2b52f78c7861f1a` [pro_narrow_original] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The spec spells out exact method signatures, last-colon parsing with brackets kept, wildcard expansion, deduplication, and non-nil return slices. Every ordering it allows (sorted or host-IP order) yields the asserted lists, so reasonable implementations pass.
  - gpt61: A correct parser that initializes PortScanSuccessOn to []string{} fails because the parser tests require nil before scanning. A correct wildcard matcher that validates addresses against ServerInfo.IPv4Addrs also fails because the wildcard fixtures provide no host addresses but expect matches.
