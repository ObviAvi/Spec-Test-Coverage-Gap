# STCG judge evaluation: `judge_v1` on `verified`

- tasks: 500, judged: 500, judged by all judges: 500
- errors per judge: {'claude': 0, 'gpt61': 0}

## Targets (ensemble, all tasks)

- recall on overspecified: - (target >= 70%)
- false-flag rate on fine: - (target <= 15%)
- **NOT MET**

## Detection

| scorer | group | recall | false-flag rate |
|---|---|---|---|
| claude | all | - | - |
| claude | source: | - | - |
| gpt61 | all | - | - |
| gpt61 | source: | - | - |
| ensemble | all | - | - |
| ensemble | source: | - | - |
| ensemble_certain_only | all | - | - |
| ensemble_certain_only | source: | - | - |

## Inter-judge agreement

- Fleiss' kappa on the flag (tasks judged by all): 0.601
- uncertain (spread >= 2): 11% (57/500, CI 9%-14%)

| pair | n | Cohen's kappa | agree |
|---|---|---|---|
| claude~gpt61 | 500 | 0.611 | 83% |

## Missed overspecified tasks (0)


## False flags on fine tasks (0)


## Uncertain tasks (reported separately) (57)

- `verified/astropy__astropy-14539` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The tests check that Q-format VLA columns compare as identical when equal and, when they differ, are reported exactly like the existing P-format VLA columns (per-row entries, total 15 of 22). That is what any fix extending the existing VLA handling to Q formats produces.
  - gpt61: The tests call TableDataDiff directly rather than exercising FITSDiff or printdiff. A correct fix that handles Q-format VLAs at FITSDiff's table-HDU comparison boundary could resolve the reported behavior while failing these direct lower-level comparisons.
- `verified/django__django-10973` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The spec explicitly asks for subprocess.run with PGPASSWORD in a custom environment, and the tests simply check that subprocess.run receives the expected args and an env whose PGPASSWORD equals the raw password, which any natural implementation satisfies.
  - gpt61: A correct fix can pass env=None to subprocess.run when no password is supplied, while passing a custom environment containing PGPASSWORD otherwise. The no-password test rejects this valid implementation because its mock unconditionally calls env.get(), which fails for None.
- `verified/django__django-11179` [] scores={'claude': 1, 'gpt61': 4} final=1
  - claude: The test checks exactly that u.pk is None after delete() on a fast-deletable model, which the spec directly states.
  - gpt61: A reasonable fix could disable the instance-specific fast-delete shortcut and use ordinary deletion cleanup to clear the PK. The test would reject it because it separately requires Collector.can_fast_delete(u) to remain True, an internal optimization requirement not stated in the specification.
- `verified/django__django-11964` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The graded assertion str(test[member.name]) == str(member.value) is exactly the spec's complaint that __str__ does not return the enum's value, applied across the TextChoices and IntegerChoices enums the issue names.
  - gpt61: A reasonable fix could normalize enum values through model-field handling, making freshly created and retrieved field values stringify identically. The test bypasses model fields and requires standalone enum members to stringify as their underlying values, so that fix would fail.
- `verified/django__django-12193` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The graded assertion checks that CheckboxInput.get_context no longer mutates the passed attrs dict, which is exactly the root cause the specification names.
  - gpt61: A developer could fix SplitArrayWidget by passing a fresh attrs dictionary to each child, eliminating checked-state leakage. That fix would still fail the direct CheckboxInput test because it leaves the caller's attrs['checked'] changed to True.
- `verified/django__django-13315` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The tests only check that formfield querysets under join-based `limit_choices_to` (Q or dict, FK or M2M) contain each matching object once, order-independently, and any correct dedup fix in the shared limit-choices path passes.
  - gpt61: A reasonable fix could deduplicate choices during ModelChoiceIterator iteration without replacing the field's underlying queryset. The form would no longer render duplicate options, but the tests would fail because they inspect queryset contents rather than generated choices.
