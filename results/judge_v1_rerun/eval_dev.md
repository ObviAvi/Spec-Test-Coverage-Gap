# STCG judge evaluation: `judge_v1_rerun` on `dev`

- tasks: 138, judged: 138, judged by all judges: 138
- errors per judge: {'claude': 0, 'gpt61': 0}

## Targets (ensemble, all tasks)

- recall on overspecified: 80% (target >= 70%)
- false-flag rate on fine: 5% (target <= 15%)
- **MET**

## Detection

| scorer | group | recall | false-flag rate |
|---|---|---|---|
| claude | all | 81% (61/75, CI 71%-89%) | 5% (3/63, CI 2%-13%) |
| claude | source:agent_consensus | - | 5% (3/63, CI 2%-13%) |
| claude | source:openai_excluded | 89% (40/45, CI 77%-95%) | - |
| claude | source:pro_narrow_original | 70% (21/30, CI 52%-83%) | - |
| gpt61 | all | 88% (66/75, CI 79%-94%) | 19% (12/63, CI 11%-30%) |
| gpt61 | source:agent_consensus | - | 19% (12/63, CI 11%-30%) |
| gpt61 | source:openai_excluded | 91% (41/45, CI 79%-96%) | - |
| gpt61 | source:pro_narrow_original | 83% (25/30, CI 66%-93%) | - |
| ensemble | all | 80% (60/75, CI 70%-87%) | 5% (3/63, CI 2%-13%) |
| ensemble | source:agent_consensus | - | 5% (3/63, CI 2%-13%) |
| ensemble | source:openai_excluded | 89% (40/45, CI 77%-95%) | - |
| ensemble | source:pro_narrow_original | 67% (20/30, CI 49%-81%) | - |
| ensemble_certain_only | all | 86% (60/70, CI 76%-92%) | 5% (3/56, CI 2%-15%) |
| ensemble_certain_only | source:agent_consensus | - | 5% (3/56, CI 2%-15%) |
| ensemble_certain_only | source:openai_excluded | 89% (40/45, CI 77%-95%) | - |
| ensemble_certain_only | source:pro_narrow_original | 80% (20/25, CI 61%-91%) | - |

## Inter-judge agreement

- Fleiss' kappa on the flag (tasks judged by all): 0.768
- uncertain (spread >= 2): 9% (12/138, CI 5%-15%)

| pair | n | Cohen's kappa | agree |
|---|---|---|---|
| claude~gpt61 | 138 | 0.770 | 88% |

## Missed overspecified tasks (15)

- `full/django__django-13199` [openai_excluded] scores={'claude': 2, 'gpt61': 3} final=2
  - claude: Every reasonable fix passes because it adds a `samesite` parameter to delete_cookie (mirroring set_cookie) and passes SESSION_COOKIE_SAMESITE from the messages storage and session middleware, the internal callers whose cookies carry that setting. That is exactly what `test_delete_cookie_samesite`, `test_cookie_setings` and the session delete tests assert.
  - gpt61: A correct fix could normalize SameSite values to canonical capitalization, emitting 'Lax' for an input of 'lax'. The deletion would preserve the cookie's SameSite policy, but test_delete_cookie_samesite would reject it because it requires the exact lowercase spelling.
- `full/django__django-16786` [openai_excluded] scores={'claude': 2, 'gpt61': 2} final=2
  - claude: The tests only check that querysets with FilteredRelation conditions referencing joined fields (directly, via another filtered relation, or via the relation path itself) return the correct rows, which is exactly the behavior the issue says is broken.
  - gpt61: The assertions extend the reported missing-JOIN problem to closely related FilteredRelation conditions and check only the resulting records, without prescribing how join dependencies are resolved.
- `full/pydata__xarray-4994` [openai_excluded] scores={'claude': 2, 'gpt61': 1} final=1
  - claude: The graded test only checks that `da.time.dt.date` equals pandas' `DatetimeIndex.date` (object array of `datetime.date`), which is exactly what the issue requests and suggests implementing.
  - gpt61: The graded `test_field_access[date]` directly checks the requested `.dt.date` functionality; it does not grade the additional, unspecified CFTime error wording.
