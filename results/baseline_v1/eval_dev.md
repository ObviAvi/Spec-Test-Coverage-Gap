# STCG judge evaluation: `baseline_v1` on `dev`

- tasks: 138, judged: 138, judged by all judges: 138
- errors per judge: {'claude': 0, 'gpt61': 0}

## Targets (ensemble, all tasks)

- recall on overspecified: 72% (target >= 70%)
- false-flag rate on fine: 6% (target <= 15%)
- **MET**

## Detection

| scorer | group | recall | false-flag rate |
|---|---|---|---|
| claude | all | 81% (61/75, CI 71%-89%) | 6% (4/63, CI 2%-15%) |
| claude | source:agent_consensus | - | 6% (4/63, CI 2%-15%) |
| claude | source:openai_excluded | 89% (40/45, CI 77%-95%) | - |
| claude | source:pro_narrow_original | 70% (21/30, CI 52%-83%) | - |
| gpt61 | all | 77% (58/75, CI 67%-85%) | 13% (8/63, CI 7%-23%) |
| gpt61 | source:agent_consensus | - | 13% (8/63, CI 7%-23%) |
| gpt61 | source:openai_excluded | 84% (38/45, CI 71%-92%) | - |
| gpt61 | source:pro_narrow_original | 67% (20/30, CI 49%-81%) | - |
| ensemble | all | 72% (54/75, CI 61%-81%) | 6% (4/63, CI 2%-15%) |
| ensemble | source:agent_consensus | - | 6% (4/63, CI 2%-15%) |
| ensemble | source:openai_excluded | 84% (38/45, CI 71%-92%) | - |
| ensemble | source:pro_narrow_original | 53% (16/30, CI 36%-70%) | - |
| ensemble_certain_only | all | 76% (54/71, CI 65%-84%) | 6% (4/63, CI 2%-15%) |
| ensemble_certain_only | source:agent_consensus | - | 6% (4/63, CI 2%-15%) |
| ensemble_certain_only | source:openai_excluded | 86% (38/44, CI 73%-94%) | - |
| ensemble_certain_only | source:pro_narrow_original | 59% (16/27, CI 41%-75%) | - |

## Inter-judge agreement

- Fleiss' kappa on the flag (tasks judged by all): 0.782
- uncertain (spread >= 2): 3% (4/138, CI 1%-7%)

| pair | n | Cohen's kappa | agree |
|---|---|---|---|
| claude~gpt61 | 138 | 0.782 | 89% |

## Missed overspecified tasks (21)

- `full/django__django-13199` [openai_excluded] scores={'claude': 2, 'gpt61': 2} final=2
  - claude: The tests use the natural `samesite` keyword that matches set_cookie and check SameSite on deleted session and messages cookies, which is what the issue asks for. Only the exact-string session assertions would reject a broader fix that also forwards httponly or secure.
  - gpt61: The tests reasonably translate the reported problem into API and integration behavior. They do not require a particular internal implementation or introduce unrelated requirements.
- `full/django__django-13447` [openai_excluded] scores={'claude': 3, 'gpt61': 1} final=1
  - claude: The test hardcodes the dictionary key 'model', which the issue never states; a correct fix using a different key such as 'model_class' would fail.
  - gpt61: The tests directly check that app-list entries include their model classes, as requested. They impose no unnecessary implementation details.
- `full/django__django-16786` [openai_excluded] scores={'claude': 2, 'gpt61': 2} final=2
  - claude: The tests check only query results for FilteredRelation conditions that span joins, plus natural chained and self-reference edge cases that a proper fix should handle. They do not depend on implementation details.
  - gpt61: The tests reasonably extend the reported JOIN and alias-resolution bug to related valid query patterns. They verify results without constraining how a correct fix resolves conditions or constructs SQL.
- `full/pydata__xarray-4994` [openai_excluded] scores={'claude': 1, 'gpt61': 1} final=1
  - claude: The graded test only checks that `.dt.date` returns the same values as pandas' `DatetimeIndex.date`, which is exactly what the issue asks for. The only implementation-specific test (the cftime error message) is not graded.
  - gpt61: The graded test directly checks the requested .dt.date functionality using the existing field-access test framework. It does not impose an implementation-specific requirement.
- `full/scikit-learn__scikit-learn-13253` [openai_excluded] scores={'claude': 2, 'gpt61': 1} final=1
  - claude: The test checks that per-column dtypes are preserved in `categories_` for a mixed-dtype DataFrame, which is exactly the behaviour the issue describes, so any correct column-wise implementation passes.
  - gpt61: The dtype assertions directly test the requested per-column dtype preservation, and the output assertions verify ordinary encoding correctness. They do not impose requirements beyond the specification.
