class Hello {
    moo() : Int { 0 };
    cow(a: Int) : Object { moo() };

    how(a: String, b: Int): Hoho {
        { self.cow(5); new Hoho; }
    };
};

class Hoho {};

class A inherits Hello {
    hel56: IO;
    moo: SELF_TYPE;

    cow(a: Int) : Object {
        { moo@Hello.how("Hello", 5); self; }
    };
};

class Main {
    main() : Object {
        0
    };
};