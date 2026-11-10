# STCG judge evaluation: `judge_v1` on `test`

- tasks: 206, judged: 206, judged by all judges: 206
- errors per judge: {'claude': 0, 'gpt61': 0}

## Targets (ensemble, all tasks)

- recall on overspecified: 89% (target >= 70%)
- false-flag rate on fine: 4% (target <= 15%)
- **MET**

## Detection

| scorer | group | recall | false-flag rate |
|---|---|---|---|
| claude | all | 89% (100/112, CI 82%-94%) | 4% (4/94, CI 2%-10%) |
| claude | source:agent_consensus | - | 4% (4/94, CI 2%-10%) |
| claude | source:openai_excluded | 97% (65/67, CI 90%-99%) | - |
| claude | source:pro_narrow_original | 78% (35/45, CI 64%-87%) | - |
| gpt61 | all | 94% (105/112, CI 88%-97%) | 18% (17/94, CI 12%-27%) |
| gpt61 | source:agent_consensus | - | 18% (17/94, CI 12%-27%) |
| gpt61 | source:openai_excluded | 97% (65/67, CI 90%-99%) | - |
| gpt61 | source:pro_narrow_original | 89% (40/45, CI 77%-95%) | - |
| ensemble | all | 89% (100/112, CI 82%-94%) | 4% (4/94, CI 2%-10%) |
| ensemble | source:agent_consensus | - | 4% (4/94, CI 2%-10%) |
| ensemble | source:openai_excluded | 97% (65/67, CI 90%-99%) | - |
| ensemble | source:pro_narrow_original | 78% (35/45, CI 64%-87%) | - |
| ensemble_certain_only | all | 90% (100/111, CI 83%-94%) | 5% (4/82, CI 2%-12%) |
| ensemble_certain_only | source:agent_consensus | - | 5% (4/82, CI 2%-12%) |
| ensemble_certain_only | source:openai_excluded | 97% (65/67, CI 90%-99%) | - |
| ensemble_certain_only | source:pro_narrow_original | 80% (35/44, CI 65%-89%) | - |

## Inter-judge agreement

- Fleiss' kappa on the flag (tasks judged by all): 0.824
- uncertain (spread >= 2): 6% (13/206, CI 4%-10%)

| pair | n | Cohen's kappa | agree |
|---|---|---|---|
| claude~gpt61 | 206 | 0.825 | 91% |

## Missed overspecified tasks (12)

- `full/django__django-12983` [openai_excluded] scores={'claude': 2, 'gpt61': 2} final=2
  - claude: Every fix that trims leading/trailing dashes and underscores from slugify's final output, as the example "___This is a test ---" -> "this-is-a-test" requires, passes all the new slugify input/output assertions.
  - gpt61: Every reasonable boundary-stripping fix should pass: the underscore, dash, and mixed-boundary assertions directly generalize the reported example, while the other assertions preserve normal slugification behavior.
- `full/pytest-dev__pytest-7158` [openai_excluded] scores={'claude': 2, 'gpt61': 2} final=2
  - claude: The test asserts the skip summary shows the path relative to the invocation directory (`tests/test_1.py`), which is exactly the behavior the issue requests; the line number and reason are pre-existing output.
  - gpt61: The assertion that the summary contains 'tests/test_1.py' checks the same invocation-relative reporting requirement using an explicitly different rootdir; the remaining output preserves ordinary skip-report behavior.
- `pro/instance_NodeBB__NodeBB-4327a09d76f10a79109da9d91c22120428d3bdb9-vnan` [pro_narrow_original] scores={'claude': 1, 'gpt61': 1} final=1
  - claude: Every reasonable fix passes: the graded test checks exactly the stated requirements. `getObjects(keys, fields)` returns the requested fields in input-key order, and a requested field missing from an object is included with value `null`.
  - gpt61: Every reasonable correct fix passes because the graded assertions directly check requested field values, explicitly required null values for absent fields, and explicitly required input-key ordering.
- `pro/instance_NodeBB__NodeBB-f9ce92df988db7c1ae55d9ef96d247d27478bc70-vf2cf3cbd463b7ad942381f1c6d077626485a1e9e` [pro_narrow_original] scores={'claude': 2, 'gpt61': 3} final=2
  - claude: The test asserts the spec-given `[[error:invalid-path]]` message, and the 500 status follows from the endpoint's existing invalid-path error handling. The spec's call for consistent error messaging points every reasonable fix to that same handling.
  - gpt61: A correct fix could immediately reject a nonexistent destination with HTTP 400 and `body.error` equal to `[[error:invalid-path]]`. The test would reject that fix because it additionally requires HTTP 500, which the specification does not mandate.
