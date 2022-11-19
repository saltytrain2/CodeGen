class Main inherits IO {
	w:IO <- new IO;
	x:Int <- in_int();
	y:String <- w.in_string();
	main():Object {{
		out_int(x);
		out_string("\n");
		out_string(y);
	}};
};
