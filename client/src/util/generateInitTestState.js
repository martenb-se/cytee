import store from "../reducers/store";
import {parseFunction} from "./parseFunctionInfo";

export function generateInitTestState() {
    const funcArguments = parseFunction(store.getState().activeFunction.activeFunction.arguments);
    const moduleArguments = [];

    for (const argumentData of funcArguments) {

        const subFunctionName = argumentData.functionName;
        for (const argument of argumentData['arguments']) {

            moduleArguments.push({
                subFunctionName: subFunctionName,
                argument: argument,
                type: 'undefined',
            });
        }
    }

    let newModuleData = {};

    if (moduleArguments.length !== 0) {
        newModuleData.argumentList = moduleArguments;
    }

    newModuleData.returnValue = {type: 'undefined'};
    return newModuleData;
}