- `full/scikit-learn__scikit-learn-13253` [openai_excluded] scores={'claude': 2, 'gpt61': 1} final=1
  - claude: The graded assertion that each `categories_[i].dtype` matches its DataFrame column's dtype (int, object, float) is exactly the per-column dtype preservation the issue asks for, so every reasonable fix passes.
  - gpt61: The graded test directly checks the requested preservation of integer, object-string, and float column dtypes in categories_, while retaining the existing one-hot encoding behavior.
- `full/sympy__sympy-12906` [openai_excluded] scores={'claude': 2, 'gpt61': 2} final=2
  - claude: The test checks only properties of a canonical form: idempotency (stated in the issue), reversal invariance and Number-on-rhs (both already enforced by existing tests). It never pins a specific output form, so any correct canonicalization fix passes.
  - gpt61: The graded assertions directly check the reported idempotence failure on related inputs, supplemented by reversal consistency and number placement supported by the existing canonicalization tests.
- `pro/instance_element-hq__element-web-71fe08ea0f159ccb707904d87f0a4aef205a167c-vnan` [pro_narrow_original] scores={'claude': 2, 'gpt61': 1} final=1
  - claude: Every asserted string ("Profile picture" aria-label, the reworded settings labels, and the encryption-event sentence) is spelled out in the requirements or is a direct substitution of "avatar" with "profile picture" in existing text.
  - gpt61: The graded changes directly check the requested terminology substitutions and the explicitly specified “Profile picture” accessible name for MemberAvatar buttons.
- `pro/instance_element-hq__element-web-7c63d52500e145d6fff6de41dd717f61ab88d02f-vnan` [pro_narrow_original] scores={'claude': 2, 'gpt61': 1} final=1
  - claude: The tests assert the spec-named class `mx_WysiwygComposer_Editor_content_placeholder` toggling on the editor's content element based on emptiness, driven by the spec-named `placeholder` prop, which is exactly what the requirements describe.
  - gpt61: The graded assertions directly check the explicitly required CSS class as content changes from empty to nonempty and back, in both required composer modes.
- `pro/instance_flipt-io__flipt-02e21636c58e86c51119b63e0fb5ca7b813b07b1` [pro_narrow_original] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The tests check the behaviors the spec spells out: `InsecureSkipVerify` mirrors `insecure_skip_tls`, `RootCAs` is set only when a CA is given, a missing CA file errors, and validation fails with the exact quoted message. The Go field names (`CaCertBytes`, `CaCertPath`, `InsecureSkipTLS`) follow the repo's existing Git storage config convention for the same yaml keys.
  - gpt61: A correct implementation could name the Go fields CACertPath and CACertBytes while mapping them to the required ca_cert_path and ca_cert_bytes configuration keys. The tests instead require CaCertPath and CaCertBytes, causing that implementation to fail compilation despite satisfying the specification.
- `pro/instance_future-architect__vuls-83bcca6e669ba2e4102f26c4a2b52f78c7861f1a` [pro_narrow_original] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The spec gives exact method names and signatures, requires non-nil empty slices, deduplication, deterministic ordering (sorted or host-IP order, which coincide in the tests), wildcard expansion and IPv6 bracket preservation, so every assertion follows directly from the stated requirements.
  - gpt61: A correct parser that initializes PortScanSuccessOn to []string{} fails the parsing tests because their whole-struct comparisons require nil at this intermediate stage. The wildcard fixtures also reject an implementation that checks successful addresses against ServerInfo.IPv4Addrs, because they require matches without configuring any host addresses.
- `pro/instance_gravitational__teleport-dd3977957a67bedaf604ad6ca255ba8c7b6704e9` [pro_narrow_original] scores={'claude': 3, 'gpt61': 1} final=1
  - claude: The test compares the full ordered principals slice and expects localhost, 127.0.0.1 and ::1 exactly between the proxy public addresses and `reversetunnel.LocalKubernetes`. A correct fix that appends the loopback principals elsewhere in the list (for example at the end) would fail, even though principal order is not semantically meaningful.
  - gpt61: The added expectations require the three loopback principals that the specification explicitly says getAdditionalPrincipals must include for proxies.
