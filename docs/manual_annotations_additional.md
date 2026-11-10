# Manual STCG Annotations — Additional Tasks (Score 3 anchors)

These extend the 7 manually-labelled calibration tasks in the research doc. They target the
previously-missing **score 3 (Mildly Overspecified / Solution Bias)** band: the test still checks
external/observable behavior, but leans toward one specific valid approach over another equally
valid one, narrowing the set of fixes that pass.

---

## Task: sympy__sympy-23950

Problem Statement:

```
Contains.as_set returns Contains

>>> Contains(x, Reals).as_set()
Contains(x, Reals)

This is wrong because Contains is not a set (it's a boolean). It results in failures in other
places because it doesn't have as_relational (since it isn't a set). For instance:

>>> Piecewise((6, Contains(x, Reals)), (7, True))
...
AttributeError: 'Contains' object has no attribute 'as_relational'
```

Test Patch:

```diff
 def test_as_set():
     x = Symbol('x')
     y = Symbol('y')
-    # Contains is a BooleanFunction whose value depends on an arg's
-    # containment in a Set -- rewriting as a Set is not yet implemented
-    raises(NotImplementedError, lambda:
-           Contains(x, FiniteSet(y)).as_set())
+    assert Contains(x, FiniteSet(y)).as_set() == FiniteSet(y)
+    assert Contains(x, S.Integers).as_set() == S.Integers
+    assert Contains(x, S.Reals).as_set() == S.Reals
```

Expected Score: 3, mildly overspecified / solution bias. The issue's only functional requirement is
that `Contains(x, S).as_set()` return *an actual set object* — i.e. something that exposes
`as_relational()` so the downstream `Piecewise` no longer crashes. The test, however, pins the
return value to the *exact containing set* (`Contains(x, FiniteSet(y)).as_set() == FiniteSet(y)`),
silently dropping the bound variable `x`. A functionally correct alternative — e.g. returning
`ConditionSet(x, Contains(x, S), S)` or any set built around `x` — would fully satisfy the issue
(it has `as_relational`, it unblocks `Piecewise`) yet fail this equality assertion. The test tests
observable output, so it is not a 4, but it narrows acceptance to one specific semantic
interpretation of "the set," making it a clean 3.

---

## Task: django__django-14534

Problem Statement:

```
BoundWidget.id_for_label ignores id set by ChoiceWidget.options

BoundField.subwidgets builds attrs where widget['attrs']['id'] holds the id we want when rendering
the label of a CheckboxSelectMultiple. However BoundWidget.id_for_label() is implemented as:

    def id_for_label(self):
        return 'id_%s_%s' % (self.data['name'], self.data['index'])

ignoring the id available through self.data['attrs']['id']. If the auto_id argument is overridden
when initializing a form, one would assume id_for_label renders that string as specified through
the auto_id format-string. By changing the code to:

    def id_for_label(self):
        return self.data['attrs']['id']

that function behaves as expected.
```

Test Patch:

```diff
@@ class BeatleForm(Form):
         fields = list(BeatleForm(auto_id=False)['name'])
         self.assertEqual(len(fields), 4)
-        self.assertEqual(fields[0].id_for_label, 'id_name_0')
+        self.assertEqual(fields[0].id_for_label, None)

+    def test_boundfield_subwidget_id_for_label(self):
+        class SomeForm(Form):
+            field = MultipleChoiceField(
+                choices=[('a', 'A'), ('b', 'B')],
+                widget=CheckboxSelectMultiple,
+            )
+        form = SomeForm(auto_id='prefix_%s')
+        subwidgets = form['field'].subwidgets
+        self.assertEqual(subwidgets[0].id_for_label, 'prefix_field_0')
+        self.assertEqual(subwidgets[1].id_for_label, 'prefix_field_1')
```