- `full/sympy__sympy-12906` [openai_excluded] scores={'claude': 2, 'gpt61': 2} final=2
  - claude: The graded test checks idempotence (the stated issue) plus reversal invariance and the numbers-on-rhs convention. These are implied by the meaning of a canonical form and by existing behaviour, not by the specific implementation.
  - gpt61: The tests reasonably generalize the requested idempotence fix using standard canonicalization invariants. They leave room for alternative implementations rather than requiring the original fix's precise output.
- `full/sympy__sympy-16334` [openai_excluded] scores={'claude': 3, 'gpt61': 2} final=2
  - claude: The tests require extra behaviors not stated in the issue: symbolic `0**0` being positive, and `is_negative` being `False`. A fix that correctly handles only the reported nonzero-exponent `is_positive` case could fail.
  - gpt61: The tests extend beyond the exact reproducer with reasonable sign and zero-exponent regression coverage. They do not impose implementation-specific requirements or reject a correct alternative fix.
- `pro/instance_element-hq__element-web-71fe08ea0f159ccb707904d87f0a4aef205a167c-vnan` [pro_narrow_original] scores={'claude': 1, 'gpt61': 1} final=1
  - claude: Every assertion checks a user-facing string or aria-label that the requirements spell out (a direct avatar-to-profile-picture substitution, or MemberAvatar's "Profile picture" ariaLabel), so a correct fix would not be rejected.
  - gpt61: The tested text and accessibility-label changes directly follow the requirements. The tests do not impose additional implementation choices beyond the requested behavior.
- `pro/instance_element-hq__element-web-7c63d52500e145d6fff6de41dd717f61ab88d02f-vnan` [pro_narrow_original] scores={'claude': 2, 'gpt61': 1} final=1
  - claude: The spec gives the exact class name and prop. Tests check the class on the textbox element, which the class name strongly implies but the spec does not state outright.
  - gpt61: The assertions directly match the specified placeholder behavior and explicitly required CSS class in both composer modes. They do not constrain a correct fix to an otherwise unspecified implementation.
- `pro/instance_flipt-io__flipt-02e21636c58e86c51119b63e0fb5ca7b813b07b1` [pro_narrow_original] scores={'claude': 3, 'gpt61': 1} final=1
  - claude: The tests depend on the Go struct field names `CaCertBytes`, `CaCertPath` and `InsecureSkipTLS`, which the spec never states (it gives only YAML keys). An idiomatic alternative such as `CACertPath` would fail to compile.
  - gpt61: The shown assertions align with explicitly required TLS and configuration behavior. They do not impose additional behavior or an arbitrary implementation strategy.
- `pro/instance_future-architect__vuls-030b2e03525d68d74cb749959aac2d7f3fc0effa` [pro_narrow_original] scores={'claude': 3, 'gpt61': 2} final=2
  - claude: The tests demand an exact list of KB numbers up to a specific (October 2024) cutoff that the spec never states. Valid updates with a different but legitimate cutoff, more or fewer recent KBs, would fail.
  - gpt61: The tests reasonably concretize the requested up-to-date mappings using specific KB identifiers and preserve existing classification behavior. There is no evident additional restriction that would reject an otherwise correct fix for the intended release snapshot.
- `pro/instance_future-architect__vuls-83bcca6e669ba2e4102f26c4a2b52f78c7861f1a` [pro_narrow_original] scores={'claude': 2, 'gpt61': 3} final=2
  - claude: The tests closely follow the detailed spec (signatures, empty-slice semantics, ordering, wildcard and IPv6 handling). Minor ambiguities remain: DeepEqual on nil vs empty slices, and asterisk matching that ignores IPv4Addrs when base has none.
  - gpt61: The tests are mostly directly specified, but impose an unnecessary nil-slice representation on parsed endpoints and assume wildcard matching need not consult host IPv4 addresses. These assertions can reject otherwise compliant implementations.
- `pro/instance_future-architect__vuls-fd18df1dd4e4360f8932bc4b894bd8b40d654e7c` [pro_narrow_original] scores={'claude': 3, 'gpt61': 2} final=2
  - claude: Most assertions follow from the spec, but the library-only scan's ServerName must change from the existing "library scan by trivy" to the filesystem artifact name, which the spec never requires. A reasonable fix that keeps the placeholder would fail.
  - gpt61: The expectations closely follow the metadata requirements. Artifact-based ServerName values are reasonably implied, though not completely explicit for non-container scans.
- `pro/instance_gravitational__teleport-87a593518b6ce94624f6c28516ce38cc30cbea5a` [pro_narrow_original] scores={'claude': 3, 'gpt61': 2} final=2
  - claude: The error-classification tests use specific unstated error strings, such as an "i/o timeout" counting as connection refused and "authentication failed" counting as an invalid user, as plain errors. Valid implementations that check mssql error numbers or other reasonable substrings would be rejected.
  - gpt61: The tests reasonably instantiate the required connectivity and error-categorization behavior using representative SQL Server messages and a test server. They impose no material implementation constraints beyond the specified public interface.
- `pro/instance_gravitational__teleport-dd3977957a67bedaf604ad6ca255ba8c7b6704e9` [pro_narrow_original] scores={'claude': 3, 'gpt61': 1} final=1
  - claude: The values required (localhost, 127.0.0.1, ::1) are clearly specified. If the comparison is order-sensitive, as I recall, the test also requires them at a specific position (before LocalKubernetes), which the spec never states.
  - gpt61: The added expectations directly test the explicitly requested loopback principals and introduce no demonstrated implementation-specific requirements.
- `pro/instance_internetarchive__openlibrary-9bdfd29fac883e77dcbc4208cab28c06fd963ab2-v76304ecdb3a5954fcf13feb710e8c40fcf24b73c` [pro_narrow_original] scores={'claude': 2, 'gpt61': 3} final=2
  - claude: The exact-string assertions encode a natural Solr serialization: parentheses only around multi-word values, aliases mapped, and operators preserved. This is mostly derivable from the requirements and existing code conventions, though a few formatting details are implicit.
  - gpt61: The tests mostly check the requested behavior, but exact serialization rejects semantically equivalent grouping. They also retain an automatic LCC wildcard convention that the specification does not explicitly require.
- `pro/instance_internetarchive__openlibrary-e1e502986a3b003899a8347ac8a7ff7b08cbfc39-v08d8e8889ec945ab821fb156c04c7d2e2810debb` [pro_narrow_original] scores={'claude': 2, 'gpt61': 3} final=2
  - claude: The exact markdown strings are mostly dictated by the requirements (stars, single space, `" | "` delimiter, JSON fourth segment); only small choices like default `json.dumps` spacing are left implicit, and they are the natural default.
  - gpt61: The tests are mildly overspecified because they require a particular JSON whitespace format, although the specification only requires valid JSON serialization. The remaining assertions directly reflect the requirements.
- `pro/instance_navidrome__navidrome-3982ba725883e71d4e3e618c61d5140eeb8d850a` [pro_narrow_original] scores={'claude': 1, 'gpt61': 3} final=1
  - claude: Every symbol the tests rely on (`Backup`, `Restore`, `Prune`, `Db()` returning `*sql.DB`) is stated in the requirements, and the dbx builder helper is defined inside the test files themselves.
  - gpt61: Most changes directly test the requested API simplification, but the persistence tests additionally constrain repository constructor arguments to a particular dbx-based design. This can reject otherwise correct implementations using *sql.DB directly throughout the repositories.
- `pro/instance_navidrome__navidrome-e12a14a87d392ac70ee4cc8079e3c3e0103dbcb2` [pro_narrow_original] scores={'claude': 2, 'gpt61': 1} final=1
  - claude: The tests check the described behaviour; the only unstated detail is the metadata map key name "channels", which is strongly implied by codebase conventions, the column name and the method name.
  - gpt61: The assertions directly exercise the requested behavior using the existing metadata representation. They do not constrain implementation choices beyond the required APIs and observable results.
- `pro/instance_qutebrowser__qutebrowser-2e961080a85d660148937ee8f0f6b3445a8f2c01-v363c8a7e5ccdf6968fc7ab84a2053ac78036691d` [pro_narrow_original] scores={'claude': 1, 'gpt61': 1} final=1
  - claude: The test checks only whether the flag appears in `qt_args` output across the spec's version/value combinations, which any correct implementation would satisfy.
  - gpt61: The tests directly exercise the requested configuration modes and version-dependent flag behavior without imposing an additional implementation requirement.
- `pro/instance_qutebrowser__qutebrowser-85b867fe8d4378c8e371f055c70452f546055854-v2ef375ac784985212b1805e1d0431dc8f1b3c171` [pro_narrow_original] scores={'claude': 1, 'gpt61': 1} final=1
  - claude: The graded tests only check correct QPoint output for valid input and that only ValueError is raised for arbitrary or overflowing input, both stated directly in the requirements. The exact-message test is not among the graded tests.
  - gpt61: The graded tests check explicitly required parsing behavior and resistance to crashes without prescribing an implementation or exact error wording.

## False flags on fine tasks (4)

- `verified/pydata__xarray-2905` [agent_consensus] scores={'claude': 3, 'gpt61': 3} final=3
  - claude: The test checks the `Variable` constructor rather than the `__setitem__` path described in the issue, so a valid fix confined to `__setitem__` would fail, although the natural fix in the shared `as_compatible_data` passes.
  - gpt61: The test imposes object-preservation behavior on Variable construction, whereas the specification concerns assignment into object-dtype arrays. An assignment-specific fix could satisfy the issue without passing this constructor test.
- `verified/django__django-11299` [agent_consensus] scores={'claude': 3, 'gpt61': 4} final=3
  - claude: The graded test asserts internal SimpleCol instances from build_where, including for an F() right-hand side the issue never mentions, rather than checking the generated SQL or constraint behaviour. Valid alternative fixes, or ones that only handle nested Q left-hand sides, would fail.
  - gpt61: The graded test mandates an internal representation rather than the requested SQL behavior. It would reject correct fixes that remove table qualification without constructing SimpleCol nodes.
- `verified/scikit-learn__scikit-learn-14983` [agent_consensus] scores={'claude': 3, 'gpt61': 4} final=3
  - claude: The test requires an exact repr string in alphabetical parameter order (n_repeats before n_splits), which contradicts the order shown in the issue's expected results, so a fix matching the issue literally would fail.
  - gpt61: The tests enforce a parameter ordering contrary to the specification’s expected output. This rejects a correct implementation that follows the documented representation format.
- `verified/django__django-13807` [agent_consensus] scores={'claude': 3, 'gpt61': 3} final=3
  - claude: The test model also uses SQL keywords as column names ('select', 'where'), which the issue (about table names only) never mentions. A fix that correctly quotes table names everywhere but leaves column names unquoted would fail the test.
  - gpt61: The test mildly broadens the requirement from supporting SQL-keyword table names to supporting SQL-keyword column names as well. It can therefore reject an otherwise correct table-name quoting fix.

## Uncertain tasks (reported separately) (4)

- `full/django__django-13447` [openai_excluded] scores={'claude': 3, 'gpt61': 1} final=1
  - claude: The test hardcodes the dictionary key 'model', which the issue never states; a correct fix using a different key such as 'model_class' would fail.
  - gpt61: The tests directly check that app-list entries include their model classes, as requested. They impose no unnecessary implementation details.
- `pro/instance_flipt-io__flipt-02e21636c58e86c51119b63e0fb5ca7b813b07b1` [pro_narrow_original] scores={'claude': 3, 'gpt61': 1} final=1
  - claude: The tests depend on the Go struct field names `CaCertBytes`, `CaCertPath` and `InsecureSkipTLS`, which the spec never states (it gives only YAML keys). An idiomatic alternative such as `CACertPath` would fail to compile.
  - gpt61: The shown assertions align with explicitly required TLS and configuration behavior. They do not impose additional behavior or an arbitrary implementation strategy.
- `pro/instance_gravitational__teleport-dd3977957a67bedaf604ad6ca255ba8c7b6704e9` [pro_narrow_original] scores={'claude': 3, 'gpt61': 1} final=1
  - claude: The values required (localhost, 127.0.0.1, ::1) are clearly specified. If the comparison is order-sensitive, as I recall, the test also requires them at a specific position (before LocalKubernetes), which the spec never states.
  - gpt61: The added expectations directly test the explicitly requested loopback principals and introduce no demonstrated implementation-specific requirements.
- `pro/instance_navidrome__navidrome-3982ba725883e71d4e3e618c61d5140eeb8d850a` [pro_narrow_original] scores={'claude': 1, 'gpt61': 3} final=1
  - claude: Every symbol the tests rely on (`Backup`, `Restore`, `Prune`, `Db()` returning `*sql.DB`) is stated in the requirements, and the dbx builder helper is defined inside the test files themselves.
  - gpt61: Most changes directly test the requested API simplification, but the persistence tests additionally constrain repository constructor arguments to a particular dbx-based design. This can reject otherwise correct implementations using *sql.DB directly throughout the repositories.
