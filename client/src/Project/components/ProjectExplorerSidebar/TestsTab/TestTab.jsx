import React, {useEffect} from 'react';
import {useSelector, useDispatch} from "react-redux";

import {selectTestList, selectTestListLoading, selectTestListError} from "../../../../reducers/testListSlice";
import {selectActiveTest, setActiveTest} from "../../../../reducers/activeTestInfoSlice";
import {setActiveFunction} from "../../../../reducers/activeFunctionSlice";

import CustomTab from "../../../../shared/components/Tab";
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

function testTabGenerator(){

    const dispatch = useDispatch();

    const testList = useSelector(selectTestList);
    const testListStateLoading = useSelector(selectTestListLoading);
    const testListError = useSelector(selectTestListError);
    const activeTest = useSelector(selectActiveTest);

    function isActiveTest(testInfo) {
        return (!isEmpty(activeTest)) &&
            (activeTest._id === testInfo._id);
    }

    if (testListStateLoading === 'loading') {
        return <div>Loading</div>
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
        <CustomTab label='Test Tab'>
            <div>Test Tab</div>
            <table>
                <thead>
                <tr>
                    <th>File Name</th>
                    <th>Function Name</th>
                    <th>Function Description</th>
                </tr>
                </thead>
                <tbody>
                {
                    testList.map(testInfo => {
                        return (
                            <tr
                                key={testInfo._id}
                                onClick={() => {
                                    dispatch(setActiveTest(testInfo));
                                    dispatch(setActiveFunction(findFunctionInfoByTestInfo(testInfo)));
                                }}
                                className={(isActiveTest(testInfo))?"active-test-info":""}
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
        </CustomTab>
    );
}

export default testTabGenerator;