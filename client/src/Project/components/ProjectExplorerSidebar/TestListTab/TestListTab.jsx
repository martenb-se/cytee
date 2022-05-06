import React, {useEffect, useState} from 'react';
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
import cloneDeep from "lodash/cloneDeep";

const checkIcon = () => {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-check"
             viewBox="0 0 16 16">
            <path
                d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"/>
        </svg>
    );
}

const clockIcon = () => {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-clock"
             viewBox="0 0 16 16">
            <path d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"/>
            <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z"/>
        </svg>
    );
}

const upArrowIcon = () => {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-sort-down"
             viewBox="0 0 16 16">
            <path
                d="M3.5 2.5a.5.5 0 0 0-1 0v8.793l-1.146-1.147a.5.5 0 0 0-.708.708l2 1.999.007.007a.497.497 0 0 0 .7-.006l2-2a.5.5 0 0 0-.707-.708L3.5 11.293V2.5zm3.5 1a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7a.5.5 0 0 1-.5-.5zM7.5 6a.5.5 0 0 0 0 1h5a.5.5 0 0 0 0-1h-5zm0 3a.5.5 0 0 0 0 1h3a.5.5 0 0 0 0-1h-3zm0 3a.5.5 0 0 0 0 1h1a.5.5 0 0 0 0-1h-1z"/>
        </svg>
    );
}

const downArrowIcon = () => {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
             className="bi bi-sort-down-alt" viewBox="0 0 16 16">
            <path
                d="M3.5 3.5a.5.5 0 0 0-1 0v8.793l-1.146-1.147a.5.5 0 0 0-.708.708l2 1.999.007.007a.497.497 0 0 0 .7-.006l2-2a.5.5 0 0 0-.707-.708L3.5 12.293V3.5zm4 .5a.5.5 0 0 1 0-1h1a.5.5 0 0 1 0 1h-1zm0 3a.5.5 0 0 1 0-1h3a.5.5 0 0 1 0 1h-3zm0 3a.5.5 0 0 1 0-1h5a.5.5 0 0 1 0 1h-5zM7 12.5a.5.5 0 0 0 .5.5h7a.5.5 0 0 0 0-1h-7a.5.5 0 0 0-.5.5z"/>
        </svg>
    );
}

function findFunctionInfoByTestInfo(testInfo) {
    for(const functionInfo of store.getState().functionList.list) {
        if ((testInfo.pathToProject === functionInfo.pathToProject) &&
            (testInfo.fileId === functionInfo.fileId) &&
            (testInfo.functionId === functionInfo.functionId)) {
            return functionInfo;
        }
    }
}

function findIfFunctionsHaveChangedByFile(fileName) {
    for (const functionInfo of store.getState().functionList.list) {
        if ((functionInfo.fileId === fileName) && functionInfo.haveFunctionChanged) {
            return true
        }
    }
    return false;
}

function sortTestList(testList, sortAttribute, sortOrder) {
    const testListClone = cloneDeep(testList);
    function sortList(a, b) {
        if (sortOrder === 'highToLow') {
            if (a[sortAttribute] > b[sortAttribute])
                return -1;
            else if (a[sortAttribute] < b[sortAttribute])
                return 1;
            else
                return 0;
        } else {
            if (a[sortAttribute] < b[sortAttribute])
                return -1;
            else if (a[sortAttribute] > b[sortAttribute])
                return 1;
            else
                return 0;
        }

    }
    return testListClone.sort(sortList);
}

function TestListTab({label}){

    const dispatch = useDispatch();

    const testList = useSelector(selectTestList);
    const testListStateLoading = useSelector(selectTestListLoading);
    const testListError = useSelector(selectTestListError);
    const activeTest = useSelector(selectActiveTest);

    const [sortAttribute, setSortAttribute] = useState('functionId');
    const [sortOrder, setSortOrder] = useState('lowToHigh');

    function isActiveTest(testInfo) {
        return (!isEmpty(activeTest)) &&
            (activeTest._id === testInfo._id);
    }

    function onClickCallback(testInfo) {
        dispatch(setActiveFunction(findFunctionInfoByTestInfo(testInfo)));
        dispatch(setActiveUnsavedTest(testInfo));
        dispatch(setActiveTest(testInfo));
    }

    function onAttributeClickCallback(headerAttribute) {
        if (sortAttribute === headerAttribute) {
            if (sortOrder === 'lowToHigh') {
                setSortOrder('highToLow');
            } else {
                setSortOrder('lowToHigh');
            }
        } else {
            setSortAttribute(headerAttribute);
        }
    }

    function onSortOrderClickCallback() {
        if (sortOrder === 'lowToHigh') {
            setSortOrder('highToLow');
        } else {
            setSortOrder('lowToHigh');
        }
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
                <thead>
                    <tr className ="table-list-header-row">
                        <th
                            className ="col-auto"
                            scope="col"
                            onClick={onSortOrderClickCallback}
                        >
                            {(sortOrder==='lowToHigh')?downArrowIcon():upArrowIcon()}
                        </th>
                        <th
                            className ="test-list-header-col"
                            scope="col"
                            onClick={() => onAttributeClickCallback('functionId')}
                        >
                            Function Name
                        </th>
                        <th
                            className ="test-list-header-col"
                            scope="col"
                            onClick={() => onAttributeClickCallback('customName')}
                        >
                            Function Description
                        </th>
                    </tr>
                </thead>
                <tbody>
                {
                    Object.keys(categorizeList(sortTestList(testList, sortAttribute, sortOrder), 'fileId')).map( fileName => {
                        const categorizedTestList = categorizeList(sortTestList(testList, sortAttribute, sortOrder), 'fileId');
                        const haveCorrespondingFunctionChanged = findIfFunctionsHaveChangedByFile(fileName);
                        return (
                            <React.Fragment key={fileName}>
                                <FileNameTableRowTestList
                                    fileName ={fileName}
                                    colSpan={"3"}
                                    haveFunctionChanged={haveCorrespondingFunctionChanged}
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
                                                <td
                                                    title={testInf.functionId}
                                                    colSpan={"2"}
                                                >
                                                    {formatTableString(testInf.functionId, 32)}
                                                </td>
                                                <td
                                                    title={testInf.customName}
                                                >
                                                    {formatTableString(testInf.customName, 32)}
                                                </td>
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

function FileNameTableRowTestList({fileName,colSpan, haveFunctionChanged}) {
    return (
        <tr className ="table-secondary">
            <td
                title={fileName}
                colSpan={colSpan}
            >
                <div className ="d-flex flex-row">
                    {
                        (haveFunctionChanged)? (
                            <span className="test-list-change-badge badge bg-warning text-black">
                                {clockIcon()}
                            </span>
                        ) : (
                            <span className="test-list-change-badge badge bg-success ">
                                {checkIcon()}
                            </span>
                        )
                    }
                <span className="bold">
                    {formatTableString(fileName, 32)}
                </span>
                </div>
            </td>
        </tr>
    );
}

export default TestListTab;