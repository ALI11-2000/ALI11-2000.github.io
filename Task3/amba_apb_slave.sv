
module amba_apb_slave
(input pclk,preset,psel,penable,pwrite,
input [7:0]paddr,pwdata,
output reg pready,
output reg [7:0]prdata);

reg [7:0] mem [63:0];
integer i;
always @(posedge pclk)
begin
	if(preset) begin
		prdata <= 8'b0;
		for(i=0;i<=63;i++);
		  mem[i] = 8'b0;
	end else
	begin
		if((psel==1'b1)&&(penable==1'b1)&&(pwrite==1'b1))
			mem[paddr]<=pwdata;
		else
		if((psel==1'b1)&&(penable==1'b1)&&(pwrite==1'b0))
			prdata<=mem[paddr];
	end
end
always @(psel,penable)
begin
if(psel==1'b1&&penable==1'b1)
	pready = 1'b1;
else
	pready = 1'b0;
end
endmodule 
