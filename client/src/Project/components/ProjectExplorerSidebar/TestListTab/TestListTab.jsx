import React, {useEffect} from 'react';
import {useSelector, useDispatch} from "react-redux";

import {selectTestList, selectTestListLoading, selectTestListError} from "../../../../reducers/testListSlice";
import {selectActiveTest, setActiveTest, setActiveUnsavedTest} from "../../../../reducers/activeTestInfoSlice";
import {setActiveFunction} from "../../../../reducers/activeFunctionSlice";

import {isEmpty} from "lodash";

import store from "../../../../reducers/store";

function findFunctionInfoByTestInfo(testInfo) {
    for(const functionInfo of store.getState().functionList.list) {
        if ((testInfo.pathToProject === functionInfo.pathToProject) &&
            (testInfo.fileId === functionInfo.fileId) &&
            (testInfo.functionId === functionInfo.functionId)) {
            return functionInfo;
        }
    }
}

function TestListTab({label}){

    const dispatch = useDispatch();

    const testList = useSelector(selectTestList);
    const testListStateLoading = useSelector(selectTestListLoading);
    const testListError = useSelector(selectTestListError);
    const activeTest = useSelector(selectActiveTest);

    function isActiveTest(testInfo) {
        return (!isEmpty(activeTest)) &&
            (activeTest._id === testInfo._id);
    }

    function onClickCallback(testInfo) {
        dispatch(setActiveFunction(findFunctionInfoByTestInfo(testInfo)));
        /*
        dispatch(setActiveTestAndUnsavedTest({
            unsavedTest: testInfo,
            test: testInfo,
        }));
         */
        dispatch(setActiveUnsavedTest(testInfo));
        dispatch(setActiveTest(testInfo));


    }

    if (testListStateLoading === 'loading') {
        return <div>Loading Test...</div>
    }

    if (testListStateLoading === 'failed') {
        return (
            <>
                <div>Error</div>
                <span>{testListError}</span>
            </>
        );
    }

    return (
        <div className='test-list-tab'>
            <table className="table table-hover">
                <thead>
                <tr>
                    <th scope="col">File Name</th>
                    <th scope="col">Function Name</th>
                    <th scope="col">Function Description</th>
                </tr>
                </thead>
                <tbody>
                {
                    testList.map(testInfo => {
                        return (
                            <tr
                                key={testInfo._id}
                                onClick={() => onClickCallback(testInfo)}
                                className={(isActiveTest(testInfo))?"table-active table-primary":""}
                            >
                                <td>{testInfo.fileId}</td>
                                <td>{testInfo.functionId}</td>
                                <td>{testInfo.customName}</td>
                            </tr>
                        )
                    })
                }
                </tbody>
            </table>
        </div>
    );
}

export default TestListTab;