- `pro/instance_internetarchive__openlibrary-a48fd6ba9482c527602bc081491d9e8ae6e8226c-vfa6ff903cb27f336e17654595dd900fa943dcd91` [pro_narrow_original] scores={'claude': 2, 'gpt61': 3} final=2
  - claude: The tests call the spec-named `process_facet` with the spec-described (value, count) tuples, and the true-first, yes/no output matches existing read_facets behaviour. The get_doc assertion checks that the output shape is preserved when the input switches from XML to a JSON dict, which any faithful refactor does.
  - gpt61: A reasonable fix could parse the required JSON fields correctly but represent an absent optional subtitle as an empty string instead of None. test_get_doc rejects that choice through whole-document equality, although the specification never fixes this missing-field default.
- `pro/instance_navidrome__navidrome-3982ba725883e71d4e3e618c61d5140eeb8d850a` [pro_narrow_original] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The graded tests only use what the spec names: package-level `Backup`/`Restore`/`Prune`, `db.Db()` returning `*sql.DB`, and repositories built from a dbx wrapper over that single connection. The only other identifiers, `Dialect` and `Driver`, are pre-existing constants.
  - gpt61: A correct fix could make the individual repository constructors accept *sql.DB and perform dbx wrapping internally. The tests instead pass *dbx.DB directly into those constructors, rejecting that fix at compile time despite its satisfying the specified unified-connection API.
- `pro/instance_navidrome__navidrome-e12a14a87d392ac70ee4cc8079e3c3e0103dbcb2` [pro_narrow_original] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The tests assert that the metadata map has a "channels" key equal to "2" for stereo inputs and that Tags.Channels() returns 2. Both follow directly from the spec's mapping requirement, the named Channels method and "channels" column, and the existing lowercase key convention.
  - gpt61: The FFmpeg tests require channel extraction to be reflected in the private e.extractMetadata helper's return value. A correct implementation could instead enrich the metadata in the parser's public entry point, producing the required externally available channel count while failing these helper-level tests.
- `pro/instance_qutebrowser__qutebrowser-2e961080a85d660148937ee8f0f6b3445a8f2c01-v363c8a7e5ccdf6968fc7ab84a2053ac78036691d` [pro_narrow_original] scores={'claude': 2, 'gpt61': 1} final=1
  - claude: The tests check only presence or absence of `--disable-accelerated-2d-canvas` through the public `qt_args`, which maps directly onto the spec's always/never/auto rule (auto means Qt 6 with Chromium < 111).
  - gpt61: The graded assertions directly check the specified presence or absence of '--disable-accelerated-2d-canvas' for always, never, and version-dependent auto modes.
- `pro/instance_qutebrowser__qutebrowser-85b867fe8d4378c8e371f055c70452f546055854-v2ef375ac784985212b1805e1d0431dc8f1b3c171` [pro_narrow_original] scores={'claude': 2, 'gpt61': 1} final=1
  - claude: The graded tests check only that valid 'x,y' strings (including negatives) become QPoints and that arbitrary or huge-integer input raises nothing but ValueError, both of which the spec states explicitly.
  - gpt61: Every reasonable correct fix passes: the QPoint equality checks directly match the specified coordinate conversion, and the randomized tests permit the explicitly required ValueError handling without imposing exact messages.

## False flags on fine tasks (3)

- `verified/pydata__xarray-2905` [agent_consensus] scores={'claude': 3, 'gpt61': 4} final=3
  - claude: The test checks the `Variable(...)` constructor path, not the `__setitem__`/`.loc` assignment named in the issue. A fix scoped to `__setitem__` that leaves `as_compatible_data`'s generic `getattr(data, 'values', data)` unwrapping in place for construction would fix the reported bug but fail the test.
  - gpt61: A correct fix localized to object-dtype assignment in `Variable.__setitem__` could preserve arbitrary objects with `.values` while leaving direct Variable construction unchanged. It would fail the test, which requires the constructor to preserve such an object in private storage.
