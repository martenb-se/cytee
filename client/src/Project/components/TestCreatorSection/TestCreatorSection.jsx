import React, {useState, useEffect, createContext, useContext, useReducer} from 'react';
import {useSelector} from "react-redux";

import {isEmpty} from "lodash";

import store from "../../../reducers/store";

// import redux selectors
import {selectActiveFunction} from '../../../reducers/activeFunctionSlice';
import {selectActiveTest} from '../../../reducers/activeTestInfoSlice';

// Local react reducer
import {unsavedTestInfoReducer, parseFunction} from './unsavedTestInfoReducer';

// Components
import TabGroup from "../../../shared/components/TabGroup";
import argumentsTabGenerator from "./ArgumentTab";
import returnTabGenerator from "./ReturnTab";
import generateExceptionTab from "./ExceptionTab";
import ModulePanel from './ModulePanel';


// Create the context used by the reducer
export const unsavedTestInfoContext = createContext();
const { Provider } = unsavedTestInfoContext;

const initUnsavedTestInfo = {
    customName: '',
    moduleData: {
        argumentList: undefined,
        returnValue: undefined
    },

};

export const moduleNameMapper= {
    argumentList: 'Arguments',
    returnValue: 'Return Value',
    exception: 'Exception',
}


function TestCreatorSection(){

    // get Active function selector
    const activeFunction = useSelector(selectActiveFunction);
    const activeTest = useSelector(selectActiveTest);

    const [initUnsavedTestInfoState, setInitUnsavedTestInfoState] = useState({});

    // TODO: If active function

    // create initial value
    useEffect(() => {
        if (!isEmpty(activeFunction.activeFunction)) {
            const funcArguments =  parseFunction(activeFunction.activeFunction.arguments);
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
            let newinitUnsavedTestInfoState = {};
            newinitUnsavedTestInfoState.customName = "";
            newinitUnsavedTestInfoState.moduleData = {
                argumentList: moduleArguments,
                returnValue: {
                    type: 'undefined',
                }
            }
            setInitUnsavedTestInfoState(newinitUnsavedTestInfoState);
        }

    }, [activeFunction])

    // if function was chosen


    // check if active function is set
    // Check if active test is set
    if (isEmpty(activeFunction.activeFunction) && isEmpty(activeTest.activeTest)) {
        return <WaitingForTestPanel />
    }

    // create local react reducer
    if (!isEmpty(initUnsavedTestInfoState)) {
        return <MainTestCreationContent initialState={initUnsavedTestInfoState}/>
    }

    return (
        <div>Processing Data...</div>
    );

}

function generateInitialTabs(moduleData) {
    const tabList = Object.keys(moduleData).map(moduleName => {
        switch (moduleName) {
            case 'argumentList':
                return argumentsTabGenerator();
            case 'returnValue':
                return returnTabGenerator();
            case 'exception':
                return generateExceptionTab();
        }
    });
    return tabList;
}

function MainTestCreationContent({initialState}) {

    const initalUnsavedTestInfoReducerState = initialState;
    const [unsavedTestInfoState, unsavedTestInfoDispatch] = useReducer(unsavedTestInfoReducer, initalUnsavedTestInfoReducerState);

    if (unsavedTestInfoState === undefined) {
        return (
            <div>Processing Data...</div>
        );
    }

    return (
        <Provider value={[unsavedTestInfoState, unsavedTestInfoDispatch]}>
            <div className="testCreatorSection-wrapper">
                <ModulePanel />
                <div className="testCreatorSection-wrapper">
                    <TestCreatorTabGroup/>
                </div>
            </div>
        </ Provider>
    )
}

function WaitingForTestPanel() {
    return (
        <div>Please select an function to create a new test or select and existing test to modify it.</div>
    );
}

function TestCreatorTabGroup() {

    const [state, dispatch] = useContext(unsavedTestInfoContext);

    const tabList = Object.keys(state.moduleData).map(moduleName => {
        switch (moduleName) {
            case 'argumentList':
                return argumentsTabGenerator();
            case 'returnValue':
                return returnTabGenerator();
            case 'exception':
                return generateExceptionTab();
        }
    });

    return (
      <TabGroup tabList={tabList}/>
    );
}

export default TestCreatorSection