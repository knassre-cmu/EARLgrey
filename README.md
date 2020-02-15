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
