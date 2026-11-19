use ondivi::define_changed_lines;
use std::collections::HashMap;

#[test]
fn test_define_changed_files() {
    let diff = include_str!("fixtures/diff.patch");
    let got = define_changed_lines(diff);

    let mut expected: HashMap<String, Vec<u64>> = HashMap::new();
    expected.insert(
        "django/db/models/sql/query.py".to_string(),
        [
            (1367..1374).collect::<Vec<_>>(),
            (1401..1408).collect::<Vec<_>>(),
            (1418..1432).collect::<Vec<_>>(),
        ]
        .concat(),
    );
    expected.insert(
        "tests/custom_lookups/tests.py".to_string(),
        (614..624).collect(),
    );
    expected.insert(
        "tests/lookup/tests.py".to_string(),
        [
            (812..846).collect::<Vec<_>>(),
            (853..860).collect::<Vec<_>>(),
            (1087..1097).collect::<Vec<_>>(),
        ]
        .concat(),
    );

    assert_eq!(got, expected);
}
