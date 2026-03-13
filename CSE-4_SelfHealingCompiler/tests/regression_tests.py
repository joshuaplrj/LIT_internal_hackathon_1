"""
MiniRust Compiler - Regression Test Suite
200 valid MiniRust programs for testing compiler correctness
"""

import os
import sys
import json
from typing import List, Dict, Tuple

# Test programs organized by category
TEST_PROGRAMS = {
    "basic_types": [
        # Test 1: Integer literals
        '''
fn main() {
    let x: i32 = 42;
    let y: i64 = 1000000;
    let z: u8 = 255;
}
''',
        # Test 2: Float literals
        '''
fn main() {
    let pi: f64 = 3.14159;
    let e: f32 = 2.718;
}
''',
        # Test 3: Boolean operations
        '''
fn main() {
    let t: bool = true;
    let f: bool = false;
    let and_result = t && f;
    let or_result = t || f;
    let not_result = !t;
}
''',
        # Test 4: String literals
        '''
fn main() {
    let s: &str = "Hello, MiniRust!";
    let empty: &str = "";
}
''',
        # Test 5: Character literals
        '''
fn main() {
    let c: char = 'A';
    let newline: char = '\\n';
}
''',
    ],
    
    "functions": [
        # Test 6: Simple function
        '''
fn add(x: i32, y: i32) -> i32 {
    x + y
}

fn main() {
    let result = add(1, 2);
}
''',
        # Test 7: Function with no return
        '''
fn print_hello() {
    println!("Hello");
}

fn main() {
    print_hello();
}
''',
        # Test 8: Multiple parameters
        '''
fn compute(a: i32, b: i32, c: i32) -> i32 {
    a + b * c
}

fn main() {
    let result = compute(1, 2, 3);
}
''',
        # Test 9: Recursive function
        '''
fn factorial(n: u64) -> u64 {
    if n <= 1 {
        1
    } else {
        n * factorial(n - 1)
    }
}

fn main() {
    let f5 = factorial(5);
}
''',
        # Test 10: Function with mutable parameter
        '''
fn increment(mut x: i32) -> i32 {
    x = x + 1;
    x
}

fn main() {
    let result = increment(10);
}
''',
    ],
    
    "control_flow": [
        # Test 11: If-else
        '''
fn main() {
    let x = 10;
    let result = if x > 5 {
        "big"
    } else {
        "small"
    };
}
''',
        # Test 12: While loop
        '''
fn main() {
    let mut i = 0;
    while i < 10 {
        i = i + 1;
    }
}
''',
        # Test 13: For loop
        '''
fn main() {
    let mut sum = 0;
    for i in 0..10 {
        sum = sum + i;
    }
}
''',
        # Test 14: Loop with break
        '''
fn main() {
    let mut count = 0;
    loop {
        count = count + 1;
        if count >= 100 {
            break;
        }
    }
}
''',
        # Test 15: Nested loops
        '''
fn main() {
    for i in 0..10 {
        for j in 0..10 {
            let product = i * j;
        }
    }
}
''',
    ],
    
    "structs": [
        # Test 16: Simple struct
        '''
struct Point {
    x: f64,
    y: f64,
}

fn main() {
    let p = Point { x: 1.0, y: 2.0 };
}
''',
        # Test 17: Struct with methods
        '''
struct Rectangle {
    width: f64,
    height: f64,
}

impl Rectangle {
    fn area(&self) -> f64 {
        self.width * self.height
    }
}

fn main() {
    let rect = Rectangle { width: 10.0, height: 5.0 };
    let a = rect.area();
}
''',
        # Test 18: Nested structs
        '''
struct Point {
    x: f64,
    y: f64,
}

struct Line {
    start: Point,
    end: Point,
}

fn main() {
    let line = Line {
        start: Point { x: 0.0, y: 0.0 },
        end: Point { x: 1.0, y: 1.0 },
    };
}
''',
        # Test 19: Struct with mutable fields
        '''
struct Counter {
    count: i32,
}

impl Counter {
    fn increment(&mut self) {
        self.count = self.count + 1;
    }
}

fn main() {
    let mut c = Counter { count: 0 };
    c.increment();
}
''',
        # Test 20: Tuple struct
        '''
struct Color(u8, u8, u8);

fn main() {
    let red = Color(255, 0, 0);
}
''',
    ],
    
    "enums": [
        # Test 21: Simple enum
        '''
enum Direction {
    North,
    South,
    East,
    West,
}

fn main() {
    let dir = Direction::North;
}
''',
        # Test 22: Enum with data
        '''
enum Shape {
    Circle(f64),
    Rectangle(f64, f64),
    Triangle(f64, f64, f64),
}

fn main() {
    let circle = Shape::Circle(5.0);
    let rect = Shape::Rectangle(10.0, 20.0);
}
''',
        # Test 23: Option enum
        '''
fn find(arr: &[i32], target: i32) -> Option<usize> {
    for i in 0..arr.len() {
        if arr[i] == target {
            return Some(i);
        }
    }
    None
}

fn main() {
    let result = find(&[1, 2, 3], 2);
}
''',
        # Test 24: Result enum
        '''
fn divide(a: f64, b: f64) -> Result<f64, &'static str> {
    if b == 0.0 {
        Err("Division by zero")
    } else {
        Ok(a / b)
    }
}

fn main() {
    let result = divide(10.0, 2.0);
}
''',
        # Test 25: Match expression
        '''
enum Message {
    Quit,
    Echo(String),
    Move { x: i32, y: i32 },
}

fn process(msg: Message) {
    match msg {
        Message::Quit => println!("Quit"),
        Message::Echo(text) => println!("{}", text),
        Message::Move { x, y } => println!("Move to ({}, {})", x, y),
    }
}

fn main() {
    process(Message::Echo("Hello".to_string()));
}
''',
    ],
    
    "ownership": [
        # Test 26: Move semantics
        '''
fn main() {
    let s1 = String::from("hello");
    let s2 = s1;  // s1 is moved
    // println!("{}", s1);  // Would error
}
''',
        # Test 27: Borrowing
        '''
fn calculate_length(s: &String) -> usize {
    s.len()
}

fn main() {
    let s = String::from("hello");
    let len = calculate_length(&s);
    println!("{}", s);  // s is still valid
}
''',
        # Test 28: Mutable borrowing
        '''
fn append_world(s: &mut String) {
    s.push_str(", world!");
}

fn main() {
    let mut s = String::from("hello");
    append_world(&mut s);
}
''',
        # Test 29: Multiple immutable borrows
        '''
fn main() {
    let s = String::from("hello");
    let r1 = &s;
    let r2 = &s;
    println!("{} and {}", r1, r2);
}
''',
        # Test 30: Lifetime annotations
        '''
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}

fn main() {
    let result = longest("hello", "world!");
}
''',
    ],
    
    "vectors": [
        # Test 31: Vector creation
        '''
fn main() {
    let v: Vec<i32> = Vec::new();
    let v2 = vec![1, 2, 3, 4, 5];
}
''',
        # Test 32: Vector operations
        '''
fn main() {
    let mut v = Vec::new();
    v.push(1);
    v.push(2);
    v.push(3);
    let first = &v[0];
}
''',
        # Test 33: Iterating over vectors
        '''
fn main() {
    let v = vec![1, 2, 3, 4, 5];
    for item in &v {
        println!("{}", item);
    }
}
''',
        # Test 34: Vector with structs
        '''
struct Point {
    x: f64,
    y: f64,
}

fn main() {
    let mut points = Vec::new();
    points.push(Point { x: 1.0, y: 2.0 });
    points.push(Point { x: 3.0, y: 4.0 });
}
''',
        # Test 35: Vector map
        '''
fn main() {
    let v = vec![1, 2, 3, 4, 5];
    let doubled: Vec<i32> = v.iter().map(|x| x * 2).collect();
}
''',
    ],
    
    "error_handling": [
        # Test 36: Result with ?
        '''
fn read_file(path: &str) -> Result<String, std::io::Error> {
    let contents = std::fs::read_to_string(path)?;
    Ok(contents)
}

fn main() {
    let result = read_file("test.txt");
}
''',
        # Test 37: Option with match
        '''
fn find_user(id: u64) -> Option<String> {
    if id == 1 {
        Some("Alice".to_string())
    } else {
        None
    }
}

fn main() {
    match find_user(1) {
        Some(name) => println!("Found: {}", name),
        None => println!("Not found"),
    }
}
''',
        # Test 38: Custom error type
        '''
enum MyError {
    NotFound,
    Invalid(String),
}

fn process(input: &str) -> Result<i32, MyError> {
    if input.is_empty() {
        return Err(MyError::Invalid("empty input".to_string()));
    }
    Ok(42)
}

fn main() {
    let result = process("");
}
''',
        # Test 39: unwrap and expect
        '''
fn main() {
    let v = vec![1, 2, 3];
    let first = v.first().unwrap();
    let second = v.get(1).expect("index out of bounds");
}
''',
        # Test 40: Error conversion
        '''
fn parse_and_double(s: &str) -> Result<i32, Box<dyn std::error::Error>> {
    let n: i32 = s.parse()?;
    Ok(n * 2)
}

fn main() {
    let result = parse_and_double("21");
}
''',
    ],
    
    "generics": [
        # Test 41: Generic function
        '''
fn largest<T: PartialOrd>(list: &[T]) -> &T {
    let mut largest = &list[0];
    for item in &list[1..] {
        if item > largest {
            largest = item;
        }
    }
    largest
}

fn main() {
    let numbers = vec![34, 50, 25, 100, 65];
    let result = largest(&numbers);
}
''',
        # Test 42: Generic struct
        '''
struct Point<T> {
    x: T,
    y: T,
}

fn main() {
    let integer = Point { x: 5, y: 10 };
    let float = Point { x: 1.0, y: 4.0 };
}
''',
        # Test 43: Generic enum (Option)
        '''
enum MyOption<T> {
    Some(T),
    None,
}

fn main() {
    let x: MyOption<i32> = MyOption::Some(5);
    let y: MyOption<f64> = MyOption::None;
}
''',
        # Test 44: Multiple generic parameters
        '''
struct Pair<T, U> {
    first: T,
    second: U,
}

fn main() {
    let pair = Pair { first: 1, second: "hello" };
}
''',
        # Test 45: Generic impl
        '''
struct Wrapper<T> {
    value: T,
}

impl<T> Wrapper<T> {
    fn new(value: T) -> Self {
        Wrapper { value }
    }
    
    fn get(&self) -> &T {
        &self.value
    }
}

fn main() {
    let w = Wrapper::new(42);
    let v = w.get();
}
''',
    ],
    
    "traits": [
        # Test 46: Simple trait
        '''
trait Summary {
    fn summarize(&self) -> String;
}

struct Article {
    title: String,
    content: String,
}

impl Summary for Article {
    fn summarize(&self) -> String {
        format!("{}: {}", self.title, &self.content[..50])
    }
}

fn main() {
    let article = Article {
        title: "Hello".to_string(),
        content: "World".to_string(),
    };
    println!("{}", article.summarize());
}
''',
        # Test 47: Default trait methods
        '''
trait Greet {
    fn name(&self) -> &str;
    
    fn greet(&self) -> String {
        format!("Hello, {}!", self.name())
    }
}

struct Person {
    name: String,
}

impl Greet for Person {
    fn name(&self) -> &str {
        &self.name
    }
}

fn main() {
    let p = Person { name: "Alice".to_string() };
    println!("{}", p.greet());
}
''',
        # Test 48: Trait bounds
        '''
fn notify(item: &impl Summary) {
    println!("Breaking news! {}", item.summarize());
}

fn main() {
    // Would call notify with a Summary implementor
}
''',
        # Test 49: Multiple trait bounds
        '''
use std::fmt::{Display, Debug};

fn print_it<T: Display + Debug>(item: T) {
    println!("Display: {}", item);
    println!("Debug: {:?}", item);
}

fn main() {
    print_it(42);
}
''',
        # Test 50: Trait objects
        '''
trait Draw {
    fn draw(&self);
}

struct Button;
struct TextField;

impl Draw for Button {
    fn draw(&self) {
        println!("Drawing button");
    }
}

impl Draw for TextField {
    fn draw(&self) {
        println!("Drawing text field");
    }
}

fn main() {
    let components: Vec<Box<dyn Draw>> = vec![
        Box::new(Button),
        Box::new(TextField),
    ];
    
    for component in &components {
        component.draw();
    }
}
''',
    ],
    
    "advanced": [
        # Test 51: Closures
        '''
fn main() {
    let add = |x: i32, y: i32| x + y;
    let result = add(1, 2);
    
    let mut count = 0;
    let mut increment = || {
        count += 1;
        count
    };
}
''',
        # Test 52: Closure with move
        '''
fn main() {
    let s = String::from("hello");
    let closure = move || {
        println!("{}", s);
    };
    closure();
    // s is no longer valid here
}
''',
        # Test 53: Iterators
        '''
fn main() {
    let v = vec![1, 2, 3, 4, 5];
    let sum: i32 = v.iter()
        .filter(|&&x| x % 2 == 0)
        .map(|&x| x * x)
        .sum();
}
''',
        # Test 54: Pattern matching
        '''
fn process(x: Option<i32>) -> &'static str {
    match x {
        Some(0) => "zero",
        Some(n) if n > 0 => "positive",
        Some(_) => "negative",
        None => "nothing",
    }
}

fn main() {
    let result = process(Some(42));
}
''',
        # Test 55: Destructuring
        '''
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p = Point { x: 1, y: 2 };
    let Point { x, y } = p;
    
    let (a, b, c) = (1, 2, 3);
}
''',
    ],
}

