class Main inherits IO{
 x: Int;
 main(): Object {{ 
		   if ((let x:Int <- 5 in x+3)+3 = 9) then {out_int(3); out_string("\n");} else foo() fi;
                }};
 foo(): SELF_TYPE {out_string("asdlkfj\n")};
};
