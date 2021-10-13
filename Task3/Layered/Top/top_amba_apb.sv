//top_amba_apb
`include "amba_apb_master.sv"
`include "amba_apb_slave.sv"
module top_amba_apb(input pclk,preset,transfer,mpwrite,
input [7:0] apb_write_paddr,apb_write_data,apb_read_paddr,
output reg [7:0]prdata,apb_read_data_out ,output psel,penable);

wire pready,pwrite;
wire [7:0] paddr,pwdata;

amba_apb_master a1(.pclk(pclk),.preset(preset),.transfer(transfer),.mpwrite(mpwrite),.pready(pready),
.apb_write_paddr(apb_write_paddr),.apb_write_data(apb_write_data),.apb_read_paddr(apb_read_paddr),.prdata(prdata),
.psel(psel),.penable(penable),.spwrite(pwrite),.paddr(paddr),.pwdata(pwdata),.apb_read_data_out(apb_read_data_out));

amba_apb_slave a2(.pclk(pclk),.preset(preset),.psel(psel),.penable(penable),.pwrite(pwrite),
.paddr(paddr),.pwdata(pwdata),.pready(pready),.prdata(prdata));


initial begin
    $dumpfile("dump.vcd");
    $dumpvars(0,top_amba_apb);
end

endmodule
