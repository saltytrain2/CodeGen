class Main inherits IO {
	w:IO <- new IO;
	z:FakeIO <- new FakeIO;
	x:Int <- in_int();
	y:String <- w.in_string();
	main():Object {{
		w.out_int(x);
		out_string("\n");
		w.out_int(z.out_string(y));
	}};
};

class FakeIO {
	z:IO <- new IO;
	out_string(x:String):Int {{ z.out_string(x); 666; }};
};
