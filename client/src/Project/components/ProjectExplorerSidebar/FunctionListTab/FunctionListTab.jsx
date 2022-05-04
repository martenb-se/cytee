import React, {useEffect, useState} from 'react';

import {useSelector, useDispatch} from "react-redux";
import {
    selectFunctionList,
    selectFunctionListError,
    selectFunctionListLoading
} from '../../../../reducers/functionListSlice';
import {selectActiveFunction, setActiveFunction} from "../../../../reducers/activeFunctionSlice";
import {setActiveUnsavedTest, setActiveTest} from "../../../../reducers/activeTestInfoSlice";
import {generateInitTestState} from "../../../../util/generateInitTestState";

import {isEmpty} from "lodash";

import './FunctionListTab.scss'
import '../ProjectExplorerSidebar.jsx.scss'

import {
    formatTableString,
    categorizeList,
    FileNameTableRow
} from "../ProjectExplorerSidebar";

import {selectTestList} from "../../../../reducers/testListSlice";

import LoadingComponent from "../../../../shared/components/LoadingComponent";
import cloneDeep from "lodash/cloneDeep";

const dependenciesIcon = () => {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
             className="bi bi-arrow-down-left" viewBox="0 0 16 16">
            <path fillRule="evenodd"
                  d="M2 13.5a.5.5 0 0 0 .5.5h6a.5.5 0 0 0 0-1H3.707L13.854 2.854a.5.5 0 0 0-.708-.708L3 12.293V7.5a.5.5 0 0 0-1 0v6z"/>
        </svg>
    );
}

const dependentsIcon = () => {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
             className="bi bi-arrow-up-right" viewBox="0 0 16 16">
            <path fillRule="evenodd"
                  d="M14 2.5a.5.5 0 0 0-.5-.5h-6a.5.5 0 0 0 0 1h4.793L2.146 13.146a.5.5 0 0 0 .708.708L13 3.707V8.5a.5.5 0 0 0 1 0v-6z"/>
        </svg>
    );
}

const testsIcon = () => {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-code-square"
             viewBox="0 0 16 16">
            <path
                d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/>
            <path
                d="M6.854 4.646a.5.5 0 0 1 0 .708L4.207 8l2.647 2.646a.5.5 0 0 1-.708.708l-3-3a.5.5 0 0 1 0-.708l3-3a.5.5 0 0 1 .708 0zm2.292 0a.5.5 0 0 0 0 .708L11.793 8l-2.647 2.646a.5.5 0 0 0 .708.708l3-3a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708 0z"/>
        </svg>
    );
}

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

function sortFunctionList(functionList, sortAttribute, sortOrder) {
    const functionListClone = cloneDeep(functionList);
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
    return functionListClone.sort(sortList);
}

function getFunctionsWithTestList(testList) {

    let functionsWithTestList = []
    for (const testInfo of testList) {
        const functionIndex = functionsWithTestList.findIndex(
            testInf => testInf.functionId === testInfo.functionId
        );
        if (functionIndex === -1) {
            functionsWithTestList.push(testInfo.functionId);
        }
    }

    return functionsWithTestList;
}

function isFileTested(fileName, testList) {
    for (const testInfo of testList)
        if (testInfo.fileId === fileName)
            return true;
    return false;
}

function isFunctionTested(functionName, testList) {
    for (const testInfo of testList)
        if (testInfo.functionId === functionName)
            return true;
    return false;
}

function haveFileChange(fileFunctionList) {
    for (const funcInf of fileFunctionList)
        if (funcInf.haveFunctionChanged)
            return true;
    return false;
}