- `verified/django__django-13512` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The tests assert that unicode in JSONField values is rendered unescaped, both in the admin edit form (`prepare_value`) and in the read-only admin display (`display_for_field`), which is exactly the symptom the issue describes.
  - gpt61: An admin-specific JSON field or widget could correctly render Unicode while leaving generic forms.JSONField.prepare_value() ASCII-escaped. The added tests reject that reasonable fix because they require literal Unicode in prepare_value() itself, not just in the admin output.
- `verified/django__django-13837` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The spec dictates using `__main__.__spec__.parent` to build `-m <pkg>`, and the test checks exactly `[sys.executable, '-m', 'utils_tests.test_module', 'runserver']` when `__main__` is a module in that package.
  - gpt61: A correct fix using a module-level `import __main__` would fail because the test replaces only sys.modules['__main__'], not the already-bound module reference. The test therefore constrains when the implementation obtains the main module, an implementation detail the specification does not require.
- `verified/django__django-14311` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The test asserts that get_child_arguments returns `-m <full dotted module name>` for a non-package module, which is exactly the behavior the issue requests; any spec-based fix (using __spec__.name, falling back to parent only for __main__) passes.
  - gpt61: A correct fix that uses sys.argv[0] to distinguish a package's __main__.py from an ordinary module file would fail because the test supplies a package-entry filename while substituting a different, non-package __main__ module. Real execution of the tested module would put main_module.py in sys.argv[0], so this failure does not demonstrate the reported bug.
- `verified/django__django-14580` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: Any reasonable fix adds the missing `from django.db import models` import to the existing `models.Model` serialization special case, which is exactly what `MigrationWriter.serialize(models.Model)` is asserted to return.
  - gpt61: A correct fix could add the required models import during migration-file generation without changing MigrationWriter.serialize(models.Model). The tests instead require that standalone serializer to return a particular expression/import combination, so that fix would fail despite generating valid migrations.
- `verified/django__django-14672` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The spec explicitly prescribes wrapping through_fields with make_hashable in ManyToManyRel.identity, and the tests only check that hashing works for list through_fields while the stored attribute remains unchanged, which that prescribed fix satisfies.
  - gpt61: A correct fix could normalize self.through_fields to a hashable tuple during initialization. The tests reject that fix because they inspect relation metadata and require through_fields to remain a list, although the specification only requires list input to work and relation hashing to succeed.
- `verified/django__django-15127` [] scores={'claude': 3, 'gpt61': 1} final=1
  - claude: A fix that makes Message.level_tag read settings dynamically (e.g., calling get_level_tags() in the property) resolves the reported symptom, but fails because the test asserts the module-level constant base.LEVEL_TAGS is reassigned under override_settings. To pass, the fix must also update base.LEVEL_TAGS itself on setting change, for example via a setting_changed receiver for MESSAGE_TAGS.
  - gpt61: The assertion self.assertEqual(base.LEVEL_TAGS, self.message_tags) directly checks the explicitly reported failure to update LEVEL_TAGS under @override_settings, without prescribing how the update is implemented.
- `verified/django__django-15561` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The test asserts zero queries when SQLite's schema editor alters a field to add or remove choices, which is exactly the noop behaviour the issue asks for. It goes through the same schema-editor entry point that AlterField uses and follows the existing noop test pattern.
  - gpt61: A correct fix in the AlterField migration operation could skip schema-editor work for choices-only changes, eliminating the reported SQL. The tests bypass that operation and directly require schema_editor.alter_field() to perform zero queries, so that fix would fail.
- `verified/django__django-15572` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The test checks that the empty-string DIRS entry is no longer normalized into a watched directory by get_template_directories(), the existing function the spec identifies as doing the normalization. Any reasonable fix that drops empty entries passes.
  - gpt61: A correct fix could exclude empty configured directories in template_changed()'s matching path while leaving the directory-collection helper unchanged. It would fix application autoreloading but fail the test's direct requirement that get_template_directories() return an empty set.
