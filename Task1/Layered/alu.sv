`timescale 1ns/1ns

module alu #(
    parameter integer width = 5
) (
    output reg [width:0] o_X,
    input [width:0] i_A,i_B,input [3:0] i_sel
);
    always_comb begin 
        case (i_sel)
            4'd0: o_X = i_A + i_B;
            4'd1: begin 
                if ( i_A > i_B)
                    o_X = i_A - i_B;
                else
                    o_X= i_B - i_A;
            end
            4'd2: o_X = i_A > i_B;
            4'd3: o_X = i_A & i_B;
            4'd4: o_X = i_A | i_B;
            4'd5: o_X = i_A ^ i_B;
            4'd6: o_X = i_A;
            4'd7: o_X = i_B;
            default: o_X = i_A;
        endcase
    end

    initial begin
        $dumpfile("dump.vcd");
        $dumpvars;
    end
    
endmodule