function FunctionListTab({label}) {

    const dispatch = useDispatch();

    const functionList = useSelector(selectFunctionList);
    const functionListLoadingState = useSelector(selectFunctionListLoading);

    const testList = useSelector(selectTestList);

    const functionListErrorMessage = useSelector(selectFunctionListError);
    const activeFunction = useSelector(selectActiveFunction);

    const [sortAttribute, setSortAttribute] = useState('functionId');
    const [sortOrder, setSortOrder] = useState('lowToHigh');

    function onClickCallback(functionInfo) {
        dispatch(setActiveFunction(functionInfo));
        dispatch(setActiveUnsavedTest({
            customName: "",
            moduleData: generateInitTestState(),
        }));
        dispatch(setActiveTest({}));
    }

    function onHeaderColClickCallback(headerAttribute) {
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

    function isActiveFunction(funcInfo) {
        return (!isEmpty(activeFunction)) &&
            (activeFunction.pathToProject === funcInfo.pathToProject) &&
            (activeFunction.fileId === funcInfo.fileId) &&
            (activeFunction.functionId === funcInfo.functionId);
    }

    useEffect(() => {
        // Set sort order depending on current sortAttribute
        if (
            (sortAttribute === 'dependencies') ||
            (sortAttribute === 'dependents') ||
            (sortAttribute === 'numberOfTests')
        ) {
            setSortOrder('highToLow');
        } else {
            setSortOrder('lowToHigh');
        }
    }, [sortAttribute])

    if ((functionListLoadingState === 'loading') ||
        (functionListLoadingState === '')) {
        return <LoadingComponent />
    }

    if (functionListLoadingState === 'failed'){
        return (
            <>
                <div>Error</div>
                <span>{functionListErrorMessage}</span>
            </>
        );
    }

    if (testList === undefined) {
        return <LoadingComponent />
    }

    return (
        <div className='function-list-tab'>

            <table className="table table-hover function-list-tab-table">
                <thead>
                <tr className ="table-list-header-row">
                    <th
                        className ="col-auto"
                        onClick={onSortOrderClickCallback}
                    >{(sortOrder==='lowToHigh')?downArrowIcon():upArrowIcon()}</th>
                    <FunctionNameHeaderCol onClickCallback={onHeaderColClickCallback}/>
                    <DependentsHeaderCol onClickCallback={onHeaderColClickCallback}/>
                    <DependenciesHeaderCol onClickCallback={onHeaderColClickCallback}/>
                    <TestsHeaderCol onClickCallback={onHeaderColClickCallback}/>
                </tr>
                </thead>
                <tbody className="function-list-table-content">
                    <FunctionListTableContent
                        functionList={functionList}
                        testList={testList}
                        sortAttribute={sortAttribute}
                        sortOrder={sortOrder}
                        onClickCallback={onClickCallback}
                        isActiveFunction={isActiveFunction}
                    />
                </tbody>
            </table>
        </div>
    );
}

function FunctionNameHeaderCol({onClickCallback}) {
    return (
        <th
            className ="function-list-header-col"
            scope="col"
            title="Function Name"
            onClick={() => onClickCallback('functionId')}
        >
          Function Name
        </th>
    );
}

function DependentsHeaderCol({onClickCallback}) {
    return (
        <th
            className ="function-list-header-col"
            scope="col"
            title="dependents"
            onClick={() => onClickCallback('dependents')}
        >
          {dependentsIcon()}
        </th>
    );
}

function DependenciesHeaderCol({onClickCallback}) {
    return (
        <th
            className ="function-list-header-col"
            scope="col"
            title="dependencies"
            onClick={() => onClickCallback('dependencies')}
        >
            {dependenciesIcon()}
        </th>
    );
}

function TestsHeaderCol({onClickCallback}) {
    return (
        <th
            className ="function-list-header-col"
            scope="col"
            title="Number of tests"
            onClick={() => onClickCallback('numberOfTests')}
        >
            {testsIcon()}
        </th>
    );
}

function FunctionListTableContent({functionList, testList, sortAttribute, sortOrder, onClickCallback, isActiveFunction}) {

    const categorizedFunctionList = categorizeList(
        sortFunctionList(functionList, sortAttribute, sortOrder),
        'fileId'
    );

    return (
      <>
          {
              Object.keys(categorizedFunctionList).map(fileName => {
                  return (
                      <React.Fragment key={fileName}>
                          <FileNameTableRowFunctionList
                            fileName={fileName}
                            testList={testList}
                            colSpan={"2"}
                            fileFunctionList={categorizedFunctionList[fileName]}

                          />
                          {
                              categorizedFunctionList[fileName].map(funcInf => {
                                  return (
                                      <tr
                                        key={funcInf._id}
                                        title={funcInf.functionId}
                                        onClick={() => onClickCallback(funcInf)}
                                        className={(isActiveFunction(funcInf))?(
                                            "table-active table-primary"
                                        ) : (
                                            (isFunctionTested(funcInf.functionId, testList) && funcInf.haveFunctionChanged)? (
                                                "table-warning"
                                            ) : (
                                                ""
                                            )
                                        )}
                                      >
                                          <td
                                            colSpan="2"

                                          >
                                              <span className="function-list-function-name">
                                                {formatTableString(funcInf.functionId, 32)}
                                              </span>
                                          </td>
                                          <td>{funcInf.dependents}</td>
                                          <td>{funcInf.dependencies}</td>
                                          <td>{funcInf.numberOfTests}</td>
                                      </tr>
                                  )
                              })
                          }
                      </React.Fragment>
                  )
              })
          }
      </>
    );

}

function FileNameTableRowFunctionList({fileName, testList, fileFunctionList, colSpan}) {

    return (
        <tr
            className ="table-secondary"
        >
            <td
                title={fileName}
                colSpan={colSpan}
                className="col"
            >
                <div className ="d-flex flex-row">
                    {
                        (isFileTested(fileName, testList) && haveFileChange(fileFunctionList))?(
                            <span className="function-list-change-badge badge bg-warning text-black">{clockIcon()}</span>
                        ):(
                            <span className="function-list-change-badge badge bg-success">{checkIcon()}</span>
                        )
                    }
                    <span className ="bold function-list-file-name">
                        {formatTableString(fileName, 32)}
                    </span>
                </div>
            </td>
            <td
                className ="bold"
            >
                {fileFunctionList.reduce((prev, curr) => prev + curr.dependents, 0)}
            </td>
            <td
                className ="bold"
            >
                {fileFunctionList.reduce((prev, curr) => prev + curr.dependencies, 0)}
            </td>
            <td
                className ="bold"
            >
                {fileFunctionList.reduce((prev, curr) => prev + curr.numberOfTests, 0)}
            </td>
        </tr>
    );
}

export default FunctionListTab;