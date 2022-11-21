class A inherits IO {
    test(b: B, a: A) : SELF_TYPE {{
        b.print();
	a.print();
	self;
    }};
    print() : SELF_TYPE { out_string("A\n") };
};

class B inherits A {
    a() : SELF_TYPE {
        let b : SELF_TYPE <- new SELF_TYPE in
            test(b, b)
    };
    print():SELF_TYPE { out_string("B\n") };
};

class Main {
    main() : Object {
        (new B).a()
    };
};
