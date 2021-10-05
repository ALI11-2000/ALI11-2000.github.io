`include "sq_root.sv"
module top (
    output reg [15:0] o_res,output reg o_done,output reg [3:0] o_cs,o_ns,
    input [15:0] i_num,input clk,rst,i_ready
);

    sq_root s1(
    .res(o_res),.done(o_done),.cs(o_cs),.ns(o_ns),
    .num(i_num),.clk(clk),.reset(rst),.ready(i_ready)
    );

    initial begin
        $dumpfile("dump.vcd");
        $dumpvars(0,top);
    end

endmodule