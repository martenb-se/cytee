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
import cloneDeep from "lodash/cloneDeep";

import {
    formatTableString,
    categorizeList,
    FileNameTableRow
} from "../ProjectExplorerSidebar";

import LoadingComponent from "../../../../shared/components/LoadingComponent";

function FunctionListTab({label}) {

    const dispatch = useDispatch();

    const functionList = useSelector(selectFunctionList);
    const functionListLoadingState = useSelector(selectFunctionListLoading);
    const functionListErrorMessage = useSelector(selectFunctionListError);

    const activeFunction = useSelector(selectActiveFunction);


    function isActiveFunction(funcInfo) {
        return (!isEmpty(activeFunction)) &&
            (activeFunction.pathToProject === funcInfo.pathToProject) &&
            (activeFunction.fileId === funcInfo.fileId) &&
            (activeFunction.functionId === funcInfo.functionId);
    }

    function onClickCallback(functionInfo) {
        dispatch(setActiveFunction(functionInfo));
        dispatch(setActiveUnsavedTest({
            customName: "",
            moduleData: generateInitTestState(),
        }));
        dispatch(setActiveTest({}));
    }

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

    return (
        <div className='function-list-tab'>
            <table className="table table-hover function-list-tab-table">
                <thead>
                <tr className ="table-list-header-row">
                    <th id="function-list-header-col" scope="col">Function Name</th>
                    <th scope="col"># Dep </th>
                    <th scope="col"># Tests </th>
                </tr>
                </thead>
                <tbody className="function-list-table-content">
                {
                    Object.keys(categorizeList(functionList, 'fileId')).sort().map( fileName => {
                        const categorizedFunctionList = categorizeList(functionList, 'fileId');
                        return (
                            <React.Fragment key={fileName}>
                                <FileNameTableRow
                                    fileName={fileName}
                                    colSpan={"3"}
                                    haveFunctionChanged={categorizedFunctionList[fileName].haveFunctionChanged}
                                />
                                {
                                    categorizedFunctionList[fileName].map(funcInf => {
                                      return (
                                          <tr
                                              key={funcInf._id}
                                              title={funcInf.functionId}
                                              onClick={() => onClickCallback(funcInf)}
                                              className={(isActiveFunction(funcInf)?"table-active table-primary":((funcInf.haveFunctionChanged)?"table-warning":""))}
                                          >
                                              <td>{formatTableString(funcInf.functionId, 32)}</td>
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
                </tbody>
            </table>
        </div>
    );
}

/*
                {functionList.map(functionInfo => {
                    return (
                        <tr
                            key={functionInfo._id}
                            onClick={() => onClickCallback(functionInfo)}
                            data-bs-toggle="modal"
                            data-bs-target="#staticBackdrop"
                            className={
                                (isActiveFunction(functionInfo)?"table-active":"") + " "
                            }
                        >
                            {functionNameComponent(functionInfo)}
                            {fileNameComponent(functionInfo)}
                            <td
                                className="function-list-tab-dependencies-col"
                            >{functionInfo.dependencies}</td>
                            <td
                                className="function-list-tab-number-of-test-col"
                            >{functionInfo.numberOfTests}</td>
                            <td>
                                <span
                                    className={(functionInfo.haveFunctionChanged)?"badge bg-warning":"badge bg-success"}
                                >
                                    {(functionInfo.haveFunctionChanged)?"Has been Altered":"Up To Date" }
                                </span>
                            </td>

                        </tr>
                    );
                })}
*/

export default FunctionListTab;