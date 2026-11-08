
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


# Find the project folder and Verilog source file.
PROJECT_DIR = Path(__file__).resolve().parent.parent
VERILOG_FILE = PROJECT_DIR / "verilog" / "sha256_top.v"

MAX_MESSAGE_BYTES = 1024
MAX_SIMULATION_CYCLES = 2000


def find_executable(name):
    """
    Find Icarus Verilog executables.
    First checks Windows PATH, then the common installation folder.
    """
    executable = shutil.which(name)

    if executable:
        return executable

    if name == "iverilog":
        possible_path = Path(r"C:\iverilog\bin\iverilog.exe")
    else:
        possible_path = Path(r"C:\iverilog\bin\vvp.exe")

    if possible_path.exists():
        return str(possible_path)

    raise FileNotFoundError(
        f"{name} was not found. Install Icarus Verilog "
        "or add C:\\iverilog\\bin to your PATH."
    )


def create_testbench(message_bytes):
    """
    Create a temporary Verilog testbench containing the user's input.
    The first message byte is placed in the most significant byte.
    """

    message_hex = message_bytes.hex().ljust(2048, "0")
    message_length = len(message_bytes)

    testbench = f"""
`timescale 1ns/1ps

module dynamic_testbench;

    reg clk;
    reg reset;
    reg start;

    reg [8191:0] message;
    reg [10:0] msg_len;

    wire [255:0] digest;
    wire done;

    integer cycles;

    sha256_top uut (
        .clk(clk),
        .reset(reset),
        .start(start),
        .message(message),
        .msg_len(msg_len),
        .digest(digest),
        .done(done)
    );

    always #5 clk = ~clk;

    initial begin
        clk = 0;
        reset = 1;
        start = 0;

        message = 8192'h{message_hex};
        msg_len = 11'd{message_length};

        #20;
        reset = 0;

        @(negedge clk);
        start = 1;

        @(negedge clk);
        start = 0;

        cycles = 0;

        while ((done !== 1'b1) && (cycles < {MAX_SIMULATION_CYCLES})) begin
            @(negedge clk);
            cycles = cycles + 1;
        end

        if (done === 1'b1) begin
            $display("HASH:%064h", digest);
        end
        else begin
            $display("SIMULATION_TIMEOUT");
        end

        $finish;
    end

endmodule
"""

    return testbench


def generate_sha256_hash(text):
    """
    Convert the input text to UTF-8 and calculate its SHA-256
    hash using the Verilog implementation.
    """

    if not isinstance(text, str):
        raise TypeError("Input must be text.")

    message_bytes = text.encode("utf-8")

    if len(message_bytes) > MAX_MESSAGE_BYTES:
        raise ValueError(
            f"Message is too long. Maximum supported size is "
            f"{MAX_MESSAGE_BYTES} UTF-8 bytes. "
            f"Your message uses {len(message_bytes)} bytes."
        )

    iverilog = find_executable("iverilog")
    vvp = find_executable("vvp")

    if not VERILOG_FILE.exists():
        raise FileNotFoundError(
            f"Verilog source file not found: {VERILOG_FILE}"
        )

    with tempfile.TemporaryDirectory() as temp_folder:

        temp_dir = Path(temp_folder)

        testbench_file = temp_dir / "dynamic_testbench.sv"
        simulation_file = temp_dir / "sha256_sim"

        testbench_file.write_text(
            create_testbench(message_bytes),
            encoding="utf-8"
        )

        # Compile the Verilog design and generated testbench.
        compile_result = subprocess.run(
            [
                iverilog,
                "-g2012",
                "-o",
                str(simulation_file),
                str(VERILOG_FILE),
                str(testbench_file)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if compile_result.returncode != 0:
            raise RuntimeError(
                "Verilog compilation failed:\n"
                + compile_result.stderr
                + compile_result.stdout
            )

        # Execute the compiled Verilog simulation.
        simulation_result = subprocess.run(
            [
                vvp,
                str(simulation_file)
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        if simulation_result.returncode != 0:
            raise RuntimeError(
                "Verilog simulation failed:\n"
                + simulation_result.stderr
                + simulation_result.stdout
            )

        output = simulation_result.stdout

        # Extract the 64-character SHA-256 digest.
        match = re.search(r"HASH:([0-9a-fA-F]{64})", output)

        if not match:
            if "SIMULATION_TIMEOUT" in output:
                raise RuntimeError(
                    "Verilog simulation timed out."
                )

            raise RuntimeError(
                "Could not retrieve the SHA-256 hash.\n"
                + output
                + simulation_result.stderr
            )

        return match.group(1).lower()
