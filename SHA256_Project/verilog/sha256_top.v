
`timescale 1ns/1ps

module sha256_top (
    input wire clk,
    input wire reset,
    input wire start,
    input wire [8191:0] message,
    input wire [10:0] msg_len,
    output reg [255:0] digest,
    output reg done
);

    reg [7:0] padded_mem [0:1087];
    reg [31:0] W [0:63];

    reg [31:0] H0,H1,H2,H3,H4,H5,H6,H7;
    reg [31:0] a,b,c,d,e,f,g,h;
    reg [31:0] T1,T2;

    reg [63:0] bit_length;

    integer padded_len;
    integer total_blocks;
    integer block_index;
    integer i;

    reg [5:0] round_count;
    reg [1:0] state;

    localparam IDLE  = 2'd0;
    localparam LOAD  = 2'd1;
    localparam ROUND = 2'd2;

    // ROTATE RIGHT
    function [31:0] ROTR;
        input [31:0] x;
        input integer n;
        begin
            ROTR = (x >> n) | (x << (32-n));
        end
    endfunction

    // CHOICE
    function [31:0] CH;
        input [31:0] x,y,z;
        begin
            CH = (x & y) ^ (~x & z);
        end
    endfunction

    // MAJORITY
    function [31:0] MAJ;
        input [31:0] x,y,z;
        begin
            MAJ = (x & y) ^ (x & z) ^ (y & z);
        end
    endfunction

    // BIG SIGMA 0
    function [31:0] BSIG0;
        input [31:0] x;
        begin
            BSIG0 = ROTR(x,2) ^ ROTR(x,13) ^ ROTR(x,22);
        end
    endfunction

    // BIG SIGMA 1
    function [31:0] BSIG1;
        input [31:0] x;
        begin
            BSIG1 = ROTR(x,6) ^ ROTR(x,11) ^ ROTR(x,25);
        end
    endfunction

    // SMALL SIGMA 0
    function [31:0] SSIG0;
        input [31:0] x;
        begin
            SSIG0 = ROTR(x,7) ^ ROTR(x,18) ^ (x >> 3);
        end
    endfunction

    // SMALL SIGMA 1
    function [31:0] SSIG1;
        input [31:0] x;
        begin
            SSIG1 = ROTR(x,17) ^ ROTR(x,19) ^ (x >> 10);
        end
    endfunction

    // SHA-256 CONSTANTS
    function [31:0] K;
        input [5:0] index;
        begin
            case(index)
                0: K=32'h428a2f98;
                1: K=32'h71374491;
                2: K=32'hb5c0fbcf;
                3: K=32'he9b5dba5;
                4: K=32'h3956c25b;
                5: K=32'h59f111f1;
                6: K=32'h923f82a4;
                7: K=32'hab1c5ed5;
                8: K=32'hd807aa98;
                9: K=32'h12835b01;
                10: K=32'h243185be;
                11: K=32'h550c7dc3;
                12: K=32'h72be5d74;
                13: K=32'h80deb1fe;
                14: K=32'h9bdc06a7;
                15: K=32'hc19bf174;
                16: K=32'he49b69c1;
                17: K=32'hefbe4786;
                18: K=32'h0fc19dc6;
                19: K=32'h240ca1cc;
                20: K=32'h2de92c6f;
                21: K=32'h4a7484aa;
                22: K=32'h5cb0a9dc;
                23: K=32'h76f988da;
                24: K=32'h983e5152;
                25: K=32'ha831c66d;
                26: K=32'hb00327c8;
                27: K=32'hbf597fc7;
                28: K=32'hc6e00bf3;
                29: K=32'hd5a79147;
                30: K=32'h06ca6351;
                31: K=32'h14292967;
                32: K=32'h27b70a85;
                33: K=32'h2e1b2138;
                34: K=32'h4d2c6dfc;
                35: K=32'h53380d13;
                36: K=32'h650a7354;
                37: K=32'h766a0abb;
                38: K=32'h81c2c92e;
                39: K=32'h92722c85;
                40: K=32'ha2bfe8a1;
                41: K=32'ha81a664b;
                42: K=32'hc24b8b70;
                43: K=32'hc76c51a3;
                44: K=32'hd192e819;
                45: K=32'hd6990624;
                46: K=32'hf40e3585;
                47: K=32'h106aa070;
                48: K=32'h19a4c116;
                49: K=32'h1e376c08;
                50: K=32'h2748774c;
                51: K=32'h34b0bcb5;
                52: K=32'h391c0cb3;
                53: K=32'h4ed8aa4a;
                54: K=32'h5b9cca4f;
                55: K=32'h682e6ff3;
                56: K=32'h748f82ee;
                57: K=32'h78a5636f;
                58: K=32'h84c87814;
                59: K=32'h8cc70208;
                60: K=32'h90befffa;
                61: K=32'ha4506ceb;
                62: K=32'hbef9a3f7;
                63: K=32'hc67178f2;
                default: K=32'h00000000;
            endcase
        end
    endfunction

    // MAIN CONTROLLER
    always @(posedge clk or posedge reset) begin

        if (reset) begin
            state <= IDLE;
            done <= 0;
            digest <= 0;
            round_count <= 0;
            block_index <= 0;

            H0 <= 32'h6a09e667;
            H1 <= 32'hbb67ae85;
            H2 <= 32'h3c6ef372;
            H3 <= 32'ha54ff53a;
            H4 <= 32'h510e527f;
            H5 <= 32'h9b05688c;
            H6 <= 32'h1f83d9ab;
            H7 <= 32'h5be0cd19;
        end

        else begin

            case(state)

                // IDLE STATE
                IDLE: begin
                    done <= 0;

                    if (start && msg_len <= 1024) begin

                        // INITIAL HASH VALUES
                        H0 = 32'h6a09e667;
                        H1 = 32'hbb67ae85;
                        H2 = 32'h3c6ef372;
                        H3 = 32'ha54ff53a;
                        H4 = 32'h510e527f;
                        H5 = 32'h9b05688c;
                        H6 = 32'h1f83d9ab;
                        H7 = 32'h5be0cd19;

                        // CLEAR PADDED MEMORY
                        for (i=0; i<1088; i=i+1)
                            padded_mem[i] = 8'h00;

                        // COPY MESSAGE BYTES
                        for (i=0; i<msg_len; i=i+1)
                            padded_mem[i] =
                                message[8191-i*8 -: 8];

                        // MESSAGE LENGTH IN BITS
                        bit_length = {53'b0,msg_len} << 3;

                        // PADDED MESSAGE LENGTH
                        padded_len =
                            ((msg_len + 9 + 63) / 64) * 64;

                        // ADD PADDING BIT
                        padded_mem[msg_len] = 8'h80;

                        // APPEND 64-BIT LENGTH
                        padded_mem[padded_len-8] = bit_length[63:56];
                        padded_mem[padded_len-7] = bit_length[55:48];
                        padded_mem[padded_len-6] = bit_length[47:40];
                        padded_mem[padded_len-5] = bit_length[39:32];
                        padded_mem[padded_len-4] = bit_length[31:24];
                        padded_mem[padded_len-3] = bit_length[23:16];
                        padded_mem[padded_len-2] = bit_length[15:8];
                        padded_mem[padded_len-1] = bit_length[7:0];

                        total_blocks = padded_len / 64;

                        block_index <= 0;
                        round_count <= 0;
                        state <= LOAD;
                    end
                end

                // LOAD STATE
                LOAD: begin

                    // LOAD FIRST 16 WORDS
                    for (i=0; i<16; i=i+1) begin
                        W[i] = {
                            padded_mem[block_index*64+i*4],
                            padded_mem[block_index*64+i*4+1],
                            padded_mem[block_index*64+i*4+2],
                            padded_mem[block_index*64+i*4+3]
                        };
                    end

                    // GENERATE REMAINING WORDS
                    for (i=16; i<64; i=i+1) begin
                        W[i] = SSIG1(W[i-2]) +
                               W[i-7] +
                               SSIG0(W[i-15]) +
                               W[i-16];
                    end

                    a <= H0;
                    b <= H1;
                    c <= H2;
                    d <= H3;
                    e <= H4;
                    f <= H5;
                    g <= H6;
                    h <= H7;

                    round_count <= 0;
                    state <= ROUND;
                end

                // ROUND STATE
                ROUND: begin

                    T1 = h + BSIG1(e) + CH(e,f,g)
                         + K(round_count) + W[round_count];

                    T2 = BSIG0(a) + MAJ(a,b,c);

                    h <= g;
                    g <= f;
                    f <= e;
                    e <= d + T1;
                    d <= c;
                    c <= b;
                    b <= a;
                    a <= T1 + T2;

                    if (round_count == 63) begin

                        // UPDATE HASH VALUES
                        H0 <= H0 + T1 + T2;
                        H1 <= H1 + a;
                        H2 <= H2 + b;
                        H3 <= H3 + c;
                        H4 <= H4 + d + T1;
                        H5 <= H5 + e;
                        H6 <= H6 + f;
                        H7 <= H7 + g;

                        if (block_index == total_blocks-1) begin

                            digest <= {
                                H0 + T1 + T2,
                                H1 + a,
                                H2 + b,
                                H3 + c,
                                H4 + d + T1,
                                H5 + e,
                                H6 + f,
                                H7 + g
                            };

                            done <= 1;
                            state <= IDLE;
                        end

                        else begin
                            block_index <= block_index + 1;
                            state <= LOAD;
                        end

                    end

                    else begin
                        round_count <= round_count + 1;
                    end

                end

                default: state <= IDLE;

            endcase
        end
    end

endmodule
