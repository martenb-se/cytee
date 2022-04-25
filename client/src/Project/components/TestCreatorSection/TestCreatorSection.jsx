import React, {useState, useEffect, createContext, useContext, useReducer} from 'react';
import cloneDeep from 'lodash/cloneDeep';
import TabGroup from "../../../shared/components/TabGroup";
import ArgumentTab from "./ArgumentTab";
import ReturnTab from "./ReturnTab";
import ExceptionTab from "./ExceptionTab";

const initLocalTestInfo ={
    activeTestInfoTab: "argumentList",
    testInfo: {
        pathToProject: "/path/to/project/src/",
        fileId: "shared/util/api",
        functionId: "db.util",
        customName: "",
        moduleData: {
            argumentList:[],
            returnValue:{}
        }
    }
}


export const localTestInfoContext = createContext();
const { Provider } = localTestInfoContext;

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

function parseFunction(args) {
    const fullArgumentList = [];
    for (const func of args) {
        const funcName = Object.keys(func)[0];
        const argList = parseFunctionArgs(func[funcName]);
        fullArgumentList.push({functionName: funcName, arguments: argList});
    }
    return fullArgumentList;
}

function localTestInfoContextReducer(state, action) {
    switch(action.type) {


        case 'setActiveTab':
            // Create copy of state
            const activeTabStateCopy = cloneDeep(state);

            // change activeTestInfoTab
            activeTabStateCopy.activeTestInfoTab = action.payload;

            // return state copy
            return activeTabStateCopy;


        case 'removeModule':

            // Create copy of state
            const removedModuleStateCopy = cloneDeep(state);

            // remove object attribute with attribute name in action
            delete removedModuleStateCopy.testInfo.moduleData[action.payload];

            // If the removed tabs is being removed then change to another tab
            if (removedModuleStateCopy.activeTestInfoTab === action.payload) {

                const moduleDataKeyList = Object.keys(removedModuleStateCopy.testInfo.moduleData).sort();

                if (moduleDataKeyList.length > 0) {
                    removedModuleStateCopy.activeTestInfoTab = moduleDataKeyList[0];
                }
            }

            //return stateCopy
            return removedModuleStateCopy;


        case 'addModule':

            // Check if given attribute already exists.
            if (action.payload in state.testInfo.moduleData) {
                return state;
            }

            // Create copy of state
            const addedModuleStateCopy = cloneDeep(state);

            // add module name to module data
            // Set the active tab to the newly added tab
            switch(action.payload) {
                case 'argumentList':
                    // TODO: Set a default value for argument list that this can be assigned to.
                    addedModuleStateCopy.testInfo.moduleData.argumentList = [];


                    addedModuleStateCopy.activeTestInfoTab = 'argumentList';
                    break;
                case 'returnValue':
                    // TODO: Set a default value for return value that this can be assigned to.
                    addedModuleStateCopy.testInfo.moduleData.returnValue = {};
                    addedModuleStateCopy.activeTestInfoTab = 'returnValue';
                    break;
                case 'exception':
                    // TODO: Set a default value for exception that this can be assigned to.
                    addedModuleStateCopy.testInfo.moduleData.exception = {};
                    addedModuleStateCopy.activeTestInfoTab = 'exception';
                    break;
            }

            // return statCopy
            return addedModuleStateCopy;

        case 'editArguments':

            break;

        default:
            throw new Error();
    }
}


function TestCreatorSection({moduleListArg}){

    // Tie the Test Creator Section to the active function info
    // const functionInfo = useSelector(state => state.activeFunctionInfo);

    // Tie the Test Creator Section to the active test info
    // const testInfo = useSelector(state => state.activeTestInfo);

    const [localTestInfoState, localTestInfoDispatch] = useReducer(localTestInfoContextReducer, initLocalTestInfo);

    return (
        <Provider value={[localTestInfoState, localTestInfoDispatch]}>
            <div className="moduleData-wrapper">
                <ModuleSelector />
                <ModuleList />
            </div>

            <div className={"testCreator-Wrapper"}>
                <div className="testCreator-header">
                    <button className="btn btn-primary">Save Test/Create Test</button>
                    <button className="btn btn-primary">Delete Test</button>
                    <button className="btn btn-primary">Cansel</button>
                    <input type="text" placeholder="Custom test name" />
                </div>
                <TestCreatorTabGroup />
            </div>

        </Provider>
    )
}

function TestCreatorTabGroup() {

    const [state, dispatch] = useContext(localTestInfoContext);

    function setActiveModuleTab(tabName) {

        // check if tab name is the same as active tab
        // could also disable selected tab through css

        dispatch({
            type:'setActiveTab',
            payload:tabName,
        });
    }

    // generate tabs for tab list
    //TODO: change name to label
    const tabList = Object.keys(state.testInfo.moduleData).map(moduleName => {
        switch(moduleName) {
            case 'argumentList':
                return {
                    tabName:"Arguments",
                    name: "argumentList",
                    content: <ArgumentTab/>
                }
            case 'returnValue':
                return {
                    tabName:"Return Value",
                    name: "returnValue",
                    content: <ReturnTab/>
                }
            case 'exception':
                return {
                    tabName:"Exception",
                    name: "exception",
                    content: <ExceptionTab/>
                }
        }
    });

    return (
        <TabGroup
        tabList={tabList}
        activeTab={state.activeTestInfoTab}
        setActiveTab={setActiveModuleTab}
        />
    );
}

function ModuleSelector() {

    const [state, dispatch] = useContext(localTestInfoContext);

    function addModule(moduleName) {
        dispatch({
            type:'addModule',
            payload: moduleName
        });
    }

    return (
        <div className="dropdown">
            <button className="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton1"
                    data-bs-toggle="dropdown" aria-expanded="false">
                Add Module
            </button>
            <ul className="dropdown-menu" aria-labelledby="dropdownMenuButton1">
                <li><button className="dropdown-item" onClick ={ () => addModule('argumentList')}>Arguments</button></li>
                <li><button className="dropdown-item" onClick ={ () => addModule('returnValue')}>Return Value</button></li>
                <li><button className="dropdown-item" onClick ={ () => addModule('exception')}>Exception</button></li>
            </ul>
        </div>
    );
}

function ModuleList() {

    const [state, dispatch] = useContext(localTestInfoContext);

    function deleteModule(moduleName) {
        dispatch({
            type:'removeModule',
            payload: moduleName
        });
    }

    return (
        <table>
            <thead>
            <tr><td>Modules</td></tr>
            </thead>
            <tbody>
                {
                 Object.keys(state.testInfo.moduleData).sort().map(moduleName => <tr key={moduleName}>
                        <td>{moduleName}</td>
                        <td><button onClick={() => deleteModule(moduleName)}>X</button></td>
                    </tr>
                )}
            </tbody>
        </table>
    )

}

export default TestCreatorSection