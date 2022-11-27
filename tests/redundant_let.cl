class Main inherits IO {
	x:Int <- 3;
	main():Object {
		let x:Int <- 3, x:Int <- x + 3, z:Int <- x + 6 in
			let x:Int <- x + 3, y:Int<- x * 6, x:Int <- x + 6, z:Int <- y * 2 in
				let y:Int <- z + 10, x:Int <- y + x + z / 3 in
					out_int(x + y + z)
	};
};