- `verified/django__django-15973` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The test asserts that the autodetector adds a dependency on the separate-app through model, which is exactly the missing dependency the issue shows. The resulting split and dependency set follow deterministically from the existing autodetector cycle handling.
  - gpt61: A correct schema-editor fix could avoid inspecting `_meta` on an unresolved explicit through reference and leave intermediary-table creation to that model's migration. The test would reject it because it requires the autodetector specifically to split Author creation and its many-to-many field into two migrations with an exact dependency graph.
- `verified/django__django-16116` [] scores={'claude': 1, 'gpt61': 3} final=1
  - claude: The test asserts SystemExit and that no migration files are written, which is exactly what the spec requests ('makemigrations --check should just exit without making migrations').
  - gpt61: A fix could suppress migration-file writes while leaving an empty migration directory created during output preparation. The test rejects that fix because it requires the directory itself to be absent, rather than merely requiring that no migrations were created.
- `verified/django__django-16950` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The graded test checks that a bound inline formset for a new parent keeps the parent's auto-generated UUID alternate key (not None) and that the child's FK matches it, which is exactly the reported bug of the id being set to null.
  - gpt61: A reasonable fix could restore the parent's UUID before saving the parent and propagate it to children during inline saving. The test instead requires the UUID and child foreign-key value to be populated immediately after formset validation, rejecting such a save-time fix.
- `verified/django__django-17084` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: Any correct fix must wrap the window-containing annotation in a subquery and aggregate in the outer query. That necessarily yields one query with two SELECTs and the asserted correct values, so every reasonable fix passes.
  - gpt61: A correct fix could use separate derived-table layers for window evaluation and annotation projection before the final aggregate. It would return the expected totals in one query but fail the requirement that the generated SQL contain exactly two SELECTs.
- `verified/matplotlib__matplotlib-20859` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: Every reasonable fix that accepts `FigureBase` in the legend parent check, as the issue suggests, passes. The assertion `leg.figure is subfig` follows from the existing `set_figure(parent)` path and the convention that subfigure artists carry the subfigure as their figure.
  - gpt61: A reasonable fix could associate the legend with the enclosing Figure while using the SubFigure's transform and legend collection for correct placement and rendering. It would fail the required identity leg.figure is subfig, which the specification does not settle.
- `verified/matplotlib__matplotlib-22719` [] scores={'claude': 1, 'gpt61': 3} final=1
  - claude: The test runs the specification's reproduction verbatim and only requires that plotting empty data on category axes emits no deprecation warning, which is what the issue reports as the bug.
  - gpt61: The test requires the reproduction to run without a deprecation warning, but the specification also permits a more accurate, actionable diagnostic. A fix that emits a dedicated empty-data deprecation warning could satisfy that alternative while still failing the smoke test.
- `verified/matplotlib__matplotlib-23476` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The graded assertion `fig2.dpi == 42` directly encodes the spec's expected outcome that dpi is unchanged after an unpickle round-trip. The private `_set_device_pixel_ratio` call is only pre-existing setup that simulates a HiDPI display, so any reasonable fix to the figure's pickling passes.
  - gpt61: A correct fix could prevent duplicate scaling during GUI canvas recreation while preserving the current DPI when a bare Figure is pickled. This test instead bypasses that GUI path and requires the bare figure's DPI to drop from 294 to 42, rejecting that reasonable fix.
- `verified/matplotlib__matplotlib-24177` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The test adds a step-histogram-shaped path patch and asserts only that the autoscaled limits contain all vertices, which is the issue's "autoscale should fit the whole histogram" behavior through the same patch-extents mechanism hist relies on.
  - gpt61: A correct histogram-level fix could update data limits directly from bin edges and density heights, fixing step-histogram autoscaling without changing generic PathPatch handling. The test never calls `hist`, so that fix could still fail its requirement that the manually added path's upper y-limit reach 0.33.
- `verified/matplotlib__matplotlib-24570` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The graded assertions check HPacker offsets for top and bottom alignment through the public `get_extent_offsets`, which map directly to the reported reversal. The VPacker checks follow automatically from the natural fix of regrouping (left, bottom) and (right, top) in the shared alignment helper.
  - gpt61: A correct HPacker-local fix can reverse its top/bottom handling without changing VPacker. The tests additionally require VPacker's `bottom` to mean left alignment and `top` to mean right alignment, behavior the issue does not specify.
