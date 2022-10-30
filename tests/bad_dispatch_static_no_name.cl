class Foo {
	x():Int { 3 };
};

class Main inherits Foo {
	y():Int { 4 };
	main():Int { self@Foo.y() };
};
