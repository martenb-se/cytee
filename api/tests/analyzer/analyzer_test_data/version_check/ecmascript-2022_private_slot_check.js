// https://exploringjs.com/impatient-js/ch_new-javascript-features.html
class Rectangle {
  constructor(height, width) {
    this.height = height;
    this.width = width;
  }
}
const someRectangle = new Rectangle()
console.log(
    "See if #privateSlot exist in someRectangle: ",
    #privateSlot in someRectangle)