- `verified/matplotlib__matplotlib-25311` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: Any correct fix must keep the unpicklable GUI canvas out of the pickled draggable-legend state, which is exactly what the `FigureCanvasAgg not in genops(pkl)` assertion checks under the Agg backend.
  - gpt61: A correct fix could make canvas references safely serializable using an Agg replacement and reconnect them on loading. Such a fix could successfully pickle and restore draggable figures but fail the test solely because its pickle stream references FigureCanvasAgg.
- `verified/matplotlib__matplotlib-25960` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The test checks subfigure bbox positions that follow exactly from the GridSpec-style wspace/hspace semantics documented in the docstring the issue links as the expected outcome, using only the public `subfigures` and `bbox` API.
  - gpt61: A correct fix could update subfigure geometry during drawing, so that plt.show() renders the requested gaps. The test instead requires final bounding boxes before any draw, rejecting that reasonable implementation.
- `verified/psf__requests-1142` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The test asserts that prepared GET (and the closely related bodyless HEAD) requests carry no Content-Length header, which is exactly the behavior the issue says is correct.
  - gpt61: A reasonable fix could strip the automatically generated header immediately before transmission, resolving requests.get while leaving Request.prepare().headers unchanged. The tests require omission at the preparation stage and also reject the specification's explicitly permitted opt-out-only solution.
- `verified/psf__requests-1921` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The test asserts that a None-valued session header is absent from the prepared request's headers. This mirrors the existing per-request None handling in the session merge step, so any natural fix in `merge_setting` or header preparation passes.
  - gpt61: A correct fix could remove None-valued headers in Session.send before transmission rather than during preparation. It would prevent the unwanted header from being sent but fail the test's requirement that Accept-Encoding already be absent immediately after prepare_request.
- `verified/psf__requests-2931` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: Every correct fix stops converting the binary payload with `to_native_string` and keeps the body as raw bytes, as in 2.8.1, so the `isinstance(request.body, bytes)` check on the spec's own input passes.
  - gpt61: A correct fix could represent binary payloads as binary streams and transmit their contents unchanged, avoiding to_native_string. It would fix the reported request but fail the test's requirement that the prepared body itself be a bytes object.
- `verified/psf__requests-6028` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The root cause of the lost proxy credentials is `prepend_scheme_if_needed` stripping userinfo, and the tests just assert that this helper returns an authenticated URL unchanged, which any fix of the root cause satisfies.
  - gpt61: A correct fix could preserve proxy credentials in request/proxy connection setup without changing prepend_scheme_if_needed. The tests would still fail because they require that particular helper to return both authenticated URLs unchanged.
- `verified/pydata__xarray-2905` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The spec pinpoints the `getattr(data, 'values', data)` line in the shared `as_compatible_data` helper. Any fix there that stops unwrapping `.values` from arbitrary objects makes the test's assertion pass: the Variable stores the CustomWithValuesAttr object itself, which `_data.item()` returns.
  - gpt61: A correct fix could prevent coercion specifically during object-dtype assignment while retaining existing constructor behavior. The test bypasses assignment and instead requires direct scalar `Variable` construction to preserve the custom object in `_data`, so that fix could fail.
- `verified/pydata__xarray-3095` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The graded check, that `IndexVariable.copy(deep=True)` stays identical (dtype preserved) for str data, is the root of the reported regression, and the spec names IndexVariable, so any reasonable fix passes.
  - gpt61: The test requires standalone IndexVariable.copy(deep=True) to preserve Unicode dtype. A reasonable fix confined to dtype-preserving coordinate copying in Dataset and DataArray, including their standard copy hooks, could satisfy the specification while still failing this test.
- `verified/pydata__xarray-4075` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: Both tests check the behavior the spec describes: bool-weighted mean equals 1 and the sum of bool weights equals 2, as stated in the issue. Any fix that casts the boolean weights to a numeric type passes, and dtype is not checked by `assert_equal`.
  - gpt61: A correct fix could cast boolean weights only within the weighted-mean computation, leaving the public sum_of_weights() method unchanged. The separate test of that method would reject this fix even though boolean-weighted means are correctly normalized.
