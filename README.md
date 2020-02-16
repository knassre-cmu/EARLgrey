EARLgrey: Easily Acessible Routine Language
(If the most popular imperative language is Java, then its opposite should be a type of tea!)

EARLgrey is a functional programming language designed to make functional programming accessible. It runs on Python using the Carnegie Mellon 15-112 graphics file (which uses tkinter).
EARLgrey is built on five fundemental types: Number (floats), Vocab (strings), Logic (boolean), Union (list), and Transform (function).

Syntax guide:

1. All lines are seperated by semicolons, i.e., whatever is between semicolons is consered a line.

  Good code:
  
    x := 4; y := 6; 
    
    z := add(x,y,5);
    
  Bad code:
  
    x := 4
    
    y := 6
    
    z := add(x,y,5)
    
2. The only legal statements are argumentative expressions that evaluate and assign the output to a variable nondestructively, and without shadowing or overwriting. The walrus operator (:=) must be used for values while the smirking operator ($=) must be used for creating transforms in genesis notation.

  Good code:
  
    x := 4;
    
    y $= n => add(n,1);
    
    z = mul(x,y(x));
    
  Bad code:
  
    x = 4;
    
    y := n => mul(n,2);
    
    x := y(x);
    
3. Function calls are made with comma-seperated paranthetical notation. Unions are deliniated by triangular brackets (< and >) while vocabs are deliniated by double quotes (" and "). Currently, nested comma-seperated values are not legal.

  Good code:
  
    x := <1, 2, 3>;
    
    y := "a BC d";
    
    z := add(1, 2, 3, 4);
    
  Bad code:
  
    x := (1, 2, 3);
    
    y := 'a BC d];
    
    z := add 1, 2, 3, 4;
    
4. Transforms can be created using genesis notation, which includes comma-seperated inputs and points to the output using the implies operator (=>). The output must be a value that does not use any nested comma-seperated values (values can be used to get around this).

  Good code:
    x $= u,n => link(u,<n>);
  
    y := <1,2,3,4>
    
    z := x(y,5);
    
  Bad code:
  
    x $= u,m,n,o -> link(u,<m,n,o>);
    
    y := x(<1,2>,3,4,5);
    
 5. Transforms can also be created by calling a builtin transform iterator (map, keep, merge, sort, etc.). These transforms take in a single transform (usually 1-input only) and return a new transform as a value that can be uses to analyze a union.
 
  Good code:
  
    x $= n => mod(n,2);
    y := keep(x);
    
    U := <1,2,3,4,5>;
    
    z := y(U);       <--- This will evaluate as <1,3,5>
    
  Bad code:
  
    x := n => mul(n,n);
    
    y $= t => map(t) <--- This part is possibly correct but 100% unecessary
    
    U := <1, 2, 3>
    
    z := y(x)(U)
    
6. Value names must be created with at least 1 letter in front and with no spaces, parenthesis, triangular brackets, colons, quotes, or dollar signs.

  Good code:
  
    alpha_beta := add(42,6);
    
    g@mma-D3ltA := sub(64,-8);
    
    S18M@&t@\/ := 5;
    
  Bad code:
  
    1variable := 6;
    
    var<name>1 := 5;
    
    :$ye<>t" := 4
    
  7. Builtin Function Library:

    • add() takes in 1+ Numbers and returns their sum

    • sub() takes in 1+ Numbers and returns their difference

    • mul() takes in 1+ Numbers and returns their product

    • div() takes in 1+ Numbers and returns their quotient

    • pow() takes in 1+ Numbers and returns the first to the power of the second

    • mod() takes in 2 Numbers and returns the first modulo the second

    • log() takes in 2 Numbers and returns the log of the first base the second

    • sin() takes in 1 Number and returns its sine

    • cos() takes in 1 Number and returns its cosine

    • tan() takes in 1 Number and returns its tangent

    • abs() takes in 1 Number and returns its absolute value

    • round() takes in 1 Number and returns its rounded vaue

    • random() takes in 2 Numbers and returns a random Number between them

    • less() takes in 2 [WILD] and returns if the first is less than the second

    • equal() takes in 2 [WILD] and returns if they are equal

    • greater() takes in 2 [WILD] and returns if the first is greater than the second

    • uni() takes in 1 Vocab and returns the unicode Number of the first character

    • chr() takes in Number and returns its unicode character as a Vocab

    • upper() takes in 1 Vocab and returns a version with all the leters capitalized

    • lower() takes in 1 Vocab and returns a version with all the characters de-capitalized

    • concat() takes in 1+ Vocabs and concatenates them into 1 Vocab

    • size() takes in 1 Vocab and returns its length as a Number

    • split() takes in 1 Vocab and returns a Union of its characters

    • join() takes in 1 Union and returns a Vocab merging its elements

    • branch() takes in 1 Logic and 2 [WILD] and returns the first if the Logic is TRUE and the second if it is FAlSE

    • or() takes in 1+ [WILD] and returns if any of them have truthiness

    • and() takes in 1+ [WILD] and returns if all of them have truthiness

    • not() takes in a Logic and returns its opposite

    • link() takes in 2+ Unions and returns a Union merging them into one

    • get() takes in a Union and an Number and returns that item of the Union

    • slice() takes in a Union and 3 Numbers and returns that Union slice of the Union

    • inside() takes in a [WILD] and a Union and returns the Logic

    • count()takes in a [WILD] and a Union and returns the Number of times the former is in the latter

    • index() takes in a [WILD] and a Union and returns the Number of the first time it appears in the Union

    • subset() takes in 2 Unions and returns if the first is a subset of the second

    • range() takes in 3 Numbers and returns a Union of that range

    • map() takes in a 1-input t and returns a t' that takes in a Union and applies t to each element

    • keep() takes in a 1-input t and returns a t' that takes in a Union and keeps the items that cause t to return TRUE

    • merge() takes in a 2-input t and returns a t' that takes in a Union merges all the elements using t

    • sort() takes in a 1-input t and returns a t' that takes in a Union and sorts the elements using t

    • max() takes in a 1-input t and returns a t' that takes in a Union and returns the element with the highest value for t

    • min() takes in a 1-input t and returns a t' that takes in a Union and returns the element with the lowest value for t
