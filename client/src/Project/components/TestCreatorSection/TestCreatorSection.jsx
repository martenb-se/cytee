import React, {useState, useEffect, createContext, useContext, useReducer} from 'react';
import {useDispatch, useSelector} from "react-redux";
import store from '../../../reducers/store';

import {isEmpty, isEqual} from "lodash";

// import redux selectors
import {selectActiveFunction} from '../../../reducers/activeFunctionSlice';
import {
    deleteTestInfo,
    selectActiveTest,
    selectActiveTestLoadingState,
    setActiveTest,
    setActiveTestEmpty,
    updateTestInfo
} from '../../../reducers/activeTestInfoSlice';
import {fetchTestList, selectTestList, selectTestListLoading} from '../../../reducers/testListSlice'

// Local react reducer
import {unsavedTestInfoReducer, parseFunction} from './unsavedTestInfoReducer';

// Components
import TabGroup from "../../../shared/components/TabGroup";
import argumentsTabGenerator from "./ArgumentTab";
import returnTabGenerator from "./ReturnTab";
import generateExceptionTab from "./ExceptionTab";
import ModulePanel from './ModulePanel';

import {saveTestInfo} from "../../../reducers/activeTestInfoSlice";
import cloneDeep from "lodash/cloneDeep";

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

    const activeFunction = useSelector(selectActiveFunction);
    const activeTest = useSelector(selectActiveTest);

    const [initUnsavedTestInfoState, setInitUnsavedTestInfoState] = useState({});

    //const [unsavedTestInfoState, unsavedTestInfoDispatch] = useReducer(unsavedTestInfoReducer, initialState);

    useEffect(() => {
        if (!isEmpty(activeFunction)) {

            if(isEmpty(activeTest)) {
                const funcArguments =  parseFunction(activeFunction.arguments);
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

                let newinitUnsavedTestInfoState = {
                    customName: "",
                    moduleData: {},
                };

                if (moduleArguments.length !== 0) {
                    newinitUnsavedTestInfoState.moduleData.argumentList = moduleArguments;
                }

                newinitUnsavedTestInfoState.moduleData.returnValue = {type: 'undefined'};

                setInitUnsavedTestInfoState(newinitUnsavedTestInfoState);
            } else {
                setInitUnsavedTestInfoState(cloneDeep(activeTest));
            }
        }
    }, [activeFunction])



    // check if active function is set
    // Check if active test is set
    if (isEmpty(activeFunction)) {
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

function MainTestCreationContent({initialState}) {


    const activeTestLoadingStatus = useSelector(selectActiveTestLoadingState);
    const activeTest = useSelector(selectActiveTest);
    const activeFunction = useSelector(selectActiveFunction);
    const testListLoadingState = useSelector(selectTestListLoading);
    const testList = useSelector(selectTestList);
    const relPathToProject= useSelector(state => state.project.path);
    const dispatch = useDispatch();

    const [unsavedTestInfoState, unsavedTestInfoDispatch] = useReducer(unsavedTestInfoReducer, initialState);

    const [loadingState, setLoadingState] = useState('');

    const actTest = useSelector(state => state.activeTest);

    useEffect(() => {
        console.log('activeTest: ', actTest);
    }, [actTest])

    useEffect(() => {
        unsavedTestInfoDispatch({type: 'setModuleData', payload: initialState});
    }, [initialState]);

    function deleteTest() {
        setLoadingState('waitingForActiveTestDeleted');
        dispatch(deleteTestInfo(activeTest._id));
    }

    function saveTest() {
        setLoadingState('waitingForActiveTest');
        dispatch(updateTestInfo({
            testId: activeTest._id,
            testModule: unsavedTestInfoState.moduleData,
            customName: unsavedTestInfoState.customName,
        }));
    }

    function createTest() {
        setLoadingState('waitingForActiveTest');
        dispatch(saveTestInfo({
            pathToProject: relPathToProject,
            fileId: activeFunction.fileId,
            functionId: activeFunction.functionId,
            testModule: unsavedTestInfoState.moduleData,
        }))
    }

    useEffect(() => {
        if ((loadingState === 'waitingForActiveTest') ||
            (loadingState === 'waitingForActiveTestDeleted')) {
            if (activeTestLoadingStatus === 'succeeded') {
                if (loadingState === 'waitingForActiveTest') {
                    setLoadingState('waitingForTestList');
                } else if (loadingState === 'waitingForActiveTestDeleted') {
                    setLoadingState('waitingForTestListDeleted');
                }
                dispatch(fetchTestList(relPathToProject));
            }
        }
    }, [activeTestLoadingStatus]);

    useEffect(() => {
        if ((loadingState === 'waitingForTestList') ||
            (loadingState === 'waitingForTestListDeleted')) {
            if (testListLoadingState === 'succeeded') {
                setLoadingState('');

                if (loadingState === 'waitingForTestList') {
                    const newActiveTestState = {
                        pathToProject: activeFunction.pathToProject,
                        fileId: activeFunction.fileId,
                        functionId: activeFunction.functionId,
                        customName: "",
                        moduleData: unsavedTestInfoState.moduleData,
                    }

                    const newTest = testList.find(testInfo => {
                        const testInfoClone = cloneDeep(testInfo);
                        delete testInfoClone._id;
                        return isEqual(testInfoClone, newActiveTestState);
                    });

                    newActiveTestState._id = newTest._id;

                    dispatch(setActiveTest(newActiveTestState));
                    unsavedTestInfoDispatch({type:'setModuleData', payload: newActiveTestState})
                } else if (loadingState === 'waitingForTestListDeleted') {
                    dispatch(setActiveTestEmpty());
                    unsavedTestInfoDispatch({type:'clearModelData'});
                }

            }
        }
    }, [testListLoadingState]);

    useEffect(() => {

    }, [loadingState])

    if (unsavedTestInfoState === undefined) {
        return (
            <div>Processing Data...</div>
        );
    }

    if (activeTestLoadingStatus === 'loading') {
        return (
            <div>Saving test...</div>
        )
    }

    return (
        <Provider value={[unsavedTestInfoState, unsavedTestInfoDispatch]}>
            <div className="testCreatorSection-wrapper">
                <ModulePanel />
                <div>
                    <TestCreatorSectionHeader
                        createTestFunc={createTest}
                        editTestFunc={saveTest}
                        removeTestFunc={deleteTest}
                    />
                    <TestCreatorTabGroup />
                </div>
            </div>
        </ Provider>
    )
}

function TestCreatorSectionHeader({createTestFunc, editTestFunc, removeTestFunc}) {

    const [state, dispatch] = useContext(unsavedTestInfoContext);

    return (
        <div className="test-creator-section-header">
            {(state._id === undefined)?
                <>
                    <div className="btn-group" role='group'>
                        <button
                            className="btn btn-primary"
                            onClick={() => createTestFunc()}
                        >Create Test</button>
                        <button
                            className="btn btn-primary"
                            onClick={() => dispatch({type:'clearModelData'})}
                        >Cancel</button>
                    </div>

                </>
                :
                <>
                <div className="btn-group" role='group'>
                    <button
                        className="btn btn-primary"
                        onClick={() => editTestFunc()}
                    >Save Test</button>
                    <button
                        className="btn btn-primary"
                        onClick={() => dispatch({type:'discardModuleDataChanges'})}
                    >Discard Changes</button>
                    <button
                        className="btn btn-danger"
                        onClick={() => removeTestFunc()}
                    >Delete</button>
                </div>
                </>
            }
        </div>
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

    console.log('tabList: ', tabList);

    return (
      <TabGroup tabList={tabList}/>
    );
}

function WaitingForTestPanel() {
    return (
        <div>Please select an function to create a new test or select and existing test to modify it.</div>
    );
}

export default TestCreatorSection