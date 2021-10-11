
module amba_apb_slave
(input pclk,preset,psel,penable,pwrite,
input [7:0]paddr,pwdata,
output reg pready,
output reg [7:0]prdata,

output reg [7:0] mem [63:0]);

integer i;
always @(posedge pclk)
begin
	pready = 0;
	if(preset) begin
		prdata <= 8'b0;
		for(i=0;i<=63;i++)
		  	mem[i] <= 8'b0;
	end else
	begin
		if((psel==1'b1)&&(penable==1'b1)&&(pwrite==1'b1)) begin
			mem[paddr] <= pwdata;
			pready <= 1;
		end else 
		if((psel==1'b1)&&(penable==1'b1)&&(pwrite==1'b0)) begin
			prdata <= mem[paddr];
			pready <= 1;
		end
	end
end

	initial begin
		pready = 0;
		$dumpfile("dump.vcd");
		$dumpvars;
	end
endmodule 