- `verified/pydata__xarray-4356` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The tests only check that a multi-dim sum/prod with min_count runs and matches the full reduction (`dim=...`), which is the only correct behavior for the shared nanops path the issue identifies.
  - gpt61: A reasonable fix could repair multidimensional min_count handling specifically for sum while leaving prod unchanged. The graded prod cases would reject that fix even though product reduction is not requested by the specification.
- `verified/pylint-dev__pylint-4604` [] scores={'claude': 4, 'gpt61': 2} final=2
  - claude: The test module does `from pylint.constants import IS_PYPY`, a constant the original fix introduced and the spec never mentions. A correct checker fix that does not add `IS_PYPY` to `pylint/constants.py` makes the whole test file fail with ImportError, failing every graded test.
  - gpt61: The no-message assertion checks the requested suppression of unused-import, extended only to closely related qualified and subscripted type comments. It does not require a particular implementation or an arbitrary observable choice.
- `verified/pytest-dev__pytest-10051` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The core assertions (`get_records("call") == []` after clear, and new records showing up afterwards) are the spec's repro. The setup-records and stash-key checks hold for any natural fix and mirror an existing test.
  - gpt61: A correct fix could invalidate the active phase's cached stash entry and serve its records directly from the live capture handler. The tests reject that implementation by requiring the private stash to retain a 'call' key after clear(), even though all specified public behavior works.
- `verified/pytest-dev__pytest-5787` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The tests check that a JSON round trip through the existing `_to_json`/`_from_json` methods preserves the existing `ExceptionChainRepr` structure (both chain entries and their descriptions), which is exactly what "serialization should include chained exceptions" asks for.
  - gpt61: A correct fix could preserve the complete formatted exception chain in a terminal-renderable longrepr without reconstructing an ExceptionChainRepr object. It would resolve the reported output loss but fail the tests' required internal type and .chain tuple structure after deserialization.
- `verified/scikit-learn__scikit-learn-13142` [] scores={'claude': 1, 'gpt61': 4} final=1
  - claude: The graded tests are essentially the issue's reproduction with a fixed seed, asserting fit_predict(X) equals predict(X) when n_init>1, which every correct fix satisfies.
  - gpt61: A correct GaussianMixture-specific fix could make fit_predict(X) agree with predict(X) for all initialization counts while leaving BayesianGaussianMixture unchanged. The graded Bayesian test rejects that fix even though the specification never requests a change to that estimator.
- `verified/scikit-learn__scikit-learn-14141` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: Any fix that adds joblib to the dependency list reported by show_versions, which is what the issue title asks for, makes `'joblib' in deps_info` true, following the existing module-name key convention.
  - gpt61: A correct fix could add joblib-version reporting to the issue template for sklearn versions above 0.20, as explicitly permitted. The test instead requires the dependency-info result to contain 'joblib', rejecting that alternative by checking a different implementation path.
- `verified/scikit-learn__scikit-learn-25232` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: Every reasonable fix forwards the spec-named `fill_value` to the existing `SimpleImputer` held in the documented `initial_imputer_` attribute, so `initial_imputer_.statistics_ == fill_value` holds.
  - gpt61: A correct fix could apply `fill_value` directly to missing entries during initialization and transformation without storing that value in the helper imputer's statistics. The test would reject it because it inspects `initial_imputer_.statistics_` rather than the initialized output.
- `verified/sphinx-doc__sphinx-10323` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The spec explicitly asks that dedent apply only to the included lines and not to prepend/append, and the test asserts exactly that through the existing LiteralIncludeReader.read() path.
  - gpt61: A correct fix could preserve leading whitespace in prepend/append during directive-option processing while leaving LiteralIncludeReader's dedent behavior unchanged. The test bypasses directive processing and requires the reader itself to exclude prepend/append from dedent, rejecting that alternative.