Expected Score: 3, mildly overspecified / solution bias. The issue describes the desired observable
behavior (when `auto_id` is overridden, the subwidget label id should reflect that prefix — the new
`test_boundfield_subwidget_id_for_label` assertion is a fair, directly-specified check of this).
What pushes it to a 3 is the *modified* existing assertion: `id_for_label` for an `auto_id=False`
form is changed from `'id_name_0'` to `None`. That `None` is not a behavior the issue requests — it
is a direct side-effect of the author's prescribed one-line implementation `return
self.data['attrs']['id']` (when there is no auto_id, `attrs` carries no id, so the method returns
`None`). A functionally reasonable alternative fix — one that honors the auto_id prefix when present
but still synthesizes a deterministic fallback id when `attrs` lacks one — would satisfy the issue
but fail the `== None` assertion. The test thereby biases acceptance toward the issue author's exact
implementation. It is not a 4 because the asserted value is still an externally-observable property,
not an internal/private state.

---

## Task: django__django-16642

Problem Statement:

```
Improper guessing of Mime Type for "br" and "Z" file types

Below FileResponse will set the content type as text/html, even if the last file extension is
"Z" or "br".
    FileResponse(open('test.html.Z', 'rb'))
    FileResponse(open('test.html.br', 'rb'))
```

Test Patch:

```diff
         test_tuples = (
             (".tar.gz", "application/gzip"),
+            (".tar.br", "application/x-brotli"),
             (".tar.bz2", "application/x-bzip"),
             (".tar.xz", "application/x-xz"),
+            (".tar.Z", "application/x-compress"),
         )
         for extension, mimetype in test_tuples:
             with self.subTest(ext=extension):
```

Expected Score: 3, mildly overspecified / solution bias. The issue's only stated requirement is
negative: a `.br` / `.Z` file must *not* be mislabeled as `text/html`. The test goes further and
pins the *exact* mime strings `application/x-brotli` and `application/x-compress`. These particular
labels are an arbitrary choice — equally defensible alternatives such as `application/brotli`,
`application/x-compressed`, or even falling back to `application/octet-stream` would all resolve the
reported "it says text/html" bug yet fail the equality check. The test validates observable behavior
(the response's content type), so it is not a 4, but it narrows the acceptable fix to one specific
encoding choice for the mime string, making it a 3.

---

## Task: django__django-13406

Problem Statement:

```
Queryset with values()/values_list() crashes when recreated from a pickled query.

When re-running a query that combines values() and annotate() (for GROUP BY) after pickling
queryset.query, the result is broken. Normally the result is a list of dicts, but here instances of
the model are returned with broken internal state — accessing .id raises
'AttributeError: NoneType object has no attribute attname'. Django retrieves the correct data but,
instead of returning dicts, tries to build model instances from data with the wrong structure.
```

Test Patch:

```diff
@@ def setUpTestData(cls):
-        Happening.objects.create()  # make sure the defaults are working (#20158)
+        cls.happening = Happening.objects.create()

+    def test_annotation_values(self):
+        qs = Happening.objects.values('name').annotate(latest_time=models.Max('when'))
+        reloaded = Happening.objects.all()
+        reloaded.query = pickle.loads(pickle.dumps(qs.query))
+        self.assertEqual(
+            reloaded.get(),
+            {'name': 'test', 'latest_time': self.happening.when},
+        )
+
+    def test_annotation_values_list(self):
+        # values_list() is reloaded to values() when using a pickled query.
+        tests = [
+            Happening.objects.values_list('name'),
+            Happening.objects.values_list('name', flat=True),
+            Happening.objects.values_list('name', named=True),
+        ]
+        for qs in tests:
+            with self.subTest(qs._iterable_class.__name__):
+                reloaded = Happening.objects.all()
+                reloaded.query = pickle.loads(pickle.dumps(qs.query))
+                self.assertEqual(reloaded.get(), {'name': 'test'})
```

Expected Score: 3, mildly overspecified / solution bias. The first test (`test_annotation_values`)
is essentially the issue's reproduction: a pickled `values().annotate()` query must yield dicts, not
broken model instances — directly specified. The score is driven up by `test_annotation_values_list`
and, tellingly, its inline comment: *"values_list() is reloaded to values() when using a pickled
query."* The issue never mentions `values_list` at all, let alone its `flat=True` / `named=True`
variants. The test bakes in a specific design decision — that *all* `values_list` flavors collapse
to plain `values()` dicts after an unpickle round-trip (note `flat=True` would normally yield bare
scalars and `named=True` named-tuples). A fix that faithfully preserved `values_list` iterable
semantics across pickling would resolve the reported crash but fail these assertions. The test still
checks observable output (the returned rows), so it is a 3 rather than a 4, but it commits the
benchmark to one particular interpretation of correct round-trip behavior that the issue does not
specify.

---

# Additional Score-2 Anchors (Reasonably Specified)

These fill out the score-2 band. A 2 differs from a 1 in that the test asserts conventions the
issue does NOT type out verbatim — standard exception types, standard equality/None semantics, or
the same implicated function re-run over related inputs — but every such addition is the obvious,
only-reasonable reading, and no functionally-correct fix is excluded (which keeps them below a 3).

---

## Task: django__django-13023

Problem Statement:

```
DecimalField.to_python() raises TypeError on dict values.

