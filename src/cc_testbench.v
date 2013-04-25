//Module: cc_testbench.v

`timescale 1ns/1ps

module cc_testbench();

    parameter Halfcycle = 5; //half period is 5ns
    
    localparam Cycle = 2*Halfcycle;
    
    reg Clock;
    
    // Clock Signal generation:
    initial Clock = 0; 
    always #(Halfcycle) Clock = ~Clock;

   // Register and wires to test the cross correlation
   reg  [15:0] A [0:19200];
   reg  [15:0] B [0:19200];
   reg  [17:0] addr;
   wire [9:0]  DUTout;
   reg  [9:0]  REFout;
   reg         rst, start;
   wire        done;
   wire        testing;
    

   //Task for checking the output
   task checkOutput;
      if (($signed(REFout) - $signed(DUTout) >= -1) && ($signed(REFout) - $signed(DUTout) <= 1)) begin
           $display("PASS    DUTout: %d, REFout: %d", $signed(DUTout), $signed(REFout));
        end
        else begin
           $display("FAIL    DUTout: %d, REFout: %d", $signed(DUTout), $signed(REFout));
	   //$finish();
        end
    endtask
   
   //This is where the modules being tested are instantiated.
   cc_1 cc_test(.rst(rst), .start(start), .m0(A[addr]), .m1(B[addr]), .clk(Clock), .index(DUTout), .done(done), .testing(testing));
   integer i;
   initial begin
      $display("\n\nSTARTING ALL TESTS");
      $readmemb( "/home/cc/cs150/sp13/class/cs150-ad/cross_correlation/src/sineCraft/sines0.txt", A);
      $readmemb("/home/cc/cs150/sp13/class/cs150-ad/cross_correlation/src/sineCraft/sines1.txt", B);
      
      REFout = -25;
      addr = 0;
      rst = 1;
      #10;
      rst = ~rst;
      start = 1;
      
      #10;
      start = 0;

      $display("\n\nENTERING FOR LOOP"); 

      // ReadInputs
      for(i = 0; i < 12800; i=i+1) begin
	 $display("addr=%6.0d  A=%5.0d  B=%5.0d", addr, A[addr], B[addr]);
	 
	 addr = addr +1;
	 #10;
      end

      // Busy
      while(~done) begin
	 #10;
      end

      // Done (WriteOutputs)
      for(i = 0; i < 12800; i=i+1) begin
	 checkOutput();
	 #10;
      end

      $finish();   
   end
endmodule
     
   
