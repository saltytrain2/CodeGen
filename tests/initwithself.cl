class Main inherits IO{
 x:SELF_TYPE <- self;
 y:Int <- 3;
 main(): Object {{
             	   out_int(y);
		   y <- 10;
		   x.out_int(y);
		   out_string("alskdfj\n");
                }};
};
