class Main inherits IO {
	x:SELF_TYPE <- copy().init(5);
	y:Int;
	init(x:Int):SELF_TYPE {{ y <- x; self; }};
	get_y():Int { y };
	main():Object {{ out_int(y); out_int(x.get_y()); }};
};
