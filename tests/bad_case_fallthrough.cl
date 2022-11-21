class Main inherits IO {
	x:String;
	main():Object { case x of 
		x : Bool => out_string("asdlfkj\n");
		x : Int => out_string("zxcmvnb\n");
		x : IO => out_string("qwioeru\n");
		x: Object => out_string("\n");
	esac
	};
};
