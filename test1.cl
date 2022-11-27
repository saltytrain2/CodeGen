class Main inherits IO {
	s:String;
	z:SELF_TYPE <- out_string("BLAHHH");
	a:Custom <- new Custom;
	r:Custom <- new Derived;
	v:Custom <- r.copy();
	o:Object;
	main():Object {{
		v.set_int(1);
		a.set_int(20);
		r.set_int(97);
		out_int(s.length());
		out_string("asldkfj\n\t\\t".concat("asdl\"fkj\r\n"));
		out_string("\n");
		out_string("alskdjf\"\t\r\w\t\\\\g98ynosdhif\nadslkjfh\n".substr(5, 26));
		out_int(r.get_int());
		out_int(v.get_int());
		z.print();
		out_string(v.type_name());
		o.abort();
	}};

	print() :SELF_TYPE { out_string("Main\n") };

};

class Custom {
	x:Int;
	set_int(y:Int):Int { x <- y };
	get_int():Int { x };
};

class Derived inherits Custom {
	set_int(y:Int):Int { x <- y / 2 };
	get_int() : Int { x + 3 };
};
