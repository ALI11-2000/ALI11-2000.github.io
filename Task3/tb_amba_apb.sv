`timescale 1ns/1ns
module tb_amba_apb;

reg pclk,preset,transfer,mpwrite;
reg [7:0] apb_write_paddr,apb_write_data,apb_read_paddr;
wire [7:0] prdata,apb_read_data_out;

top_amba_apb dut(pclk,preset,transfer,mpwrite,apb_write_paddr,apb_write_data,apb_read_paddr,prdata,apb_read_data_out,psel,penable);

initial begin
    pclk = 1'b0;
    forever #5 pclk = ~pclk;
end

initial 
begin
transfer = 0;
preset=1'b1;
#10;
preset=1'b0;
#50;
preset=1'b1;
#10;
preset=1'b0;
@(posedge pclk);
transfer = 1;
mpwrite = 1;
apb_write_paddr = 8'd3;
apb_write_data = 8'h21;
repeat(3)@(posedge pclk)
transfer = 0;
@(posedge pclk)
transfer = 1;
mpwrite = 1;
apb_write_paddr = 8'd14;
apb_write_data = 8'h50;
repeat(3)@(posedge pclk)
transfer = 1;
mpwrite = 0;
apb_write_paddr = 8'd3;
apb_write_data = 8'h50;
repeat(3)@(posedge pclk)
transfer = 1;
mpwrite = 0;
apb_write_paddr = 8'd14;
apb_write_data = 8'd50;
repeat(3)@(posedge pclk);
$stop;
end



    
endmodule