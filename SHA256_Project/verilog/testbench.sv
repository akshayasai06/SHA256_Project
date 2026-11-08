
`timescale 1ns/1ps

module testbench;

    // -----------------------------------------
    // INPUTS AND OUTPUTS
    // -----------------------------------------

    reg clk;
    reg reset;
    reg start;

    reg [8191:0] message;
    reg [10:0] msg_len;

    wire [255:0] digest;
    wire done;

    reg [8191:0] long_message;

    integer i;
    integer cycles;
    integer pass_count;
    integer fail_count;

    // -----------------------------------------
    // SHA-256 MODULE INSTANTIATION
    // -----------------------------------------

    sha256_top uut (
        .clk(clk),
        .reset(reset),
        .start(start),
        .message(message),
        .msg_len(msg_len),
        .digest(digest),
        .done(done)
    );

    // -----------------------------------------
    // CLOCK GENERATION
    // -----------------------------------------

    always #5 clk = ~clk;

    // -----------------------------------------
    // TEST TASK
    // -----------------------------------------

    task run_test;

        input [8191:0] test_message;
        input [10:0] length;
        input [255:0] expected_hash;

        begin

            // Apply input at falling edge
            @(negedge clk);

            message = test_message;
            msg_len = length;
            start = 1'b1;

            // Give the DUT one clock edge to accept input
            @(negedge clk);
            start = 1'b0;

            // Wait for completion with a timeout
            cycles = 0;

            while ((done !== 1'b1) && (cycles < 2000)) begin
                @(negedge clk);
                cycles = cycles + 1;
            end

            $display("");
            $display("========================================");
            $display("MESSAGE LENGTH : %0d bytes", length);

            if (done !== 1'b1) begin

                $display("ERROR: Simulation timed out!");
                $display("RESULT: FAIL");

                fail_count = fail_count + 1;

            end

            else begin

                $display("GENERATED HASH:");
                $display("%064h", digest);

                $display("EXPECTED HASH:");
                $display("%064h", expected_hash);

                if (digest === expected_hash) begin

                    $display("RESULT: PASS");
                    pass_count = pass_count + 1;

                end

                else begin

                    $display("RESULT: FAIL");
                    fail_count = fail_count + 1;

                end

            end

            $display("========================================");

            // Allow done to return to zero
            @(negedge clk);

        end

    endtask

    // -----------------------------------------
    // MAIN TEST SEQUENCE
    // -----------------------------------------

    initial begin

        clk = 0;
        reset = 1;
        start = 0;

        message = 0;
        msg_len = 0;
        long_message = 0;

        pass_count = 0;
        fail_count = 0;
        cycles = 0;

        // Reset the SHA-256 module
        #20;
        reset = 0;

        // -------------------------------------
        // TEST 1: EMPTY MESSAGE
        // -------------------------------------

        $display("");
        $display("TEST 1: EMPTY MESSAGE");

        run_test(
            8192'b0,
            11'd0,
            256'he3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
        );

        // -------------------------------------
        // TEST 2: abc
        // -------------------------------------

        $display("");
        $display("TEST 2: abc");

        run_test(
    {8'h61, 8'h62, 8'h63, 8168'b0},
    11'd3,
    256'hba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
);

        // -------------------------------------
        // TEST 3: 56 CONSECUTIVE 'a' CHARACTERS
        // -------------------------------------

        $display("");
        $display("TEST 3: 56 CONSECUTIVE a CHARACTERS");

        long_message = 0;

        for (i = 0; i < 56; i = i + 1) begin
            long_message[8191-i*8 -: 8] = 8'h61;
        end

        run_test(
            long_message,
            11'd56,
            256'hb35439a4ac6f0948b6d6f9e3c6af0f5f590ce20f1bde7090ef7970686ec6738a
        );

        // -------------------------------------
        // TEST 4: UTF-8 EMOJI MESSAGE
        // Message: Hi 😊
        // -------------------------------------

        $display("");
        $display("TEST 4: UTF-8 EMOJI MESSAGE (Hi emoji)");

        run_test(
            {
                8'h48,  // H
                8'h69,  // i
                8'h20,  // Space
                8'hF0,  // Emoji UTF-8 byte 1
                8'h9F,  // Emoji UTF-8 byte 2
                8'h98,  // Emoji UTF-8 byte 3
                8'h8A,  // Emoji UTF-8 byte 4
                8136'b0
            },
            11'd7,
            256'h4971ae030223539e954b803966646594acacc904d02346c44f028c65efe2e4da
        );

        // -------------------------------------
        // FINAL TEST SUMMARY
        // -------------------------------------

        $display("");
        $display("========================================");
        $display("         SHA-256 TEST SUMMARY");
        $display("========================================");

        $display("TOTAL TESTS : 4");
        $display("PASSED      : %0d", pass_count);
        $display("FAILED      : %0d", fail_count);

        if (fail_count == 0)
            $display("OVERALL RESULT: ALL TESTS PASSED");
        else
            $display("OVERALL RESULT: SOME TESTS FAILED");

        $display("========================================");

        $finish;

    end

endmodule
