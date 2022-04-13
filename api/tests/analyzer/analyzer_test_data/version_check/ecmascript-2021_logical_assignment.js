// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Logical_OR_assignment
const a = { duration: 50, title: '' };

a.duration ||= 10;
console.log(a.duration);
// expected output: 50

a.title ||= 'title is empty.';
console.log(a.title);
// expected output: "title is empty"