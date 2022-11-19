class Main inherits IO {
	s:String;
	z:SELF_TYPE <- out_string("BLAHHH");
	r:Custom <- new Custom;
	v:Custom <- r.copy();
	o:Object;
	main():Object {{
		v.set_int(1);
		out_int(s.length());
		out_string("asldkfj\n\t\\t".concat("asdl\"fkj\r\n"));
		out_string("\n");
		out_string("alskdjf\"\t\r\w\t\\\\g98ynosdhif\nadslkjfh\n".substr(0, 50));
		out_int(r.get_int());
		o.abort();
	}};

};

class Custom {
	x:Int;
	set_int(y:Int):Int { x <- y };
	get_int():Int { x };
};
