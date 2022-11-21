class Main inherits IO{
 x:Int;
 y:String;
 main(): Object {{ 
                 out_string("test");
                 out_int(5);
                 y <- in_string();
                 x <- in_int();
		out_string(y);
		out_int(x);
                }};
};
