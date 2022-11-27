class Foo {};

class Main inherits IO {
	x:Foo <- new Foo;
	y:Foo <- new Foo;
	z:Foo <- y;

	counter:Int <- 0;
	ref:Base <- new Base;
	topLevel:Base <- new DerivedFour;

	main():Object {{
		if 5 < 10 then out_int(0) else 0 fi ;
		if 15 < 10 then out_int(1) else 0 fi ;
		if "STRIN" <= "STRING" then out_int(2) else 0 fi;
		if "SOIUE" < "SOIUE" then out_int(3) else 0 fi;
		if 10 <= 10 then out_int(4) else 0 fi;
		if 30 = 30 then out_int(5) else 0 fi;
		if true < false then out_int(6) else 0 fi;
		if false < true then out_int(7) else 0 fi;
		if x = y then out_int(8) else 0 fi;
		if x = z then out_int(9) else 0 fi;
		out_string("\n");
		if y = z then out_int(0) else 0 fi;
		if y < z then out_int(1) else 0 fi;
		if z <= y then out_int(2) else 0 fi;
		if 10 * ~3 = ~30 then out_int(3) else 0 fi;
		
		while not topLevel = ref loop {
			topLevel.print();
			counter <- counter + 1;
			case topLevel of
				x:IO => topLevel <- new DerivedOne;
				x:DerivedOne=> topLevel <- new DerivedFive;
				x:DerivedTwo => topLevel <- new DerivedFour;
				x:DerivedThree => topLevel <- new Base;
				x:DerivedFour => topLevel <- new DerivedThree;
				x:DerivedFive => topLevel <- new DerivedTwo;
			esac;
			topLevel.print();
			more_collusion(counter);
		} pool;
	}};

	more_collusion(y:Int):Object {{
		if mod(y, 13) = 0 then topLevel <- new DerivedThree else 0 fi;
		topLevel.print();
		if mod(y, 126) = 0 then topLevel <- ref else 0 fi;
	}};

	mod(x:Int, rhs:Int):Int { x - x / rhs * rhs };
};


class Base  inherits IO {
	print():Object { out_string("Base\n") };
};


class DerivedOne inherits Base {
	print():Object { out_string("Derived1\n") };
};

class DerivedTwo inherits DerivedOne {
	print():Object { out_string("DerivedTwo\n") };
};

class DerivedThree inherits DerivedTwo {
	print():Object { out_string("DerivedThree\n") };
};

class DerivedFour inherits DerivedThree {
	print():Object { out_string("DerivedFour\n") };
};

class DerivedFive inherits DerivedFour {
	print():Object { out_string("DerivedFive\n") };
};

