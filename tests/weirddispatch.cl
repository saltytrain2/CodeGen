class A {
    test(b: B, a: A) : SELF_TYPE {
        self
    };
};

class B inherits A {
    a() : SELF_TYPE {
        let b : SELF_TYPE <- new SELF_TYPE in
            test(b, b)
    };
};

class Main {
    main() : Object {
        0
    };
};