A call to DecimalField.to_python() with a dictionary as the value parameter produces TypeError
instead of ValidationError. This is a problem, for example, when you try to save a model object and
a decimal field got set to a dictionary by mistake. The TypeError makes it hard to track the problem
to the field if the object has a lot of fields.
```

Test Patch:

```diff
@@ def test_to_python(self):
         self.assertEqual(f.to_python(2.0625), Decimal('2.062'))
         self.assertEqual(f.to_python(2.1875), Decimal('2.188'))
-        msg = '“abc” value must be a decimal number.'
-        with self.assertRaisesMessage(ValidationError, msg):
-            f.to_python('abc')
+
+    def test_invalid_value(self):
+        field = models.DecimalField(max_digits=4, decimal_places=2)
+        msg = '“%s” value must be a decimal number.'
+        tests = [
+            (), [], {}, set(), object(), complex(),
+            'non-numeric string', b'non-numeric byte-string',
+        ]
+        for value in tests:
+            with self.subTest(value):
+                with self.assertRaisesMessage(ValidationError, msg % (value,)):
+                    field.clean(value, None)
```

Expected Score: 2, reasonably specified. The issue names both the exception type (it should raise
`ValidationError` rather than `TypeError`) and one input (`dict`). The test asserts that
`ValidationError`, carrying the framework's pre-existing message `"%s" value must be a decimal
number.`, is raised for the `dict` case AND for a battery of related non-numeric inputs — `()`,
`[]`, `set()`, `object()`, `complex()`, a non-numeric string, and a byte-string — all through the
same `clean()` / `to_python()` entry point. None of those extra types is typed in the issue, but
raising the standard `ValidationError` for any non-decimal value is the only reasonable reading, and
broadening a regression to related inputs is normal test hygiene (the rubric's "re-running the SAME
implicated function with related inputs"). There is no alternative-fix trap: any fix that converts
the `TypeError` into the standard `ValidationError` passes every case. The reliance on the standard
exception type and unstated-but-obvious related inputs is exactly what lifts it from a 1 to a 2.

---

## Task: astropy__astropy-7606

Problem Statement:

```
Unit equality comparison with None raises TypeError for UnrecognizedUnit

>>> x = u.Unit('asdf', parse_strict='silent')
>>> x == None   # Should be False
TypeError: None is not a valid Unit
```
(`UnrecognizedUnit.__eq__` calls `Unit(other, ...)`, which raises `TypeError` when `other` is `None`.)

Test Patch:

```diff
@@ def test_unknown_unit3():
     assert unit != unit3
     assert not unit.is_equivalent(unit3)

+    # Also test basic (in)equalities.
+    assert unit == "FOO"
+    assert unit != u.m
+    # next two from gh-7603.
+    assert unit != None  # noqa
+    assert unit not in (None, u.m)
```

Expected Score: 2, reasonably specified. The issue states one behavior directly: `UnrecognizedUnit
== None` should be `False`, not a `TypeError`. The `assert unit != None` line is that directly-
specified check. What the test adds on top are standard equality/membership conventions the issue
never types out: `unit == "FOO"` (equality against its own unparsed name), `unit != u.m`, and
`unit not in (None, u.m)` (container membership, which drives `__eq__` against several operand
types). A competent reader would expect that "comparison should not raise" generalizes to `__eq__`
degrading gracefully to `True`/`False` for any non-unit or `None` operand — these are the obvious
consequences, not arbitrary choices. Any fix that stops `__eq__` from raising on `None`/incomparable
inputs satisfies all of them, so no valid alternative is excluded. The dependence on inferred-but-
unstated standard conventions (rather than verbatim issue text) is what makes it a 2 rather than a 1.
