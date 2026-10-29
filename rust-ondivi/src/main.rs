use clap::Parser;
use ondivi::{define_changed_lines, filter_out_violations};
use std::io::{self, Read};
use std::process::{exit, Command};

#[derive(Parser)]
#[command(name = "ondivi", about = "Ondivi (Only diff violations)")]
struct Cli {
    /// Commit or branch which will contain legacy code. Program filters out violations on baseline.
    #[arg(long, default_value = "master")]
    baseline: String,

    /// Path to file with violations. Expected "utf-8" encoding.
    #[arg(long)]
    fromfile: Option<String>,

    /// Template for parsing linter messages. Supported placeholders: {filename}, {line_num:d}, and any other {name}.
    #[arg(long, default_value = "{filename}:{line_num:d}{other}")]
    format: String,

    /// Show only violations.
    #[arg(long)]
    only_violations: bool,

    /// Randomly add N additional violations from the linter output that are not present in the diff.
    #[arg(long)]
    random_additional: Option<i64>,
}

fn read_linter_output(fromfile: &Option<String>) -> Vec<String> {
    match fromfile {
        Some(fp) => {
            let path = std::path::Path::new(fp);
            if !path.exists() {
                println!("File with violations \"{}\" not found", fp);
                exit(1);
            }
            let text = std::fs::read_to_string(path).unwrap_or_default();
            let trimmed = text.trim();
            if trimmed.is_empty() {
                vec![]
            } else {
                trimmed.lines().map(String::from).collect()
            }
        }
        None => {
            let mut buf = String::new();
            io::stdin().read_to_string(&mut buf).unwrap_or_default();
            let trimmed = buf.trim();
            if trimmed.is_empty() {
                vec![]
            } else {
                trimmed.lines().map(String::from).collect()
            }
        }
    }
}

fn run_git_diff(baseline: &str) -> Result<String, ()> {
    let output = Command::new("git")
        .args([
            "diff",
            "--unified=0",
            "--no-ext-diff",
            "--src-prefix=a/",
            "--dst-prefix=b/",
            baseline,
        ])
        .output();
    match output {
        Ok(o) => {
            // git diff exits 0 when no differences, 1 when there are differences.
            // Exit codes >= 128 indicate errors (e.g., bad revision).
            let code = o.status.code().unwrap_or(-1);
            if code >= 128 {
                Err(())
            } else {
                Ok(String::from_utf8_lossy(&o.stdout).into_owned())
            }
        }
        Err(_) => Err(()),
    }
}

fn main() {
    let cli = Cli::parse();

    if let Some(n) = cli.random_additional {
        if n < 1 {
            eprintln!(
                "Invalid \"size\" value. Expected positive integer got: \"{n}\""
            );
            exit(2);
        }
        eprintln!("--random-additional is not yet implemented in the Rust version");
        exit(2);
    }

    let linter_output = read_linter_output(&cli.fromfile);

    let diff = match run_git_diff(&cli.baseline) {
        Ok(d) => d,
        Err(_) => {
            print!("Revision \"{}\" not found", cli.baseline);
            exit(1);
        }
    };

    let changed = define_changed_lines(&diff);
    let (filtered, violation_found) = filter_out_violations(
        &changed,
        &linter_output,
        &cli.format,
        cli.only_violations,
    );

    if !filtered.is_empty() {
        println!("{}", filtered.join("\n"));
    }
    if violation_found {
        exit(1);
    }
}