- `pro/instance_ansible__ansible-b5e0293645570f3f404ad1dbbe5f006956ada0df-v0f01c69f1e2528b935359cfe578530722bca2c59` [pro_narrow_original] scores={'claude': 2, 'gpt61': 3} final=2
  - claude: Every graded assertion maps directly to the stated requirements: no separators between `<S>` entries in the same block, no trimming of the trailing `\r\n`, and empty input producing empty output.
  - gpt61: The tests additionally require `_x005F_x005F_` to collapse to `_x005F_`. A reasonable implementation following the specified special handling of `_x005F_` could preserve it when no complete escape token follows, returning `_x005F_x005F_` instead.
- `pro/instance_ansible__ansible-ea04e0048dbb3b63f876aad7020e1de8eee9f362-v1055803c3a812189a1133297f7f5468579283f86` [pro_narrow_original] scores={'claude': 2, 'gpt61': 2} final=2
  - claude: The tests check exactly the requirement-listed output shapes, ordering, and the verbatim AssertionError message 'implementation error -- version and date must not both be set' when both version and date are provided (passed, here as empty strings, consistent with None defaults).
  - gpt61: Every reasonable fix passes: the output assertions directly match the Requirements, and rejecting two explicitly supplied empty-string arguments is a reasonable boundary check of the specified version/date mutual exclusion and exact AssertionError message.
- `pro/instance_flipt-io__flipt-a42d38a1bb1df267c53d9d4a706cf34825ae3da9` [pro_narrow_original] scores={'claude': 2, 'gpt61': 2} final=2
  - claude: The tests check that `authentication.session.csrf.key` loads into `AuthenticationSession.CSRF.Key` via the specified `AuthenticationSessionCSRF` struct and binds to the specified env var. The only unstated detail, the parent field name `CSRF`, follows directly from Go initialism convention and the given struct name.
  - gpt61: The shown graded assertion checks the explicitly required configuration mapping through the declared CSRF configuration type, using the conventional CSRF member name; the unspecified cookie-name assertion is outside the listed graded tests.
- `pro/instance_future-architect__vuls-aaea15e516ece43978cf98e09e52080478b1d39f` [pro_narrow_original] scores={'claude': 2, 'gpt61': 1} final=1
  - claude: The only test change is calling `searchCache` with the map by value instead of a pointer, which the spec states directly, and TestRemoveInactive only needs the package to compile with its existing, spec-consistent filtering.
  - gpt61: The changed call passes the cache map directly to searchCache, exactly matching the explicit requirement to eliminate pointer indirection while preserving value and existence results.
- `pro/instance_internetarchive__openlibrary-3c48b4bb782189e0858e6c3fc7956046cf3e1cfb-v2d9a6c849c60ed19fd0858ce9e40b7cc8e097e59` [pro_narrow_original] scores={'claude': 2, 'gpt61': 3} final=2
  - claude: The tests only check that the parsed `languages` include all 041 languages, with the 008 language first and no duplicates, which the spec states directly. It even gives the expected `["eng", "wel"]` for equalsign_title.mrc.
  - gpt61: The German/Latin expectations require German before Latin, although the specification does not establish that ordering. A correct merge that returns ['lat', 'ger'], for example through set-based deduplication, would fail those expectations despite retaining both languages.
- `pro/instance_internetarchive__openlibrary-798055d1a19b8fa0983153b709f460be97e33064-v13642507b4fc1f8d234172bf8129942da2c2ca26` [pro_narrow_original] scores={'claude': 2, 'gpt61': 3} final=2
  - claude: The exact-dict assertion matches the spec's enumerated fields and values: publishers, the 'eng' language, the four-character year, the standard_ebooks ID format, the first-content description and the first image-rel https cover. The remaining details, such as ID normalization, come from the existing map_data logic, so every reasonable fix passes.
  - gpt61: A correct fix could alphabetically sort the subject terms, since the specification requires their inclusion but does not require feed order. The test rejects that fix by comparing the subjects list in its exact original order.
- `pro/instance_internetarchive__openlibrary-dbbd9d539c6d4fd45d5be9662aa19b6d664b5137-v08d8e8889ec945ab821fb156c04c7d2e2810debb` [pro_narrow_original] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The graded assertion is that from_input builds the record solely from the urlencoded body (key, name 'foo data', unflattened seeds list), which directly matches the requirements that the body take exclusive precedence and that seeds unflatten into a list.
  - gpt61: A correct fix using web.input(_method='post') to isolate submitted form fields would fail because the test makes every web.input call return the conflicting dictionary. The test therefore requires a particular data-access path rather than merely correct body precedence and seed reconstruction.
