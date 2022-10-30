class Main 
inherits IO {

	main() : 
	Object {
		let balanced : EmptyIntTree <- new EmptyIntTree,
			unbalanced : EmptyIntTree <- new EmptyIntTree in {
			balanced <- balanced.insert(6);
			balanced <- balanced.insert(8);
				let balanced : EmptyIntTree <- new EmptyIntTree,
					dummy : DummyClass in {
					balanced.print_inorder();
					dummy <- new DummyClass;
					dummy.print();
				};
			balanced <- balanced.insert(5);
			balanced <- balanced.insert(2);
			balanced <- balanced.insert(7);
			balanced <- balanced.insert(10);
			balanced <- balanced.insert(21);
			balanced <- balanced.double_root();
			balanced.printVal();
			balanced.print_inorder();
			balanced@EmptyIntTree.print_inorder();
		}
	};
};

class EmptyIntTree inherits IO {
	isNull() : Bool { tRUE };
	getVal() : Int { 0 };
	getLeft() : EmptyIntTree { new EmptyIntTree };
	getRight() : SELF_TYPE { self };
	getCount() : Int { 0 };
	add(val : Int) : Int { 0 };
	print_inorder() : Object { true };
	printVal() : Object { true };
	insert(val : Int) : EmptyIntTree { (new IntTreeNode).init(val, self, self) };
	double_root() : EmptyIntTree { self };
};


class IntTreeNode inherits EmptyIntTree {
	mVal : Int <- 0;
	mLeft : EmptyIntTree <- new EmptyIntTree;
	mRight : EmptyIntTree <- new EmptyIntTree;
	mDummy : EmptyIntTree;
	
	init(val : Int, left : EmptyIntTree, right : EmptyIntTree) : IntTreeNode {
		{
			mVal <- val;
			mLeft <- left;
			mRight <- right;
			self;
		}
	};

	isNull() : Bool { false }; -- try some comments
	getVal() : Int { mVal };
	getCount() : Int { 1 + mRight.getCount() + mLeft.getCount() };
	add(val : Int) : Int { mVal <- mVal + val };

	insert(val : Int) : EmptyIntTree {
		{
			if not not val 
			< mVal then {
				val <- val * 1;
				mLeft <- mLeft.insert(val);
			}
			else if mVal < val then
				mRight <- mRight.insert(val)
			else
				self
			fi fi;
			self;
		}
	};
	
	printVal() : Object {
		{
			out_string("num elements: ");
			out_int(getCount());
			out_string("\n");
		}
	};

	print_inorder() : Object {
		{
			mLeft.print_inorder();
			out_int(mVal);
			out_string("\n");
			mRight.print_inorder();
		}
	};

	double_root() : EmptyIntTree {{
		mVal <- (5 + 2 * 6 / 3 * 5 - 23) * mVal;
		self;
	}};
};



class DummyClass {
	print() : Object {
		true
	};
};
