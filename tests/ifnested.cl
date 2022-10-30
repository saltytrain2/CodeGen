class Main {
	main():Int { 3 };
};

class Foo {
	x:Int;
};

class Test {
  x:Int;
  bar():Int { if x = 3 then {if x < 2 then new Foo else isvoid baz fi;} else false fi};
};