- `pro/instance_qutebrowser__qutebrowser-3d01c201b8aa54dd71d4f801b1dd12feb4c0a08a-v5fc38aaf22415ab0b70567368332beee7955b367` [pro_narrow_original] scores={'claude': 2, 'gpt61': 1} final=1
  - claude: Every reasonable fix passes because the graded assertions map directly to the stated requirements: `_glob` yields only the immediate `.html` files as relative POSIX paths (the spec's own example lists), and `read_file` serves from the preloaded cache without calling the existing loader.
  - gpt61: The glob assertions reproduce the explicitly required paths and filtering, while the cache assertion directly verifies the specified absence of loader calls after preloading.

## False flags on fine tasks (4)

- `verified/sphinx-doc__sphinx-10466` [agent_consensus] scores={'claude': 3, 'gpt61': 3} final=3
  - claude: The test asserts `msg1.locations` equals an exact ordered list. A fix that deduplicates with `list(set(locations))`, exactly as the issue proposes, produces an arbitrary order and fails. The fix needs to deduplicate while preserving a deterministic order: insertion order or `sorted(set(...))`.
  - gpt61: The test requires unique locations in first-occurrence order, although the specification only requires removing duplicates. The specification's own list(set(locations)) solution can fix the bug while failing that exact-order assertion.
- `verified/matplotlib__matplotlib-22865` [agent_consensus] scores={'claude': 3, 'gpt61': 4} final=3
  - claude: The tests pin the exact set of divider segments: no line at the non-extended end for 'min' and 'max', and every edge drawn inside `cbar.dividers`. A correct fix that adds dividers at both ends whenever extended, or that draws the extremity edges on the extend patches instead of the dividers LineCollection, renders correctly but fails the assertions.
  - gpt61: A correct fix could render the missing extension separators with separate artists while leaving cbar.dividers unchanged. The tests would reject it because they require the new edges to appear in that particular collection, with exact segment arrays and ordering.
- `verified/django__django-16899` [agent_consensus] scores={'claude': 3, 'gpt61': 3} final=3
  - claude: The tests demand the exact string "The value of 'readonly_fields[N]' refers to '<name>', which is not a callable, an attribute of ..., or an attribute of ...". A fix that includes the field name with other wording, e.g. "readonly_fields[0] ('i_dont_exist') is not a callable...", would fail the equality check.
  - gpt61: A correct fix could include the offending name parenthetically after readonly_fields[index], rather than use the exact “refers to '<name>', which is not” construction. Both tests would reject that clear diagnostic solely because its wording differs.
- `verified/scikit-learn__scikit-learn-10297` [agent_consensus] scores={'claude': 3, 'gpt61': 3} final=3
  - claude: The test requires `cv_values_` to have shape (n_samples, 1, n_alphas) for a 1-D binary y. A fix that follows the spec's quoted documentation, which gives `[n_samples, n_alphas]` for single-target y, and squeezes the singleton target axis would fail.
  - gpt61: A correct fix could return `cv_values_` with shape `(5, 3)` for the 1-D binary target, consistent with the documented two-dimensional form. The test instead requires `(5, 1, 3)`, choosing a singleton target axis that the specification does not mandate.

## Uncertain tasks (reported separately) (13)

- `verified/django__django-17084` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: Any correct fix must wrap the window-containing annotation in a subquery and aggregate in the outer query. That necessarily yields one query with two SELECTs and the asserted correct values, so every reasonable fix passes.
  - gpt61: A correct fix could use separate derived-table layers for window evaluation and annotation projection before the final aggregate. It would return the expected totals in one query but fail the requirement that the generated SQL contain exactly two SELECTs.
- `verified/matplotlib__matplotlib-25311` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: Any correct fix must keep the unpicklable GUI canvas out of the pickled draggable-legend state, which is exactly what the `FigureCanvasAgg not in genops(pkl)` assertion checks under the Agg backend.
  - gpt61: A correct fix could make canvas references safely serializable using an Agg replacement and reconnect them on loading. Such a fix could successfully pickle and restore draggable figures but fail the test solely because its pickle stream references FigureCanvasAgg.
- `verified/matplotlib__matplotlib-22719` [agent_consensus] scores={'claude': 1, 'gpt61': 3} final=1
  - claude: The test runs the specification's reproduction verbatim and only requires that plotting empty data on category axes emits no deprecation warning, which is what the issue reports as the bug.
  - gpt61: The test requires the reproduction to run without a deprecation warning, but the specification also permits a more accurate, actionable diagnostic. A fix that emits a dedicated empty-data deprecation warning could satisfy that alternative while still failing the smoke test.
- `verified/sphinx-doc__sphinx-9320` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The test simply answers the existing-conf.py prompt with an empty string and asserts that `ask_user` raises `SystemExit`, which is exactly the spec's expected behavior that pressing Enter exits.
  - gpt61: A correct fix could return a cancellation result from ask_user and have the CLI caller terminate normally. That resolves the reported behavior but fails the test because it requires SystemExit from ask_user itself.
- `verified/sphinx-doc__sphinx-8551` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The issue asks that :type:/:rtype: xrefs look names up the same way explicit py roles do. The test checks the same context attributes that explicit roles already attach and that resolve_xref already consumes: py:module and py:class on the pending_xref. Any reasonable fix therefore produces them.
  - gpt61: A correct fix could obtain scope from the enclosing Python description during reference resolution instead of attaching it to every pending reference during parsing. The test would reject that fix because it requires exact py:module and py:class attributes on the unresolved nodes, despite correct final links and no ambiguity warnings.
- `verified/sympy__sympy-17139` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The tests check that `simplify(cos(x)**I)` (the reported example) and related complex exponents come back unchanged without crashing, and that `_TR56`, the exact function in the traceback, leaves complex-exponent powers unchanged, which any fix at the identified site does.
  - gpt61: The tests require the private _TR56 helper itself to accept complex exponents. A correct fix that protects complex powers in the public transformation wrappers would make simplify work but still fail the direct helper assertions.
- `verified/pytest-dev__pytest-5787` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The tests check that a JSON round trip through the existing `_to_json`/`_from_json` methods preserves the existing `ExceptionChainRepr` structure (both chain entries and their descriptions), which is exactly what "serialization should include chained exceptions" asks for.
  - gpt61: A correct fix could preserve the complete formatted exception chain in a terminal-renderable longrepr without reconstructing an ExceptionChainRepr object. It would resolve the reported output loss but fail the tests' required internal type and .chain tuple structure after deserialization.
- `verified/django__django-16116` [agent_consensus] scores={'claude': 1, 'gpt61': 3} final=1
  - claude: The test asserts SystemExit and that no migration files are written, which is exactly what the spec requests ('makemigrations --check should just exit without making migrations').
  - gpt61: A fix could suppress migration-file writes while leaving an empty migration directory created during output preparation. The test rejects that fix because it requires the directory itself to be absent, rather than merely requiring that no migrations were created.
- `verified/django__django-13315` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The tests only check that formfield querysets under join-based `limit_choices_to` (Q or dict, FK or M2M) contain each matching object once, order-independently, and any correct dedup fix in the shared limit-choices path passes.
  - gpt61: A reasonable fix could deduplicate choices during ModelChoiceIterator iteration without replacing the field's underlying queryset. The form would no longer render duplicate options, but the tests would fail because they inspect queryset contents rather than generated choices.
- `verified/scikit-learn__scikit-learn-13142` [agent_consensus] scores={'claude': 1, 'gpt61': 4} final=1
  - claude: The graded tests are essentially the issue's reproduction with a fixed seed, asserting fit_predict(X) equals predict(X) when n_init>1, which every correct fix satisfies.
  - gpt61: A correct GaussianMixture-specific fix could make fit_predict(X) agree with predict(X) for all initialization counts while leaving BayesianGaussianMixture unchanged. The graded Bayesian test rejects that fix even though the specification never requests a change to that estimator.
- `verified/sphinx-doc__sphinx-10323` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The spec explicitly asks that dedent apply only to the included lines and not to prepend/append, and the test asserts exactly that through the existing LiteralIncludeReader.read() path.
  - gpt61: A correct fix could preserve leading whitespace in prepend/append during directive-option processing while leaving LiteralIncludeReader's dedent behavior unchanged. The test bypasses directive processing and requires the reader itself to exclude prepend/append from dedent, rejecting that alternative.
- `verified/django__django-15572` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The test checks that the empty-string DIRS entry is no longer normalized into a watched directory by get_template_directories(), the existing function the spec identifies as doing the normalization. Any reasonable fix that drops empty entries passes.
  - gpt61: A correct fix could exclude empty configured directories in template_changed()'s matching path while leaving the directory-collection helper unchanged. It would fix application autoreloading but fail the test's direct requirement that get_template_directories() return an empty set.
- `pro/instance_internetarchive__openlibrary-dbbd9d539c6d4fd45d5be9662aa19b6d664b5137-v08d8e8889ec945ab821fb156c04c7d2e2810debb` [pro_narrow_original] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The graded assertion is that from_input builds the record solely from the urlencoded body (key, name 'foo data', unflattened seeds list), which directly matches the requirements that the body take exclusive precedence and that seeds unflatten into a list.
  - gpt61: A correct fix using web.input(_method='post') to isolate submitted form fields would fail because the test makes every web.input call return the conflicting dictionary. The test therefore requires a particular data-access path rather than merely correct body precedence and seed reconstruction.
