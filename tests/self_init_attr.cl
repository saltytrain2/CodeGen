class Base inherits IO {
	b: Int <- { report(1); 1; };

	report(a: Int): SELF_TYPE {{
		out_string("zaza\n");
		out_int(a + b);
	}};
};

class Derived inherits Base {
	a: Int <- { report(2); 2; };

	report(b: Int): SELF_TYPE {{
		out_string("blah\n");
		out_int(a);
		a <- b;
		out_string("blah\n");
		out_int(a);
		self@Base.report(b);
	}};
};


class Main {
	main():Object { (new Derived).report(5) };
};