def generate_all_tests() -> List[Dict]:
    """Generate all 200 test programs"""
    tests = []
    test_id = 1
    
    for category, programs in TEST_PROGRAMS.items():
        for program in programs:
            tests.append({
                "id": test_id,
                "category": category,
                "code": program.strip(),
                "expected": "success"
            })
            test_id += 1
    
    # Generate additional tests to reach 200
    additional_templates = [
        ("basic_types", "fn main() { let x: {type} = {value}; }"),
        ("functions", "fn func_{id}(x: i32) -> i32 {{ x + {id} }}\nfn main() {{ let _ = func_{id}(1); }}"),
        ("control_flow", "fn main() {{ if {cond} {{ let x = 1; }} }}"),
    ]
    
    while test_id <= 200:
        for category, template in additional_templates:
            if test_id > 200:
                break
            
            if category == "basic_types":
                types_values = [
                    ("i8", "127"), ("i16", "32767"), ("i32", "2147483647"),
                    ("u8", "255"), ("u16", "65535"), ("u32", "4294967295"),
                    ("f32", "3.14"), ("f64", "2.718"), ("bool", "true"),
                ]
                for t, v in types_values:
                    if test_id > 200:
                        break
                    tests.append({
                        "id": test_id,
                        "category": category,
                        "code": template.format(type=t, value=v),
                        "expected": "success"
                    })
                    test_id += 1
            
            elif category == "functions":
                tests.append({
                    "id": test_id,
                    "category": category,
                    "code": template.format(id=test_id),
                    "expected": "success"
                })
                test_id += 1
            
            elif category == "control_flow":
                conditions = ["true", "false", "1 > 0", "x == 5", "y <= 10"]
                for cond in conditions:
                    if test_id > 200:
                        break
                    code = f"fn main() {{ let x = 5; let y = 10; if {cond} {{ let z = 1; }} }}"
                    tests.append({
                        "id": test_id,
                        "category": category,
                        "code": code,
                        "expected": "success"
                    })
                    test_id += 1
    
    return tests[:200]

def save_tests(tests: List[Dict], output_dir: str):
    """Save tests to files"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save as JSON
    with open(os.path.join(output_dir, "all_tests.json"), "w") as f:
        json.dump(tests, f, indent=2)
    
    # Save individual test files
    for test in tests:
        filename = f"test_{test['id']:03d}_{test['category']}.mr"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w") as f:
            f.write(test["code"])
    
    print(f"Generated {len(tests)} test files in {output_dir}")

if __name__ == "__main__":
    tests = generate_all_tests()
    save_tests(tests, "tests/valid_programs")
    
    # Print summary
    categories = {}
    for test in tests:
        cat = test["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nTest Summary:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count} tests")
