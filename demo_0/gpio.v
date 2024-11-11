`timescale 1ns/1ps

module gpio_controller(
    input wire clk,    // Wishbone clock
    input wire rst_n,    // Wishbone reset
    input wire [31:0] wb_dat_i, // Wishbone data input
    output reg [31:0] wb_dat_o, // Wishbone data output
    input wire [31:0] wb_adr_i, // Wishbone address input
    input wire wb_we_i,     // Wishbone write enable
    input wire wb_stb_i,    // Wishbone strobe
    input wire wb_cyc_i,
    output reg wb_ack_o,    // Wishbone acknowledge output

    input wire [15:0]gpio_idr,
    output reg [15:0]gpio_odr
);

//----------------------------------------------------------------------------------------

localparam GPIO_MEM_ADDR = 32'h8000_1000; // BE CAREFUL THAT ADDRESS MUST MATCH THE SOC ADDRESS ON BASE SCRIPT !!!

//----------------------------------------------------------------------------------------

// Register Addresses
localparam GPIO_IDR_ADDR = GPIO_MEM_ADDR + 32'h0;
localparam GPIO_ODR_ADDR = GPIO_MEM_ADDR + 32'h04;


// Wishbone interface logic
always @(posedge clk, negedge rst_n) begin
    if (~rst_n) begin
        // Reset all registers
        gpio_odr <= 0;
        wb_ack_o <= 0;
        wb_dat_o <= 0;
    end else begin
        wb_ack_o <= wb_cyc_i && wb_stb_i;
        if (wb_stb_i && wb_cyc_i) begin // Strobe and not already acknowledged
            if (wb_we_i) begin // Write operation
                case (wb_adr_i)
                    GPIO_ODR_ADDR: gpio_odr <= wb_dat_i[15:0];
                endcase
            end else begin // Read operation
                case (wb_adr_i)
                    GPIO_IDR_ADDR: wb_dat_o <= {16'h0, gpio_idr};
                    GPIO_ODR_ADDR: wb_dat_o <= {16'h0, gpio_odr};
                    default :     wb_dat_o <= 32'hFFFFFFFF;
                endcase
            end
        end
    end
end

endmodule