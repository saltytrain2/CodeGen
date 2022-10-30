class Main inherits IO {
  my_void_io : IO ; -- no initializer =\> void value
  main() : Object {
    my_void_io.out_string("Hello, world.\n")
  } ;
} ;
