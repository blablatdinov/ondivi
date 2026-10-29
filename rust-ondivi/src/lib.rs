pub mod changed_lines;
pub mod violations;

pub use changed_lines::{define_changed_lines, ChangedLines};
pub use violations::filter_out_violations;
