const exportedOriginalFunction = (argA, argB) => {
    console.log("Running exported function")
}

export {exportedOriginalFunction as exportedRenamedFunction}