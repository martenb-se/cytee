import React, {useState, useEffect, createContext, useContext, useReducer} from 'react';
import {useDispatch, useSelector} from "react-redux";
import store from '../../../reducers/store';

import {isEmpty, isEqual} from "lodash";

// import redux selectors
import {selectActiveFunction} from '../../../reducers/activeFunctionSlice';
import {
    deleteTestInfo,
    discardUnsavedChanges,
    selectActiveTest,
    selectActiveTestLoadingState,
    setActiveTest,
    setActiveTestEmpty,
    updateTestInfo,

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
import TestCreatorTabGroup from "./TestCreatorTabGroup/TestCreatorTabGroup";

import {
    selectUnsavedActiveTest,
    updateUnsavedCustomName,
    setActiveUnsavedTest
} from "../../../reducers/activeTestInfoSlice";

import {saveTestInfo} from "../../../reducers/activeTestInfoSlice";
import cloneDeep from "lodash/cloneDeep";
import {generateInitTestState} from "../../../util/generateInitTestState";

import './TestCreatorSection.scss'

export const moduleNameMapper= {
    argumentList: 'Arguments',
    returnValue: 'Return Value',
    exception: 'Exception',
}

function TestCreatorSection() {

    const activeFunction = useSelector(selectActiveFunction);

    if (isEmpty(activeFunction)) {
        return <WaitingForTestPanel />
    }

    return (
        <div className="test-creator-section-wrapper border-top row">
            <div className = "col-3">
                <ModulePanel />
            </div>
            <div className ="col-9">
                <TestCreatorHeaderSection />
                <TestCreatorTabGroup />
            </div>
        </div>
    );
}

function TestCreatorHeaderSection() {

    const unsavedTest = useSelector(selectUnsavedActiveTest);
    const test = useSelector(selectActiveTest);
    const testLoadingState = useSelector(selectActiveTestLoadingState);
    const projectPath = useSelector(state => state.project.path);
    const dispatch = useDispatch();

    const [createLoadingState, setCreateLoadingState] = useState('');
    const [updateLoadingState, setUpdateLoadingState] = useState('');
    const [deleteLoadingState, setDeleteLoadingState] = useState('');

    useEffect(() => {
        if (createLoadingState === "loading") {
            if (testLoadingState === "succeeded") {
                dispatch(setActiveUnsavedTest(test));
                dispatch(fetchTestList(projectPath));
                setCreateLoadingState('');
            }

        } else if (updateLoadingState === "loading") {
            if (testLoadingState === "succeeded") {
                dispatch(fetchTestList(projectPath));
                setUpdateLoadingState('');
            }

        } else if (deleteLoadingState === "loading") {
            if (testLoadingState === "succeeded") {
                dispatch(fetchTestList(projectPath));
                dispatch(setActiveUnsavedTest({
                    customName: "",
                    moduleData: generateInitTestState()
                }))
                dispatch(setActiveTest({}));
                setDeleteLoadingState('');
            }
        }
    }, [testLoadingState])

    function createTestCallback(e) {
        e.preventDefault();
        dispatch(saveTestInfo({}));
        setCreateLoadingState("loading");
    }

    function updateTestCallback(e) {
        e.preventDefault();
        dispatch(updateTestInfo({}));
        setUpdateLoadingState("loading");
    }

    function deleteTestCallback(e) {
        e.preventDefault();
        dispatch(deleteTestInfo({}));
        setDeleteLoadingState('loading');
    }

    function discardTestCallback(e) {
        e.preventDefault();
        dispatch(discardUnsavedChanges({}));
    }

    function cancelCallback(e) {
        e.preventDefault();
        dispatch(setActiveUnsavedTest({
            customName: "",
            moduleData: generateInitTestState(),
        }));
    }

    function onCustomNameChangeCallback(e) {
        e.preventDefault();
        dispatch(updateUnsavedCustomName(e.target.value));
    }

    if (isEmpty(test)) {
        return (
            <form>

                <div className="test-creator-section-header">
                    <div className="btn-group">
                        <button
                            className="btn btn-primary"
                            onClick={createTestCallback}
                            disabled={testLoadingState==='loading'}
                        >
                            Create Test
                        </button>
                        <button
                            className="btn btn-primary"
                            onClick={cancelCallback}
                            disabled={testLoadingState==='loading'}
                        >
                            Cancel
                        </button>
                    </div>
                </div>

                <div className="mb-3">
                    <label htmlFor="test-creator-section-custom-name-input">Custom Name</label>
                    <input
                        className="test-creator-section-custom-name-input form-control"
                        type="text"
                        onChange={onCustomNameChangeCallback}
                        value={unsavedTest.customName}
                        disabled={testLoadingState==='loading'}
                    />
                </div>

            </form>
        );
    }

    return (
        <form>
            <div className="test-creator-section-header">
                <div className="btn-group">
                    <button
                        className="btn btn-primary"
                        onClick={updateTestCallback}
                        disabled={
                        (testLoadingState==='loading') || (isEqual(unsavedTest, test))
                    }
                    >
                        Save Test
                    </button>
                    <button
                        className="btn btn-primary"
                        onClick={discardTestCallback}
                        disabled={
                        (testLoadingState==='loading') || (isEqual(unsavedTest, test))
                    }
                    >
                        Discard Changes
                    </button>
                    <button
                        className="btn btn-danger"
                        onClick={deleteTestCallback}
                        disabled={testLoadingState==='loading'}
                    >
                        Delete
                    </button>
                </div>
            </div>
            <div className="mb-3">
                <label htmlFor="test-creator-section-custom-name-input">Custom Name</label>
                <input
                    className="test-creator-section-custom-name-input form-control"
                    type="text"
                    onChange={onCustomNameChangeCallback}
                    value={unsavedTest.customName}
                    disabled={testLoadingState==='loading'}
                />
            </div>
        </form>
    );

}

/*

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
        dispatch(deleteTestInfo());
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
            customName: unsavedTestInfoState.customName
        }))
    }

    function changeName(e) {
        unsavedTestInfoDispatch({type: 'customName/rename', payload: e.target.value});
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
                        customName: unsavedTestInfoState.customName,
                        moduleData: unsavedTestInfoState.moduleData,
                        _id: activeTest._id,
                    }

                    dispatch(setActiveTest(newActiveTestState));
                    unsavedTestInfoDispatch({type:'setModuleData', payload: newActiveTestState})
                } else if (loadingState === 'waitingForTestListDeleted') {
                    dispatch(setActiveTestEmpty());
                    unsavedTestInfoDispatch({type:'clearModelData'});
                }
            }
        }
    }, [testListLoadingState]);

    if (unsavedTestInfoState === undefined) {
        return (
            <div>Processing Data...</div>
        );
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
                        setCustomNameFunc={changeName}
                    />
                    <TestCreatorTabGroup />
                </div>
            </div>
        </ Provider>
    )
}

function TestCreatorSectionHeader({createTestFunc, editTestFunc, removeTestFunc, setCustomNameFunc}) {

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
            <input type='text' value={state.customName} onChange={setCustomNameFunc}/>
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
*/
function WaitingForTestPanel() {
    return (
        <div>Please select an function to create a new test or select and existing test to modify it.</div>
    );
}

export default TestCreatorSection