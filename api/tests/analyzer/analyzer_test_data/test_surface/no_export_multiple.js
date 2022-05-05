const privateFunctionA = (argA, argB) => {
    console.log("Running private function")
}

function privateFunctionB(argA, argB) {
    console.log("Running private function")
}

class PrivateClass {
    someFunction(someArgument) {
        console.log("Not exported")
    }
}

const privateObject = {
  objectPropertyFunction: (argA) =>
      console.log(argA)
}