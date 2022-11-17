class Main inherits IO {
	a:Z <- new Z;
	p():SELF_TYPE { out_string("asdf\n") };
	main():Object { (a.m()).p() };
};

class Z inherits IO {
	p():SELF_TYPE { out_string("qwer\n") };
	m():SELF_TYPE { self };
};

