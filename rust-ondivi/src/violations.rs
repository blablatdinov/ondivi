fn is_regex_meta(c: char) -> bool {
    matches!(c, '.' | '^' | '$' | '*' | '+' | '?' | '(' | ')' | '[' | ']' | '{' | '}' | '|' | '\\' | '/')
}

use regex::Regex;
use std::sync::OnceLock;

use crate::changed_lines::ChangedLines;

fn template_to_regex(template: &str) -> Regex {
    // Convert a simple {name} or {name:spec} template into a regex with named groups.
    // {name:d} -> digit-only; {name} / {name:...} -> non-greedy anything.
    let mut pattern = String::from("^");
    let mut chars = template.chars().peekable();
    while let Some(c) = chars.next() {
        if c == '{' {
            // Collect until matching '}'
            let mut field = String::new();
            while let Some(fc) = chars.next() {
                if fc == '}' {
                    break;
                }
                field.push(fc);
            }
            // Split name:spec
            let (name, spec) = match field.split_once(':') {
                Some((n, s)) => (n, Some(s)),
                None => (field.as_str(), None),
            };
            let name = if name.is_empty() {
                "unnamed"
            } else {
                name
            };
            if let Some(s) = spec {
                if s.contains('d') {
                    pattern.push_str(&format!("(?P<{}>\\d+)", name));
                } else {
                    pattern.push_str(&format!("(?P<{}>.*?)", name));
                }
            } else {
                pattern.push_str(&format!("(?P<{}>.*?)", name));
            }
        } else if is_regex_meta(c) {
            pattern.push('\\');
            pattern.push(c);
        } else {
            pattern.push(c);
        }
    }
    pattern.push('$');
    Regex::new(&pattern).expect("invalid violation format template")
}

pub struct Violation {
    pub line_num: u64,
    pub filename: String,
}

pub fn parse_violation(raw: &str, template: &str) -> Option<Violation> {
    static RE_CACHE: OnceLock<Regex> = OnceLock::new();
    // We only cache one template at a time (CLI uses one); simple approach: build per call.
    let _ = RE_CACHE;
    let re = template_to_regex(template);
    let caps = re.captures(raw)?;
    let line_num = caps.name("line_num")?.as_str().parse().ok()?;
    let filename_raw = caps.name("filename")?.as_str();
    let filename = filename_raw.replace('\\', "/").replace("./", "");
    Some(Violation { line_num, filename })
}

pub fn filter_out_violations(
    changed_lines: &ChangedLines,
    linter_out: &[String],
    violation_format: &str,
    only_violations: bool,
) -> (Vec<String>, bool) {
    let mut filtered = Vec::new();
    let mut violation_found = false;
    for raw in linter_out {
        let (line_for_out, is_violation) = match parse_violation(raw, violation_format) {
            Some(viol) => {
                let is_target_file = changed_lines.contains_key(&viol.filename);
                let on_changed = changed_lines
                    .get(&viol.filename)
                    .map(|lines| lines.contains(&viol.line_num))
                    .unwrap_or(false);
                if is_target_file && on_changed {
                    (true, true)
                } else {
                    (false, false)
                }
            }
            None => (true, false),
        };
        violation_found = violation_found || is_violation;
        if is_violation || (line_for_out && !only_violations) {
            filtered.push(raw.clone());
        }
    }
    (filtered, violation_found)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn to_map(pairs: &[(&str, &[u64])]) -> ChangedLines {
        pairs
            .iter()
            .map(|(f, l)| (f.to_string(), l.to_vec()))
            .collect()
    }

    #[test]
    fn test_without_violation() {
        let (violations, found) = filter_out_violations(
            &ChangedLines::new(),
            &["All checks passed".to_string()],
            "{filename}:{line_num:d}:{col_num:d}: {message}",
            false,
        );
        assert_eq!(violations, vec!["All checks passed".to_string()]);
        assert!(!found);
    }

    #[test]
    fn test_custom_format() {
        let (violations, found) = filter_out_violations(
            &to_map(&[("file.py", &[12])]),
            &["line=12 file=file.py message=`print` found".to_string()],
            "line={line_num:d} file={filename} {other}",
            false,
        );
        assert_eq!(violations, vec!["line=12 file=file.py message=`print` found".to_string()]);
        assert!(found);
    }

    #[test]
    fn test_not_target_violation() {
        let (violations, found) = filter_out_violations(
            &to_map(&[("file.py", &[1, 2])]),
            &["file.py:3:1: line too long".to_string()],
            "{filename}:{line_num:d}:{col_num:d}: {message}",
            false,
        );
        assert!(violations.is_empty());
        assert!(!found);
    }

    #[test]
    fn test_file_without_diff() {
        let (violations, found) = filter_out_violations(
            &to_map(&[("file.py", &[1, 2])]),
            &["foo.py:3:1: line too long".to_string()],
            "{filename}:{line_num:d}:{col_num:d}: {message}",
            false,
        );
        assert!(violations.is_empty());
        assert!(!found);
    }

    #[test]
    fn test_only_violations() {
        let (violations, found) = filter_out_violations(
            &to_map(&[("file.py", &[3])]),
            &[
                "file.py:3:1: line too long".to_string(),
                "Info message".to_string(),
            ],
            "{filename}:{line_num:d}:{col_num:d}: {message}",
            true,
        );
        assert_eq!(violations, vec!["file.py:3:1: line too long".to_string()]);
        assert!(found);
    }

    #[test]
    fn test_path_starts_with_dot() {
        let (violations, found) = filter_out_violations(
            &to_map(&[("file.py", &[3])]),
            &["./file.py:3:1: line too long".to_string()],
            "{filename}:{line_num:d}:{col_num:d}: {message}",
            false,
        );
        assert_eq!(violations, vec!["./file.py:3:1: line too long".to_string()]);
        assert!(found);
    }
}
