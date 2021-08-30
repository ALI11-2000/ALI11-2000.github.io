`timescale 1ns/1ns

module alu #(
    parameter integer width = 5
) (
    output reg [width:0] X,
    input [width:0] A,B,input [3:0] sel
);
    always_comb begin 
        case (sel)
            4'd0: X = A + B;
            4'd1: begin 
                if ( A > B)
                    X = A - B;
                else
                    X= B - A;
            end
            4'd2: X = A > B;
            4'd3: X = A & B;
            4'd4: X = A | B;
            4'd5: X = A ^ B;
            4'd6: X = A;
            4'd7: X = B;
            default: X = A;
        endcase
    end
    
endmodule