- `verified/django__django-11299` [agent_consensus] scores={'claude': 4, 'gpt61': 4} final=4
  - claude: The graded test inspects internal Query.build_where output, requiring nested lookups and a resolved F('id') rhs to be SimpleCol instances. A fix that corrects the CheckConstraint SQL another way (e.g. alias-free compilation in _get_check_sql) fails, as does a fix that doesn't make F() expressions resolve to SimpleCol.
  - gpt61: A correct fix could remove table qualification during CheckConstraint SQL compilation while leaving Query.build_where() column objects unchanged. The graded test would reject it because it requires those intermediate objects to be SimpleCol instances rather than checking that the generated constraint SQL works.
- `verified/scikit-learn__scikit-learn-14983` [agent_consensus] scores={'claude': 3, 'gpt61': 3} final=3
  - claude: The test requires the repr parameters in alphabetical order ('n_repeats=6, n_splits=2, random_state=None'), but the issue's expected output lists n_splits before n_repeats. A fix that produces exactly the repr shown in the issue fails the string comparison.
  - gpt61: A correct fix preserving the specification's demonstrated parameter order would produce 'RepeatedKFold(n_splits=2, n_repeats=6, random_state=None)' and the analogous stratified representation. Both tests reject these strings because they require n_repeats before n_splits.

## Uncertain tasks (reported separately) (12)

- `verified/django__django-14311` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The test asserts only that `get_child_arguments()` keeps the full dotted module name (`-m utils_tests.test_module.main_module`) when `__main__` is a non-package module, which is exactly the spec's requirement. Any natural fix building on the existing `__spec__`-based logic passes.
  - gpt61: A correct fix could use `sys.argv[0]` to distinguish package `__main__.py` execution from ordinary module execution. The test substitutes `main_module` as `__main__` but leaves argv pointing to the package's `__main__.py`, rejecting that reasonable implementation through inconsistent mocked interpreter state.
- `verified/sphinx-doc__sphinx-11445` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The tests check that prepend_prolog, the function that misplaces the prolog, no longer treats a ':mod:`foo`' title line as docinfo and puts the prolog at the top with the existing blank-line convention, which is the only reasonable correct output.
  - gpt61: The tests require an exact intermediate StringList representation from prepend_prolog. A correct fix that preserves the prolog's trailing blank line with '<rst_prolog>' provenance instead of replacing it with ('<generated>', 0, '') would render the heading and toctree correctly but fail the graded assertion.
- `verified/sphinx-doc__sphinx-10673` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: Any fix that accepts genindex/modindex/search as toctree items naturally keeps them in the toctree node's existing `entries` list as (None, docname), which is exactly what the test asserts.
  - gpt61: The test requires special-page entries to remain title-less tuples in a particular internal toctree node. A correct implementation that assigns generated-page titles during parsing would eliminate the reported warnings and produce working links, but fail the required entries=[(None, ...)] assertion.
- `verified/sphinx-doc__sphinx-7757` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The test runs the issue's exact signature through the existing parser that the py domain uses and checks that b keeps its default '0' (string form, as for other defaults) and that c keeps '1', which any root-cause fix produces.
  - gpt61: A correct fix in the Python directive's signature-processing/rendering path could display positional-only defaults without changing `inspect.signature_from_str`. The graded test bypasses that entry point and requires the utility's intermediate parameter defaults to be repaired.
- `verified/sphinx-doc__sphinx-8120` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: Every reasonable fix passes: the test checks that a user locale_dirs sphinx.po overrides the built-in translation (via the existing app.translator and the rendered HTML), which is exactly what the issue asks for, just with a different message ('Quick search').
  - gpt61: A correct fix could refresh translations at the start of app.build(), producing the requested custom captions and other translated HTML. It would nevertheless fail because the test requires app.translator to expose the override immediately after application construction.
- `verified/sympy__sympy-15345` [agent_consensus] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The assertion that Max and Min print as "Max[x, y, z]*Min[y, z]" maps directly to the spec's requested Max[...] syntax, extended to the obviously related Min. It uses existing separator and ordering conventions, so any reasonable fix produces this output.
  - gpt61: A reasonable fix could add correct Mathematica printing for Max alone, including arbitrary arguments and products, while leaving Min unchanged. The test additionally requires Min[y, z], covering a separate function not implicated by the specification.
