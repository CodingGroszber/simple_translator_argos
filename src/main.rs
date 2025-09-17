// main.rs
//
// Spawns the Python exe as child with piped stdio, passing --pipe arg to enable simple output mode.
// After spawning, reads from stdout until "READY" is received (consuming any initial stdout outputs like warnings).
// Then sends strings, reads responses line-by-line.
// Pipes stderr in a thread to print logs/errors (e.g., INFO, warnings).
//
// Use Hungarian test strings for hu->en model.
// At end, if all went well (exit success and received expected number of responses), print "all translations were succesful! the end!"

use std::io::{self, BufRead, BufWriter, Write};
use std::process::{Command, Stdio};
use std::thread;

fn main() -> io::Result<()> {
    let exe_path = "dist\\__main__.exe";

    let mut child = Command::new(exe_path)
        .arg("--pipe") // Enable pipe mode in Python
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("Failed to spawn the Python exe process");

    println!("Spawned the process.");

    let child_stdin = child.stdin.take().expect("Failed to open child stdin");
    let child_stdout = child.stdout.take().expect("Failed to open child stdout");
    let child_stderr = child.stderr.take().expect("Failed to open child stderr");

    // Thread to read and print stderr (for logs/errors)
    let stderr_handle = thread::spawn(move || {
        let mut reader = io::BufReader::new(child_stderr);
        let mut line = String::new();
        loop {
            match reader.read_line(&mut line) {
                Ok(0) => break, // EOF
                Ok(_) => {
                    print!("Child STDERR: {}", line);
                    line.clear();
                }
                Err(_) => break,
            }
        }
    });

    let mut writer = BufWriter::new(child_stdin);
    let mut reader = io::BufReader::new(child_stdout);

    // Handshake: Read from stdout until "READY" is received, print/discarding initial lines (e.g., warnings)
    loop {
        let mut line = String::new();
        reader
            .read_line(&mut line)
            .expect("Failed to read from child stdout during handshake");
        let trimmed = line.trim();
        if trimmed == "READY" {
            println!("Received READY signal from Python.");
            break;
        } else if !trimmed.is_empty() {
            println!("Initial stdout from Python: {}", trimmed);
        }
    }

    // Now send strings in loop
    let strings_to_send = vec![
        "Ezt én magam írom a terminálba.",
        "Ez egy másik teszt mondat.",
        "Harmadik mondat a teszteléshez.",
    ];

    let mut received_count = 0;

    for s in strings_to_send.iter() {
        writeln!(writer, "{}", s).expect("Failed to write to child stdin");
        writer.flush().expect("Failed to flush child stdin");
        println!("Sent: {}", s);

        let mut response = String::new();
        reader
            .read_line(&mut response)
            .expect("Failed to read from child stdout");
        let trimmed = response.trim();
        println!("Received: {}", trimmed);
        if trimmed.ends_with("_ok") {
            received_count += 1;
        }
    }

    drop(writer); // Close stdin -> EOF to Python

    let exit_status = child.wait().expect("Failed to wait on child process");
    stderr_handle.join().expect("Failed to join stderr thread");

    if exit_status.success() && received_count == strings_to_send.len() {
        println!("Child process terminated successfully.");
        println!("all translations were succesful! the end!");
    } else {
        println!("Child process terminated with error: {:?}", exit_status);
    }

    Ok(())
}
