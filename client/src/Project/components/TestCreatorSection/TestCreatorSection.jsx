import React, {useState, useEffect, createContext, useContext, useReducer} from 'react';
import {useDispatch, useSelector} from "react-redux";

import {isEmpty, isEqual} from "lodash";

import {
    selectActiveFunction,
    clearChanges,
    selectActiveFunctionLoadingState
} from '../../../reducers/activeFunctionSlice';
import {
    deleteTestInfo,
    discardUnsavedChanges,
    selectActiveTest,
    selectActiveTestLoadingState,
    setActiveTest,
    updateTestInfo,

} from '../../../reducers/activeTestInfoSlice';
import {fetchTestList, selectTestList, selectTestListLoading} from '../../../reducers/testListSlice'

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
import {fetchFunctionList, selectFunctionListLoading} from "../../../reducers/functionListSlice";

export const moduleNameMapper= {
    argumentList: 'Arguments',
    returnValue: 'Return Value',
    exception: 'Exception',
}

const initLocalTabState = [];

export const localTabGroupContext = createContext();
const { Provider } = localTabGroupContext;

function localTabGroupReducer(state, action) {
    switch(action.type) {
        case 'addChildTab':
            const addChildLocalTabsClone = cloneDeep(state);
            if (addChildLocalTabsClone.findIndex(childTab => childTab.eventKey === action.payload.eventKey) === -1) {
                addChildLocalTabsClone.push(cloneDeep(action.payload));
            }
            return addChildLocalTabsClone;
        case 'removeChildTab':
            const removeChildLocalTabsClone = cloneDeep(state);
            const childIndex = removeChildLocalTabsClone.findIndex(childTab => childTab.eventKey === action.payload);
            if (childIndex !== -1) {
                removeChildLocalTabsClone.splice(childIndex, 1);
            }
            return removeChildLocalTabsClone;
        case 'removeAllChildTabs':
            return [];

    }
}


function TestCreatorSection() {

    const activeFunction = useSelector(selectActiveFunction);
    const test = useSelector(selectActiveTest);

    const [localTabState, localTabDispatch] = useReducer(localTabGroupReducer, initLocalTabState);

    useEffect(() => {
        localTabDispatch({
            type:'removeAllChildTabs'
        });
    }, [test, activeFunction])

    if (isEmpty(activeFunction)) {
        return <WaitingForTestPanel />
    }

    return (
        <Provider value={[localTabState, localTabDispatch]}>
            <div className="test-creator-section-wrapper h-100 border-top row flex-row">
                <div className = "col-2 test-creator-section-wrapper-header">
                    <ModulePanel />
                </div>
                <div className ="col-10 test-creator-section-wrapper-content">
                    <TestCreatorHeaderSection />
                    <TestCreatorTabGroup />
                </div>
            </div>
        </Provider>
    )
}

function TestCreatorHeaderSection() {

    const unsavedTest = useSelector(selectUnsavedActiveTest);

    const activeFunction = useSelector(selectActiveFunction);
    const activeFunctionLoadingState = useSelector(selectActiveFunctionLoadingState);

    const test = useSelector(selectActiveTest);
    const testLoadingState = useSelector(selectActiveTestLoadingState);

    const functionListLoadingState = useSelector(selectFunctionListLoading);

    const projectPath = useSelector(state => state.project.path);

    const dispatch = useDispatch();

    const [createLoadingState, setCreateLoadingState] = useState('');
    const [updateLoadingState, setUpdateLoadingState] = useState('');
    const [deleteLoadingState, setDeleteLoadingState] = useState('');
    const [clearLoadingState, setClearLoadingState] = useState('');
    const [fetchingFunctionListLoadingState, setFetchingFunctionListLoadingState] = useState('');

    const [tabState, tabDispatch] = useContext(localTabGroupContext);


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

    useEffect(() => {
        if (clearLoadingState === "loading") {
            if (activeFunctionLoadingState === "succeeded") {
                dispatch(fetchFunctionList(projectPath));
                setClearLoadingState('');
                setFetchingFunctionListLoadingState('loading');
            }
        }
    }, [activeFunctionLoadingState])

    useEffect(() => {
       if (fetchingFunctionListLoadingState === 'loading') {
           dispatch(fetchTestList(projectPath));
           setFetchingFunctionListLoadingState('');
       }
    }, [functionListLoadingState])

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
        tabDispatch({
            type: 'removeAllChildTabs',
        });
        dispatch(discardUnsavedChanges({}));
    }

    function cancelCallback(e) {
        e.preventDefault();
        tabDispatch({
           type: 'removeAllChildTabs',
        });
        dispatch(setActiveUnsavedTest({
            customName: "",
            moduleData: generateInitTestState(),
        }));
    }

    function onCustomNameChangeCallback(e) {
        e.preventDefault();
        dispatch(updateUnsavedCustomName(e.target.value));
    }

    function onTestShouldPersistCallback(e) {
        e.preventDefault();
        dispatch(clearChanges({}));
        setClearLoadingState('loading');

    }

    return (
        <form>
            <div className ="test-creator-section-header">
                <div className ="btn-group">
                    {
                        (isEmpty(test))? (
                            <>
                                <button
                                    className ="btn btn-primary"
                                    onClick={createTestCallback}
                                >
                                    Create Test
                                </button>
                                <button
                                    className ="btn btn-primary"
                                    onClick={cancelCallback}
                                >
                                    Cancel
                                </button>
                            </>
                        ) : (
                            (activeFunction.haveFunctionChanged) ? (
                                <>
                                    <button
                                        className ="btn btn-warning"
                                        onClick={onTestShouldPersistCallback}
                                    >
                                        Test Should Persist
                                    </button>
                                    <button
                                        className="btn btn-danger"
                                        onClick ={(e) => {
                                            deleteTestCallback(e);
                                            onTestShouldPersistCallback(e);
                                        }}
                                    >
                                        Delete
                                    </button>
                                </>


                            ) : (
                                <>
                                    <button
                                        className ="btn btn-primary"
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
                                    >
                                        Discard Changes
                                    </button>
                                    <button
                                        className="btn btn-danger"
                                        onClick ={deleteTestCallback}
                                    >
                                        Delete
                                    </button>
                                </>
                            )
                        )
                    }
                </div>
            </div>

            <div>
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

    if (isEmpty(test)) {
        return (
            <form>
                <div className="test-creator-section-header flex-column">
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

function WaitingForTestPanel() {
    return (
        <div className=" d-flex ">
            <div className ="alert alert-secondary">
                <h4 className="alert-heading">Info </h4>
                Please select an function to create a new test or select and existing test to modify it. When you are done creating tests press the button labeled 'generate tests'.
            </div>
        </div>
    );
}

export default TestCreatorSection