- `verified/django__django-13807` [agent_consensus] scores={'claude': 1, 'gpt61': 3} final=1
  - claude: The test calls check_constraints(table_names=['order']) and expects IntegrityError, which directly matches the issue's described crash path; any fix that quotes the table names passes.
  - gpt61: A reasonable fix can quote table names in both PRAGMA statements without repairing keyword-column handling. The test also requires reserved primary-key and foreign-key column names to work during violation reporting, so that table-name fix can still raise a SQL syntax error instead of IntegrityError.
- `pro/instance_flipt-io__flipt-02e21636c58e86c51119b63e0fb5ca7b813b07b1` [pro_narrow_original] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The tests check the behaviors the spec spells out: `InsecureSkipVerify` mirrors `insecure_skip_tls`, `RootCAs` is set only when a CA is given, a missing CA file errors, and validation fails with the exact quoted message. The Go field names (`CaCertBytes`, `CaCertPath`, `InsecureSkipTLS`) follow the repo's existing Git storage config convention for the same yaml keys.
  - gpt61: A correct implementation could name the Go fields CACertPath and CACertBytes while mapping them to the required ca_cert_path and ca_cert_bytes configuration keys. The tests instead require CaCertPath and CaCertBytes, causing that implementation to fail compilation despite satisfying the specification.
- `pro/instance_future-architect__vuls-83bcca6e669ba2e4102f26c4a2b52f78c7861f1a` [pro_narrow_original] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The spec gives exact method names and signatures, requires non-nil empty slices, deduplication, deterministic ordering (sorted or host-IP order, which coincide in the tests), wildcard expansion and IPv6 bracket preservation, so every assertion follows directly from the stated requirements.
  - gpt61: A correct parser that initializes PortScanSuccessOn to []string{} fails the parsing tests because their whole-struct comparisons require nil at this intermediate stage. The wildcard fixtures also reject an implementation that checks successful addresses against ServerInfo.IPv4Addrs, because they require matches without configuring any host addresses.
- `pro/instance_gravitational__teleport-dd3977957a67bedaf604ad6ca255ba8c7b6704e9` [pro_narrow_original] scores={'claude': 3, 'gpt61': 1} final=1
  - claude: The test compares the full ordered principals slice and expects localhost, 127.0.0.1 and ::1 exactly between the proxy public addresses and `reversetunnel.LocalKubernetes`. A correct fix that appends the loopback principals elsewhere in the list (for example at the end) would fail, even though principal order is not semantically meaningful.
  - gpt61: The added expectations require the three loopback principals that the specification explicitly says getAdditionalPrincipals must include for proxies.
- `pro/instance_navidrome__navidrome-3982ba725883e71d4e3e618c61d5140eeb8d850a` [pro_narrow_original] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The graded tests only use what the spec names: package-level `Backup`/`Restore`/`Prune`, `db.Db()` returning `*sql.DB`, and repositories built from a dbx wrapper over that single connection. The only other identifiers, `Dialect` and `Driver`, are pre-existing constants.
  - gpt61: A correct fix could make the individual repository constructors accept *sql.DB and perform dbx wrapping internally. The tests instead pass *dbx.DB directly into those constructors, rejecting that fix at compile time despite its satisfying the specified unified-connection API.
- `pro/instance_navidrome__navidrome-e12a14a87d392ac70ee4cc8079e3c3e0103dbcb2` [pro_narrow_original] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The tests assert that the metadata map has a "channels" key equal to "2" for stereo inputs and that Tags.Channels() returns 2. Both follow directly from the spec's mapping requirement, the named Channels method and "channels" column, and the existing lowercase key convention.
  - gpt61: The FFmpeg tests require channel extraction to be reflected in the private e.extractMetadata helper's return value. A correct implementation could instead enrich the metadata in the parser's public entry point, producing the required externally available channel count while failing these helper-level tests.
