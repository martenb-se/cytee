import cloneDeep from "lodash/cloneDeep";
import store from "../../../reducers/store";

import argumentsTabGenerator from "./ArgumentTab";
import returnTabGenerator from "./ReturnTab";
import generateExceptionTab from "./ExceptionTab";


function parseFunctionArgs(args) {
    const argumentList = [];

    for (const argumentData of args) {
        switch(argumentData.type) {
            case 'Identifier':
                argumentList.push(argumentData.name);
                break;
            case 'Property':
                argumentList.push(argumentData.key.name)
                break;
            case 'ObjectPattern':
                const objRecList = parseFunctionArgs(argumentData.properties);
                argumentList.push(...objRecList);
                break;
            case 'ArrayPattern':
                const arrRecList = parseFunctionArgs(argumentData.elements);
                argumentList.push(...arrRecList);
                break;
            case 'RestElement':
                argumentList.push('RestElement');
                break;
            default:
                break;
        }
    }
    return argumentList;
}

export function parseFunction(args) {
    const fullArgumentList = [];
    for (const func of args) {
        const funcName = Object.keys(func)[0];
        const argList = parseFunctionArgs(func[funcName]);
        fullArgumentList.push({functionName: funcName, arguments: argList});
    }
    return fullArgumentList;
}

function generateInitTestState() {
    const funcArguments =  parseFunction(store.getState().activeFunction.activeFunction.arguments);
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


export function unsavedTestInfoReducer(state, action) {

    const initialCommand = (new RegExp('^[^/]*')).exec(action.type)[0];
    switch (initialCommand) {
        case 'setModuleData':
            return cloneDeep(action.payload);
        case 'clearModelData':
            const clearTestInfoClone = cloneDeep(state);
            clearTestInfoClone.moduleData = generateInitTestState();
            if (clearTestInfoClone._id !== undefined) {
                delete clearTestInfoClone._id;
            }
            return clearTestInfoClone;
        case 'discardModuleDataChanges':
            const discardTestInfoClone = cloneDeep(state);
            discardTestInfoClone.moduleData = cloneDeep(store.getState().activeTest.test.moduleData);
            return discardTestInfoClone;
        case 'moduleData':
            return moduleDataSubReducer(state, action);
        case 'argumentList':
            return argumentListSubReducer(state, action);
        case 'returnValue':
            return returnValueSubReducer(state, action);
        case 'exception':
            return exceptionSubReducer(state, action);
        case 'customName':
            return customNameSubReducer(state, action);
        default:
            return state;
    }
}

function moduleDataSubReducer(state, action) {

    switch (action.type) {

        case 'moduleData/addModule':

            if (action.payload in state) {
                return state;
            }

            const addModuleNewState = cloneDeep(state);
            const functionInfo =  store.getState().activeFunction.activeFunction;

            switch (action.payload) {
                case 'argumentList':
                    const funcArguments =  parseFunction(functionInfo.arguments)
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

                    addModuleNewState.moduleData.argumentList = moduleArguments;
                    break;
                case 'returnValue':
                    addModuleNewState.moduleData.returnValue = {type: 'undefined'};
                    break;
                case 'exception':
                    addModuleNewState.moduleData.exception = {exception: ''};
                    break;
                default:
                    break;
            }
            return addModuleNewState;

        case 'moduleData/removeModule':
            const removeModuleNewState = cloneDeep(state);

            delete removeModuleNewState.moduleData[action.payload];

            return removeModuleNewState;
        default:
            throw new Error();
    }
}

function argumentListSubReducer(state, action) {
    switch (action.type) {
        case 'argumentList/changeArgument':
            const newStateClone = cloneDeep(state);
            const argumentIndex = newStateClone.moduleData.argumentList.findIndex(
                (argument) => (
                    (argument.argument === action.payload.argument) &&
                    (argument.subFunctionName === action.payload.subFunctionName)
                )
            );
            newStateClone.moduleData.argumentList.splice(argumentIndex, 1, action.payload);
            return newStateClone;
        case 'argumentList/changeArgumentList':
            break;
        default:
            throw new Error();
    }
}

function returnValueSubReducer(state, action) {
    switch (action.type) {
        case 'returnValue/updateReturnValue':
            const newStateClone = cloneDeep(state);
            newStateClone.moduleData.returnValue = action.payload;
            return newStateClone;
        default:
            throw new Error();
    }
}

function exceptionSubReducer(state, action) {
    switch (action.type) {
        case 'exception/updateException':
            break;
        default:
            throw new Error();
    }
}

function customNameSubReducer(state, action) {
    switch (action.type) {
        case 'customName/rename':
            const renameCustomName = cloneDeep(state);
            renameCustomName.customName = action.payload;
            console.log('renameCustomName: ', renameCustomName);
            return renameCustomName;
        default:
            throw new Error();
    }
}

export function unsavedTestInfoReducer2(state, action) {
    switch(action.type) {

        case 'addModule':

            if (action.payload in state) {
                return state;
            }

            const addModuleNewState = cloneDeep(state);
            const functionInfo =  store.getState().activeFunction.activeFunction;

            switch (action.payload) {
                case 'argumentList':
                    const funcArguments =  parseFunction(functionInfo.arguments)
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
                addModuleNewState.moduleData.argumentList = moduleArguments;
                break;


                case 'returnValue':
                    addModuleNewState.moduleData.returnValue = {type: 'undefined'};
                    break;

                case 'exception':
                    addModuleNewState.moduleData.exception = {exception: ''};
                    break;
            }
            return addModuleNewState;
        case 'removeModule':
            const removeModuleNewState = cloneDeep(state);

            delete removeModuleNewState.moduleData[action.payload];

            return removeModuleNewState;

        case 'editModule':
            const editModuleNewState = cloneDeep(state);
            editModuleNewState.moduleData[action.payload.moduleName] = action.payload.moduleData;
            return editModuleNewState;
        default:
            throw new Error();

    }
}