- `verified/sphinx-doc__sphinx-10435` [] scores={'claude': 1, 'gpt61': 3} final=1
  - claude: The graded assertion checks, verbatim, the exact `\sphinxupquote{%\n...%\n}}` markup that the issue gives as the expected output.
  - gpt61: The test requires percent-commented boundary newlines in the generated LaTeX. A correct fix that removes the boundary newlines entirely would produce the desired PDF spacing but fail this assertion.
- `verified/sphinx-doc__sphinx-10673` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The test asserts that the toctree keeps the entries `(None, 'genindex')`, `(None, 'modindex')` and `(None, 'search')` instead of dropping them with a warning; any fix that includes these names following the existing (title, docname) entry convention passes.
  - gpt61: A correct fix could populate generated-page titles when recognizing these special toctree entries, producing working links without warnings. The test would reject it because it requires the internal app.env.tocs entries to retain exactly (None, 'genindex'), (None, 'modindex'), and (None, 'search').
- `verified/sphinx-doc__sphinx-11445` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The tests assert that ``:mod:`foo` `` is not treated as docinfo, so the prolog is inserted at the top with the existing generated blank line. That follows directly from the bug report and the existing behavior of `prepend_prolog`.
  - gpt61: A correct fix could recognize the role-containing heading and surround the inserted prolog with harmless blank-line padding. Both graded tests would reject that fix because they require an exact intermediate StringList layout and provenance, rather than checking that the heading renders and appears in the toctree.
