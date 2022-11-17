class Main inherits IO {
	s:String;
	r:Custom <- new Custom;
	v:Custom <- r.copy();
	main():Object {{
		v.set_int(1);
		s.concat("BLAHHH");
		out_string(s);
		out_string("\n");
		out_int(r.get_int());
	}};

};

class Custom {
	x:Int;
	set_int(y:Int):Int { x <- y };
	get_int():Int { x };
};
