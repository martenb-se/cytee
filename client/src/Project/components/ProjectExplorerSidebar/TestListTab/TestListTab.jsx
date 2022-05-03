import React, {useEffect} from 'react';
import {useSelector, useDispatch} from "react-redux";

import {selectTestList, selectTestListLoading, selectTestListError} from "../../../../reducers/testListSlice";
import {selectActiveTest, setActiveTest, setActiveUnsavedTest} from "../../../../reducers/activeTestInfoSlice";
import {selectActiveFunction, setActiveFunction} from "../../../../reducers/activeFunctionSlice";

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

    function testListTableRow(testInfo) {

        const funcInfo =findFunctionInfoByTestInfo(testInfo);
        if (!funcInfo.haveFunctionChanged) {
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
            );
        } else {
            return (
                <tr
                    key={testInfo._id}
                    onClick={() => onClickCallback(testInfo)}
                    className={((isActiveTest(testInfo))?"table-active table-primary":"") + (" table-warning")}
                >
                    <td>{testInfo.fileId}</td>
                    <td>{testInfo.functionId}</td>
                    <td>{testInfo.customName}</td>
                    <td>
                        {/*https://icons.getbootstrap.com/icons/exclamation-triangle/*/}
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                             className="bi bi-exclamation-triangle" viewBox="0 0 16 16">
                            <path
                                d="M7.938 2.016A.13.13 0 0 1 8.002 2a.13.13 0 0 1 .063.016.146.146 0 0 1 .054.057l6.857 11.667c.036.06.035.124.002.183a.163.163 0 0 1-.054.06.116.116 0 0 1-.066.017H1.146a.115.115 0 0 1-.066-.017.163.163 0 0 1-.054-.06.176.176 0 0 1 .002-.183L7.884 2.073a.147.147 0 0 1 .054-.057zm1.044-.45a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566z"/>
                            <path
                                d="M7.002 12a1 1 0 1 1 2 0 1 1 0 0 1-2 0zM7.1 5.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995z"/>
                        </svg>
                    </td>
                </tr>
                )
        }
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
                    testList.map(testInfo => testListTableRow(testInfo))
                }
                </tbody>
            </table>
        </div>
    );
}

export default TestListTab;