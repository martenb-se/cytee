import React, {useEffect} from 'react';
import {useSelector, useDispatch} from "react-redux";

import {selectTestList, selectTestListLoading, selectTestListError} from "../../../../reducers/testListSlice";
import {selectActiveTest, setActiveTest, setActiveUnsavedTest} from "../../../../reducers/activeTestInfoSlice";
import {selectActiveFunction, setActiveFunction} from "../../../../reducers/activeFunctionSlice";

import {isEmpty} from "lodash";

import store from "../../../../reducers/store";

import './TestListTab.scss';
import '../ProjectExplorerSidebar.jsx.scss';

import {FileNameTableRow, formatTableString, categorizeList} from "../ProjectExplorerSidebar";
import LoadingComponent from "../../../../shared/components/LoadingComponent";

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

    useEffect(() => {

    }, [testList])

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
        return <LoadingComponent />
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
                <thead >
                <tr className ="table-list-header-row">
                    <th scope="col">Function Name</th>
                    <th scope="col">Function Description</th>
                </tr>
                </thead>
                <tbody>
                {
                    Object.keys(categorizeList(testList, 'fileId')).sort().map( fileName => {
                        const categorizedTestList = categorizeList(testList, 'fileId');
                        const firstFuncInf= findFunctionInfoByTestInfo(categorizedTestList[fileName][0]);
                        return (
                            <React.Fragment key={fileName}>
                                <FileNameTableRow
                                    fileName ={fileName}
                                    colSpan={"3"}
                                    haveFunctionChanged={firstFuncInf.haveFunctionChanged}
                                />
                                {
                                    categorizedTestList[fileName].map(testInf => {
                                        const funcInfo = findFunctionInfoByTestInfo(testInf);
                                        return (
                                            <tr
                                                key={testInf._id}
                                                onClick={() => onClickCallback(testInf)}
                                                className={(isActiveTest(testInf))?"table-active table-primary ":((funcInfo.haveFunctionChanged)?"table-warning":"")}
                                            >
                                                <td>{formatTableString(testInf.functionId)}</td>
                                                <td>{formatTableString(testInf.customName)}</td>
                                            </tr>
                                        )
                                    })
                                }
                            </React.Fragment>
                        )
                    })
                }
                </tbody>
            </table>
        </div>
    );
}

export default TestListTab;