class Main inherits IO {
 b:B <- new B;
 main(): Object { if not b@A.foo(5,b,b,b) then out_string("Bar\n") else out_string("Baz\n") fi }; 
};

class A inherits IO {
    foo(a:Int, b: B, c:A, d:B) : Bool {{
       out_int(5); true;
    }};
  
};

class B inherits A {

    foo(a:Int, b: B, c:A, d:B) : Bool {{
       out_int(6); false;
    }};  
};



