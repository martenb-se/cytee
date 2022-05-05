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

import LoadingComponent from "../../../../shared/components/LoadingComponent";

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
                    <th title="dependents" scope="col">{dependentsIcon()}</th>
                    <th title="dependencies" scope="col">{dependenciesIcon()}</th>
                    <th title="tests" scope="col">{testsIcon()}</th>
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
                                    colSpan={"4"}
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
                </tbody>
            </table>
        </div>
    );
}

export default FunctionListTab;