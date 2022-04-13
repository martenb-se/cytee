// https://www.digitalocean.com/community/tutorials/js-es2020
class Message {
  #message = "Howdy";
  greet() {
    console.log(this.#message);
  }
}
const greeting = new Message()
greeting.greet()
console.log(greeting.#message)