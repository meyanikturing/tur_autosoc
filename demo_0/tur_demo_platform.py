
from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform

_io = [
    # Clk / Rst
    ("core_clk", 0, Pins(1) ),
    ("core_rst", 0, Pins(1) ),


    # 7 Segment Display
    ("seg_disp",  0, Pins(1) ),
    ("seg_disp",  1, Pins(1) ),
    ("seg_disp",  2, Pins(1) ),
    ("seg_disp",  3, Pins(1) ),
    ("seg_disp",  4, Pins(1) ),
    ("seg_disp",  5, Pins(1) ),
    ("seg_disp",  6, Pins(1) ),
    ("seg_disp",  7, Pins(1) ),
    ("seg_disp",  8, Pins(1) ),
    ("seg_disp",  9, Pins(1) ),
    ("seg_disp", 10, Pins(1) ),
    ("seg_disp", 11, Pins(1) ),
    ("seg_disp", 12, Pins(1) ),
    ("seg_disp", 13, Pins(1) ),
    ("seg_disp", 14, Pins(1) ),
    ("seg_disp", 15, Pins(1) ),


    # Switches
    ("user_sw",  0, Pins(1) ),
    ("user_sw",  1, Pins(1) ),
    ("user_sw",  2, Pins(1) ),
    ("user_sw",  3, Pins(1) ),
    ("user_sw",  4, Pins(1) ),
    ("user_sw",  5, Pins(1) ),
    ("user_sw",  6, Pins(1) ),
    ("user_sw",  7, Pins(1) ),
    ("user_sw",  8, Pins(1),),
    ("user_sw",  9, Pins(1),),
    ("user_sw", 10, Pins(1) ),
    ("user_sw", 11, Pins(1) ),
    ("user_sw", 12, Pins(1),),
    ("user_sw", 13, Pins(1) ),
    ("user_sw", 14, Pins(1) ),
    ("user_sw", 15, Pins(1) ),

    # Serial UART Pins 
    ("serial", 0,
        Subsignal("tx", Pins(1)),
        Subsignal("rx", Pins(1)),
        1,
    ),
    
]



class Platform(GenericPlatform):
    def __init__(self, vname=""):
        GenericPlatform.__init__(self, "", _io)
        
    def build(self, fragment, build_dir, **kwargs):
        os.makedirs(build_dir, exist_ok=True)
        os.chdir(build_dir)
        top_output = self.get_verilog(fragment, name="top")
        top_output.write("top.v")

    def get_verilog(self, fragment, **kwargs):
        return verilog.convert(fragment, platform=self, regular_comb=False, **kwargs)

    def _new_print_combinatorial_logic_sim(f, ns):
        r = ""
        if f.comb:
            from collections import defaultdict

            target_stmt_map = defaultdict(list)

            for statement in verilog.flat_iteration(f.comb):
                targets = verilog.list_targets(statement)
                for t in targets:
                    target_stmt_map[t].append(statement)

            groups = verilog.group_by_targets(f.comb)

            for n, (t, stmts) in enumerate(target_stmt_map.items()):
                assert isinstance(t, Signal)
                if len(stmts) == 1 and isinstance(stmts[0], verilog._Assign):
                    r += "assign " + verilog._print_node(ns, verilog._AT_BLOCKING, 0, stmts[0])
                else:
                    r += "always @(*) begin\n"
                    # r += "\t" + ns.get_name(t) + " <= " + _print_expression(ns, t.reset)[0] + ";\n"
                    # r += _print_node(ns, _AT_NONBLOCKING, 1, stmts, t)
                    r += "\t" + ns.get_name(t) + " = " + verilog._print_expression(ns, t.reset)[0] + ";\n"
                    r += verilog._print_node(ns, verilog._AT_BLOCKING, 1, stmts, t)
                    r += "end\n"
        r += "\n"
        return r

    verilog._print_combinatorial_logic_sim = _new_print_combinatorial_logic_sim

    def _new_print_module(f, ios, name, ns, attr_translate):
        sigs = verilog.list_signals(f) | verilog.list_special_ios(f, ins=True, outs=True, inouts=True)
        special_outs = verilog.list_special_ios(f, ins=False, outs=True, inouts=True)
        inouts = verilog.list_special_ios(f, ins=False, outs=False, inouts=True)
        targets = verilog.list_targets(f) | special_outs
        wires = verilog._list_comb_wires(f) | special_outs
        r = "module " + name + "(\n"
        r += "`ifdef USE_POWER_PINS\n"
        r += "    inout VPWR,	    /* 1.8V domain */\n"
        r += "    inout VGND,\n"
        r += "`endif\n"
        firstp = True
        for sig in sorted(ios, key=lambda x: x.duid):
            if not firstp:
                r += ",\n"
            firstp = False
            attr = verilog._print_attribute(sig.attr, attr_translate)
            if attr:
                r += "\t" + attr
            sig.type = "wire"
            sig.name = ns.get_name(sig)
            if sig in inouts:
                sig.direction = "inout"
                r += "\tinout wire " + verilog._print_signal(ns, sig)
            elif sig in targets:
                sig.direction = "output"
                if sig in wires:
                    r += "\toutput wire " + verilog._print_signal(ns, sig)
                else:
                    sig.type = "reg"
                    r += "\toutput reg " + verilog._print_signal(ns, sig)
            else:
                sig.direction = "input"
                r += "\tinput wire " + verilog._print_signal(ns, sig)
        r += "\n);\n\n"
        for sig in sorted(sigs - ios, key=lambda x: x.duid):
            attr = verilog._print_attribute(sig.attr, attr_translate)
            if attr:
                r += attr + " "
            if sig in wires:
                r += "wire " + verilog._print_signal(ns, sig) + ";\n"
            else:
                r += "reg " + verilog._print_signal(ns, sig) + " = " + verilog._print_expression(ns, sig.reset)[0] + ";\n"
        r += "\n"
        return r

    verilog._print_module = _new_print_module