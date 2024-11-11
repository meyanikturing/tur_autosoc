from litex.soc.interconnect import stream
from litex.soc.interconnect.csr import *
from litex.soc.interconnect import wishbone #for bus connections

class gpio_controller(Module):
    def __init__(self, platform, idr_pins, odr_pins):

        platform.add_source("./gpio.v")
                
        self.bus = bus = wishbone.Interface(addressing="byte")

        self.idr_pins = idr_pins
        self.odr_pins = odr_pins

        self.clk = Signal()
        self.rst_n = Signal()
        self.wb_dat_i = Signal(32)
        self.wb_dat_o = Signal(32)
        self.wb_adr_i = Signal(32)
        self.wb_we_i = Signal()
        self.wb_stb_i = Signal()
        self.wb_cyc_i = Signal()
        self.wb_ack_o = Signal()
        self.gpio_idr = Signal(16)
        self.gpio_odr = Signal(16)

        # # #

        self.specials += Instance("gpio_controller",
            i_clk=self.clk,
            i_rst_n=self.rst_n,
            i_wb_dat_i=self.wb_dat_i,
            o_wb_dat_o=self.wb_dat_o,
            i_wb_adr_i=self.wb_adr_i,
            i_wb_we_i=self.wb_we_i,
            i_wb_stb_i=self.wb_stb_i,
            i_wb_cyc_i=self.wb_cyc_i,
            o_wb_ack_o=self.wb_ack_o,
            i_gpio_idr=self.gpio_idr,
            o_gpio_odr=self.gpio_odr,
        )

        self.comb += [
            self.wb_adr_i.eq(bus.adr),
            self.wb_dat_i.eq(bus.dat_w),
            self.wb_we_i.eq(bus.we),
            self.wb_stb_i.eq(bus.stb),
            self.wb_cyc_i.eq(bus.cyc),
            bus.ack.eq(self.wb_ack_o),
            bus.dat_r.eq(self.wb_dat_o),
            
            self.clk.eq(ClockSignal("sys")),
            self.rst_n.eq(~ResetSignal("sys")),
            self.odr_pins.eq(self.gpio_odr),
            self.gpio_idr.eq(self.idr_pins)
        ]