- `verified/sphinx-doc__sphinx-7440` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: Any fix that makes glossary terms case-sensitive (as the issue's 'MySQL != mysql' demands) registers the term under its original case, so get_objects() yields ('TERM2', 'TERM2', 'term', 'index', 'term-TERM2', -1) and the node and index ids already preserve case.
  - gpt61: A correct fix could distinguish glossary terms case-sensitively while retaining lowercase-normalized, collision-disambiguated anchors. It would fail the doctree index-entry and inventory assertions requiring the exact anchor `term-TERM2`.
- `verified/sphinx-doc__sphinx-7757` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The bug lives in signature_from_str, which the directive uses to parse arglists. The test checks the spec's exact example, asserting `b.default == '0'`, using the existing string-default convention, so any reasonable fix passes.
  - gpt61: A correct fix could preserve positional-only defaults in the Python directive's parsing/rendering path while leaving `inspect.signature_from_str` unchanged. The graded test instead requires that helper itself to return specific intermediate default values, so that fix would fail despite producing the required documentation.
- `verified/sphinx-doc__sphinx-8120` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: Any correct fix must make the user's sphinx.po override the built-in 'sphinx' catalog that backs the existing `app.translator`, so both the gettext assertion and the 'QUICK SEARCH' HTML check follow directly from the issue's expected behaviour.
  - gpt61: A correct fix could load the project-local system catalog at the beginning of the build and produce all the requested translated output. It would nevertheless fail because the test requires app.translator to expose the override immediately after application construction, before app.build() runs.
- `verified/sphinx-doc__sphinx-8551` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The issue asks that :type:/:rtype: xrefs look names up the same way explicit py roles do. The test checks the same context attributes that explicit roles already attach and that resolve_xref already consumes: py:module and py:class on the pending_xref. Any reasonable fix therefore produces them.
  - gpt61: A correct fix could obtain scope from the enclosing Python description during reference resolution instead of attaching it to every pending reference during parsing. The test would reject that fix because it requires exact py:module and py:class attributes on the unresolved nodes, despite correct final links and no ambiguity warnings.
- `verified/sphinx-doc__sphinx-9258` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The test checks that `int | str` yields two pending_xrefs separated by a verbatim ' | ' emphasis node. That is exactly what extending the existing delimiter-splitting used for 'or' produces, so it is the only reasonable rendering.
  - gpt61: A correct fix could render independently linked union members with an ordinary text separator. The test rejects that fix because it requires the separator to be an addnodes.literal_emphasis node in an exact intermediate doctree structure.
- `verified/sphinx-doc__sphinx-9281` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The assertion `object_description(MyEnum.FOO) == "MyEnum.FOO"` matches the spec's expected `MyEnum.ValueA` format exactly, and `object_description` is the existing helper Sphinx uses to render default values, so any natural fix passes.
  - gpt61: A correct fix could format Enum defaults in the signature-rendering code without changing `inspect.object_description`. The test bypasses signature rendering and requires that helper itself to return `"MyEnum.FOO"`, rejecting that reasonable implementation.
- `verified/sphinx-doc__sphinx-9320` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The test simply answers the existing-conf.py prompt with an empty string and asserts that `ask_user` raises `SystemExit`, which is exactly the spec's expected behavior that pressing Enter exits.
  - gpt61: A correct fix could return a cancellation result from ask_user and have the CLI caller terminate normally. That resolves the reported behavior but fails the test because it requires SystemExit from ask_user itself.
- `verified/sphinx-doc__sphinx-9591` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The graded assertion checks that the property's ": str" annotation now contains a pending_xref for the type, which is the requested cross-referencing, built the same way PyAttribute and PyVariable already build their :type: annotations in this file.
  - gpt61: The tests require a particular intermediate doctree structure, not merely a working type cross-reference. A correct fix that places the separator and linked type in separate sibling annotation nodes would fail despite resolving the reported bug.
- `verified/sphinx-doc__sphinx-9658` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The test asserts that restify, the function that renders the Bases line, returns the full dotted name of a mocked class (`unknown.secret.Class`), which is exactly the spec's expected `torch.nn.Module` behavior; both a restify-level fix and a mock-level `__qualname__` fix pass.
  - gpt61: A reasonable fix could correct mocked-base references in autodoc's class-documentation path while leaving generic `restify` behavior unchanged. The test bypasses that documentation path and requires a particular result from `restify` directly, so that correct fix could fail.
- `verified/sphinx-doc__sphinx-9673` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The test checks that a documented `:returns:` field (what Napoleon emits) gets a 'Return type: int' added, which is exactly the spec's expected behavior rendered in autodoc's existing rtype format.
  - gpt61: A correct fix in Napoleon's Google-style return-field conversion could restore return annotations without fixing the test's directly supplied reST ':returns:' field. The test also rejects the explicitly permitted alternative of displaying the type within the return description.
- `verified/sympy__sympy-15345` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The assertion checks Max and Min (its direct twin) printed with Mathematica brackets, using the printer's existing ", " separator convention and natural x, y, z ordering, so any reasonable fix passes.
  - gpt61: The assertion additionally requires fixing Min printing, a separate function absent from the issue. A reasonable Max-only printer fix would resolve the reported defect and related Max inputs but fail because Min(y,z) still prints with parentheses.
- `verified/sympy__sympy-17139` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The tests check that `simplify(cos(x)**I)` (the reported example) and related complex exponents come back unchanged without crashing, and that `_TR56`, the exact function in the traceback, leaves complex-exponent powers unchanged, which any fix at the identified site does.
  - gpt61: The tests require the private _TR56 helper itself to accept complex exponents. A correct fix that protects complex powers in the public transformation wrappers would make simplify work but still fail the direct helper assertions.
- `verified/sympy__sympy-22714` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: Every reasonable fix passes, because the test only checks that Point(1, 2) under evaluate(False) no longer raises, and the spec's traceback places the failing check in Point.__new__.
  - gpt61: The test requires direct Point construction to work, rather than the reported Point2D entry point. A reasonable fix in Point2D that guards its delegation to Point against disabled evaluation would resolve the issue but still fail the test's standalone Point call.
- `verified/sympy__sympy-23413` [] scores={'claude': 2, 'gpt61': 4} final=2
  - claude: The graded change asserts that `hermite_normal_form([[2,7],[0,0],[0,0]])` equals `[[1],[0],[0]]`, which is the unique correct HNF under the existing drop-zero-columns convention. Any fix for the false rank-deficiency bug in the issue produces it.
  - gpt61: The polys test additionally requires repairing the separate DomainMatrix-facing HNF API. A correct general repair made at the specified Matrix entry point could leave that API unchanged and therefore fail the graded DomainMatrix assertion.
