class Main inherits IO{
 x:Bool;
 y:IO;
 z:X;
 main(): Object {{ 
                   if isvoid true then
			out_int(1)
		   else 
			out_int(2)
		   fi;
		   if isvoid false then
			out_int(3)
		   else
			out_int(4)
		   fi;
		   if isvoid x then
			out_int(5)
		   else
			out_int(6)
		   fi;
		   if isvoid y then
			out_int(7)
		   else 
			out_int(8)
		   fi;
		   if isvoid z then
			out_int(9)
		   else
			out_int(0)
		   fi;
		   out_string("\n");
                }};
};


class X {
	x:Int;
};
