class Main inherits IO {
	x:Bar <- new Bar;
	y:Foo <- new Zed;
	out_int(x:Int):SELF_TYPE { self };
	shared():Int { 3 };
	main():SELF_TYPE {{ out_int(12736); out_string("\n"); }};
};

class Foo inherits IO {
	shared():String { "asdlfkj\n" };
	x:SELF_TYPE <- out_string(shared());
};

class Zed inherits Foo {
	shared():String { "qweiury\n" };	
	y:SELF_TYPE <- out_string(shared());
};

class Bar inherits IO {
	x:IO <- new IO;
	shared():String { "9999" };
	out_string(x:String):SELF_TYPE { out_int(9999) };
	z:SELF_TYPE <- out_string(shared());
};
