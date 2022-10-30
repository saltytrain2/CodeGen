class Main inherits IO {
	x : Int <- 0;
	y : Int;
	z(x:Int) : Int {
		x
	};
	main():Int { 3 };
};

class Foo inherits Main {
	w : Int <- 1;
};

class Bar 
inherits FoO {
	v : Int <- 2;
};
