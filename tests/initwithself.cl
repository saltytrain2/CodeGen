class Main inherits IO{
 x:SELF_TYPE <- self;
 y:Int;
 main(): Object {{
		   y <- 3;
             	   print();
		   y <- 10;
		   x.out_int(y);
		   x.print();
		   out_string("alskdfj\n");
                }};

print():SELF_TYPE { out_int(y) };
};
