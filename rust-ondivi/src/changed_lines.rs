use std::collections::HashMap;

pub type ChangedLines = HashMap<String, Vec<u64>>;

pub fn define_changed_lines(diff: &str) -> ChangedLines {
    let mut changed: ChangedLines = HashMap::new();
    let mut current_file = String::new();
    for line in diff.lines() {
        if line.starts_with("diff --git") {
            current_file = line.split(" b/").last().unwrap_or("").trim().to_string();
            changed.entry(current_file.clone()).or_default();
        } else if line.starts_with("@@") {
            let parts: Vec<&str> = line.split("@@").collect();
            let hunk = parts.get(1).unwrap_or(&"").trim();
            let added = hunk.split('+').nth(1).unwrap_or("").trim();
            let (start, num_lines) = if let Some((s, n)) = added.split_once(',') {
                let start: u64 = s.parse().unwrap_or(0);
                let raw: u64 = n.parse().unwrap_or(0);
                let num_lines = if raw > 0 { raw - 1 } else { 0 };
                (start, num_lines)
            } else {
                let start: u64 = added.parse().unwrap_or(0);
                (start, 0u64)
            };
            let nums: Vec<u64> = (start..=start + num_lines).collect();
            if !current_file.is_empty() {
                changed.entry(current_file.clone()).or_default().extend(nums);
            }
        }
    }
    changed
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_define_filename() {
        let got = define_changed_lines("diff --git XX b/ XX b/ file.py");
        assert_eq!(got, [("file.py".to_string(), vec![])].into_iter().collect());
    }
}
