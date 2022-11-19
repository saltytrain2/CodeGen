class Main inherits IO {
	x:String;
	y:Int <- 444;
	z:Int <- 555;
	main():Object {{ out_int(222/333-y*z+666-777); out_string("\n"); }};
	str():Object { out_string(x) };
};

class Z {
	main():Object { 3 };
};
